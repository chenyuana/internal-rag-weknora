package searchutil

import (
	"github.com/stretchr/testify/require"
	"testing"
)

func TestCaptionForMarkdownImageUsesOnlyImmediateDescriptiveParagraph(t *testing.T) {
	for _, tc := range []struct{ body, want string }{
		{"![figure p8](https://example.com/a.png)\n\nPressure versus temperature\n\nOther text", "Pressure versus temperature"},
		{"![figure p8](https://example.com/a.png)\n\n![Other figure](https://example.com/b.png)", "figure p8"},
		{"![figure p8](https://example.com/a.png)\n\nSource image on page 8; no OCR transcription available.", "figure p8"},
		{"![figure p8](https://example.com/a.png)\n\n$$a=b$$", "figure p8"},
		{"![Figure 3 profile](https://example.com/a.png)\n\nOther text", "Figure 3 profile"},
	} {
		loc := MarkdownImageRegex.FindStringSubmatchIndex(tc.body)
		require.Equal(t, tc.want, CaptionForMarkdownImage(tc.body, loc))
	}
}
