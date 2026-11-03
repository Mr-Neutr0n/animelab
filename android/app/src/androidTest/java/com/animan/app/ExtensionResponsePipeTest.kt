package com.animan.app

import android.os.ParcelFileDescriptor
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.IOException
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class ExtensionResponsePipeTest {
    @Test fun closedReaderDoesNotCrashOwnerAndNextRequestStillWorks() {
        val uncaught = AtomicReference<Throwable>()
        val executor = Executors.newSingleThreadExecutor { task ->
            Thread(task, "response-pipe-regression").apply {
                uncaughtExceptionHandler = Thread.UncaughtExceptionHandler { _, error -> uncaught.set(error) }
            }
        }
        val release = CountDownLatch(1)
        try {
            val abandoned = ExtensionResponsePipe.open(executor) {
                check(release.await(5, TimeUnit.SECONDS))
                ByteArray(1024 * 1024)
            }
            abandoned.close()
            release.countDown()
            val next = ExtensionResponsePipe.open(executor) { "next response".toByteArray() }
            ParcelFileDescriptor.AutoCloseInputStream(next).use {
                assertEquals("next response", String(it.readBytes()))
            }
            executor.shutdown()
            assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS))
            assertNull("Closing a response reader must not escape the executor", uncaught.get())
        } finally {
            release.countDown()
            executor.shutdownNow()
        }
    }

    @Test fun saturatedGatewayReportsRequestFailureWithoutLeavingAnOpenPipe() {
        val executor = Executors.newSingleThreadExecutor()
        executor.shutdown()
        try {
            ExtensionResponsePipe.open(executor) { ByteArray(0) }.close()
            fail("A rejected request must fail immediately")
        } catch (expected: IOException) {
            assertEquals("The source network gateway is busy", expected.message)
        }
    }
}
