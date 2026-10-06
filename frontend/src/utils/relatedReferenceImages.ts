export type RelatedImage = { url: string; caption: string; chunk_id: string }
export type ImageReference = { id?: string; related_images?: RelatedImage[] }

function figureNumbers(text: string): Set<string> {
  const numbers = new Set<string>()
  const sequence = /(?:fig(?:ure)?s?\.?|图)\s*\d+(?:[.-]\d+)+(?:\s*(?:,|，|、|and|&|和|与)\s*\d+(?:[.-]\d+)+)*/gi
  for (const match of text.matchAll(sequence)) {
    for (const number of match[0].match(/\d+(?:[.-]\d+)+/g) || []) {
      numbers.add(number.replace(/-/g, '.'))
    }
  }
  return numbers
}

export function selectRelatedReferenceImages(answer: string, references: ImageReference[]): RelatedImage[] {
  const cited = new Set(
    Array.from(answer.matchAll(/<kb\b[^>]*\bchunk_id="([^"]+)"[^>]*\/>/g), (match) => match[1]),
  )
  const mentioned = figureNumbers(answer)
  if (!cited.size || !mentioned.size) return []

  const images: RelatedImage[] = []
  const seen = new Set<string>()
  for (const reference of references) {
    if (!reference.id || !cited.has(reference.id)) continue
    for (const image of reference.related_images || []) {
      if (!image.url || seen.has(image.url)) continue
      if (![...figureNumbers(image.caption)].some((number) => mentioned.has(number))) continue
      seen.add(image.url)
      images.push(image)
      if (images.length >= 4) return images
    }
  }
  return images
}
