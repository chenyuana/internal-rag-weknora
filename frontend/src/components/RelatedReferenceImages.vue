<template>
  <div v-if="images.length" class="related-reference-images">
    <div class="related-reference-images__title">相关原图</div>
    <a
      v-for="image in images"
      :key="image.url"
      :href="image.url"
      target="_blank"
      rel="noopener noreferrer"
      class="related-reference-images__item"
    >
      <img :src="image.url" :alt="image.caption" loading="lazy" />
      <span>{{ image.caption }}</span>
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { isValidImageURL } from '@/utils/security'
import { selectRelatedReferenceImages, type ImageReference } from '@/utils/relatedReferenceImages'

const props = defineProps<{ answer: string; references?: ImageReference[] | null }>()

const images = computed(() =>
  selectRelatedReferenceImages(props.answer, props.references || []).filter((image) => isValidImageURL(image.url)),
)
</script>

<style scoped>
.related-reference-images { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0; }
.related-reference-images__title { flex-basis: 100%; font-weight: 600; }
.related-reference-images__item { display: flex; flex-direction: column; width: 180px; gap: 4px; font-size: 12px; }
.related-reference-images__item img { width: 180px; height: 130px; object-fit: contain; border-radius: 4px; background: var(--td-bg-color-secondarycontainer); }
</style>
