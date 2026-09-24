package service

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
)

func TestMentionedACNumbers(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name   string
		query  string
		expect []string
	}{
		{
			name:   "underscore form from the failing case",
			query:  "AC_20-27G的主要内容是什么",
			expect: []string{"20-27G"},
		},
		{
			name:   "spaced form with a trailing question",
			query:  "AC 20-18B 的指导目的是什么？",
			expect: []string{"20-18B"},
		},
		{
			name:   "no separator at all",
			query:  "AC20-27G 讲了什么",
			expect: []string{"20-27G"},
		},
		{
			name:   "lowercase",
			query:  "ac_20-27g 的主要内容",
			expect: []string{"20-27G"},
		},
		{
			name:   "preceded by a non-ASCII character",
			query:  "编号AC_20-27G的主要内容",
			expect: []string{"20-27G"},
		},
		{
			name:   "comma-separated context",
			query:  "按 AC 20-24D，航空器运营方可以使用哪些燃油和润滑油？",
			expect: []string{"20-24D"},
		},
		{
			name:   "revision letter is optional",
			query:  "AC 20-27 的主要内容是什么",
			expect: []string{"20-27"},
		},
		{
			name:   "multi-part file name keeps only the number",
			query:  "AC_20-138D_part01_p0001-0200.pdf 的内容",
			expect: []string{"20-138D"},
		},
		{
			name:   "two numbers keep first-seen order",
			query:  "AC 20-27G 与 AC 20-37E 的区别",
			expect: []string{"20-27G", "20-37E"},
		},
		{
			name:   "no mention at all",
			query:  "推力反向器操作试验需要证明哪些发动机安全性？",
			expect: nil,
		},
		{
			name:   "a run-together number is not rounded to its neighbour",
			query:  "AC 20-27GX 是什么",
			expect: nil,
		},
		{
			name:   "more than the limit is a comparison, not a lookup",
			query:  "AC 20-1、AC 20-2、AC 20-3、AC 20-4 分别是什么",
			expect: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			assert.Equal(t, tt.expect, mentionedACNumbers(tt.query))
		})
	}
}

// TestMentionedACNumbersReadsBothQueries pins that the verbatim question is
// read as well as the retrieval query. The retrieval query may be an LLM
// rewrite, and a rewrite that normalises or drops the number would otherwise
// remove the only usable signal in the turn.
func TestMentionedACNumbersReadsBothQueries(t *testing.T) {
	t.Parallel()

	assert.Equal(t, []string{"20-27G"}, mentionedACNumbers("", "AC_20-27G的主要内容是什么"))
	assert.Equal(t, []string{"20-27G"}, mentionedACNumbers("AC_20-27G的主要内容是什么", ""))
	assert.Equal(t, []string{"20-27G"}, mentionedACNumbers("AC_20-27G的主要内容", "AC_20-27G的主要内容"))
}

func TestNormalizeACDocumentID(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name   string
		doc    string
		expect string
		ok     bool
	}{
		{name: "plain file name", doc: "AC_20-27G.pdf", expect: "20-27G", ok: true},
		{name: "spaced file name", doc: "AC 20-18B.pdf", expect: "20-18B", ok: true},
		{name: "no revision letter", doc: "AC_20-100.pdf", expect: "20-100", ok: true},
		{name: "title without extension", doc: "AC_20-24D", expect: "20-24D", ok: true},
		{
			name:   "multi-part file name",
			doc:    "AC_20-138D_part01_p0001-0200.pdf",
			expect: "20-138D",
			ok:     true,
		},
		{
			name:   "title with a descriptive tail",
			doc:    "AC_20-27G Certification and Operation of Amateur-Built Aircraft.pdf",
			expect: "20-27G",
			ok:     true,
		},
		{name: "windows path", doc: `C:\kbs\AC_20-29C.pdf`, expect: "20-29C", ok: true},
		{name: "not a circular at all", doc: "23-48.pdf", expect: "", ok: false},
		{name: "neighbouring number is not rounded", doc: "AC_20-27GX.pdf", expect: "", ok: false},
		{name: "empty", doc: "", expect: "", ok: false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			got, ok := normalizeACDocumentID(tt.doc)
			assert.Equal(t, tt.ok, ok)
			assert.Equal(t, tt.expect, got)
		})
	}
}

