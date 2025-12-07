// worker.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Simple health check for sanity
    if (pathname === "/health" || pathname === "/") {
      return jsonResponse({
        status: "ok",
        message: "Cloudflare Pup backend is running",
      });
    }

    // ---- Pup-style API ----

    // 1) Status endpoint expected by PupClient.get_status()
    if (pathname === "/api/v1/status" && request.method === "GET") {
      return jsonResponse({
        // These names are chosen to match what PupStatus is very likely expecting.
        available: true,
        version: "0.1.0",
        connected: true,
        demo_mode: false,
        message: "Cloudflare Worker backend",
        // Very simple capabilities list – safe for Pydantic to consume
        capabilities: [
          {
            name: "chat",
            enabled: true,
            description: "Chat via Cloudflare Worker + OpenAI/Syn",
          },
        ],
      });
    }

    // 2) Chat endpoint expected by PupClient.say_woof()/chat()
    if (pathname === "/api/v1/chat" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return jsonResponse(
          { error: "Invalid JSON body" },
          { status: 400 }
        );
      }

      const userMessage = body?.message ?? "";
      const context = body?.context ?? null;

      const start = Date.now();

      let reply;
      try {
        reply = await callLLM(userMessage, context, env);
      } catch (e) {
        console.error("LLM error:", e);
        reply =
          "🐕 (Cloudflare backend) I tried to call the model but something went wrong: " +
          (e?.message || String(e));
      }

      const executionTime = (Date.now() - start) / 1000.0;

      return jsonResponse({
        success: true,
        response: reply,
        execution_time: executionTime,
      });
    }

    // Unknown route
    return new Response("Not found", { status: 404 });
  },
};

/**
 * Minimal helper to talk to OpenAI/Syn using fetch.
 * Uses SYN_API_KEY if present, otherwise OPEN_API_KEY.
 */
async function callLLM(message, context, env) {
  const apiKey = env.SYN_API_KEY || env.OPEN_API_KEY;
  if (!apiKey) {
    return (
      "No API key configured in Cloudflare Worker. " +
      "Set SYN_API_KEY or OPEN_API_KEY in the Worker environment."
    );
  }

  // Basic prompt – you can tune this later
  const userContent = context
    ? `Context:\n${JSON.stringify(context)}\n\nUser: ${message}`
    : message;

  // Standard Chat Completions call; adjust model if you like
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4.1-mini",
      messages: [{ role: "user", content: userContent }],
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`OpenAI HTTP ${res.status}: ${text}`);
  }

  const data = await res.json();
  const choice = data.choices?.[0];
  const content = choice?.message?.content;
  return content || "Model returned no content.";
}

// Helper to build JSON responses
function jsonResponse(data, { status = 200, headers = {} } = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });
}
