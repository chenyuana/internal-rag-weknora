package service

import (
	"context"
	"regexp"
	"strings"

	"github.com/Tencent/WeKnora/internal/searchutil"
	"github.com/Tencent/WeKnora/internal/types"
)

var figureNumber = regexp.MustCompile(`(?i)\b(?:fig(?:ure)?\.?)\s*(\d+(?:[.-]\d+)*)\b`)
var figureSequence = regexp.MustCompile(`(?i)\bfig(?:ure)?s?\.?\s*\d+(?:[.-]\d+)*(?:\s*(?:,|and|&|和|与)\s*\d+(?:[.-]\d+)*)*`)
var numberInSequence = regexp.MustCompile(`\d+(?:[.-]\d+)*`)
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
		for _, image := range relatedCaptionImages(ref.Content, wanted, byKnowledge[ref.KnowledgeID]) {
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
					if strings.ReplaceAll(number[1], "-", ".") == wantedNumber {
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
