package handler

import (
	"bytes"
	"encoding/json"
	"github.com/Tencent/WeKnora/internal/types"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// Ragas forwards one imported sample to the private evaluation worker.
// The existing evaluation route group supplies tenant authentication and Admin RBAC.
func (e *EvaluationHandler) Ragas(c *gin.Context) {
	endpoint := strings.TrimRight(os.Getenv("RAGAS_WORKER_URL"), "/")
	if endpoint == "" {
		c.JSON(503, gin.H{"error": "尚未配置 RAGAS_WORKER_URL，请先启动评测服务"})
		return
	}
	body, err := io.ReadAll(http.MaxBytesReader(c.Writer, c.Request.Body, 2<<20))
	if err != nil {
		c.JSON(400, gin.H{"error": "评测样本不能超过 2MB"})
		return
	}
	var payload map[string]json.RawMessage
	if json.Unmarshal(body, &payload) != nil || payload == nil {
		c.JSON(400, gin.H{"error": "无效评测样本"})
		return
	}
	// Ignore any browser-supplied credentials. Resolve the model within the authenticated tenant.
	delete(payload, "judge")
	if e.modelService != nil {
		var modelID string
		if json.Unmarshal(payload["model_id"], &modelID) != nil || modelID == "" {
			c.JSON(400, gin.H{"error": "请选择评判模型"})
			return
		}
		model, lookupErr := e.modelService.GetModelByID(c.Request.Context(), modelID)
		if lookupErr != nil || model == nil || model.Type != types.ModelTypeKnowledgeQA {
			c.JSON(400, gin.H{"error": "评判模型不可用"})
			return
		}
		baseURL := strings.TrimRight(model.Parameters.BaseURL, "/")
		if model.Source == types.ModelSourceLocal {
			baseURL += "/v1"
		}
		if baseURL == "" {
			c.JSON(400, gin.H{"error": "请先在模型设置中配置 API 地址"})
			return
		}
		for _, suffix := range []string{"/chat/completions", "/responses"} {
			baseURL = strings.TrimSuffix(baseURL, suffix)
		}
		headers := map[string]string{}
		for k, v := range model.Parameters.CustomHeaders {
			switch strings.ToLower(k) {
			case "authorization", "api-key", "content-type", "accept", "host":
				continue
			}
			headers[k] = v
		}
		payload["judge"], _ = json.Marshal(map[string]interface{}{"model": model.Name, "api_key": model.Parameters.APIKey, "base_url": baseURL, "headers": headers})
	}
	delete(payload, "model_id")
	body, err = json.Marshal(payload)
	if err != nil {
		c.JSON(400, gin.H{"error": "无效评测样本"})
		return
	}
	req, err := http.NewRequestWithContext(c.Request.Context(), http.MethodPost, endpoint+"/score", bytes.NewReader(body))
	if err != nil {
		c.JSON(503, gin.H{"error": "评测服务配置无效"})
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+os.Getenv("RAGAS_WORKER_TOKEN"))
	client := &http.Client{Timeout: 180 * time.Second, CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return http.ErrUseLastResponse }}
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(502, gin.H{"error": "评测服务不可用或超时"})
		return
	}
	defer resp.Body.Close()
	result, err := io.ReadAll(io.LimitReader(resp.Body, 2<<20))
	if err != nil {
		c.JSON(502, gin.H{"error": "读取评测结果失败"})
		return
	}
	c.Data(resp.StatusCode, "application/json", result)
}
