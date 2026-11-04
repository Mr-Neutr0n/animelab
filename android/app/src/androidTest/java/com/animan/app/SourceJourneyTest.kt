package com.animan.app

import android.content.Intent
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.net.HttpURLConnection
import java.net.Proxy
import java.net.URL
import java.net.URLEncoder
import java.util.concurrent.TimeUnit

/** Opt-in live checks; the main app, APKs and other hosts are never modified. */
@RunWith(AndroidJUnit4::class)
class SourceJourneyTest {
    private class TrialFailure(val code: String, val domain: String) : RuntimeException(code)
    private fun encoded(value: String) = URLEncoder.encode(value, "UTF-8")
    private fun request(path: String, body: JSONObject? = null): JSONObject {
        val connection = URL(EngineHost.baseUrl + path).openConnection(Proxy.NO_PROXY) as HttpURLConnection
        try {
            connection.connectTimeout = 5000; connection.readTimeout = 180000
            connection.setRequestProperty("X-Animan-Session", EngineHost.token)
            if (body != null) {
                connection.requestMethod = "POST"; connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { it.write(body.toString().toByteArray()) }
            }
            val code = connection.responseCode
            val data = (if (code < 400) connection.inputStream else connection.errorStream).bufferedReader().use { it.readText() }
            if (code >= 400) {
                val failure = JSONObject(data)
                val failureCode = failure.optString("code", "http_$code").takeIf { it.matches(Regex("[a-z0-9_]{1,80}")) } ?: "http_$code"
                val domain = failure.optString("domain").takeIf { it.matches(Regex("[A-Za-z0-9.-]{1,253}")) } ?: ""
                throw TrialFailure(failureCode, domain)
            }
            return if (data.trimStart().startsWith("[")) JSONObject().put("tasks", JSONArray(data)) else JSONObject(data)
        } finally { connection.disconnect() }
    }

