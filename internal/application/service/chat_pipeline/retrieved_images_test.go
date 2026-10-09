package chatpipeline

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"image"
	"image/png"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/Tencent/WeKnora/internal/models/api"
	"github.com/Tencent/WeKnora/internal/models/api/openaicompletions"
	"github.com/Tencent/WeKnora/internal/models/chat"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/stretchr/testify/require"
)

func testImageBytes(t *testing.T) []byte {
	t.Helper()
	var buf bytes.Buffer
	require.NoError(t, png.Encode(&buf, image.NewRGBA(image.Rect(0, 0, 2, 2))))
	return buf.Bytes()
}

func TestSelectRetrievedImagesUsesMatchedPassageAndDeduplicates(t *testing.T) {
	refs := []*types.SearchResult{{ID: "chunk", KnowledgeID: "doc", KnowledgeTitle: "AC_20-69.pdf",
		MatchedContent: "a. Compass (See Figure 1).",
		Content:        "![Signature](https://example.com/sign.png)\n![Figure 2 Attitude](https://example.com/2.png)\n![Figure 1 Compass Area](https://example.com/1.png)",
		RelatedImages:  []types.RelatedImage{{URL: "https://example.com/1.png", Caption: "Figure 1 Compass Area"}},
	}, {ID: "web", ChunkType: "web_search", Content: "![Figure 1](https://example.com/web.png)"}}
	images := selectRetrievedImages("解释罗盘面积公式", refs)
	require.Len(t, images, 3)
	require.Equal(t, "https://example.com/1.png", images[0].URL)
	require.Equal(t, "chunk", images[0].SourceChunkID)

	refs[0].MatchedContent = "![Figure 2 Attitude](https://example.com/2.png)"
	images = selectRetrievedImages("解释仪表", refs)
	require.Equal(t, "https://example.com/2.png", images[0].URL)
}

func TestSelectRetrievedImagesRespectsLimitAndHTML(t *testing.T) {
	var content strings.Builder
	for i := 0; i < 8; i++ {
		content.WriteString("![image](https://example.com/" + string(rune('a'+i)) + ".png)\n")
	}
	images := selectRetrievedImages("", []*types.SearchResult{{Content: content.String()}})
	require.Len(t, images, maxRetrievedImages)
	images = selectRetrievedImages("", []*types.SearchResult{{Content: `<img src="https://example.com/image.png">`}})
	require.Len(t, images, 1)
	require.Equal(t, "https://example.com/image.png", images[0].URL)
}

func TestRetrievedImageResolverTrustedIngestionAndLimits(t *testing.T) {
	imageBytes := testImageBytes(t)
	asset := "/api/v1/ingestion/jobs/" + strings.Repeat("a", 32) + "/assets/" + strings.Repeat("b", 20)
	requests := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		requests++
		require.Equal(t, asset, req.URL.Path)
		_, _ = w.Write(imageBytes)
	}))
	defer server.Close()
	r := newRetrievedImageResolver(nil, nil, nil)
	r.ingestionOrigin = "http://localhost:8080"
	r.ingestionBase = server.URL
	data, size, err := r.resolve(context.Background(), 1, "http://localhost:8080"+asset)
	require.NoError(t, err)
	require.Equal(t, len(imageBytes), size)
	require.Equal(t, "data:image/png;base64,"+base64.StdEncoding.EncodeToString(imageBytes), data)
	_, _, err = r.resolve(context.Background(), 1, "http://localhost:8080/admin")
	require.Error(t, err)
	require.Equal(t, 1, requests)
	_, _, err = r.resolve(context.Background(), 1, "http://localhost:8080"+asset+"?url=http://127.0.0.1")
	require.Error(t, err)
	require.Equal(t, 1, requests)
	_, err = readLimitedImage(strings.NewReader(strings.Repeat("x", maxRetrievedImageBytes+1)))
	require.Error(t, err)
	_, _, err = r.resolve(context.Background(), 1, "data:image/png;base64,"+base64.StdEncoding.EncodeToString([]byte("not an image")))
	require.Error(t, err)
}

func TestRetrievedImageResolverDoesNotFollowIngestionRedirect(t *testing.T) {
	requests := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, req *http.Request) {
		requests++
		http.Redirect(w, req, "/admin", http.StatusFound)
	}))
	defer server.Close()
	r := newRetrievedImageResolver(nil, nil, nil)
	r.ingestionOrigin = "http://localhost:8080"
	r.ingestionBase = server.URL
	_, _, err := r.resolve(context.Background(), 1, "http://localhost:8080/api/v1/ingestion/jobs/"+strings.Repeat("a", 32)+"/assets/"+strings.Repeat("b", 20))
	require.Error(t, err)
	require.Equal(t, 1, requests)
}

func TestRetrievedImagesReachWireWithSourceAndPreserveUploads(t *testing.T) {
	data := "data:image/png;base64," + base64.StdEncoding.EncodeToString(testImageBytes(t))
	cm := &types.ChatManage{
		PipelineRequest: types.PipelineRequest{Query: "解释两个半径", ChatModelSupportsVision: true, Images: []string{data}},
		PipelineState: types.PipelineState{UserContent: "解释两个半径", MergeResult: []*types.SearchResult{{
			ID: "chunk-1", KnowledgeID: "doc-1", KnowledgeTitle: "AC_20-69.pdf", KnowledgeBaseID: "kb-1", Content: "Figure 1 Compass Area",
		}}, RetrievedImages: []types.RetrievedImage{{URL: "https://example.com/figure.png", Caption: "Figure 1 Compass Area",
			KnowledgeTitle: "AC_20-69.pdf", SourceChunkID: "chunk-1", DataURL: data}}},
	}
	messages, registry := prepareMessagesWithModelContext(context.Background(), cm)
	messages = registry.EncodeMessages(messages)
	messages = appendRetrievedImageMessage(context.Background(), messages, cm, registry)
	require.Equal(t, []string{data}, messages[len(messages)-2].Images)
	parts := messages[len(messages)-1].MultiContent
	require.Len(t, parts, 3)
	require.Contains(t, parts[1].Text, "Figure 1 Compass Area")
	require.Contains(t, parts[1].Text, registry.ChunkHandle("chunk-1"))
	require.Equal(t, "high", parts[2].ImageURL.Detail)
	client := openaicompletions.New(openaicompletions.Config{Settings: api.DefaultOpenAICompletions()})
	body, err := client.BuildRequestBody(messages, &api.Options{RequireImageInput: true}, true)
	require.NoError(t, err)
	wire, err := json.Marshal(body)
	require.NoError(t, err)
	require.Equal(t, 2, strings.Count(string(wire), `"type":"image_url"`))
	require.Contains(t, string(wire), `"detail":"high"`)
	require.Contains(t, string(wire), data)
}

func TestRetrievedImageFailureIsExplicitAndDoesNotAttachURL(t *testing.T) {
	cm := &types.ChatManage{PipelineState: types.PipelineState{RetrievedImages: []types.RetrievedImage{{
		Caption: "Figure 1", ReadError: "图片读取失败，本次没有读取原图",
	}}}}
	_, registry := prepareMessagesWithModelContext(context.Background(), cm)
	messages := appendRetrievedImageMessage(context.Background(), []chat.Message{{Role: "user", Content: "query"}}, cm, registry)
	parts := messages[1].MultiContent
	require.Len(t, parts, 2)
	require.Contains(t, parts[1].Text, "没有读取原图")
}
