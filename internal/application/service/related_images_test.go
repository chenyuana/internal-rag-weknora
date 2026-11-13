package service

import (
	"encoding/json"
	"testing"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
)

func TestRelatedTableImagesRecoverTitlesAndContinuations(t *testing.T) {
	table := func(id string, index, page int, text string, rows [][]string) *types.Chunk {
		meta, err := json.Marshal(map[string]interface{}{"asset_ids": []string{id}, "page_start": page, "table_rows": rows})
		require.NoError(t, err)
		return &types.Chunk{ID: id, ChunkIndex: index, ParentChunkID: "parent", IsEnabled: true,
			ChunkType: types.ChunkTypeText, Metadata: meta,
			Content: text + "\n\n![table p8](http://localhost:8080/api/v1/ingestion/jobs/job/assets/" + id + ")"}
	}
	chunks := []*types.Chunk{
		{ID: "heading", ChunkIndex: 20, ParentChunkID: "parent", IsEnabled: true, ChunkType: types.ChunkTypeText, Content: "Table III\n\nFriction"},
		table("iii", 21, 8, "Altitude (feet)=1,000", [][]string{{"Altitude", "Tolerance"}, {"1,000", "70"}}),
		{ID: "heading4", ChunkIndex: 22, ParentChunkID: "parent", IsEnabled: true, ChunkType: types.ChunkTypeText, Content: "Table IV"},
		table("iv8", 23, 8, "Altitude-Pressure", [][]string{{"Altitude", "Pressure"}, {"0", "29.921"}}),
		table("iv9", 24, 9, "500: 29.38", [][]string{{"500", "29.38"}, {"17,500", "15.25"}}),
		table("iv10", 25, 10, "DRS_64-14", [][]string{{"18,000", "14.94"}, {"35,000", "7.04"}}),
		table("iv11", 26, 11, "DRS_64-14", [][]string{{"35,332", "6.93"}, {"50,000", "3,436"}}),
		table("other", 27, 12, "Other table", [][]string{{"Altitude", "Other"}, {"60,000", "1"}}),
	}
	images := relatedTableImages("Table III and Table IV", chunks)
	require.Len(t, images, 5)
	require.Equal(t, "Table III — page 8", images[0].Caption)
	require.Equal(t, "iv11", images[4].ChunkID)
	require.Len(t, relatedTableImages("Table III", chunks), 1)
	require.Empty(t, relatedTableImages("Unrelated paragraph", chunks))
	chunks[4].IsEnabled = false
	require.Len(t, relatedTableImages("Table IV", chunks), 1)
}

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

func TestReferencedAppendixFigureNumbers(t *testing.T) {
 require.Equal(t, []string{"a.1", "a.2"}, referencedFigureNumbers("Figures A-1 and A-2 show cabin view."))
}
