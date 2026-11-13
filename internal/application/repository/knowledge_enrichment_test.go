package repository

import (
	"context"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
	"testing"
	"time"
)

func TestKnowledgeEnrichmentClaimAndRollback(t *testing.T) {
	db := setupKnowledgeTestDB(t)
	r := &knowledgeRepository{db: db}
	ctx := context.Background()
	require.NoError(t, db.Exec("INSERT INTO knowledges(id, tenant_id, knowledge_base_id, parse_status, summary_status) VALUES ('doc', 7, 'kb', 'completed', 'completed')").Error)
	stamp := time.Now().UTC().Truncate(time.Microsecond)
	claimed, err := r.ClaimKnowledgeEnrichment(ctx, 8, "kb", "doc", stamp)
	require.NoError(t, err)
	require.False(t, claimed)
	claimed, err = r.ClaimKnowledgeEnrichment(ctx, 7, "other", "doc", stamp)
	require.NoError(t, err)
	require.False(t, claimed)
	claimed, err = r.ClaimKnowledgeEnrichment(ctx, 7, "kb", "doc", stamp)
	require.NoError(t, err)
	require.True(t, claimed)
	claimed, err = r.ClaimKnowledgeEnrichment(ctx, 7, "kb", "doc", stamp)
	require.NoError(t, err)
	require.False(t, claimed)
	require.NoError(t, r.ReleaseKnowledgeEnrichment(ctx, 7, "kb", "doc", stamp.Add(time.Second)))
	var kn types.Knowledge
	require.NoError(t, db.First(&kn, "id = ?", "doc").Error)
	require.Equal(t, types.ParseStatusProcessing, kn.ParseStatus)
	require.NoError(t, r.ReleaseKnowledgeEnrichment(ctx, 7, "kb", "doc", stamp))
	require.NoError(t, db.First(&kn, "id = ?", "doc").Error)
	require.Equal(t, types.ParseStatusCompleted, kn.ParseStatus)
	require.Equal(t, "completed", kn.SummaryStatus)
}
