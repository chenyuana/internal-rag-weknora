package service

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/Tencent/WeKnora/internal/searchutil"
	"github.com/Tencent/WeKnora/internal/types"
)

var figureNumber = regexp.MustCompile(`(?i)\b(?:fig(?:ure)?\.?)\s*((?:[A-Z][.-])?\d+(?:[.-]\d+)*)\b`)
var figureSequence = regexp.MustCompile(`(?i)\bfig(?:ure)?s?\.?\s*(?:[A-Z][.-])?\d+(?:[.-]\d+)*(?:\s*(?:,|and|&|和|与)\s*(?:[A-Z][.-])?\d+(?:[.-]\d+)*)*`)
var numberInSequence = regexp.MustCompile(`(?:[A-Z][.-])?\d+(?:[.-]\d+)*`)
var markdownImage = regexp.MustCompile(`(?s)!\[([^]]*)\]\((https?://[^)\s]+)\)`)

func referencedFigureNumbers(content string) []string {
	seen := make(map[string]bool)
	var numbers []string
	for _, sequence := range figureSequence.FindAllString(content, -1) {
		for _, number := range numberInSequence.FindAllString(sequence, -1) {
			number = strings.ToLower(strings.ReplaceAll(number, "-", "."))
			if !seen[number] {
				seen[number] = true
				numbers = append(numbers, number)
			}
		}
	}
	return numbers
}

// attachRelatedImages adds figures explicitly identified by number or caption. Merely
// sharing a document or page is insufficient evidence that a picture belongs
// to the passage, and would show unrelated figures for broad text answers.
func (s *sessionService) attachRelatedImages(ctx context.Context, refs []*types.SearchResult) {
	if s.chunkService == nil {
		return
	}
	repo := s.chunkService.GetRepository()
	if repo == nil {
		return
	}
	byKnowledge := make(map[string][]*types.Chunk)
	failed := make(map[string]bool)
	for _, ref := range refs {
		if ref == nil || ref.KnowledgeID == "" || ref.ChunkType == "web_search" {
			continue
		}
		wanted := referencedFigureNumbers(ref.Content)

		if _, ok := byKnowledge[ref.KnowledgeID]; !ok && !failed[ref.KnowledgeID] {
			if len(byKnowledge)+len(failed) >= 4 {
				continue
			}
			chunks, err := repo.ListChunksByKnowledgeIDAndTypes(
				ctx, types.MustTenantIDFromContext(ctx), ref.KnowledgeID,
				[]types.ChunkType{types.ChunkTypeText, types.ChunkTypeParentText},
			)
			if err != nil {
				failed[ref.KnowledgeID] = true
				continue
			}
			byKnowledge[ref.KnowledgeID] = chunks
		}
		images := relatedTableImages(ref.Content, byKnowledge[ref.KnowledgeID])
		images = append(images, relatedCaptionImages(ref.Content, wanted, byKnowledge[ref.KnowledgeID])...)
		for _, image := range images {
			if len(ref.RelatedImages) >= 12 {
				break
			}
			exists := false
			for _, old := range ref.RelatedImages {
				if old.URL == image.URL {
					exists = true
					break
				}
			}
			if !exists {
				ref.RelatedImages = append(ref.RelatedImages, image)
			}
		}
	}
}

var tableHeading = regexp.MustCompile(`(?im)^\s*Table\s+([IVXLCDM]+|[0-9]+)\b`)
var tableMention = regexp.MustCompile(`(?i)\bTable\s+([IVXLCDM]+|[0-9]+)\b`)

