package service

import (
	"encoding/json"
	"testing"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
)

func TestInternalRAGContextHeader(t *testing.T) {
	require.Equal(t, "Part 23 > 23.1309", internalRAGContextHeader(types.InternalRAGChunk{
		Title:       "23.1309",
		SectionPath: []string{"Part 23"},
	}))
	require.Equal(t, "Part 23", internalRAGContextHeader(types.InternalRAGChunk{
		Title:       "Part 23",
		SectionPath: []string{"Part 23"},
	}))
}

func TestInternalRAGChunkWireFormat(t *testing.T) {
	var chunk types.InternalRAGChunk
	err := json.Unmarshal([]byte(`{
		"chunk_id":"external-1","parent_chunk_id":"parent-1","title":"Limitations",
		"text":"required content","page_start":2,"page_end":3,
		"section_path":["Part 23"],"keywords":["airworthiness"],
		"question_aliases":["What is required?"],"table_rows":[{"a":"b"}]
	}`), &chunk)
	require.NoError(t, err)
	require.Equal(t, "external-1", chunk.ChunkID)
	require.Equal(t, 2, chunk.PageStart)
	require.Len(t, chunk.TableRows, 1)
}
