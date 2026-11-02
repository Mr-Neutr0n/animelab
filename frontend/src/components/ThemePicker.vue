<template>
  <div class="theme-picker">
    <div class="theme-modes" role="group" :aria-label="tx('Mode d’affichage')">
      <button
        v-for="mode in modes"
        :key="mode.id"
        type="button"
        :aria-pressed="themeMode === mode.id"
        @click="choose(mode.id, palette)"
      >
        <Check v-if="themeMode === mode.id" aria-hidden="true" />{{ tx(mode.label) }}
      </button>
    </div>
    <div class="theme-variants" role="group" :aria-label="tx('Palette de couleurs')">
      <button
        v-for="variant in variants"
        :key="variant.id"
        type="button"
        class="theme-variant"
        :aria-pressed="palette === variant.id"
        @click="choose(themeMode, variant.id)"
      >
        <span
          class="theme-mini"
          :style="{ '--mini-bg': variant.background, '--mini-accent': variant.accent }"
        >
          <span class="mini-heading"></span><span class="mini-card"><i></i><i></i></span>
          <span class="mini-nav"><i></i><i></i><i></i></span>
          <Check v-if="palette === variant.id" class="mini-check" aria-hidden="true" />
        </span>
        <span>{{ tx(variant.label) }}</span>
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { themeMode, palette, setAppearance } from '@/stores/appearance'
import type { Palette, ThemeMode } from '@/types/startup'
import { tx } from '@/utils/locale'
const emit = defineEmits<{ change: [] }>()
const modes: { id: ThemeMode; label: string }[] = [
  { id: 'system', label: 'Système' },
  { id: 'light', label: 'Clair' },
  { id: 'dark', label: 'Sombre' },
]
const variants: { id: Palette; label: string; background: string; accent: string }[] = [
  { id: 'teal', label: 'Turquoise', background: '#0b1517', accent: '#80d3dc' },
  { id: 'lavender', label: 'Violet', background: '#15121d', accent: '#c6b5ff' },
  { id: 'ember', label: 'Ambre', background: '#1c1510', accent: '#ffbc87' },
  { id: 'amoled', label: 'AMOLED', background: '#000000', accent: '#a8dfcf' },
]
function choose(mode: ThemeMode, variant: Palette) {
  setAppearance(mode, variant)
  emit('change')
}
</script>
<style scoped>
.theme-picker {
  width: 100%;
}
.theme-modes {
  display: flex;
  border: 1px solid var(--line-strong);
  border-radius: 99px;
  overflow: hidden;
}
.theme-modes button {
  flex: 1;
  min-width: 0;
  min-height: 44px;
  background: transparent;
  color: var(--text);
  border: 0;
  border-right: 1px solid var(--line-strong);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}
.theme-modes button:last-child {
  border: 0;
}
.theme-modes button[aria-pressed='true'] {
  background: var(--accent-container);
  color: var(--on-accent-container);
}
.theme-modes svg {
  width: 16px;
  height: 16px;
}
.theme-variants {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 28px;
}
.theme-variant {
  background: transparent;
  color: var(--muted);
  border: 0;
  padding: 0;
  font-size: 12px;
  min-width: 0;
}
.theme-variant[aria-pressed='true'] {
  color: var(--text);
}
.theme-mini {
  display: flex;
  position: relative;
  flex-direction: column;
  padding: 10px 7px 0;
  height: 150px;
  background: var(--mini-bg);
  border: 3px solid transparent;
  border-radius: 18px;
  margin-bottom: 10px;
  overflow: hidden;
}
.theme-variant[aria-pressed='true'] .theme-mini {
  border-color: var(--accent);
}
.mini-heading {
  width: 70%;
  height: 10px;
  background: #dce6e7;
  border-radius: 9px;
  margin-bottom: 12px;
}
.mini-card {
  display: flex;
  align-items: start;
  gap: 3px;
  background: #ffffff25;
  width: 75%;
  height: 54px;
  padding: 5px;
  border-radius: 8px;
}
.mini-card i {
  background: var(--mini-accent);
  width: 12px;
  height: 9px;
  border-radius: 4px;
}
.mini-card i:last-child {
  opacity: 0.45;
}
.mini-nav {
  display: flex;
  gap: 7px;
  align-items: center;
  margin: auto -7px 0;
  padding: 10px 7px;
  background: #ffffff13;
}
.mini-nav i {
  width: 10px;
  height: 10px;
  background: #899596;
  border-radius: 100%;
}
.mini-nav i:first-child {
  background: var(--mini-accent);
}
.mini-check {
  position: absolute;
  top: 7px;
  right: 4px;
  width: 18px;
  height: 18px;
  padding: 2px;
  background: var(--accent);
  color: var(--bg);
  border-radius: 99px;
}
@media (max-width: 380px) {
  .theme-variants {
    gap: 6px;
  }
  .theme-variant {
    font-size: 10px;
  }
  .theme-mini {
    height: 128px;
    padding-inline: 5px;
  }
}
</style>
