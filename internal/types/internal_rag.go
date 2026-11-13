package types

// InternalRAGChunk is one already-cleaned and already-split passage exported by
// internal-rag. WeKnora persists it as-is and only performs retrieval indexing.
type InternalRAGChunk struct {
	ChunkID             string   `json:"chunk_id"`
	ParentChunkID       string   `json:"parent_chunk_id"`
	Title               string   `json:"title"`
	Text                string   `json:"text"`
	PageStart           int      `json:"page_start"`
	PageEnd             int      `json:"page_end"`
	SectionPath         []string `json:"section_path"`
	BlockIDs            []string `json:"block_ids"`
	ArticleIDRaw        string   `json:"article_id_raw"`
	ArticleIDNormalized string   `json:"article_id_normalized"`
	ArticleParentID     string   `json:"article_parent_id"`
	ArticleAliases      []string `json:"article_aliases"`
	Keywords            []string `json:"keywords"`
	QuestionAliases     []string `json:"question_aliases"`
	AssetIDs            []string `json:"asset_ids"`
	TableHTML           []string `json:"table_html"`
	TableRows           []any    `json:"table_rows"`
	FormulaLatex        []string `json:"formula_latex"`
	RelatedChunks       []string `json:"related_chunks"`
	ContentType         string   `json:"content_type"`
}

// InternalRAGImportRequest is the stable wire contract used by the bridge.
type InternalRAGImportRequest struct {
	SchemaVersion        string             `json:"schema_version"`
	SourceDocumentID     string             `json:"source_document_id" binding:"required"`
	SourceName           string             `json:"source_name" binding:"required"`
	SourcePath           string             `json:"source_path"`
	SourceSHA256         string             `json:"source_sha256"`
	NormalizedTextSHA256 string             `json:"normalized_text_sha256"`
	ParserName           string             `json:"parser_name"`
	ParserVersion        string             `json:"parser_version"`
	DryRun               bool               `json:"dry_run"`
	Chunks               []InternalRAGChunk `json:"chunks" binding:"required,min=1"`
}

type InternalRAGImportResult struct {
	KnowledgeID string `json:"knowledge_id,omitempty"`
	Action      string `json:"action"`
	ChunkCount  int    `json:"chunk_count"`
	WikiStatus  string `json:"wiki_status,omitempty"`
}

// ExistingChunksEnrichRequest explicitly selects a bounded set of documents.
type ExistingChunksEnrichRequest struct {
	KnowledgeIDs []string `json:"knowledge_ids" binding:"required,min=1,max=20"`
	Wiki         bool     `json:"wiki"`
	Graph        bool     `json:"graph"`
	DryRun       bool     `json:"dry_run"`
}

type ExistingChunksEnrichResult struct {
	KnowledgeID string `json:"knowledge_id"`
	Action      string `json:"action"`
	ChunkCount  int    `json:"chunk_count"`
}
