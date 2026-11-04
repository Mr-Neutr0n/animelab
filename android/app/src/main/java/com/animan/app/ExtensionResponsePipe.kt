package com.animan.app

import android.os.ParcelFileDescriptor
import android.util.Log
import java.io.IOException
import java.util.concurrent.Executor
import java.util.concurrent.RejectedExecutionException

/** The extension worker may close its reader on cancellation, timeout or death. */
object ExtensionResponsePipe {
    fun open(executor: Executor, response: () -> ByteArray): ParcelFileDescriptor {
        val pipe = try {
            ParcelFileDescriptor.createPipe()
        } catch (error: IOException) {
            // Binder can marshal a RuntimeException to the caller. A checked
            // IOException escaping a Kotlin AIDL implementation cannot be used
            // as its transaction failure reply.
            throw IllegalStateException("The source response pipe is unavailable", error)
        }
        try {
            executor.execute {
                try {
                    ParcelFileDescriptor.AutoCloseOutputStream(pipe[1]).use { output ->
                        output.write(response())
                    }
                } catch (_: IOException) {
                    // A closed remote reader is an ordinary failed request. Never
                    // let EPIPE escape the executor and kill the Python owner.
                    Log.d("ExtensionResponsePipe", "Extension response reader closed")
                }
            }
        } catch (error: RejectedExecutionException) {
            // No writer was scheduled: neither end can be handed to a caller.
            pipe.forEach { try { it.close() } catch (_: IOException) { } }
            throw IllegalStateException("The source network gateway is busy", error)
        }
        return pipe[0]
    }
}
