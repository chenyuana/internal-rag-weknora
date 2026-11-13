package chatpipeline

import (
	"context"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"

	"github.com/Tencent/WeKnora/internal/logger"
	"github.com/Tencent/WeKnora/internal/searchutil"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
)

// PluginWikiRecall uses published topics as a discovery layer. The answer sees
// original chunks, never synthesized Wiki prose presented as original evidence.
type PluginWikiRecall struct {
	kb        interfaces.KnowledgeBaseService
	wiki      interfaces.WikiPageService
	chunks    interfaces.ChunkRepository
	knowledge interfaces.KnowledgeRepository
}

func NewPluginWikiRecall(events *EventManager, kb interfaces.KnowledgeBaseService, wiki interfaces.WikiPageService, chunks interfaces.ChunkRepository, knowledge interfaces.KnowledgeRepository) *PluginWikiRecall {
	p := &PluginWikiRecall{kb: kb, wiki: wiki, chunks: chunks, knowledge: knowledge}
	events.Register(p)
	return p
}

func (p *PluginWikiRecall) ActivationEvents() []types.EventType {
	return []types.EventType{types.CHUNK_SEARCH, types.CHUNK_SEARCH_PARALLEL}
}

func (p *PluginWikiRecall) OnEvent(ctx context.Context, _ types.EventType, cm *types.ChatManage, next func() *PluginError) *PluginError {
	if !cm.NeedsRetrieval() {
		return next()
	}
	err := next()
	if err != nil && err.ErrorType != ErrSearchNothing.ErrorType {
		return err
	}
	terms := wikiRecallTerms(cm.Query)
	if len(terms) == 0 || p.wiki == nil {
		return err
	}
	patterns := make([]string, len(terms))
	for i, term := range terms {
		patterns[i] = regexp.QuoteMeta(term)
	}
	seen := map[string]bool{}
	for _, r := range cm.SearchResult {
		if r != nil {
			seen[r.ID] = true
		}
	}
	added := 0
	for _, target := range cm.SearchTargets {
		if target == nil || target.KnowledgeBaseID == "" {
			continue
		}
		// Document/tag constraints must never be widened by a Wiki reference.
		if (len(target.TagIDs) > 0 || len(target.ScopeTagIDs) > 0 || target.Type == types.SearchTargetTypeKnowledge) && len(target.KnowledgeIDs) == 0 {
			continue
		}
		kb, readErr := p.kb.GetKnowledgeBaseByID(ctx, target.KnowledgeBaseID)
		// Shared-tenant Wiki recall is deliberately left to the access-aware Agent
		// tools; this owner-scoped path must not bypass their grants.
		if readErr != nil || kb == nil || !kb.IsWikiEnabled() || kb.TenantID != cm.TenantID || (target.TenantID != 0 && target.TenantID != kb.TenantID) {
			continue
		}
		pages, searchErr := p.wiki.SearchPages(ctx, kb.ID, strings.Join(patterns, "|"), 50)
		if searchErr != nil {
			logger.Warnf(ctx, "WikiRecall: topic search failed for %s: %v", kb.ID, searchErr)
			continue
		}
		allowed := map[string]bool{}
		for _, id := range target.KnowledgeIDs {
			allowed[id] = true
		}
		var candidates []*types.WikiPage
		scores := map[*types.WikiPage]int{}
		for _, page := range pages {
			if page == nil || page.KnowledgeBaseID != kb.ID || page.Status != types.WikiPageStatusPublished || len(page.ChunkRefs) == 0 {
				continue
			}
			if !wikiRecallTopicMatch(page, terms) {
				continue
			}
			if len(allowed) > 0 {
				inScope := false
				for _, ref := range page.SourceRefs {
					if allowed[types.WikiSourceKnowledgeID(ref)] {
						inScope = true
						break
					}
				}
				if !inScope {
					continue
				}
			}
			candidates = append(candidates, page)
			scores[page] = wikiRecallScore(page, terms)
		}
		sort.SliceStable(candidates, func(i, j int) bool { return scores[candidates[i]] > scores[candidates[j]] })
		refs := map[string]string{}
		ids := []string{}
		// A topic can identify the right document while citing a different
		// section. Search that bounded document scope for the user's question.
		discoveredDocs := []string{}
		docPage := map[string]string{}
		for _, page := range candidates[:min(5, len(candidates))] {
			for _, source := range page.SourceRefs {
				id := types.WikiSourceKnowledgeID(source)
				if id == "" || docPage[id] != "" || len(discoveredDocs) >= 5 || (len(allowed) > 0 && !allowed[id]) {
					continue
				}
				docPage[id] = page.Slug
				discoveredDocs = append(discoveredDocs, id)
			}
		}
		if len(discoveredDocs) > 0 && (kb.IsVectorEnabled() || kb.IsKeywordEnabled()) {
			hits, scopeErr := p.kb.HybridSearch(ctx, kb.ID, types.SearchParams{QueryText: cm.Query, OriginalQuery: cm.Query, KnowledgeIDs: discoveredDocs, MatchCount: 32, SkipContextEnrichment: true})
			if scopeErr != nil {
				logger.Warnf(ctx, "WikiRecall: scoped evidence search failed: %v", scopeErr)
			}
			for _, hit := range hits {
				if hit != nil && hit.KnowledgeBaseID == kb.ID && docPage[hit.KnowledgeID] != "" && !seen[hit.ID] && refs[hit.ID] == "" && len(ids) < 32 {
					refs[hit.ID] = docPage[hit.KnowledgeID]
					ids = append(ids, hit.ID)
				}
			}
		}
		for _, page := range candidates[:min(5, len(candidates))] {
			for _, id := range page.ChunkRefs {
				if !seen[id] && refs[id] == "" && len(ids) < 32 {
					refs[id] = page.Slug
					ids = append(ids, id)
				}
			}
		}
		if len(ids) == 0 {
			continue
		}
		chunks, readErr := p.chunks.ListChunksByID(ctx, kb.TenantID, ids)
		if readErr != nil {
			logger.Warnf(ctx, "WikiRecall: evidence load failed: %v", readErr)
			continue
		}
		docIDs := []string{}
		for _, chunk := range chunks {
			if chunk != nil && chunk.KnowledgeBaseID == kb.ID && chunk.TenantID == kb.TenantID {
				docIDs = append(docIDs, chunk.KnowledgeID)
			}
		}
		docs, readErr := p.knowledge.GetKnowledgeBatch(ctx, kb.TenantID, docIDs)
		if readErr != nil {
			continue
		}
		docByID := map[string]*types.Knowledge{}
		for _, doc := range docs {
			if doc != nil {
				docByID[doc.ID] = doc
			}
		}
		for _, chunk := range chunks {
			if chunk == nil || chunk.TenantID != kb.TenantID || chunk.KnowledgeBaseID != kb.ID || !chunk.IsEnabled || seen[chunk.ID] || refs[chunk.ID] == "" {
				continue
			}
			if len(allowed) > 0 && !allowed[chunk.KnowledgeID] {
				continue
			}
			doc := docByID[chunk.KnowledgeID]
			if doc == nil || doc.TenantID != kb.TenantID || doc.KnowledgeBaseID != kb.ID || doc.EnableStatus != "enabled" || doc.ParseStatus == types.ParseStatusDeleting || doc.ParseStatus == types.ParseStatusCancelled {
				continue
			}
			r := chunk2SearchResult(chunk, doc)
			r.MatchType = types.MatchTypeWiki
			if r.Metadata == nil {
				r.Metadata = map[string]string{}
			}
			r.Metadata["wiki_recall_page"] = refs[chunk.ID]
			cm.SearchResult = append(cm.SearchResult, r)
			seen[chunk.ID] = true
			added++
		}
		logger.Infof(ctx, "WikiRecall: kb=%s topic_candidates=%d original_chunks=%d session=%s", kb.ID, len(candidates), len(ids), cm.SessionID)
	}
	if added > 0 {
		searchutil.EnrichSearchResultsImageInfo(ctx, p.chunks, cm.TenantID, cm.SearchResult)
		logger.Infof(ctx, "WikiRecall: added=%d session=%s", added, cm.SessionID)
		return nil
	}
	return err
}

