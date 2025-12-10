package com.albertoroca.pupsdk.model

import com.squareup.moshi.Json

/*** Request/response payloads shared by the SDK. */

data class PupChatRequest(
    val message: String,
    @Json(name = "include_reasoning")
    val includeReasoning: Boolean = false,
    @Json(name = "auto_execute")
    val autoExecute: Boolean = false,
    val context: Map<String, String>? = null
)

data class PupChatResponse(
    val success: Boolean,
    val response: String,
    val reasoning: String? = null,
    @Json(name = "execution_time")
    val executionTime: Double? = null
)

data class PupStatus(
    val available: Boolean,
    val version: String,
    val connected: Boolean,
    @Json(name = "demo_mode")
    val demoMode: Boolean,
    val message: String? = null,
    val capabilities: List<PupCapability> = emptyList()
)

data class PupCapability(
    val name: String,
    val enabled: Boolean,
    val description: String? = null
)

data class PupErrorResponse(
    val error: String? = null,
    val message: String? = null
)
