package com.albertoroca.pupsdk

/**
 * Immutable configuration for [PupClient]. All values are in milliseconds unless stated
 * otherwise.
 */
data class PupClientConfig(
    val baseUrl: String,
    val apiKey: String? = null,
    val connectTimeoutMillis: Long = 10_000,
    val readTimeoutMillis: Long = 30_000,
    val userAgent: String = DEFAULT_USER_AGENT,
    val dnsOverrides: Map<String, List<String>> = emptyMap()
) {
    init {
        require(baseUrl.isNotBlank()) { "baseUrl cannot be blank" }
        require(connectTimeoutMillis > 0) { "connectTimeoutMillis must be > 0" }
        require(readTimeoutMillis > 0) { "readTimeoutMillis must be > 0" }
    }

    companion object {
        const val DEFAULT_USER_AGENT = "PupSDK-Android/1.0"
    }
}

class PupSdkException(message: String, cause: Throwable? = null) : Exception(message, cause)
