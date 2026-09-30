package service

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/google/uuid"
)

const internalRAGSourceIDKey = "internal_rag_source_document_id"

func internalRAGJSON(value any) types.JSON {
	b, _ := json.Marshal(value)
	return types.JSON(b)
}

func internalRAGContextHeader(c types.InternalRAGChunk) string {
	parts := append([]string(nil), c.SectionPath...)
	if c.Title != "" && (len(parts) == 0 || parts[len(parts)-1] != c.Title) {
		parts = append(parts, c.Title)
	}
	if len(parts) == 0 {
		return ""
	}
	return strings.Join(parts, " > ")
}

// ImportInternalRAG bypasses document parsing and chunking. processChunks is
// deliberately reused for quota checks, embeddings, and configured index stores.
func (s *knowledgeService) ImportInternalRAG(ctx context.Context, kbID string, payload *types.InternalRAGImportRequest) (*types.InternalRAGImportResult, error) {
	if payload == nil || strings.TrimSpace(payload.SourceDocumentID) == "" || strings.TrimSpace(payload.SourceName) == "" {
		return nil, errors.New("source_document_id and source_name are required")
	}
	if len(payload.Chunks) == 0 {
		return nil, errors.New("at least one chunk is required")
	}
	for i, c := range payload.Chunks {
		if strings.TrimSpace(c.ChunkID) == "" || strings.TrimSpace(c.Text) == "" {
			return nil, fmt.Errorf("chunk %d requires chunk_id and non-empty text", i)
		}
	}

	kb, err := s.kbService.GetKnowledgeBaseByID(ctx, kbID)
	if err != nil {
		return nil, err
	}
	ctx, err = withKBWriteTenantInfo(ctx, kb, s.tenantRepo)
	if err != nil {
		return nil, err
	}
	tenantID := types.MustTenantIDFromContext(ctx)
	existing, findErr := s.repo.FindByMetadataKey(ctx, tenantID, kbID, internalRAGSourceIDKey, payload.SourceDocumentID)
	if findErr != nil {
		return nil, findErr
	}
	if existing != nil && existing.ParseStatus == types.ParseStatusCompleted && payload.NormalizedTextSHA256 != "" {
		meta, _ := existing.Metadata.Map()
		if current, _ := meta["internal_rag_normalized_text_sha256"].(string); current == payload.NormalizedTextSHA256 {
			return &types.InternalRAGImportResult{KnowledgeID: existing.ID, Action: "skipped", ChunkCount: len(payload.Chunks)}, nil
		}
	}
	if payload.DryRun {
		action := "created"
		if existing != nil {
			action = "updated"
		}
		return &types.InternalRAGImportResult{Action: "validated_" + action, ChunkCount: len(payload.Chunks)}, nil
	}

	now := time.Now()
	meta := map[string]any{
		"source_system": "internal-rag", internalRAGSourceIDKey: payload.SourceDocumentID,
		"internal_rag_source_sha256":          payload.SourceSHA256,
		"internal_rag_normalized_text_sha256": payload.NormalizedTextSHA256,
		"internal_rag_schema_version":         payload.SchemaVersion,
		"internal_rag_parser_name":            payload.ParserName,
		"internal_rag_parser_version":         payload.ParserVersion,
		"internal_rag_source_path":            payload.SourcePath,
	}
	action := "created"
	knowledge := existing
	if knowledge == nil {
		knowledge = &types.Knowledge{ID: uuid.NewString(), TenantID: tenantID, KnowledgeBaseID: kbID, CreatedAt: now}
	} else {
		action = "updated"
	}
	knowledge.Type = "internal_rag"
	knowledge.Channel = types.ChannelAPI
	knowledge.Title = payload.SourceName
	knowledge.Source = "internal-rag"
	knowledge.FileName = payload.SourceName
	knowledge.FileType = "internal_rag"
	knowledge.FileHash = payload.SourceSHA256
	knowledge.Metadata = internalRAGJSON(meta)
	knowledge.ParseStatus = types.ParseStatusProcessing
	knowledge.EnableStatus = "disabled"
	knowledge.EmbeddingModelID = kb.EmbeddingModelID
	knowledge.ErrorMessage = ""
	knowledge.UpdatedAt = now
	if existing == nil {
		if err := s.repo.CreateKnowledge(ctx, knowledge); err != nil {
			return nil, err
		}
	} else if err := s.repo.UpdateKnowledge(ctx, knowledge); err != nil {
		return nil, err
	}

	parentIndex := map[string]int{}
	parents := make([]types.ParsedParentChunk, 0)
	parentBodies := map[string][]string{}
	for _, c := range payload.Chunks {
		if c.ParentChunkID != "" {
			parentBodies[c.ParentChunkID] = append(parentBodies[c.ParentChunkID], c.Text)
		}
	}
	for _, c := range payload.Chunks {
		if c.ParentChunkID == "" {
			continue
		}
		if _, ok := parentIndex[c.ParentChunkID]; ok {
			continue
		}
		parentIndex[c.ParentChunkID] = len(parents)
		body := strings.Join(parentBodies[c.ParentChunkID], "\n\n")
		parents = append(parents, types.ParsedParentChunk{Content: body, Seq: len(parents), End: len([]rune(body))})
	}
	parsed := make([]types.ParsedChunk, 0, len(payload.Chunks))
	for i, c := range payload.Chunks {
		pi := -1
		if c.ParentChunkID != "" {
			pi = parentIndex[c.ParentChunkID]
		}
		parsed = append(parsed, types.ParsedChunk{Content: c.Text, ContextHeader: internalRAGContextHeader(c), Seq: i, Start: 0, End: len([]rune(c.Text)), ParentIndex: pi})
	}
	if err := s.processChunks(ctx, kb, knowledge, parsed, ProcessChunksOptions{ParentChunks: parents, SkipPostProcess: true}); err != nil {
		return nil, err
	}
	refreshed, err := s.repo.GetKnowledgeByID(ctx, tenantID, knowledge.ID)
	if err != nil {
		return nil, err
	}
	if refreshed.ParseStatus != types.ParseStatusCompleted {
		return nil, fmt.Errorf("indexing did not complete: status=%s error=%s", refreshed.ParseStatus, refreshed.ErrorMessage)
	}

	stored, err := s.chunkRepo.ListAllChunksByKnowledgeID(ctx, tenantID, knowledge.ID)
	if err != nil {
		return nil, err
	}
	for _, c := range stored {
		if c.ChunkType != types.ChunkTypeText || c.ChunkIndex < 0 || c.ChunkIndex >= len(payload.Chunks) {
			continue
		}
		src := payload.Chunks[c.ChunkIndex]
		c.Metadata = internalRAGJSON(map[string]any{
			"external_chunk_id": src.ChunkID, "external_parent_chunk_id": src.ParentChunkID,
			"page_start": src.PageStart, "page_end": src.PageEnd, "section_path": src.SectionPath,
			"block_ids": src.BlockIDs, "article_id_raw": src.ArticleIDRaw,
			"article_id_normalized": src.ArticleIDNormalized, "article_parent_id": src.ArticleParentID,
			"article_aliases": src.ArticleAliases, "keywords": src.Keywords,
			"question_aliases": src.QuestionAliases, "asset_ids": src.AssetIDs,
			"table_html": src.TableHTML, "table_rows": src.TableRows,
			"formula_latex": src.FormulaLatex, "related_chunks": src.RelatedChunks,
			"content_type": src.ContentType,
		})
	}
	if err := s.chunkRepo.SaveChunks(ctx, stored); err != nil {
		return nil, err
	}
	return &types.InternalRAGImportResult{KnowledgeID: knowledge.ID, Action: action, ChunkCount: len(payload.Chunks)}, nil
}
