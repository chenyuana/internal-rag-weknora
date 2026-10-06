package service

import (
	"context"
	"regexp"
	"strings"

	"github.com/Tencent/WeKnora/internal/types"
)

var figureNumber = regexp.MustCompile(`(?i)\b(?:fig(?:ure)?\.?)\s*(\d+(?:[.-]\d+)+)\b`)
var figureSequence = regexp.MustCompile(`(?i)\bfig(?:ure)?s?\.?\s*\d+(?:[.-]\d+)+(?:\s*(?:,|and|&|和|与)\s*\d+(?:[.-]\d+)+)*`)
var numberInSequence = regexp.MustCompile(`\d+(?:[.-]\d+)+`)
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

// attachRelatedImages adds only figures named in a retrieved passage. Merely
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
		if len(wanted) == 0 {
			continue
		}
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
		seen := make(map[string]bool)
		for _, figure := range wanted {
			if len(ref.RelatedImages) >= 12 {
				break
			}
			for _, chunk := range byKnowledge[ref.KnowledgeID] {
				if len(ref.RelatedImages) >= 12 {
					break
				}
				if chunk == nil || !chunk.IsEnabled {
					continue
				}
				for _, image := range markdownImage.FindAllStringSubmatch(chunk.Content, -1) {
					caption := strings.ReplaceAll(image[1], `\]`, "]")
					matched := false
					for _, number := range figureNumber.FindAllStringSubmatch(caption, -1) {
						if strings.ToLower(strings.ReplaceAll(number[1], "-", ".")) == figure {
							matched = true
							break
						}
					}
					if matched && !seen[image[2]] {
						seen[image[2]] = true
						ref.RelatedImages = append(ref.RelatedImages, types.RelatedImage{
							URL: image[2], Caption: strings.TrimSpace(caption), ChunkID: chunk.ID,
						})
						if len(ref.RelatedImages) >= 12 {
							break
						}
					}
				}
			}
		}
	}
}