func wikiRecallTerms(query string) []string {
	stop := map[string]bool{"每天": true, "一台": true, "另一": true, "没有": true, "如何": true, "哪些": true, "说明": true, "问题": true, "是否": true, "什么": true, "根据": true, "请问": true, "可以": true, "应该": true, "这个": true, "属于": true, "负责": true}
	seen := map[string]bool{}
	terms := []string{}
	for _, raw := range types.Jieba.CutForSearch(query, true) {
		term := strings.ToLower(strings.TrimSpace(raw))
		if utf8.RuneCountInString(term) < 2 || stop[term] || seen[term] {
			continue
		}
		seen[term] = true
		terms = append(terms, term)
	}
	sort.SliceStable(terms, func(i, j int) bool { return utf8.RuneCountInString(terms[i]) > utf8.RuneCountInString(terms[j]) })
	return terms[:min(20, len(terms))]
}

func wikiRecallScore(page *types.WikiPage, terms []string) int {
	score := 0
	title := strings.ToLower(page.Title)
	aliases := strings.ToLower(strings.Join(page.Aliases, " "))
	summary := strings.ToLower(page.Summary)
	content := strings.ToLower(page.Content)
	for _, term := range terms {
		if strings.Contains(title, term) {
			score += 8
		}
		if strings.Contains(aliases, term) {
			score += 6
		}
		if strings.Contains(summary, term) {
			score += 3
		}
		if strings.Contains(content, term) {
			score++
		}
	}
	return score
}

// A generic word in a long page body is insufficient to nominate its sources.
func wikiRecallTopicMatch(page *types.WikiPage, terms []string) bool {
	generic := map[string]bool{"安装": true, "已安装": true, "组件": true, "部件": true, "系统": true, "设备": true, "设计": true, "方法": true, "条件": true, "要求": true, "说明": true, "数据": true, "接口": true, "电源": true, "航空器": true, "飞机": true, "机载": true, "标准": true, "指导": true, "分类": true, "ac": true}
	identity := strings.ToLower(page.Title + " " + strings.Join(page.Aliases, " "))
	for _, term := range terms {
		if generic[term] {
			continue
		}
		if _, err := strconv.Atoi(term); err == nil {
			continue
		}
		if strings.Contains(identity, term) {
			return true
		}
	}
	return false
}
