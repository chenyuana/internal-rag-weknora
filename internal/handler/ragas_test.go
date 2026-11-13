package handler

import (
	"context"
	"encoding/json"
	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/gin-gonic/gin"
)

type ragasTestModels struct{ interfaces.ModelService }

func (ragasTestModels) GetModelByID(_ context.Context, id string) (*types.Model, error) {
	return &types.Model{Name: "test-model", Type: types.ModelTypeKnowledgeQA, Parameters: types.ModelParameters{BaseURL: "https://model.example/v1", APIKey: "server-secret"}}, nil
}

func TestRagasProxy(t *testing.T) {
	gin.SetMode(gin.TestMode)
	worker := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/score" || r.Header.Get("Authorization") != "Bearer secret" {
			t.Error("invalid worker request")
		}
		var body map[string]interface{}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			t.Fatal(err)
		}
		judge := body["judge"].(map[string]interface{})
		if judge["api_key"] != "server-secret" || judge["model"] != "test-model" {
			t.Error("browser credentials were trusted")
		}
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"scores":{"faithfulness":0.75}}`))
	}))
	defer worker.Close()
	t.Setenv("RAGAS_WORKER_URL", worker.URL)
	t.Setenv("RAGAS_WORKER_TOKEN", "secret")
	router := gin.New()
	router.POST("/", (&EvaluationHandler{modelService: ragasTestModels{}}).Ragas)
	result := httptest.NewRecorder()
	router.ServeHTTP(result, httptest.NewRequest("POST", "/", strings.NewReader(`{"model_id":"id","user_input":"test","judge":{"api_key":"attacker"}}`)))
	if result.Code != 200 || !strings.Contains(result.Body.String(), "0.75") {
		t.Fatalf("unexpected response: %d %s", result.Code, result.Body.String())
	}
	t.Setenv("RAGAS_WORKER_URL", "")
	result = httptest.NewRecorder()
	router.ServeHTTP(result, httptest.NewRequest("POST", "/", strings.NewReader(`{}`)))
	if result.Code != 503 {
		t.Fatalf("expected unconfigured worker error, got %d", result.Code)
	}
}