// Recover table assets independently of parser alt labels. For legacy data,
// accept an unlabelled continuation only across adjacent chunks/pages with
// the same parent and column count and an increasing numeric first column.
func relatedTableImages(content string, chunks []*types.Chunk) []types.RelatedImage {
	wanted := map[string]bool{}
	for _, m := range tableMention.FindAllStringSubmatch(content, -1) {
		wanted[strings.ToUpper(m[1])] = true
	}
	ordered := make([]*types.Chunk, 0, len(chunks))
	for _, c := range chunks {
		if c != nil && c.IsEnabled && c.ChunkType == types.ChunkTypeText {
			ordered = append(ordered, c)
		}
	}
	sort.Slice(ordered, func(i, j int) bool { return ordered[i].ChunkIndex < ordered[j].ChunkIndex })
	type tableMetadata struct {
		Assets []string   `json:"asset_ids"`
		Rows   [][]string `json:"table_rows"`
		Page   int        `json:"page_start"`
	}
	number := func(s string) (float64, error) {
		return strconv.ParseFloat(strings.ReplaceAll(strings.TrimSpace(s), ",", ""), 64)
	}
	var images []types.RelatedImage
	seen := map[string]bool{}
	label := ""
	var previous *types.Chunk
	var prevMeta tableMetadata
	for _, c := range ordered {
		var meta tableMetadata
		_ = json.Unmarshal(c.Metadata, &meta)
		heading := tableHeading.FindStringSubmatch(c.Content)
		adjacent := previous != nil && c.ChunkIndex == previous.ChunkIndex+1 &&
			c.ParentChunkID != "" && c.ParentChunkID == previous.ParentChunkID
		if len(heading) > 1 {
			label = strings.ToUpper(heading[1])
		} else if !(adjacent && len(meta.Rows) > 0 && len(prevMeta.Rows) == 0 && len(previous.Content) <= 300 && tableHeading.MatchString(previous.Content) && label != "") {
			continuation := adjacent && label != "" && len(meta.Rows) > 0 && len(prevMeta.Rows) > 0 &&
				meta.Page == prevMeta.Page+1 && len(meta.Rows[0]) == len(prevMeta.Rows[0]) && len(meta.Rows[0]) > 0
			if continuation {
				first, err1 := number(meta.Rows[0][0])
				lastRow := prevMeta.Rows[len(prevMeta.Rows)-1]
				if len(lastRow) == 0 {
					continuation = false
				} else {
					last, err2 := number(lastRow[0])
					continuation = err1 == nil && err2 == nil && first > last
				}
			}
			if !continuation {
				label = ""
			}
		}
		if label != "" && wanted[label] && len(meta.Rows) > 0 {
			for _, match := range markdownImage.FindAllStringSubmatch(c.Content, -1) {
				url := match[2]
				assetMatched := false
				for _, asset := range meta.Assets {
					if asset != "" && strings.HasSuffix(url, "/assets/"+asset) {
						assetMatched = true
					}
				}
				if assetMatched && !seen[url] {
					seen[url] = true
					images = append(images, types.RelatedImage{URL: url, Caption: fmt.Sprintf("Table %s — page %d", label, meta.Page), ChunkID: c.ID})
				}
			}
		}
		previous, prevMeta = c, meta
	}
	return images
}

// Captions must occur verbatim in the retrieved context of the same document.
// A shared document/page alone does not establish relevance.
func relatedCaptionImages(content string, wanted []string, chunks []*types.Chunk) []types.RelatedImage {
	seen := make(map[string]bool)
	var images []types.RelatedImage
	type siblingKey struct {
		parent string
		index  int
	}
	siblings := make(map[siblingKey]*types.Chunk)
	for _, chunk := range chunks {
		if chunk != nil && chunk.IsEnabled && chunk.ChunkType == types.ChunkTypeText {
			siblings[siblingKey{chunk.ParentChunkID, chunk.ChunkIndex}] = chunk
		}
	}
	normalize := func(s string) string { return strings.ToLower(strings.Join(strings.Fields(s), " ")) }
	contextText := normalize(content)
	for _, chunk := range chunks {
		if chunk == nil || !chunk.IsEnabled || chunk.ChunkType == types.ChunkTypeParentText {
			continue
		}
		for _, loc := range markdownImage.FindAllStringSubmatchIndex(chunk.Content, -1) {
			url := chunk.Content[loc[4]:loc[5]]
			caption := searchutil.CaptionForMarkdownImage(chunk.Content, loc)
			// A parser may split the immediately following caption into its
			// own child. Use current enabled siblings, never a stale parent copy.
			if !searchutil.DescriptiveImageCaption(caption) && loc[1] == len(strings.TrimRight(chunk.Content, "\n \t")) && chunk.ParentChunkID != "" {
				if next := siblings[siblingKey{chunk.ParentChunkID, chunk.ChunkIndex + 1}]; next != nil && len(next.Content) <= 300 {
					caption = searchutil.CaptionForMarkdownImage(chunk.Content+"\n\n"+next.Content, loc)
				}
			}
			matched := searchutil.DescriptiveImageCaption(caption) && strings.Contains(contextText, normalize(caption))
			for _, number := range figureNumber.FindAllStringSubmatch(caption, -1) {
				for _, wantedNumber := range wanted {
					if strings.ToLower(strings.ReplaceAll(number[1], "-", ".")) == wantedNumber {
						matched = true
					}
				}
			}
			if matched && !seen[url] {
				seen[url] = true
				images = append(images, types.RelatedImage{URL: url, Caption: caption, ChunkID: chunk.ID})
			}
		}
	}
	return images
}