// stubExactKnowledgeRepo serves the name-substring candidate page and counts
// calls, so the stand-down guards can be asserted without a database.
type stubExactKnowledgeRepo struct {
	interfaces.KnowledgeRepository
	documents  []*types.Knowledge
	searchCall int
}

func (r *stubExactKnowledgeRepo) SearchKnowledgeInScopes(
	context.Context, []types.KnowledgeSearchScope, string, int, int, []string,
) ([]*types.Knowledge, bool, int64, error) {
	r.searchCall++
	return r.documents, false, int64(len(r.documents)), nil
}

func exactTestKnowledgeBase() []*types.KnowledgeBase {
	return []*types.KnowledgeBase{{ID: "kb-1", TenantID: 10000, Type: types.KnowledgeBaseTypeDocument}}
}

// TestPinNamedDocumentsStandsDown pins every guard that keeps this pass from
// changing behavior for questions that do not name a document outright. Each
// case must leave the candidate list byte-for-byte unchanged and must not reach
// the repository at all.
func TestPinNamedDocumentsStandsDown(t *testing.T) {
	t.Parallel()

	chunks := []*types.IndexWithScore{{ChunkID: "chunk-a", KnowledgeID: "doc-a", Score: 0.01}}

	tests := []struct {
		name   string
		params types.SearchParams
	}{
		{
			name:   "no document number in the question",
			params: types.SearchParams{QueryText: "推力反向器操作试验需要证明哪些发动机安全性？"},
		},
		{
			name: "caller pinned explicit documents",
			params: types.SearchParams{
				QueryText:    "AC_20-27G的主要内容是什么",
				KnowledgeIDs: []string{"doc-a"},
			},
		},
		{
			name: "caller scoped by tag",
			params: types.SearchParams{
				QueryText: "AC_20-27G的主要内容是什么",
				TagIDs:    []string{"tag-1"},
			},
		},
		{
			name: "caller scoped by scope tag",
			params: types.SearchParams{
				QueryText:   "AC_20-27G的主要内容是什么",
				ScopeTagIDs: []string{"tag-1"},
			},
		},
		{
			name:   "comparison question mentioning many documents",
			params: types.SearchParams{QueryText: "AC 20-1、AC 20-2、AC 20-3、AC 20-4 分别是什么"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel()
			repo := &stubExactKnowledgeRepo{}
			svc := &knowledgeBaseService{kgRepo: repo}

			got := svc.pinNamedDocuments(context.Background(), chunks, exactTestKnowledgeBase(), tt.params)

			require.Len(t, got, len(chunks))
			assert.Equal(t, "chunk-a", got[0].ChunkID)
			assert.Zero(t, repo.searchCall, "guards must not query the repository")
		})
	}
}

// TestPinNamedDocumentsIgnoresNonMatchingCandidates pins the exactness of the
// name comparison: a repository substring hit is not enough, the document's own
// name must be the mentioned number.
func TestPinNamedDocumentsIgnoresNonMatchingCandidates(t *testing.T) {
	t.Parallel()

	candidates := []*types.Knowledge{
		{
			ID:              "doc-neighbour",
			KnowledgeBaseID: "kb-1",
			FileName:        "AC_20-27GX.pdf",
			Title:           "AC_20-27GX.pdf",
			ParseStatus:     types.ParseStatusCompleted,
			EnableStatus:    "enabled",
		},
		{
			ID:              "doc-disabled",
			KnowledgeBaseID: "kb-1",
			FileName:        "AC_20-27G.pdf",
			Title:           "AC_20-27G.pdf",
			ParseStatus:     types.ParseStatusCompleted,
			EnableStatus:    "disabled",
		},
		{
			ID:              "doc-unparsed",
			KnowledgeBaseID: "kb-1",
			FileName:        "AC_20-27G.pdf",
			Title:           "AC_20-27G.pdf",
			ParseStatus:     "processing",
			EnableStatus:    "enabled",
		},
	}

	repo := &stubExactKnowledgeRepo{documents: candidates}
	svc := &knowledgeBaseService{kgRepo: repo}

	documents := svc.findNamedDocuments(context.Background(), []types.KnowledgeSearchScope{
		{TenantID: 10000, KBID: "kb-1"},
	}, []string{"20-27G"})

	assert.Empty(t, documents)
	assert.Equal(t, 1, repo.searchCall)
}

