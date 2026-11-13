package chatpipeline

import (
	"context"
	"testing"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
	"github.com/stretchr/testify/require"
)

type wikiRecallKB struct {
	interfaces.KnowledgeBaseService
	kb *types.KnowledgeBase
}

func (s *wikiRecallKB) GetKnowledgeBaseByID(context.Context, string) (*types.KnowledgeBase, error) {
	return s.kb, nil
}

type wikiRecallPages struct {
	interfaces.WikiPageService
	pages []*types.WikiPage
	calls int
}

func (s *wikiRecallPages) SearchPages(context.Context, string, string, int) ([]*types.WikiPage, error) {
	s.calls++
	return s.pages, nil
}

type wikiRecallChunks struct {
	interfaces.ChunkRepository
	chunks []*types.Chunk
}

func (s *wikiRecallChunks) ListChunksByID(context.Context, uint64, []string) ([]*types.Chunk, error) {
	return s.chunks, nil
}
func (s *wikiRecallChunks) ListChunksByParentIDs(context.Context, uint64, []string) ([]*types.Chunk, error) {
	return nil, nil
}

type wikiRecallDocuments struct {
	interfaces.KnowledgeRepository
	docs []*types.Knowledge
}

func (s *wikiRecallDocuments) GetKnowledgeBatch(context.Context, uint64, []string) ([]*types.Knowledge, error) {
	return s.docs, nil
}

func TestWikiRecallReturnsOriginalEvidenceWithinDocumentScope(t *testing.T) {
	pageService := &wikiRecallPages{pages: []*types.WikiPage{
		{KnowledgeBaseID: "kb", Slug: "concept/display", Title: "显示器安装", Status: types.WikiPageStatusPublished, Content: "synthesized claims", SourceRefs: types.StringArray{"doc", "other"}, ChunkRefs: types.StringArray{"c1", "c2"}},
		{KnowledgeBaseID: "kb", Slug: "draft", Title: "显示器", Status: types.WikiPageStatusDraft, SourceRefs: types.StringArray{"doc"}, ChunkRefs: types.StringArray{"c3"}},
	}}
	p := &PluginWikiRecall{kb: &wikiRecallKB{kb: &types.KnowledgeBase{ID: "kb", TenantID: 7, IndexingStrategy: types.IndexingStrategy{WikiEnabled: true}}}, wiki: pageService, chunks: &wikiRecallChunks{chunks: []*types.Chunk{
		{ID: "c1", TenantID: 7, KnowledgeBaseID: "kb", KnowledgeID: "doc", Content: "original evidence", IsEnabled: true},
		{ID: "c2", TenantID: 7, KnowledgeBaseID: "kb", KnowledgeID: "other", Content: "outside document scope", IsEnabled: true},
		{ID: "c3", TenantID: 7, KnowledgeBaseID: "kb", KnowledgeID: "doc", Content: "draft evidence", IsEnabled: true},
	}}, knowledge: &wikiRecallDocuments{docs: []*types.Knowledge{
		{ID: "doc", TenantID: 7, KnowledgeBaseID: "kb", EnableStatus: "enabled", FileName: "source.pdf"},
		{ID: "other", TenantID: 7, KnowledgeBaseID: "kb", EnableStatus: "enabled"},
	}}}
	cm := &types.ChatManage{}
	cm.Query = "显示器如何安装"
	cm.TenantID = 7
	cm.SearchTargets = types.SearchTargets{{Type: types.SearchTargetTypeKnowledge, KnowledgeBaseID: "kb", TenantID: 7, KnowledgeIDs: []string{"doc"}}}
	err := p.OnEvent(context.Background(), types.CHUNK_SEARCH, cm, func() *PluginError { return ErrSearchNothing })
	require.Nil(t, err)
	require.Len(t, cm.SearchResult, 1)
	require.Equal(t, "original evidence", cm.SearchResult[0].Content)
	require.Equal(t, "source.pdf", cm.SearchResult[0].KnowledgeFilename)
	require.Equal(t, types.MatchTypeWiki, cm.SearchResult[0].MatchType)
	require.Equal(t, "concept/display", cm.SearchResult[0].Metadata["wiki_recall_page"])
}

func TestWikiRecallDoesNotWidenTagsOrCrossTenantScope(t *testing.T) {
	for _, target := range []*types.SearchTarget{
		{KnowledgeBaseID: "kb", TagIDs: []string{"tag"}},
		{KnowledgeBaseID: "kb", TenantID: 8},
	} {
		pages := &wikiRecallPages{}
		p := &PluginWikiRecall{kb: &wikiRecallKB{kb: &types.KnowledgeBase{ID: "kb", TenantID: 7, IndexingStrategy: types.IndexingStrategy{WikiEnabled: true}}}, wiki: pages}
		cm := &types.ChatManage{}
		cm.Query = "显示器安装"
		cm.TenantID = 7
		cm.SearchTargets = types.SearchTargets{target}
		require.Same(t, ErrSearchNothing, p.OnEvent(context.Background(), types.CHUNK_SEARCH, cm, func() *PluginError { return ErrSearchNothing }))
		require.Zero(t, pages.calls)
	}
}

func TestWikiRecallIgnoresGenericBodyMatches(t *testing.T) {
	page := &types.WikiPage{Title: "电子飞行包组件安装", Content: "电源系统检查方法", Aliases: types.StringArray{"EFB"}}
	require.False(t, wikiRecallTopicMatch(page, []string{"发动机", "检查", "方法", "系统", "安装", "20"}))
	require.True(t, wikiRecallTopicMatch(page, []string{"电子飞行包", "安装"}))
}
