export type RelatedImage = { url: string; caption: string; chunk_id: string }
export type ImageReference = { id?: string; related_images?: RelatedImage[] }

function imageIdentifiers(text: string): Set<string> {
  const ids = new Set([...figureNumbers(text)].map((number) => `figure:${number}`))
  for (const match of text.matchAll(/(?:\bTable\s+|表\s*)([IVXLCDM]+|[0-9]+)\b/gi)) {
    const label = match[1].toUpperCase()
    const values: Record<string, number> = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 }
    let number = Number(label)
    if (Number.isNaN(number)) {
      number = 0
      for (let i = 0; i < label.length; i++) {
        const value = values[label[i]]
        number += value < (values[label[i + 1]] || 0) ? -value : value
      }
    }
    ids.add(`table:${number}`)
  }
  return ids
}

function figureNumbers(text: string): Set<string> {
  const numbers = new Set<string>()
  const sequence = /(?:fig(?:ure)?s?\.?|图)\s*(?:[A-Z][.-])?\d+(?:[.-]\d+)*(?:\s*(?:,|，|、|and|&|和|与)\s*(?:[A-Z][.-])?\d+(?:[.-]\d+)*)*/gi
  for (const match of text.matchAll(sequence)) {
    for (const number of match[0].match(/(?:[A-Z][.-])?\d+(?:[.-]\d+)*/g) || []) {
      numbers.add(number.toUpperCase().replace(/-/g, '.'))
    }
  }
  return numbers
}

export function selectRelatedReferenceImages(answer: string, references: ImageReference[]): RelatedImage[] {
  const cited = new Set(
    Array.from(answer.matchAll(/<kb\b[^>]*\bchunk_id="([^"]+)"[^>]*\/>/g), (match) => match[1]),
  )
  const mentioned = imageIdentifiers(answer)
  if (!cited.size || !mentioned.size) return []
  const limit = [...mentioned].some((id) => id.startsWith('table:')) ? 12 : 4

  const images: RelatedImage[] = []
  const seen = new Set<string>()
  for (const reference of references) {
    if (!reference.id || !cited.has(reference.id)) continue
    for (const image of reference.related_images || []) {
      if (!image.url || seen.has(image.url)) continue
      if (![...imageIdentifiers(image.caption)].some((number) => mentioned.has(number))) continue
      seen.add(image.url)
      images.push(image)
      if (images.length >= limit) return images
    }
  }
  return images
}
