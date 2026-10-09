package chatpipeline

import (
	"bytes"
	"context"
	"encoding/base64"
	"fmt"
	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/Tencent/WeKnora/internal/types"
	"github.com/Tencent/WeKnora/internal/types/interfaces"
	"github.com/Tencent/WeKnora/internal/utils"
)

const (
	maxRetrievedImageBytes      = 5 * 1024 * 1024
	maxRetrievedImageTotalBytes = 15 * 1024 * 1024
)

var ingestionAssetPathRE = regexp.MustCompile(`^/api/v1/ingestion/jobs/[a-f0-9]{32}/assets/[a-f0-9]{20,64}$`)

type retrievedImageResolver struct {
	tenants         interfaces.TenantRepository
	storage         interfaces.StorageBackendResolver
	resources       interfaces.ResourceCatalog
	publicClient    *http.Client
	ingestionClient *http.Client
	ingestionOrigin string
	ingestionBase   string
}

func newRetrievedImageResolver(tenants interfaces.TenantRepository,
	storage interfaces.StorageBackendResolver, resources interfaces.ResourceCatalog,
) *retrievedImageResolver {
	return &retrievedImageResolver{
		tenants: tenants, storage: storage, resources: resources,
		publicClient: utils.NewSSRFSafeHTTPClient(utils.SSRFSafeHTTPClientConfig{
			Timeout: 5 * time.Second, MaxRedirects: 2, SameOriginRedirectsOnly: true,
		}),
		ingestionClient: &http.Client{Timeout: 5 * time.Second,
			Transport:     &http.Transport{},
			CheckRedirect: func(_ *http.Request, _ []*http.Request) error { return http.ErrUseLastResponse }},
		ingestionOrigin: strings.TrimRight(os.Getenv("WEKNORA_INGESTION_IMAGE_ORIGIN"), "/"),
		ingestionBase:   strings.TrimRight(os.Getenv("WEKNORA_INGESTION_IMAGE_BASE_URL"), "/"),
	}
}

func (r *retrievedImageResolver) resolve(ctx context.Context, tenantID uint64, imageURL string) (string, int, error) {
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	var data []byte
	var err error
	if strings.HasPrefix(imageURL, "data:") {
		if len(imageURL) > (maxRetrievedImageBytes*4/3)+1024 {
			return "", 0, fmt.Errorf("image exceeds size limit")
		}
		prefix, encoded, ok := strings.Cut(imageURL, ",")
		if !ok || !strings.HasPrefix(prefix, "data:image/") || !strings.HasSuffix(prefix, ";base64") {
			return "", 0, fmt.Errorf("unsupported image data URI")
		}
		data, err = base64.StdEncoding.DecodeString(encoded)
	} else if strings.HasPrefix(imageURL, "resource://") || strings.HasPrefix(imageURL, "local://") || strings.HasPrefix(imageURL, "storage://") {
		data, err = r.readStored(ctx, tenantID, imageURL)
	} else {
		data, err = r.readHTTP(ctx, imageURL)
	}
	if err != nil {
		return "", 0, err
	}
	if len(data) == 0 || len(data) > maxRetrievedImageBytes {
		return "", 0, fmt.Errorf("empty or oversized image")
	}
	config, format, err := image.DecodeConfig(bytes.NewReader(data))
	if err != nil {
		return "", 0, fmt.Errorf("invalid raster image: %w", err)
	}
	if config.Width <= 0 || config.Height <= 0 || int64(config.Width)*int64(config.Height) > 40_000_000 {
		return "", 0, fmt.Errorf("image dimensions exceed limit")
	}
	mime := map[string]string{"jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif"}[format]
	if mime == "" {
		return "", 0, fmt.Errorf("unsupported image format")
	}
	return "data:" + mime + ";base64," + base64.StdEncoding.EncodeToString(data), len(data), nil
}

func (r *retrievedImageResolver) readHTTP(ctx context.Context, rawURL string) ([]byte, error) {
	u, err := url.Parse(rawURL)
	if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" || u.User != nil {
		return nil, fmt.Errorf("invalid image URL")
	}
	client := r.publicClient
	// Only this administrator-configured origin and exact asset endpoint may
	// bypass public-network SSRF checks. No arbitrary paths or redirects.
	if u.Scheme+"://"+u.Host == r.ingestionOrigin && r.ingestionBase != "" &&
		ingestionAssetPathRE.MatchString(u.Path) && u.RawQuery == "" && u.Fragment == "" && u.RawPath == "" {
		base, parseErr := url.Parse(r.ingestionBase)
		if parseErr != nil || (base.Scheme != "http" && base.Scheme != "https") || base.Host == "" ||
			base.User != nil || base.RawQuery != "" || base.Fragment != "" || (base.Path != "" && base.Path != "/") {
			return nil, fmt.Errorf("invalid ingestion image backend")
		}
		base.Path = u.Path
		u = base
		client = r.ingestionClient
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, err
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("image server returned HTTP %d", resp.StatusCode)
	}
	if resp.ContentLength > maxRetrievedImageBytes {
		return nil, fmt.Errorf("image exceeds size limit")
	}
	return readLimitedImage(resp.Body)
}

func readLimitedImage(reader io.Reader) ([]byte, error) {
	data, err := io.ReadAll(io.LimitReader(reader, maxRetrievedImageBytes+1))
	if err != nil {
		return nil, err
	}
	if len(data) > maxRetrievedImageBytes {
		return nil, fmt.Errorf("image exceeds size limit")
	}
	return data, nil
}

func (r *retrievedImageResolver) readStored(ctx context.Context, tenantID uint64, ref string) ([]byte, error) {
	if r.resources == nil || r.tenants == nil || r.storage == nil {
		return nil, fmt.Errorf("storage resolver unavailable")
	}
	path, resource, err := r.resources.ResolvePath(ctx, ref)
	if err != nil {
		return nil, err
	}
	owner := utils.ParseTenantIDFromStoragePath(path)
	if resource != nil {
		owner = resource.TenantID
	}
	// The retrieval context carries the effective KB tenant. Do not accept an
	// embedded storage link pointing into a different tenant's files.
	if tenantID == 0 || owner != tenantID {
		return nil, fmt.Errorf("image tenant does not match retrieval tenant")
	}
	tenant, err := r.tenants.GetTenantByID(ctx, owner)
	if err != nil {
		return nil, err
	}
	if tenant == nil {
		return nil, fmt.Errorf("image tenant not found")
	}
	backendID, inner, scoped := types.ParseStorageBackendPath(path)
	if resource != nil && resource.StorageBackendID != "" {
		backendID = resource.StorageBackendID
	}
	providerPath := path
	if scoped {
		providerPath = inner
	}
	provider := types.ParseProviderScheme(providerPath)
	if provider == "" {
		provider = "local"
	}
	fileSvc, _, err := r.storage.ResolveFileService(ctx, tenant, backendID, provider, os.Getenv("LOCAL_STORAGE_BASE_DIR"))
	if err != nil {
		return nil, err
	}
	reader, err := fileSvc.GetFile(ctx, path)
	if err != nil {
		return nil, err
	}
	defer reader.Close()
	return readLimitedImage(reader)
}
