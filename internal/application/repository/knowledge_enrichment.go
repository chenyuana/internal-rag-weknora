package repository

import (
	"context"
	"github.com/Tencent/WeKnora/internal/types"
	"time"
)

// ClaimKnowledgeEnrichment serializes generation against other processing.
func (r *knowledgeRepository) ClaimKnowledgeEnrichment(ctx context.Context, tenantID uint64, kbID, id string, stamp time.Time) (bool, error) {
	result := r.db.WithContext(ctx).Model(&types.Knowledge{}).
		Where("id = ? AND tenant_id = ? AND knowledge_base_id = ? AND parse_status = ? AND pending_subtasks_count = 0", id, tenantID, kbID, types.ParseStatusCompleted).
		Updates(map[string]interface{}{"parse_status": types.ParseStatusProcessing, "updated_at": stamp, "error_message": ""})
	return result.RowsAffected == 1, result.Error
}

// ReleaseKnowledgeEnrichment only rolls back the exact claim that failed enqueue.
func (r *knowledgeRepository) ReleaseKnowledgeEnrichment(ctx context.Context, tenantID uint64, kbID, id string, stamp time.Time) error {
	return r.db.WithContext(ctx).Model(&types.Knowledge{}).
		Where("id = ? AND tenant_id = ? AND knowledge_base_id = ? AND parse_status = ? AND updated_at = ? AND pending_subtasks_count = 0", id, tenantID, kbID, types.ParseStatusProcessing, stamp).
		Updates(map[string]interface{}{"parse_status": types.ParseStatusCompleted, "updated_at": time.Now()}).Error
}
