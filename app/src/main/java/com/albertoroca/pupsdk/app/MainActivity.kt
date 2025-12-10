package com.albertoroca.pupsdk.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.albertoroca.pupsdk.PupClient
import com.albertoroca.pupsdk.PupClientConfig
import com.albertoroca.pupsdk.PupSdkException
import com.albertoroca.pupsdk.app.ui.theme.PupTheme
import kotlinx.coroutines.launch

private const val DEFAULT_BACKEND = "https://pup-sdk.alroca308.workers.dev"

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val client = PupClient(
            PupClientConfig(
                baseUrl = DEFAULT_BACKEND,
                dnsOverrides = mapOf(
                    "pup-sdk.alroca308.workers.dev" to listOf(
                        "104.21.50.6",
                        "172.67.198.178"
                    )
                )
            )
        )

        setContent {
            PupTheme {
                PupDemoScreen(client = client)
            }
        }
    }
}

@Composable
private fun PupDemoScreen(client: PupClient) {
    val scope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }

    var statusText by remember { mutableStateOf("Tap \"Check Status\" to connect...") }
    var message by remember { mutableStateOf("Tell me a joke") }
    var responseText by remember { mutableStateOf("") }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .padding(20.dp)
                .fillMaxSize(),
            verticalArrangement = Arrangement.Top,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(text = "Pup SDK", style = MaterialTheme.typography.headlineMedium)
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = statusText, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = {
                scope.launch {
                    try {
                        val status = client.status()
                        statusText = "Status: ${status.message ?: "connected"}" +
                            " • available=${status.available}"
                    } catch (ex: Exception) {
                        statusText = "Status failed: ${ex.message}".trim()
                    }
                }
            }) {
                Text("Check Status")
            }
            Spacer(modifier = Modifier.height(24.dp))
            OutlinedTextField(
                value = message,
                onValueChange = { message = it },
                label = { Text("Message") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = {
                    scope.launch {
                        try {
                            val reply = client.chat(message)
                            responseText = reply.response
                        } catch (ex: PupSdkException) {
                            snackbarHostState.showSnackbar(ex.message ?: "Chat failed")
                        } catch (ex: Exception) {
                            snackbarHostState.showSnackbar("Chat failed: ${ex.message}")
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Send Message")
            }
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = if (responseText.isBlank()) "Response will appear here" else responseText,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}
