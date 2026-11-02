import { computed, ref } from 'vue'
import { readPreference, writePreference } from '@/utils/locale'
import type { Palette, ThemeMode } from '@/types/startup'

const saved = readPreference('theme')
export const themeMode = ref<ThemeMode>(saved === 'light' || saved === 'system' ? saved : 'dark')
const savedPalette = readPreference('palette')
export const palette = ref<Palette>(
  ['teal', 'lavender', 'ember', 'amoled'].includes(savedPalette || '')
    ? (savedPalette as Palette)
    : 'teal',
)
const systemDark = ref(true)
export const effectiveTheme = computed(() =>
  themeMode.value === 'system' ? (systemDark.value ? 'dark' : 'light') : themeMode.value,
)
function paint() {
  document.documentElement.dataset.theme = effectiveTheme.value
  document.documentElement.dataset.palette = palette.value
  document.documentElement.style.colorScheme = effectiveTheme.value
}
export function setAppearance(mode: ThemeMode, variant: Palette) {
  themeMode.value = mode
  palette.value = variant
  writePreference('theme', mode)
  writePreference('palette', variant)
  paint()
}
export function initializeAppearance() {
  const media = window.matchMedia('(prefers-color-scheme: dark)')
  systemDark.value = media.matches
  media.addEventListener('change', (event) => {
    systemDark.value = event.matches
    paint()
  })
  paint()
}
