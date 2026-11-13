package service

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/hibiken/asynq"
	"os"
	"strings"
	"time"
)

type knowledgeEnrichmentClaimer interface {
	ClaimKnowledgeEnrichment(context.Context, uint64, string, string, time.Time) (bool, error)
	ReleaseKnowledgeEnrichment(context.Context, uint64, string, string, time.Time) error
}

func (s *knowledgeService) EnrichExistingChunks(ctx context.Context, kbID string, req *types.ExistingChunksEnrichRequest) ([]types.ExistingChunksEnrichResult, error) {
	if req == nil || len(req.KnowledgeIDs) == 0 || len(req.KnowledgeIDs) > 20 || (!req.Wiki && !req.Graph) {
		return nil, errors.New("select 1–20 documents and at least one of wiki/graph")
	}
	kb, err := s.kbService.GetKnowledgeBaseByID(ctx, kbID)
	if err != nil {
		return nil, err
	}
	ctx, err = withKBWriteTenantInfo(ctx, kb, s.tenantRepo)
	if err != nil {
		return nil, err
	}
	if req.Wiki && !kb.IndexingStrategy.WikiEnabled {
		return nil, errors.New("enable Wiki on this knowledge base first")
	}
	if req.Graph && (s.graphEngine == nil || !strings.EqualFold(os.Getenv("NEO4J_ENABLE"), "true") || !kb.IsGraphEnabled()) {
		return nil, errors.New("graph storage and knowledge base graph extraction must be enabled first")
	}
	tenantID := types.MustTenantIDFromContext(ctx)
	results := make([]types.ExistingChunksEnrichResult, 0, len(req.KnowledgeIDs))
	seen := map[string]bool{}
	// Validate the whole selection before mutating or scheduling any document.
	for _, id := range req.KnowledgeIDs {
		if seen[id] {
			return nil, errors.New("duplicate knowledge id")
		}
		seen[id] = true
		kn, err := s.repo.GetKnowledgeByID(ctx, tenantID, id)
		if err != nil {
			return nil, err
		}
		if kn == nil || kn.KnowledgeBaseID != kbID {
			return nil, errors.New("document does not belong to this knowledge base")
		}
		if kn.ParseStatus != types.ParseStatusCompleted || kn.PendingSubtasksCount != 0 {
			return nil, fmt.Errorf("document %s is not idle and completed", id)
		}
		overrides, _ := kn.ProcessOverrides()
		if req.Graph && !ResolveProcessConfig(kb, overrides).GraphEnabled {
			return nil, fmt.Errorf("graph extraction disabled for document %s", id)
		}
		chunks, err := s.chunkRepo.ListChunksByKnowledgeIDAndTypes(ctx, tenantID, id, []types.ChunkType{types.ChunkTypeText, types.ChunkTypeImageOCR, types.ChunkTypeImageCaption})
		if err != nil {
			return nil, err
		}
		if len(chunks) == 0 {
			return nil, fmt.Errorf("document %s has no existing text chunks", id)
		}
		for _, chunk := range chunks {
			if chunk == nil || chunk.TenantID != tenantID || chunk.KnowledgeID != id || chunk.KnowledgeBaseID != kbID {
				return nil, errors.New("existing chunk scope does not match selected document")
			}
		}
		results = append(results, types.ExistingChunksEnrichResult{KnowledgeID: id, Action: "validated", ChunkCount: len(chunks)})
	}
	if req.DryRun {
		return results, nil
	}
	claimer, ok := s.repo.(knowledgeEnrichmentClaimer)
	if !ok || s.task == nil {
		return nil, errors.New("enrichment scheduling unavailable")
	}
	for i := range results {
		id := results[i].KnowledgeID
		stamp := time.Now().UTC().Truncate(time.Microsecond)
		claimed, err := claimer.ClaimKnowledgeEnrichment(ctx, tenantID, kbID, id, stamp)
		if err != nil {
			return results[:i], err
		}
		if !claimed {
			return results[:i], fmt.Errorf("document %s is already processing or changed", id)
		}
		_, attempt, err := s.tracker().OpenAttempt(ctx, id, "")
		if err == nil {
			body, marshalErr := json.Marshal(types.KnowledgePostProcessPayload{TenantID: tenantID, KnowledgeBaseID: kbID, KnowledgeID: id, Language: types.LanguageFromContextOrDefault(ctx), Attempt: attempt, EnrichmentOnly: true, EnrichWiki: req.Wiki, EnrichGraph: req.Graph})
			err = marshalErr
			if err == nil {
				_, err = s.task.Enqueue(asynq.NewTask(types.TypeKnowledgePostProcess, body, knowledgePostProcessTaskOptions()...))
			}
		}
		if err != nil {
			rollbackCtx, cancel := context.WithTimeout(context.WithoutCancel(ctx), 10*time.Second)
			rollbackErr := claimer.ReleaseKnowledgeEnrichment(rollbackCtx, tenantID, kbID, id, stamp)
			cancel()
			return results[:i], errors.Join(err, rollbackErr)
		}
		results[i].Action = "queued"
	}
	return results, nil
}
