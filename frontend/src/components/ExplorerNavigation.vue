<template>
  <nav class="explorer-navigation" :aria-label="tx('Explorer')">
    <RouterLink
      to="/sources"
      :class="{ selected: active === 'sources' }"
      :aria-current="active === 'sources' ? 'page' : undefined"
    >
      <Compass :size="19" /> {{ tx('Sources') }}
    </RouterLink>
    <RouterLink
      to="/extensions"
      :class="{ selected: active === 'extensions' }"
      :aria-current="active === 'extensions' ? 'page' : undefined"
    >
      <Puzzle :size="19" /> {{ tx('Extensions') }}
    </RouterLink>
  </nav>
</template>
<script setup lang="ts">
import { Compass, Puzzle } from 'lucide-vue-next'
import { tx } from '@/utils/locale'
defineProps<{ active: 'sources' | 'extensions' }>()
</script>
<style scoped>
.explorer-navigation {
  display: flex;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.5rem;
  gap: 1rem;
}
a {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1rem;
  color: var(--muted);
  text-decoration: none;
  border-bottom: 3px solid transparent;
}
a.selected {
  color: var(--accent);
  border-bottom-color: var(--accent);
}
</style>
