package eu.kanade.tachiyomi.network

import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.Interceptor
import okhttp3.Response

/** Static scripts belong to the source page even when an APK omits its headers. */
class SourceScriptRefererInterceptor(private val sourceUrl: () -> String) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val source = sourceUrl().toHttpUrlOrNull()
        val target = request.url
        val sameOrigin = source != null && source.scheme == target.scheme &&
            source.host == target.host && source.port == target.port
        if (!sameOrigin || request.header("Referer") != null || request.method !in setOf("GET", "HEAD") ||
            !target.encodedPath.endsWith(".js", ignoreCase = true)) {
            return chain.proceed(request)
        }
        // Only a public origin: never copy credentials, query or fragment from
        // extension preferences into an HTTP header.
        val origin = requireNotNull(source).newBuilder().username("").password("")
            .encodedPath("/").query(null).fragment(null).build().toString()
        return chain.proceed(request.newBuilder().header("Referer", origin).build())
    }
}
