# 🐕 Pup SDK for Android

The brand-new Pup SDK is a modern Android/Kotlin client that talks to the
Alberto backend (FastAPI deployment or Cloudflare Worker). It wraps all HTTP
plumbing behind a small, testable API so you can embed "Alberto the sassy code
puppy" directly inside your Android apps.

## ✨ Highlights
- **Kotlin-first library** built with coroutines and OkHttp
- **Android Library module** (`sdk/`) ready for publication to MavenLocal or any
  artifact repository
- **Manual DNS override support** (handy when `*.workers.dev` is blocked)
- **Type-safe models** for chat + status calls
- **Sample usage snippet** ready for Jetpack Compose or XML based apps

## 🏗️ Project layout
```
pup-sdk/
├── build.gradle.kts              # Root Gradle build config
├── gradle.properties
├── settings.gradle.kts           # Declares :sdk and :app modules
├── app/                          # Runnable demo app (Jetpack Compose)
│   └── src/main/java/com/...     # MainActivity + theme
├── sdk/                          # Android library module
│   ├── build.gradle.kts
│   └── src/main/java/...         # Kotlin sources
└── README.md
```

## 🚀 Getting Started

1. **Open in Android Studio** (Giraffe+ recommended)
   - `File → Open…` and choose the `pup-sdk` directory
   - Studio will download the Gradle wrapper on first sync

2. **Run the demo app**
   - In Android Studio, select the `app` run configuration and click ▶️
   - The Compose UI lets you check backend status and send a chat message with
     no extra configuration

3. **Publish the SDK to MavenLocal (optional)**
   ```bash
   ./gradlew publishToMavenLocal
   ```

4. **Use the SDK in your own app**
   ```kotlin
   val client = PupClient(
       config = PupClientConfig(
           baseUrl = "https://pup-sdk.alroca308.workers.dev",
           apiKey = System.getenv("OPEN_API_KEY"),
       )
   )

   lifecycleScope.launch {
       val status = client.status()
       val reply = client.chat("Tell me a joke")
   }
   ```

## ⚙️ Environment configuration
The SDK honours runtime flags you supply through `PupClientConfig`:

| Property | Purpose |
|----------|---------|
| `baseUrl` | Backend URL (Cloudflare Worker, FastAPI bridge, etc.) |
| `apiKey` | Optional bearer token sent as `Authorization: Bearer` |
| `connectTimeout`, `readTimeout` | Millisecond-level control for OkHttp |
| `dnsOverrides` | `Map<String, List<String>>` to force specific IPs |

Example DNS override if `*.workers.dev` won’t resolve:
```kotlin
val config = PupClientConfig(
    baseUrl = "https://pup-sdk.alroca308.workers.dev",
    dnsOverrides = mapOf(
        "pup-sdk.alroca308.workers.dev" to listOf("104.21.50.6", "172.67.198.178")
    )
)
```

## 📦 Releasing
This repo is structured like a typical Android/Gradle library so you can:

- Publish to Maven Central / GPR using your preferred Gradle plugin
- Attach Dokka/Javadoc tasks for API docs
- Ship ProGuard/R8 consumer rules via `consumer-rules.pro`

## 🧪 Next steps
- Add instrumentation/unit tests inside `sdk/src/test` or
  `sdk/src/androidTest`
- Build a sample Compose app inside a `sample/` module for live demos
- Hook CI (GitHub Actions) to run `./gradlew lint test` on pull requests

Have fun building with Alberto on Android! 🐶💻
