package openaicompletions

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/Tencent/WeKnora/internal/models/api"
	"github.com/stretchr/testify/require"
)

func TestRequiredImagesAreNeverSilentlyRetriedAsText(t *testing.T) {
	for _, stream := range []bool{false, true} {
		t.Run(map[bool]string{false: "completion", true: "stream"}[stream], func(t *testing.T) {
			calls := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
				calls++
				w.WriteHeader(http.StatusBadRequest)
				_, _ = w.Write([]byte(`{"error":{"message":"image input unsupported"}}`))
			}))
			defer server.Close()
			c := newClient(t, func(cfg *Config) { cfg.Endpoint.BaseURL = server.URL; cfg.Endpoint.Client = server.Client() })
			messages := []api.Message{{Role: "user", MultiContent: []api.MessageContentPart{{Type: "image_url", ImageURL: &api.ImageURL{URL: "data:image/png;base64,YQ=="}}}}}
			var err error
			if stream {
				_, err = c.ChatStream(context.Background(), messages, &api.Options{RequireImageInput: true})
			} else {
				_, err = c.Chat(context.Background(), messages, &api.Options{RequireImageInput: true})
			}
			require.ErrorContains(t, err, "image input unsupported")
			require.Equal(t, 1, calls)
		})
	}
}

func TestRequiredImagesRejectTextOnlyProtocol(t *testing.T) {
	c := newClient(t, func(cfg *Config) { cfg.Settings.SupportsMultiContent = false })
	_, err := c.Chat(context.Background(), nil, &api.Options{RequireImageInput: true})
	require.ErrorContains(t, err, "required image input")
}
