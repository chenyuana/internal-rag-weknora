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

test('shows every page of a cited table and keeps other tables excluded', () => {
  const answer = 'Table III 和 Table IV。<kb chunk_id="source" />'
  const related_images = ['I', 'III', 'IV — page 8', 'IV — page 9', 'IV — page 10', 'IV — page 11'].map((name) => ({ url: `https://assets/${name}`, caption: `Table ${name}`, chunk_id: name }))
  assert.equal(selectRelatedReferenceImages(answer, [{ id: 'source', related_images }]).length, 5)
  assert.deepEqual(selectRelatedReferenceImages(answer, [{ id: 'uncited', related_images }]), [])
})

test('matches Chinese table numbers to Roman source captions', () => {
  const refs = [{ id: 'source', related_images: [{ url: 'https://assets/iii', caption: 'Table III — page 8', chunk_id: 'iii' }] }]
  assert.equal(selectRelatedReferenceImages('表3的内容。<kb chunk_id="source" />', refs).length, 1)
})

test('matches appendix and single-level figure numbers', () => {
  for (const number of ['A-1', '2']) {
    const refs = [{id: 'source', related_images: [{url: 'https://assets/figure', caption: `Figure ${number}`, chunk_id: 'figure'}]}]
    assert.equal(selectRelatedReferenceImages(`图 ${number}。<kb chunk_id="source" />`, refs).length, 1)
  }
})
