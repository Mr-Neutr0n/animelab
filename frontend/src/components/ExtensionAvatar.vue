<template>
  <span class="extension-avatar" aria-hidden="true">
    <img
      v-if="src && !failed"
      :src="src"
      alt=""
      loading="lazy"
      referrerpolicy="no-referrer"
      @error="failed = true"
    />
    <span v-else>{{
      name
        .replace(/^Aniyomi:\s*/i, '')
        .slice(0, 2)
        .toUpperCase()
    }}</span>
  </span>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ name: string; src?: string | null }>()
const failed = ref(false)
watch(
  () => props.src,
  () => {
    failed.value = false
  },
)
</script>
<style scoped>
.extension-avatar {
  flex: 0 0 48px;
  width: 48px;
  height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--panel-subtle, var(--panel));
  color: var(--accent);
  font-weight: 700;
  overflow: hidden;
}
img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
