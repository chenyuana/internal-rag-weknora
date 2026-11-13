package service

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
)

func TestInternalRAGAutomaticWikiHonorsKBAndReportsQueueFailure(t *testing.T) {
	ctx := types.WithExecutionTenant(context.Background(), 7)
	ctx = context.WithValue(ctx, types.TenantInfoContextKey, &types.Tenant{ID: 7})
	repo := &enrichRequestRepo{docs: map[string]*types.Knowledge{
		"doc": {ID: "doc", TenantID: 7, KnowledgeBaseID: "kb", ParseStatus: types.ParseStatusCompleted},
	}}
	kb := &types.KnowledgeBase{ID: "kb", TenantID: 7}
	svc := &knowledgeService{repo: repo, kbService: &enrichRequestKB{kb: kb},
		chunkRepo: &wikiEnqueueFailureChunkRepo{chunks: []*types.Chunk{{ID: "c", TenantID: 7, KnowledgeBaseID: "kb", KnowledgeID: "doc", ChunkType: types.ChunkTypeText, Content: "original"}}}, task: &enrichFailQueue{}}
	require.NoError(t, svc.enqueueInternalRAGWiki(ctx, kb, "doc"))
	require.Zero(t, repo.claims)
	kb.IndexingStrategy.WikiEnabled = true
	require.ErrorContains(t, svc.enqueueInternalRAGWiki(ctx, kb, "doc"), "queue unavailable")
	require.Equal(t, 1, repo.claims)
	require.Equal(t, 1, repo.releases)
	require.Equal(t, "original", svc.chunkRepo.(*wikiEnqueueFailureChunkRepo).chunks[0].Content)
}

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
