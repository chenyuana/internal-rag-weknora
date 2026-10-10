package searchutil

import (
	"regexp"
	"strings"
	"unicode/utf8"
)

var genericImageCaption = regexp.MustCompile(`(?i)^(?:figure|fig|image|source image)(?:[\s,.]*(?:p|page)?\s*\d+)?$`)

// DescriptiveImageCaption accepts human-readable captions, not parser
// placeholders, page labels or equation crops. It never invents a figure number.
func DescriptiveImageCaption(caption string) bool {
	c := strings.TrimSpace(caption)
	return utf8.RuneCountInString(c) >= 12 && !genericImageCaption.MatchString(c) &&
		!strings.Contains(strings.ToLower(c), "no ocr transcription") &&
		!strings.Contains(c, "$$") && !strings.Contains(c, "![") &&
		!strings.Contains(c, "<") && !strings.HasPrefix(c, "#")
}

// CaptionForMarkdownImage uses the immediately following paragraph when the
// parser only supplied a generic alt label. No page or image order inference.
func CaptionForMarkdownImage(content string, loc []int) string {
	caption := strings.TrimSpace(content[loc[2]:loc[3]])
	if !genericImageCaption.MatchString(caption) {
		return caption
	}
	paragraph := strings.SplitN(strings.TrimSpace(content[loc[1]:]), "\n\n", 2)[0]
	if len(paragraph) <= 300 && DescriptiveImageCaption(paragraph) {
		return strings.TrimSpace(paragraph)
	}
	return caption
}
