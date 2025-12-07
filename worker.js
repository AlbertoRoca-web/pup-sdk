export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;

    // Health check for sanity
    if (pathname === "/health" || pathname === "/") {
      return jsonResponse({
        status: "ok",
        message: "Cloudflare Worker is running",
      });
    }

    // ---- Pup-style API skeletons ----
    if (pathname === "/api/v1/status") {
      // TODO: adjust shape once we fully align with PupStatus
      return jsonResponse({
        available: true,
        version: "0.1.0",
        // Placeholder fields – we'll refine once we see PupStatus
        capabilities: [],
        message: "Cloudflare Pup backend placeholder",
      });
    }

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

      // For now: simple echo. Later, call OpenAI/Syn here using env.OPEN_API_KEY / env.SYN_API_KEY.
      const reply =
        "🐕 (Cloudflare stub) I received your message: " + userMessage;

      return jsonResponse({
        success: true,
        response: reply,
        execution_time: 0.01,
      });
    }

    // 404 for anything else
    return new Response("Not found", { status: 404 });
  },
};

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
