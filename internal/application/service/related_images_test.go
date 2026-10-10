package service

import (
	"testing"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
)

func TestReferencedFigureNumbers(t *testing.T) {
	require.Equal(t, []string{"3.4", "3.5"}, referencedFigureNumbers(
		"Figure 3.4 and 3.5 show typical recordings; section 3.6 is unrelated.",
	))
	require.Empty(t, referencedFigureNumbers("Only section 3.4 and table 3.5 are mentioned."))
}

func TestRelatedImagesRecoverSplitCaptionWithoutInferringFigureNumber(t *testing.T) {
	chunks := []*types.Chunk{
		{ID: "image", IsEnabled: true, ChunkType: types.ChunkTypeText, ParentChunkID: "parent", ChunkIndex: 4, Content: "Source image on page 9; no OCR transcription available.\n\n![figure p9](https://example.com/chart.png)"},
		{ID: "caption", IsEnabled: true, ChunkType: types.ChunkTypeText, ParentChunkID: "parent", ChunkIndex: 5, Content: "Temperature and pressure relationship"},
		{ID: "other", IsEnabled: true, ChunkType: types.ChunkTypeText, Content: "![Unrelated diagram](https://example.com/other.png)"},
	}
	images := relatedCaptionImages("The temperature and pressure relationship is described below.", nil, chunks)
	require.Len(t, images, 1)
	require.Equal(t, "image", images[0].ChunkID)
	require.Equal(t, "Temperature and pressure relationship", images[0].Caption)
	require.Empty(t, referencedFigureNumbers(images[0].Caption))
	chunks[1].IsEnabled = false
	require.Empty(t, relatedCaptionImages("Temperature and pressure relationship", nil, chunks))
	chunks[1].IsEnabled = true
	chunks[0].IsEnabled = false
	require.Empty(t, relatedCaptionImages("Temperature and pressure relationship", nil, chunks))
}

func TestFigureCaptionImageIsDiscoverable(t *testing.T) {
	content := "FIGURE 3.4\n\n![TYPICAL HORIZONTAL DISTRIBUTION\nFIGURE 3.4](http://localhost:8080/api/v1/ingestion/jobs/job/assets/image)"
	images := markdownImage.FindAllStringSubmatch(content, -1)
	require.Len(t, images, 1)
	require.Equal(t, "3.4", figureNumber.FindStringSubmatch(images[0][1])[1])
}

func TestReferencedSingleFigureNumber(t *testing.T) {
	require.Equal(t, []string{"1", "2"}, referencedFigureNumbers("Compass (See Figure 1); Attitude (See Figure 2)."))
	require.Empty(t, referencedFigureNumbers("Section 1 and table 2."))
	require.Equal(t, "1", figureNumber.FindStringSubmatch("Figure 1 Compass Area")[1])
}
