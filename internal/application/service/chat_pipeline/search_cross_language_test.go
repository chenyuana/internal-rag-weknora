package chatpipeline

import (
	"context"
	"errors"
	"testing"

	"github.com/Tencent/WeKnora/internal/models/chat"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
	"github.com/stretchr/testify/require"
)

type crossLanguageTestModel struct {
	interfaces.ModelService
	fail bool
}

func (m crossLanguageTestModel) GetChatModel(context.Context, string) (chat.Chat, error) {
	if m.fail {
		return nil, errors.New("translation model unavailable")
	}
	return crossLanguageTestChat{}, nil
}

type crossLanguageChatInterface = chat.Chat

type crossLanguageTestChat struct{ crossLanguageChatInterface }

func (crossLanguageTestChat) Chat(context.Context, []chat.Message, *chat.ChatOptions) (*types.ChatResponse, error) {
	return &types.ChatResponse{Content: "fuselage layout"}, nil
}

type crossLanguageTestKB struct {
	failingSearchKnowledgeBaseService
}

func (s crossLanguageTestKB) HybridSearch(_ context.Context, _ string, params types.SearchParams) ([]*types.SearchResult, error) {
	common := &types.SearchResult{ID: "shared", Content: "Shared evidence"}
	if params.QueryText == "fuselage layout" {
		return []*types.SearchResult{common, {ID: "en", Content: "English evidence"}}, nil
	}
	return []*types.SearchResult{common, {ID: "zh", Content: "中文证据"}}, nil
}

func TestCrossLanguageSearchCombinesCandidatesWhenEnabled(t *testing.T) {
	for _, tc := range []struct {
		name      string
		enabled   bool
		modelFail bool
		wantIDs   []string
	}{
		{name: "disabled", wantIDs: []string{"shared", "zh"}},
		{name: "enabled", enabled: true, wantIDs: []string{"shared", "zh", "en"}},
		{name: "translation unavailable", enabled: true, modelFail: true, wantIDs: []string{"shared", "zh"}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			search := &PluginSearchParallel{searchPlugin: &PluginSearch{
				knowledgeBaseService: &crossLanguageTestKB{},
				modelService:         crossLanguageTestModel{fail: tc.modelFail},
			}}
			cm := &types.ChatManage{
				PipelineRequest: types.PipelineRequest{
					Query:               "机身布局",
					CrossLanguageSearch: tc.enabled,
					SearchTargets: types.SearchTargets{{
						Type:            types.SearchTargetTypeKnowledgeBase,
						KnowledgeBaseID: "kb-1",
					}},
				},
				PipelineState: types.PipelineState{RewriteQuery: "机身布局"},
			}
			err := search.OnEvent(context.Background(), types.CHUNK_SEARCH_PARALLEL, cm, func() *PluginError { return nil })
			require.Nil(t, err)
			var ids []string
			for _, result := range cm.SearchResult {
				ids = append(ids, result.ID)
			}
			require.Equal(t, tc.wantIDs, ids)
			require.Equal(t, tc.enabled && !tc.modelFail, cm.CrossLanguageCandidates)
			require.Equal(t, "机身布局", cm.RewriteQuery)
		})
	}
}
