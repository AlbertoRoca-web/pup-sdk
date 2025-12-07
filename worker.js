// worker.js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Health check
    if (pathname === "/health" || pathname === "/") {
      return jsonResponse({
        status: "ok",
        message: "Cloudflare Pup backend is running (stub)",
      });
    }

    // ---- Pup-style API: STATUS ----
    if (pathname === "/api/v1/status" && request.method === "GET") {
      return jsonResponse({
        available: true,
        version: "0.1.0",
        connected: true,
        demo_mode: false,
        message: "Cloudflare Worker backend (stub)",
        capabilities: [
          {
            name: "chat",
            enabled: true,
            description: "Stub chat via Cloudflare Worker",
          },
        ],
      });
    }

    // ---- Pup-style API: CHAT ----
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

      // No OpenAI calls yet – just echo back
      const reply =
        "🐕 (Cloudflare stub backend) I got your message: " + userMessage;

      return jsonResponse({
        success: true,
        response: reply,
        execution_time: 0.01,
      });
    }

    // Unknown route
    return new Response("Not found", { status: 404 });
  },
};

// Small helper for JSON responses
function jsonResponse(data, { status = 200, headers = {} } = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
  });
}
