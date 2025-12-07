// cf-worker.js
// Minimal Pup backend running on Cloudflare Workers.
// Implements:
//   GET  /           → simple stub
//   GET  /api/v1/status → PupStatus-compatible JSON
//   POST /api/v1/chat   → ChatResponse-compatible JSON (echo or LLM)

// Helper: JSON response with CORS
function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json",
      "access-control-allow-origin": "*",
    },
  });
}

// Optional: very tiny timer for execution_time
function nowMs() {
  return Date.now();
}

export default {
  /**
   * Cloudflare Worker entrypoint
   * @param {Request} request
   * @param {Record<string,string>} env  - bindings (OPEN_API_KEY, SYN_API_KEY, etc.)
   */
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Root stub for manual testing
    if (path === "/" || path === "") {
      return jsonResponse({
        status: "ok",
        message: "Cloudflare Pup backend is running (stub)",
      });
    }

    // Pup status endpoint
    if (path === "/api/v1/status" && request.method === "GET") {
      return handleStatus(env);
    }

    // Pup chat endpoint
    if (path === "/api/v1/chat" && request.method === "POST") {
      return handleChat(request, env);
    }

    // Not found
    return jsonResponse({ error: "Not found" }, 404);
  },
};

function handleStatus(env) {
  // Shape is designed to be compatible with PupStatus(**response)
  const body = {
    available: true,
    version: "0.1.0",
    message: "Cloudflare Pup backend is ready",
    capabilities: [
      {
        name: "chat",
        enabled: true,
        description: "Basic chat via Cloudflare Worker backend",
      },
    ],
  };
  return jsonResponse(body, 200);
}

async function handleChat(request, env) {
  let payload;
  try {
    payload = await request.json();
  } catch (err) {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  const userMessage = (payload && payload.message) || "";

  const started = nowMs();

  // If you want real LLM responses, uncomment the OpenAI call below
  // and make sure OPEN_API_KEY is set as a Worker environment variable.
  //
  // For now, we’ll do a simple echo so everything works without extra config.

  const hasOpenAIKey = !!env.OPEN_API_KEY;

  let answer;

  if (hasOpenAIKey && userMessage.trim()) {
    // --- Real OpenAI call (non-streaming) ---
    try {
      const openaiResponse = await fetch(
        "https://api.openai.com/v1/chat/completions",
        {
          method: "POST",
          headers: {
            "content-type": "application/json",
            Authorization: `Bearer ${env.OPEN_API_KEY}`,
          },
          body: JSON.stringify({
            model: "gpt-4.1-mini",
            messages: [
              {
                role: "system",
                content:
                  "You are Alberto the code puppy, a playful but helpful coding assistant. Keep answers concise.",
              },
              { role: "user", content: userMessage },
            ],
          }),
        }
      );

      if (!openaiResponse.ok) {
        const text = await openaiResponse.text();
        console.error("OpenAI error:", openaiResponse.status, text);
        answer =
          "🐕 Cloudflare backend: I tried to talk to the model but got an error from the API.";
      } else {
        const data = await openaiResponse.json();
        const choice = data.choices && data.choices[0];
        answer =
          (choice &&
            choice.message &&
            (choice.message.content || "").toString()) ||
          "🐕 Cloudflare backend: I got an empty response from the model.";
      }
    } catch (err) {
      console.error("OpenAI fetch failed:", err);
      answer =
        "🐕 Cloudflare backend: I hit a network error talking to the model.";
    }
  } else {
    // Fallback / debug echo mode
    answer = `🐕 (Cloudflare backend stub) You said: "${userMessage}"`;
  }

  const elapsed = (nowMs() - started) / 1000.0;

  // Shape compatible with ChatResponse(**response)
  const body = {
    success: true,
    response: answer,
    execution_time: elapsed,
  };

  return jsonResponse(body, 200);
}
