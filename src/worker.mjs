// worker.mjs
// Cloudflare Worker backend for Pup SDK.
//
// Implements a minimal Pup-compatible API:
//   GET  /               -> simple health JSON
//   GET  /health         -> simple health JSON (for PupClient.test_connection())
//   GET  /api/v1/status  -> PupStatus-compatible JSON
//   POST /api/v1/chat    -> ChatRequest -> OpenAI -> ChatResponse-compatible JSON
//
// It reads the OpenAI/Syn key from:
//   1. HTTP Authorization: Bearer <key>   (from PupClient in HuggingFace)
//   2. env.SYN_API_KEY
//   3. env.OPEN_API_KEY

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const { pathname } = url;

    const json = (data, init = {}) =>
      new Response(JSON.stringify(data), {
        status: init.status ?? 200,
        headers: {
          "content-type": "application/json; charset=utf-8",
          ...init.headers,
        },
      });

    // ---------------------------------------------------------------------
    // Basic health endpoints
    // ---------------------------------------------------------------------
    if (pathname === "/" || pathname === "/health") {
      return json({
        status: "ok",
        message: "Cloudflare Pup backend is running",
      });
    }

    // ---------------------------------------------------------------------
    // PupStatus-compatible status endpoint
    // ---------------------------------------------------------------------
    if (pathname === "/api/v1/status") {
      return json({
        available: true,
        version: "0.1.0",
        connected: true,
        demo_mode: false,
        message: "Cloudflare Pup backend is ready",
        capabilities: [
          {
            name: "chat",
            enabled: true,
            description: "Basic chat via Cloudflare Worker backend",
          },
        ],
      });
    }

    // ---------------------------------------------------------------------
    // Chat endpoint: POST /api/v1/chat
    // ---------------------------------------------------------------------
    if (pathname === "/api/v1/chat") {
      if (request.method !== "POST") {
        return json({ error: "Use POST for /api/v1/chat" }, { status: 405 });
      }

      // Parse ChatRequest body
      let body;
      try {
        body = await request.json();
      } catch {
        body = {};
      }

      const userMessage =
        (body && body.message) ||
        "Say hello like Alberto the sassy code puppy and mention that no message was provided.";

      const start = Date.now();

      // 1) Try to grab key from Authorization: Bearer <key>
      const authHeader = request.headers.get("authorization") || "";
      let headerKey = null;
      if (authHeader.toLowerCase().startsWith("bearer ")) {
        headerKey = authHeader.slice(7).trim();
      }

      // 2) Fallback to Worker env vars
      const apiKey = headerKey || env.SYN_API_KEY || env.OPEN_API_KEY;

      // If there is still no key, return a friendly message
      if (!apiKey) {
        const executionTime = (Date.now() - start) / 1000.0;
        return json({
          success: true,
          response:
            "🐕 Woof! Cloudflare backend is up, but I have no API key. " +
            "Either send an Authorization: Bearer <key> header, or set SYN_API_KEY / OPEN_API_KEY on the Worker.",
          execution_time: executionTime,
        });
      }

      // Call OpenAI Chat Completions API
      const openaiResponse = await fetch(
        "https://api.openai.com/v1/chat/completions",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "gpt-4o-mini",
            messages: [
              {
                role: "system",
                content:
                  "You are Alberto, a sassy but extremely helpful code puppy running behind a Cloudflare Worker backend. Be concise and code-focused.",
              },
              {
                role: "user",
                content: userMessage,
              },
            ],
          }),
        },
      );

      if (!openaiResponse.ok) {
        const errText = await openaiResponse.text();
        return json(
          {
            success: false,
            error: "Upstream OpenAI error",
            details: errText.slice(0, 1000),
          },
          { status: 502 },
        );
      }

      const openaiJson = await openaiResponse.json();
      const reply =
        openaiJson?.choices?.[0]?.message?.content?.trim() ||
        "🐕 Woof! I couldn't parse OpenAI's reply, but the backend is alive.";

      const executionTime = (Date.now() - start) / 1000.0;

      // This shape matches ChatResponse(**response) in the Pup SDK
      return json({
        success: true,
        response: reply,
        execution_time: executionTime,
      });
    }

    // ---------------------------------------------------------------------
    // Unknown route
    // ---------------------------------------------------------------------
    return json({ error: "Not found" }, { status: 404 });
  },
};
