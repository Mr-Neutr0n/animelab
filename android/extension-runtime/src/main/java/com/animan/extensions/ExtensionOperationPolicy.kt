package com.animan.extensions

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.TimeoutCancellationException

/** A source callback may expand seasons or resolve several hosters serially. */
object ExtensionOperationPolicy {
    fun workerTimeoutMillis(operation: String): Long = when (operation) {
        "search", "detail" -> 90_000
        "hosters", "videos" -> 120_000
        "resolve_video" -> 60_000
        else -> 45_000
    }

    fun parentTimeoutMillis(operation: String): Long = workerTimeoutMillis(operation) + 15_000

    fun failureCode(error: Throwable): String = when (error) {
        is TimeoutCancellationException -> "extension_runtime_timeout"
        is CancellationException -> "cancelled"
        is LinkageError -> "extension_abi_incompatible"
        is SecurityException -> "extension_untrusted"
        is UnsupportedOperationException, is NotImplementedError -> "source_operation_unsupported"
        else -> "extension_runtime_error"
    }
}