    @Test(timeout = 1500000) fun installed_anime_sources_to_download() {
        val arguments = InstrumentationRegistry.getArguments()
        assumeTrue("Explicit opt-in live network test", arguments.getString("live_sources") == "true")
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals("Use only the separate validation app", "com.animan.app.a11test", context.packageName)
        EngineHost.start(context, true)
        val proof = JSONArray()
        ActivityScenario.launch<MainActivity>(Intent(context, MainActivity::class.java)).use { scenario ->
            scenario.onActivity { it.window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON) }
            val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(100)
            while (!EngineHost.ready && EngineHost.error == null && System.nanoTime() < deadline) Thread.sleep(250)
            assertNull(EngineHost.error); assertTrue(EngineHost.ready)
            StorageAccess.useDownloads()
            for ((suffix, query) in listOf("animesama" to "Bleach", "voiranime" to "One Piece")) {
                val pkg = "eu.kanade.tachiyomi.animeextension.fr.$suffix"
                val row = JSONObject().put("package", pkg)
                var phase = "inventory"
                try {
                    val packages = request("/api/extensions/android").getJSONArray("packages")
                    val descriptor = (0 until packages.length()).map { packages.getJSONObject(it) }.single { it.getString("pkg") == pkg }
                    row.put("version", descriptor.getString("version"))
                    phase = "trust"
                    request("/api/extensions/android/$pkg/trust", JSONObject().put("approved", true).put("signer", descriptor.getString("signer")).put("versionCode", descriptor.getString("versionCode")))
                    val inventory = request("/api/extensions/android").getJSONArray("packages")
                    val loaded = (0 until inventory.length()).map { inventory.getJSONObject(it) }.single { it.getString("pkg") == pkg }
                    val source = "aniyomi:" + loaded.getJSONArray("sources").getJSONObject(0).getString("id")
                    row.put("source", source)
                    phase = "search"
                    val search = request("/api/search?q=${encoded(query)}&source=${encoded(source)}&include_challenges=true")
                    val results = search.getJSONArray("results")
                    row.put("searchResults", results.length())
                    check(results.length() > 0) { "empty_search" }
                    // Prefer season one or VF when those variants are returned.
                    val titles = (0 until results.length()).map { results.getJSONObject(it) }
                    val selected = titles.firstOrNull { it.getString("title").equals("One Piece (VF)", true) } ?: titles.firstOrNull { if (suffix == "animesama") it.getString("title").endsWith("Saison 1") else it.getString("title").contains("(VF)") } ?: titles.first()
                    phase = "detail"
                    val url = selected.getString("url")
                    val detail = request("/api/anime/detail?url=${encoded(url)}&source=${encoded(source)}")
                    assertEquals(source, detail.getString("source"))
                    val anime = detail.getJSONObject("anime")
                    row.put("title", anime.getString("title"))
                    val episodes = anime.getJSONArray("episodes")
                    row.put("episodes", episodes.length())
                    check(episodes.length() > 0) { "empty_episodes" }
                    val episode = (0 until episodes.length()).map { episodes.getJSONObject(it) }.filter { it.getInt("number") >= 0 }.minBy { it.getInt("number") }
                    val episodeUrl = episode.getString("playerUrl")
                    row.put("episode", episode.getInt("number")).put("versionLabel", episode.optString("version"))
                    phase = "resolve"
                    val resolved = request("/api/media/stream/resolve?animeName=${encoded(anime.getString("title"))}&episodeNumber=${episode.getInt("number")}&episodeUrl=${encoded(episodeUrl)}&animeUrl=${encoded(url)}&source=${encoded(source)}&quality=480p")
                    row.put("streamResolved", resolved.optBoolean("success"))
                    check(resolved.optBoolean("success")) { "stream_unresolved" }
                    if (arguments.getString("download_episode") == "true") {
                        phase = "batch_download"
                        val name = "AnimeLab validation $suffix"
                        val batch = request("/api/download/batch", JSONObject().put("animeName", name).put("source", source).put("preferredQuality", "480p").put("episodes", JSONArray().put(JSONObject()
                            .put("number", episode.getInt("number")).put("version", episode.optString("version"))
                            .put("animeUrl", url).put("url", episodeUrl).put("fileName", "$name.mp4")
                            .put("outputProfile", JSONObject().put("version", 1).put("mode", "ORIGINAL").put("keepOriginals", false)))))
                        assertEquals(1, batch.getInt("count"))
                        val end = System.nanoTime() + TimeUnit.SECONDS.toNanos(480)
                        var done = false
                        while (System.nanoTime() < end) {
                            val tasks = request("/api/download/status").getJSONArray("tasks")
                            val task = (0 until tasks.length()).map { tasks.getJSONObject(it) }.firstOrNull { it.getString("animeName") == name }
                            if (task != null) {
                                row.put("downloadStatus", task.getString("status")).put("downloadedBytes", task.optLong("downloadedBytes"))
                                    .put("verificationStatus", task.optString("verificationStatus")).put("exportStatus", task.optString("exportStatus"))
                                if (task.getString("status") in setOf("COMPLETED", "FAILED", "VERIFICATION_REQUIRED", "CANCELLED")) { done = true; break }
                            }
                            Thread.sleep(2000)
                        }
                        check(done && row.optString("downloadStatus") == "COMPLETED") { "download_incomplete" }
                    }
                    row.put("passed", true)
                } catch (failure: Exception) {
                    row.put("passed", false).put("phase", phase).put("failureType", failure.javaClass.simpleName)
                    if (failure is TrialFailure) row.put("failureCode", failure.code).put("verificationDomain", failure.domain)
                    // Keep live endpoints, cookies, resolved video tokens and response bodies private.
                } finally {
                    proof.put(row)
                    android.util.Log.i("ANIMELAB_JOURNEY", row.toString())
                }
            }
        }
        java.io.File(requireNotNull(context.getExternalFilesDir(null)), "source-journey.json").writeText(proof.toString(2))
        assertTrue("See ANIMELAB_JOURNEY for the exact phase", (0 until proof.length()).all { proof.getJSONObject(it).optBoolean("passed") })
    }
}
