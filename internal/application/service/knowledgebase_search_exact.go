package service

import (
	"context"
	"path"
	"regexp"
	"strings"

	"github.com/Tencent/WeKnora/internal/logger"
	"github.com/Tencent/WeKnora/internal/types"
)

// A document number is an identifier, not a semantic token. When a question
// names a circular by number ("AC 20-27G的主要内容是什么"), neither retrieval
// channel carries that identifier:
//
//   - The embedding model sees "AC 20-27G" as an arbitrary symbol string, so
//     the vector is dominated by the generic remainder of the question and the
//     named document ranks far outside the candidate pool.
//   - The keyword analyzer splits the number into its digits and letters
//     ("ac", "20", "27", "g"), which in a corpus where every document is
//     titled "AC <number>" are among the most common tokens that exist.
//
// The result is that a document the user named outright can lose to whatever
// unrelated passage the generic remainder of the question happens to resemble.
// The lookup below restores the missing signal by reading the number as an
// identifier and matching it against document names, where it is authoritative.
//
// It is deliberately narrow: it runs only for a complete number, only inside
// knowledge bases the caller was already authorized for, and it only guarantees
// representation in the candidate list — it never replaces the ordinary
// ranking, and it never invents evidence.
const (
	// exactDocumentLookupLimit bounds how many numbers one turn resolves. A
	// question naming many circulars is comparing them, and expanding every
	// mention would displace the ordinary ranking without answering it.
	exactDocumentLookupLimit = 3
	// exactDocumentChunkBudget is how many passages one resolved document may
	// contribute.
	exactDocumentChunkBudget = 3
	// exactDocumentCandidatePage bounds the name-substring candidates examined
	// per number before the exact comparison below.
	exactDocumentCandidatePage = 50
)

// acNumberPattern recognises a document number the way users and file names
// write one: "AC 20-27G", "AC_20-27G", "AC20-27G". Two details carry the
// precision:
//
//   - The revision letter is optional, so a bare "AC 20-27" is still recognised
//     as a mention. It simply will not resolve to a document, which is the
//     desired conservative outcome.
//   - The trailing group requires a non-alphanumeric character (or the end of
//     the text) after the number. That is what stops "AC 20-27GX" from being
//     read as "20-27G" and quietly pinning a neighbouring document, while still
//     accepting "AC_20-138D_part01_p0001-0200.pdf" and "AC 20-27G的主要内容".
//
// \b is the ASCII word boundary, so a mention preceded by a non-ASCII character
// ("编号AC_20-27G") is recognised as well.
var acNumberPattern = regexp.MustCompile(
	`(?i)\bAC[\s_\-]*(\d{1,3})\s*-\s*(\d{1,4})\s*([A-Z]?)(?:[^0-9A-Za-z]|$)`,
)

// mentionedACNumbers returns the distinct document numbers mentioned across the
// given queries, in first-seen order. Passing the caller's verbatim question
// alongside the retrieval query matters because the retrieval query may be a
// rewrite, and a rewrite may normalise or drop the number.
//
// A question that mentions more than exactDocumentLookupLimit numbers is
// treated as a comparison question and yields nothing: pinning every mentioned
// document would crowd out the passages that actually answer the comparison.
func mentionedACNumbers(queries ...string) []string {
	var numbers []string
	seen := make(map[string]bool)
	for _, query := range queries {
		for _, match := range acNumberPattern.FindAllStringSubmatch(query, -1) {
			number := strings.ToUpper(match[1] + "-" + match[2] + match[3])
			if seen[number] {
				continue
			}
			seen[number] = true
			numbers = append(numbers, number)
			if len(numbers) > exactDocumentLookupLimit {
				return nil
			}
		}
	}
	return numbers
}

