package service

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
	"github.com/hibiken/asynq"
	"github.com/stretchr/testify/require"
	"testing"
	"time"
)

func TestExistingChunkEnrichmentOnlySchedulesWiki(t *testing.T) {
	pending := &wikiEnqueueFailurePendingRepo{}
	queue := &wikiEnqueueFailureTaskQueue{}
	svc, repo := newWikiEnqueueTestService("doc-existing", pending, queue)
	repo.knowledge.SummaryStatus = types.SummaryStatusCompleted
	body, err := json.Marshal(types.KnowledgePostProcessPayload{TenantID: 7, KnowledgeBaseID: "kb-wiki", KnowledgeID: "doc-existing", EnrichmentOnly: true, EnrichWiki: true})
	require.NoError(t, err)
	require.NoError(t, svc.Handle(context.Background(), asynq.NewTask(types.TypeKnowledgePostProcess, body)))
	require.Equal(t, 1, repo.expectedSubtasks)
	require.Equal(t, []string{types.TypeWikiIngest}, queue.taskTypes)
	require.Equal(t, types.SummaryStatusCompleted, repo.knowledge.SummaryStatus)
	require.Equal(t, "plain text", svc.chunkRepo.(*wikiEnqueueFailureChunkRepo).chunks[0].Content)
}

type enrichRequestRepo struct {
	interfaces.KnowledgeRepository
	docs             map[string]*types.Knowledge
	claims, releases int
}

func (r *enrichRequestRepo) GetKnowledgeByID(_ context.Context, _ uint64, id string) (*types.Knowledge, error) {
	return r.docs[id], nil
}
func (r *enrichRequestRepo) ClaimKnowledgeEnrichment(_ context.Context, _ uint64, _, _ string, _ time.Time) (bool, error) {
	r.claims++
	return true, nil
}
func (r *enrichRequestRepo) ReleaseKnowledgeEnrichment(_ context.Context, _ uint64, _, _ string, _ time.Time) error {
	r.releases++
	return nil
}

type enrichRequestKB struct {
	interfaces.KnowledgeBaseService
	kb *types.KnowledgeBase
}

func (s *enrichRequestKB) GetKnowledgeBaseByID(context.Context, string) (*types.KnowledgeBase, error) {
	return s.kb, nil
}

type enrichFailQueue struct{ interfaces.TaskEnqueuer }

func (q *enrichFailQueue) Enqueue(*asynq.Task, ...asynq.Option) (*asynq.TaskInfo, error) {
	return nil, errors.New("queue unavailable")
}

func TestExistingChunkEnrichmentValidatesBeforeScheduling(t *testing.T) {
	ctx := types.WithExecutionTenant(context.Background(), 7)
	ctx = context.WithValue(ctx, types.TenantInfoContextKey, &types.Tenant{ID: 7})
	repo := &enrichRequestRepo{docs: map[string]*types.Knowledge{
		"doc":     {ID: "doc", TenantID: 7, KnowledgeBaseID: "kb", ParseStatus: types.ParseStatusCompleted},
		"foreign": {ID: "foreign", TenantID: 7, KnowledgeBaseID: "other", ParseStatus: types.ParseStatusCompleted},
	}}
	svc := &knowledgeService{repo: repo, kbService: &enrichRequestKB{kb: &types.KnowledgeBase{ID: "kb", TenantID: 7, IndexingStrategy: types.IndexingStrategy{WikiEnabled: true}}}, chunkRepo: &wikiEnqueueFailureChunkRepo{chunks: []*types.Chunk{{ID: "c", TenantID: 7, KnowledgeBaseID: "kb", KnowledgeID: "doc", ChunkType: types.ChunkTypeText, Content: "original"}}}, task: &enrichFailQueue{}}
	result, err := svc.EnrichExistingChunks(ctx, "kb", &types.ExistingChunksEnrichRequest{KnowledgeIDs: []string{"doc"}, Wiki: true, DryRun: true})
	require.NoError(t, err)
	require.Equal(t, "validated", result[0].Action)
	require.Zero(t, repo.claims)
	_, err = svc.EnrichExistingChunks(ctx, "kb", &types.ExistingChunksEnrichRequest{KnowledgeIDs: []string{"doc", "foreign"}, Wiki: true})
	require.ErrorContains(t, err, "does not belong")
	require.Zero(t, repo.claims)
	_, err = svc.EnrichExistingChunks(ctx, "kb", &types.ExistingChunksEnrichRequest{KnowledgeIDs: []string{"doc"}, Wiki: true})
	require.ErrorContains(t, err, "queue unavailable")
	require.Equal(t, 1, repo.claims)
	require.Equal(t, 1, repo.releases)
	require.Equal(t, "original", svc.chunkRepo.(*wikiEnqueueFailureChunkRepo).chunks[0].Content)
}
