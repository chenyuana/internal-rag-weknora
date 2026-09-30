import assert from 'node:assert/strict'
import test from 'node:test'
import { selectRelatedReferenceImages } from './relatedReferenceImages.ts'

test('shows only figures named in the answer and tied to a cited chunk', () => {
  const answer = '图 3.4、3.5 是测量曲线。<kb doc="AC_20-74.pdf" chunk_id="text-1" kb_id="kb" />'
  const refs = [
    {
      id: 'text-1',
      related_images: [
        { url: 'https://assets/3.1', caption: 'Figure 3.1', chunk_id: 'a' },
        { url: 'https://assets/3.4', caption: 'Figure 3.4', chunk_id: 'b' },
        { url: 'https://assets/3.5', caption: 'Figure 3.5', chunk_id: 'c' },
      ],
    },
    { id: 'uncited', related_images: [{ url: 'https://assets/3.4-other', caption: 'Figure 3.4', chunk_id: 'd' }] },
  ]
  assert.deepEqual(selectRelatedReferenceImages(answer, refs).map((image) => image.url), [
    'https://assets/3.4', 'https://assets/3.5',
  ])
})

test('does not show pictures for a text-only answer without figure numbers', () => {
  const answer = '测量在实验室进行。<kb chunk_id="text-1" />'
  const refs = [{ id: 'text-1', related_images: [{ url: 'https://assets/3.1', caption: 'Figure 3.1', chunk_id: 'a' }] }]
  assert.deepEqual(selectRelatedReferenceImages(answer, refs), [])
})