// normalizeACDocumentID reduces a document file name or title to its number
// ("AC_20-27G.pdf" -> "20-27G", "AC_20-138D_part01_p0001-0200.pdf" -> "20-138D"),
// reporting false when the name does not denote a circular at all. The name is
// matched with the same pattern as a question, so a name that merely contains a
// number-like substring ("AC_20-27GX") is rejected rather than rounded to its
// neighbour.
func normalizeACDocumentID(name string) (string, bool) {
	stem := strings.TrimSpace(path.Base(strings.ReplaceAll(name, `\`, "/")))
	if stem == "" {
		return "", false
	}
	// The extension is irrelevant to the match; trimming it keeps the
	// trailing-character rule independent of the file type.
	stem = strings.TrimSuffix(strings.ToUpper(stem), ".PDF")

	match := acNumberPattern.FindStringSubmatch(stem)
	if match == nil {
		return "", false
	}
	return strings.ToUpper(match[1] + "-" + match[2] + match[3]), true
}

// namesACDocument reports whether the document itself is the given number, as
// opposed to merely containing it somewhere in its name.
func namesACDocument(knowledge *types.Knowledge, number string) bool {
	for _, name := range []string{knowledge.FileName, knowledge.Title} {
		if id, ok := normalizeACDocumentID(name); ok && id == number {
			return true
		}
	}
	return false
}

// pinNamedDocuments guarantees that a document the question names by number is
// represented in the candidate list.
//
// It runs before the MatchCount truncation because that truncation is the last
// point at which a document that lost the ranking can still be kept: merge,
// rerank and filter only ever remove candidates. Appending after the truncation
// would be a no-op.
func (s *knowledgeBaseService) pinNamedDocuments(
	ctx context.Context,
	chunks []*types.IndexWithScore,
	kbs []*types.KnowledgeBase,
	params types.SearchParams,
) []*types.IndexWithScore {
	// An explicit document or tag selection is the caller's own scope. Widening
	// it to every document the question happens to mention would override that
	// choice, so this pass stands down entirely.
	if len(params.KnowledgeIDs) > 0 || len(params.TagIDs) > 0 || len(params.ScopeTagIDs) > 0 {
		return chunks
	}

	numbers := mentionedACNumbers(params.OriginalQuery, params.QueryText)
	if len(numbers) == 0 {
		return chunks
	}

	scopes := make([]types.KnowledgeSearchScope, 0, len(kbs))
	for _, kb := range kbs {
		if kb != nil {
			scopes = append(scopes, types.KnowledgeSearchScope{TenantID: kb.TenantID, KBID: kb.ID})
		}
	}
	if len(scopes) == 0 {
		return chunks
	}

	documents := s.findNamedDocuments(ctx, scopes, numbers)
	if len(documents) == 0 {
		return chunks
	}

	// Duplicate suppression is scoped to the pinned set only. A named document's
	// passage is very often already somewhere in this list — the list is still
	// untruncated here, so "already present at position 200" is precisely the
	// case the truncation below discards. Skipping on presence would make the
	// whole pass a no-op for exactly the documents that need it.
	pinned := make([]*types.IndexWithScore, 0, len(documents)*exactDocumentChunkBudget)
	seen := make(map[string]bool, len(pinned))
	for _, document := range documents {
		for _, chunk := range s.namedDocumentChunks(ctx, document, params) {
			if chunk == nil || chunk.ChunkID == "" || seen[chunk.ChunkID] {
				continue
			}
			seen[chunk.ChunkID] = true
			pinned = append(pinned, chunk)
		}
	}
	if len(pinned) == 0 {
		logger.Warnf(ctx, "Documents named by the query %v resolved but contributed no passage", numbers)
		return chunks
	}

	logger.Infof(ctx, "Pinned %d passage(s) from %d document(s) named by the query %v",
		len(pinned), len(documents), numbers)
	return promoteNamedChunks(pinned, chunks)
}

// promoteNamedChunks places the pinned passages ahead of the remaining
// candidates and drops their older copies, so each chunk appears exactly once
// and the pinned ones survive the MatchCount truncation the caller applies next.
func promoteNamedChunks(pinned, candidates []*types.IndexWithScore) []*types.IndexWithScore {
	promoted := make(map[string]bool, len(pinned))
	for _, chunk := range pinned {
		if chunk != nil && chunk.ChunkID != "" {
			promoted[chunk.ChunkID] = true
		}
	}

	out := make([]*types.IndexWithScore, 0, len(pinned)+len(candidates))
	out = append(out, pinned...)
	for _, chunk := range candidates {
		if chunk == nil || promoted[chunk.ChunkID] {
			continue
		}
		out = append(out, chunk)
	}
	return out
}

// findNamedDocuments resolves mentioned numbers to documents inside the mirrors
// of already-authorized knowledge bases. Only a completed, enabled document
// whose own name is exactly the mentioned number qualifies.
func (s *knowledgeBaseService) findNamedDocuments(
	ctx context.Context,
	scopes []types.KnowledgeSearchScope,
	numbers []string,
) []*types.Knowledge {
	if s.kgRepo == nil {
		return nil
	}

	var documents []*types.Knowledge
	seen := make(map[string]bool)
	for _, number := range numbers {
		// The repository narrows by name or title substring; the exact
		// normalised comparison below is what separates "20-27G" from its
		// neighbours ("20-27GX", "20-274", ...).
		candidates, _, _, err := s.kgRepo.SearchKnowledgeInScopes(
			ctx, scopes, number, 0, exactDocumentCandidatePage, nil,
		)
		if err != nil {
			logger.Warnf(ctx, "Document lookup for %s failed: %v", number, err)
			continue
		}
		for _, candidate := range candidates {
			if candidate == nil || seen[candidate.ID] {
				continue
			}
			if candidate.ParseStatus != types.ParseStatusCompleted || candidate.EnableStatus != "enabled" {
				continue
			}
			if !namesACDocument(candidate, number) {
				continue
			}
			seen[candidate.ID] = true
			documents = append(documents, candidate)
		}
	}
	return documents
}

// namedDocumentChunks retrieves passages from one resolved document by running
// the ordinary hybrid retrieval constrained to it. Reusing that path keeps
// thresholds, fusion and result assembly identical to a normal search; only the
// scope narrows. The recursion terminates because the inner call is told not to
// run this pass again.
func (s *knowledgeBaseService) namedDocumentChunks(
	ctx context.Context,
	document *types.Knowledge,
	params types.SearchParams,
) []*types.IndexWithScore {
	scoped := types.SearchParams{
		QueryText:             params.QueryText,
		QueryEmbedding:        params.QueryEmbedding,
		KnowledgeBaseIDs:      []string{document.KnowledgeBaseID},
		KnowledgeIDs:          []string{document.ID},
		VectorThreshold:       params.VectorThreshold,
		KeywordThreshold:      params.KeywordThreshold,
		MatchCount:            exactDocumentChunkBudget,
		SkipContextEnrichment: true,
		DisableKeywordsMatch:  params.DisableKeywordsMatch,
		DisableVectorMatch:    params.DisableVectorMatch,
	}
	results, err := s.hybridSearch(ctx, document.KnowledgeBaseID, scoped, false)
	if err != nil {
		logger.Warnf(ctx, "Document lookup retrieval failed for %s: %v", document.ID, err)
		return nil
	}

	chunks := make([]*types.IndexWithScore, 0, len(results))
	for _, result := range results {
		if result == nil || result.ID == "" {
			continue
		}
		// buildChunkIndex reads exactly these fields. The passage body and all
		// display metadata are re-read from the database by
		// processSearchResults, so nothing needs to be carried across but the
		// identity, the score and the match type.
		chunks = append(chunks, &types.IndexWithScore{
			ID:              result.ID,
			Content:         result.Content,
			ChunkID:         result.ID,
			KnowledgeID:     result.KnowledgeID,
			KnowledgeBaseID: result.KnowledgeBaseID,
			Score:           result.Score,
			MatchType:       result.MatchType,
			IsEnabled:       true,
		})
	}
	return chunks
}
