package service

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestReferencedFigureNumbers(t *testing.T) {
	require.Equal(t, []string{"3.4", "3.5"}, referencedFigureNumbers(
		"Figure 3.4 and 3.5 show typical recordings; section 3.6 is unrelated.",
	))
	require.Empty(t, referencedFigureNumbers("Only section 3.4 and table 3.5 are mentioned."))
}

func TestFigureCaptionImageIsDiscoverable(t *testing.T) {
	content := "FIGURE 3.4\n\n![TYPICAL HORIZONTAL DISTRIBUTION\nFIGURE 3.4](http://localhost:8080/api/v1/ingestion/jobs/job/assets/image)"
	images := markdownImage.FindAllStringSubmatch(content, -1)
	require.Len(t, images, 1)
	require.Equal(t, "3.4", figureNumber.FindStringSubmatch(images[0][1])[1])
}

func TestReferencedSingleFigureNumber(t *testing.T) {
 require.Equal(t, []string{"1", "2"}, referencedFigureNumbers("Compass (See Figure 1); Attitude (See Figure 2)."))
 require.Empty(t, referencedFigureNumbers("Section 1 and table 2."))
 require.Equal(t, "1", figureNumber.FindStringSubmatch("Figure 1 Compass Area")[1])
}
