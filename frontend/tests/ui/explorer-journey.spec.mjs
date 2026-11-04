import { test, expect } from '@playwright/test'
import { mockApp } from './fixtures.mjs'

const sid = 'aniyomi:1152921504606846977'
const anime = {
  title: 'One Piece (VF)',
  url: 'https://example.test/series',
  source: sid,
  imageUrl: '',
  studio: 'Toei Animation',
  genres: ['Action'],
  nativeMetadata: { status: 1 },
  episodes: [3, 2, 1].map((number) => ({
    number,
    title: `Épisode ${number} VF`,
    version: 'VF',
    playerUrl: `https://example.test/ep/${number}`,
  })),
}

test('compact APK list retains source preferences, enablement and exact 64-bit identities', async ({
  page,
}) => {
  await mockApp(page)
  await page.setViewportSize({ width: 360, height: 780 })
  const identity = {
    pkg: 'fixture.one',
    name: 'Anime-Sama',
    version: '14.33',
    versionCode: '33',
    trusted: true,
    compatible: true,
    state: 'loaded',
    signer: 'a'.repeat(64),
    sources: [
      { id: sid.slice(8), name: 'Anime-Sama (FR)', lang: 'fr', enabled: true, configurable: true },
    ],
  }
  await page.route('**/api/extensions/android', (route) =>
    route.fulfill({ json: { available: true, packages: [identity], operations: [] } }),
  )
  await page.route('**/api/extensions/repositories', (route) =>
    route.fulfill({ json: { repositories: [] } }),
  )
  const preferences = []
  await page.route('**/api/extensions/android/sources/*/*', (route) => {
    preferences.push({
      url: decodeURIComponent(route.request().url()),
      body: route.request().postDataJSON(),
    })
    return route.fulfill({
      json: {
        result: [
          {
            key: 'quality',
            type: 'select',
            title: 'Preferred quality',
            enabled: true,
            value: '1080p',
            entries: ['480p', '1080p'],
            entryValues: ['480p', '1080p'],
          },
        ],
      },
    })
  })
  await page.goto('/app/extensions')
  await page.getByLabel('Rechercher une extension').fill('Anime-Sama')
  await expect(page.locator('.apk-item')).toHaveCount(1)
  await page.locator('.apk-details > summary').click()
  await expect(page.getByLabel('Activer cette source')).toBeChecked()
  await page.getByRole('button', { name: 'Préférences de la source', exact: true }).click()
  await page.getByLabel('Preferred quality').selectOption('480p')
  await page.getByRole('button', { name: 'Enregistrer', exact: true }).click()
  await expect
    .poll(() =>
      preferences.some(
        (item) =>
          item.url.includes(sid) &&
          item.url.endsWith('/set_preferences') &&
          item.body.quality === '480p',
      ),
    )
    .toBe(true)
  await expect(page.getByRole('link', { name: 'Ouvrir la source', exact: true })).toHaveAttribute(
    'href',
    /aniyomi.*1152921504606846977/,
  )
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(
    true,
  )
})

test('descending native episodes start and queue from episode one and preserve the APK source', async ({
  page,
}) => {
  await mockApp(page)
  await page.route('**/api/anime/detail?**', (route) =>
    route.fulfill({
      json: {
        success: true,
        anime,
        source: sid,
        sourceName: 'Voiranime (FR)',
        downloadedEpisodes: [],
        watchedEpisodes: [],
      },
    }),
  )
  const queued = []
  await page.route('**/api/download/batch', (route) => {
    queued.push(route.request().postDataJSON())
    return route.fulfill({ json: { success: true, count: 1 } })
  })
  await page.goto(
    `/app/anime?url=${encodeURIComponent(anime.url)}&source=${encodeURIComponent(sid)}`,
  )
  await expect(page.getByText('Toei Animation', { exact: true })).toBeVisible()
  await expect(page.getByText('En cours • Voiranime (FR)')).toBeVisible()
  await page.getByLabel('Ordre des épisodes').selectOption('asc')
  await expect(page.locator('.tachiyomi-ep-title').first()).toContainText('1')
  await page.getByTitle('Téléchargement massif').click()
  await page.getByRole('button', { name: 'Épisode suivant' }).click()
  await page.getByRole('button', { name: 'Ajouter à la file', exact: true }).click()
  await expect.poll(() => queued.length).toBe(1)
  expect(queued[0].source).toBe(sid)
  expect(queued[0].episodes.map((ep) => [ep.number, ep.version, ep.url])).toEqual([
    [1, 'VF', 'https://example.test/ep/1'],
  ])
})

test('an empty episode list offers retry and does not show a nonfunctional play button', async ({
  page,
}) => {
  await mockApp(page)
  let calls = 0
  await page.route('**/api/anime/detail?**', (route) => {
    calls++
    return route.fulfill({
      json: {
        success: true,
        anime: { ...anime, episodes: [] },
        source: sid,
        downloadedEpisodes: [],
        watchedEpisodes: [],
      },
    })
  })
  await page.goto(
    `/app/anime?url=${encodeURIComponent(anime.url)}&source=${encodeURIComponent(sid)}`,
  )
  await expect(
    page.getByText('La source n’a renvoyé aucun épisode pour cette série.'),
  ).toBeVisible()
  await expect(page.locator('.tachiyomi-fab')).toHaveCount(0)
  await page.getByRole('button', { name: 'Réessayer', exact: true }).click()
  await expect.poll(() => calls).toBe(2)
})

test('a player challenge exposes verification and retries the selected APK episode', async ({
  page,
}) => {
  await mockApp(page)
  await page.setViewportSize({ width: 360, height: 780 })
  await page.route('**/api/anime/detail?**', (route) =>
    route.fulfill({
      json: { success: true, anime, source: sid, downloadedEpisodes: [], watchedEpisodes: [] },
    }),
  )
  let calls = 0
  await page.route('**/api/media/stream/resolve?**', (route) => {
    calls++
    return calls === 1
      ? route.fulfill({
          status: 409,
          json: {
            code: 'verification_required',
            domain: 'video.example',
            url: 'https://video.example/embed',
            error: 'Verification needed',
          },
        })
      : route.fulfill({
          json: { streamUrl: '/api/media/extension-resource/fixture', subtitles: [] },
        })
  })
  await page.route('**/api/network/recheck', (route) =>
    route.fulfill({ json: { success: true, domain: 'video.example', resumed: 0 } }),
  )
  await page.goto(
    `/app/anime?url=${encodeURIComponent(anime.url)}&source=${encodeURIComponent(sid)}`,
  )
  await page.getByRole('button', { name: 'Lire l’épisode 1 VF', exact: true }).click()
  const verification = page.getByRole('region', { name: 'Accès au site bloqué' })
  await expect(verification).toBeVisible()
  await expect(verification.getByRole('link')).toHaveAttribute(
    'href',
    'https://video.example/embed',
  )
  await verification.getByRole('button', { name: 'Je suis revenu, réessayer' }).click()
  await expect.poll(() => calls).toBe(2)
  await expect(verification).toHaveCount(0)
})
