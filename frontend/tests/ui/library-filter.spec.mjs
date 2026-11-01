import { test, expect } from '@playwright/test'
import { mockApp } from './fixtures.mjs'

// Small mocked entries: the filter is a client-side view over what the store
// already loaded, so nothing here touches the network or the database.
const favorites = [
  {
    url: 'https://example.test/soma',
    title: 'Shokugeki no Sōma',
    imageUrl: 'https://example.test/soma.jpg',
    source: 'french-manga',
    autoDownload: false,
  },
  {
    url: 'https://example.test/pokemon',
    title: 'Pokémon',
    imageUrl: 'https://example.test/pokemon.jpg',
    source: 'voir-anime',
    autoDownload: true,
  },
]

async function openLibrary(page, list) {
  await mockApp(page)
  await page.route('**/api/favorites', (route) => route.fulfill({ json: list }))
  await page.goto('/app/library')
}

const search = (page) =>
  page.getByRole('searchbox', { name: 'Filtrer les titres de la bibliothèque' })

for (const width of [390, 1440]) {
  test(`a plain keyboard search finds accented titles at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 850 })
    await openLibrary(page, favorites)
    await expect(page.getByText('Shokugeki no Sōma')).toBeVisible()

    await search(page).fill('soma')
    await expect(page.getByText('Shokugeki no Sōma')).toBeVisible()
    await expect(page.getByText('Pokémon')).toHaveCount(0)

    // Case and accents fold both ways, so the accented side is reachable too.
    await search(page).fill('POKÉMON')
    await expect(page.getByText('Pokémon')).toBeVisible()
    await expect(page.getByText('Shokugeki no Sōma')).toHaveCount(0)

    // Clearing restores the same entries: the store was never filtered.
    await page.getByRole('button', { name: 'Effacer le filtre' }).first().click()
    await expect(page.getByText('Shokugeki no Sōma')).toBeVisible()
    await expect(page.getByText('Pokémon')).toBeVisible()
  })
}

test('a filter with no match is not confused with an empty library', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 850 })
  await openLibrary(page, favorites)

  await search(page).fill('zzzz')
  await expect(page.getByText('Aucune série ne correspond à votre filtre')).toBeVisible()
  await expect(page.getByText('Aucun animé dans votre bibliothèque')).toHaveCount(0)

  // The no-match state carries its own clear action, next to the field's.
  await expect(page.getByRole('button', { name: 'Effacer le filtre' })).toHaveCount(2)
  await page.getByRole('button', { name: 'Effacer le filtre' }).last().click()
  await expect(page.getByText('Pokémon')).toBeVisible()
})

test('an empty library keeps its own message and shows no filter result state', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 850 })
  await openLibrary(page, [])

  await expect(page.getByText('Aucun animé dans votre bibliothèque')).toBeVisible()
  await expect(page.getByText('Aucune série ne correspond à votre filtre')).toHaveCount(0)
})

test('distinct sources stay separate entries when their titles match', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 850 })
  await openLibrary(page, [
    { ...favorites[0], url: 'https://example.test/soma-vf', source: 'french-manga' },
    { ...favorites[0], url: 'https://example.test/soma-vostfr', source: 'voir-anime' },
  ])

  await search(page).fill('soma')
  await expect(page.locator('.anime-card')).toHaveCount(2)
})
