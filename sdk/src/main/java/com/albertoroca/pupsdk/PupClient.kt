package com.albertoroca.pupsdk

import com.albertoroca.pupsdk.model.PupChatRequest
import com.albertoroca.pupsdk.model.PupChatResponse
import com.albertoroca.pupsdk.model.PupErrorResponse
import com.albertoroca.pupsdk.model.PupStatus
import com.albertoroca.pupsdk.network.ManualDns
import com.squareup.moshi.JsonAdapter
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response

/** Core entry point for interacting with the Alberto backend on Android. */
class PupClient(
    private val config: PupClientConfig,
    okHttpClient: OkHttpClient? = null
) {
    private val baseUrl = config.baseUrl.trimEnd('/')

    private val moshi: Moshi = Moshi.Builder()
        .add(KotlinJsonAdapterFactory())
        .build()

    private val chatAdapter: JsonAdapter<PupChatResponse> = moshi.adapter(PupChatResponse::class.java)
    private val statusAdapter: JsonAdapter<PupStatus> = moshi.adapter(PupStatus::class.java)
    private val errorAdapter: JsonAdapter<PupErrorResponse> = moshi.adapter(PupErrorResponse::class.java)
    private val requestAdapter: JsonAdapter<PupChatRequest> = moshi.adapter(PupChatRequest::class.java)

    private val httpClient: OkHttpClient = okHttpClient ?: buildClient()

    private fun buildClient(): OkHttpClient {
        val builder = OkHttpClient.Builder()
            .connectTimeout(config.connectTimeoutMillis, TimeUnit.MILLISECONDS)
            .readTimeout(config.readTimeoutMillis, TimeUnit.MILLISECONDS)
            .callTimeout(config.readTimeoutMillis + config.connectTimeoutMillis, TimeUnit.MILLISECONDS)

        ManualDns.fromStrings(config.dnsOverrides)?.let { dns ->
            builder.dns(dns)
        }

        return builder.build()
    }

    /** Fetches the backend status. */
    suspend fun status(): PupStatus = executeJson(
        requestBuilder("/api/v1/status").get().build(),
        statusAdapter
    )

    /** Sends a chat message to Alberto. */
    suspend fun chat(
        message: String,
        includeReasoning: Boolean = false,
        autoExecute: Boolean = false,
        context: Map<String, String>? = null
    ): PupChatResponse {
        val payload = PupChatRequest(message, includeReasoning, autoExecute, context)
        val json = requestAdapter.toJson(payload)
        val body = json.toRequestBody(JSON_MEDIA_TYPE)

        val request = requestBuilder("/api/v1/chat")
            .post(body)
            .build()

        return executeJson(request, chatAdapter)
    }

    private fun requestBuilder(path: String): Request.Builder {
        val url = if (path.startsWith("http")) path else baseUrl + path
        return Request.Builder()
            .url(url)
            .addHeader("Accept", "application/json")
            .addHeader("User-Agent", config.userAgent)
            .apply {
                config.apiKey?.takeIf { it.isNotBlank() }?.let { key ->
                    addHeader("Authorization", "Bearer $key")
                }
            }
    }

    private suspend fun <T> executeJson(
        request: Request,
        adapter: JsonAdapter<T>
    ): T = withContext(Dispatchers.IO) {
        val response = runCatching { httpClient.newCall(request).execute() }
            .getOrElse { throw PupSdkException("Network error", it) }

        response.use {
            if (!response.isSuccessful) {
                throw PupSdkException(buildHttpError(response))
            }

            val body = response.body?.string()
                ?: throw PupSdkException("Empty response body")

            adapter.fromJson(body)
                ?: throw PupSdkException("Failed to parse response")
        }
    }

    private fun buildHttpError(response: Response): String {
        val body = try {
            response.body?.string()
        } catch (_: IOException) {
            null
        }

        val parsed = body?.let { errorAdapter.fromJson(it) }
        val errorMessage = parsed?.error ?: parsed?.message
        val fallback = if (body.isNullOrBlank()) "HTTP ${response.code}" else body
        return errorMessage ?: fallback ?: "Unknown error"
    }

    companion object {
        private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()
    }
}