func TestFindNamedDocumentsAcceptsExactAndMultiPartNames(t *testing.T) {
	t.Parallel()

	candidates := []*types.Knowledge{
		{
			ID:              "doc-plain",
			KnowledgeBaseID: "kb-1",
			FileName:        "AC_20-27G.pdf",
			Title:           "AC_20-27G.pdf",
			ParseStatus:     types.ParseStatusCompleted,
			EnableStatus:    "enabled",
		},
		{
			ID:              "doc-part",
			KnowledgeBaseID: "kb-1",
			FileName:        "AC_20-138D_part01_p0001-0200.pdf",
			Title:           "AC_20-138D_part01_p0001-0200.pdf",
			ParseStatus:     types.ParseStatusCompleted,
			EnableStatus:    "enabled",
		},
	}

	repo := &stubExactKnowledgeRepo{documents: candidates}
	svc := &knowledgeBaseService{kgRepo: repo}

	documents := svc.findNamedDocuments(context.Background(), []types.KnowledgeSearchScope{
		{TenantID: 10000, KBID: "kb-1"},
	}, []string{"20-27G", "20-138D"})

	require.Len(t, documents, 2)
	assert.Equal(t, "doc-plain", documents[0].ID)
	assert.Equal(t, "doc-part", documents[1].ID)
}

func TestNamesACDocument(t *testing.T) {
	t.Parallel()

	document := &types.Knowledge{FileName: "AC_20-24D.pdf", Title: "AC_20-24D.pdf"}
	assert.True(t, namesACDocument(document, "20-24D"))
	assert.False(t, namesACDocument(document, "20-24"))
	assert.False(t, namesACDocument(document, "20-27G"))
}

// TestPromoteNamedChunks is the regression for the case that made the first
// deployment a partial success. The pin pass runs while the candidate list is
// still untruncated, and a named document's passage is usually already in that
// list — just below the cut. Treating "already present" as "nothing to do" made
// the pass a no-op for precisely the documents it exists to rescue, while still
// appearing to work for documents whose passages happened to be absent.
func TestPromoteNamedChunks(t *testing.T) {
	t.Parallel()

	chunk := func(id string) *types.IndexWithScore {
		return &types.IndexWithScore{ChunkID: id, KnowledgeID: "doc-" + id}
	}
	ids := func(chunks []*types.IndexWithScore) []string {
		out := make([]string, 0, len(chunks))
		for _, c := range chunks {
			out = append(out, c.ChunkID)
		}
		return out
	}

	t.Run("a passage already below the cut is moved to the front, once", func(t *testing.T) {
		t.Parallel()
		candidates := []*types.IndexWithScore{chunk("a"), chunk("b"), chunk("target"), chunk("c")}
		got := promoteNamedChunks([]*types.IndexWithScore{chunk("target")}, candidates)

		assert.Equal(t, []string{"target", "a", "b", "c"}, ids(got))
	})

	t.Run("absent passages are prepended and order is preserved", func(t *testing.T) {
		t.Parallel()
		candidates := []*types.IndexWithScore{chunk("a"), chunk("b")}
		got := promoteNamedChunks([]*types.IndexWithScore{chunk("x"), chunk("y")}, candidates)

		assert.Equal(t, []string{"x", "y", "a", "b"}, ids(got))
	})

	t.Run("mixed: one moved, one prepended", func(t *testing.T) {
		t.Parallel()
		candidates := []*types.IndexWithScore{chunk("a"), chunk("target"), chunk("b")}
		got := promoteNamedChunks([]*types.IndexWithScore{chunk("x"), chunk("target")}, candidates)

		assert.Equal(t, []string{"x", "target", "a", "b"}, ids(got))
	})

	t.Run("no pinned passages leaves the candidates untouched", func(t *testing.T) {
		t.Parallel()
		candidates := []*types.IndexWithScore{chunk("a"), chunk("b")}
		assert.Equal(t, []string{"a", "b"}, ids(promoteNamedChunks(nil, candidates)))
	})

	t.Run("nil entries never break the identity", func(t *testing.T) {
		t.Parallel()
		candidates := []*types.IndexWithScore{chunk("a"), nil, chunk("b")}
		assert.Equal(t, []string{"a", "b"}, ids(promoteNamedChunks(nil, candidates)))
	})
}
