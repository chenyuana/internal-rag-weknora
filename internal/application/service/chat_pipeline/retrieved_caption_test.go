package chatpipeline

import (
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
	"testing"
)

func TestSelectRetrievedImagesKeepsDescriptiveFiguresAheadOfEquationCrops(t *testing.T) {
	ref := &types.SearchResult{ID: "source", Content: "![$$x=1$$](https://example.com/a.png)\n![$$y=2$$](https://example.com/b.png)\n![$$z=3$$](https://example.com/c.png)\n![Temperature pressure relationship](https://example.com/chart1.png)",
		RelatedImages: []types.RelatedImage{{URL: "https://example.com/chart2.png", Caption: "Flow rate and pressure relationship", ChunkID: "figure"}}}
	images := selectRetrievedImages("Compare the two diagrams and calculate the values", []*types.SearchResult{ref})
	require.Len(t, images, maxRetrievedImages)
	require.Equal(t, "https://example.com/chart1.png", images[0].URL)
	require.Equal(t, "https://example.com/chart2.png", images[1].URL)
	require.Equal(t, "figure", images[1].ChunkID)
	require.Equal(t, "source", images[1].SourceChunkID)
}
