// worker.js (or src/index.ts if that's your entrypoint)

export default {
  /**
   * Cloudflare Worker entrypoint.
   * This implements a minimal Pup-compatible backend:
   *   - GET  /               -> simple health stub
   *   - GET  /health         -> health stub for test_connection()
   *   - GET  /api/v1/status  -> PupStatus shape
   *   - POST /api/v1/chat    -> Pup ChatResponse shape
   */
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const { pathname } = url;

    // Small helper to send JSON
    const json = (data, status = 200, extraHeaders = {}) =>
      new Response(JSON.stringify(data), {
        status,
        headers: {
          "content-type": "application/json; charset=utf-8",
          ...extraHeaders,
        },
      });

    // Root stub
    if (pathname === "/" && request.method === "GET") {
      return json({
        status: "ok",
        message: "Cloudflare Pup backend is running (stub)",
      });
    }

    // Simple health endpoint for PupClient.test_connection()
    if (pathname === "/health" && request.method === "GET") {
      return json({ status: "ok" });
    }

    // PupStatus for PupClient.get_status()
    if (pathname === "/api/v1/status" && request.method === "GET") {
      return json({
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
      });
    }

    // Main chat endpoint – PupClient._request("POST", "/chat")
    if (pathname === "/api/v1/chat") {
      if (request.method !== "POST") {
        return json({ error: "Use POST for /api/v1/chat" }, 405);
      }

      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "Invalid JSON body" }, 400);
      }

      const message =
        body?.message ??
        body?.prompt ??
        "No message provided to Cloudflare Pup backend.";

      // We'll try to use an LLM if a key is configured, otherwise stub.
      const apiKey = env.SYN_API_KEY || env.OPEN_API_KEY;

      let replyText;

      if (!apiKey) {
        // No LLM key configured in Worker – safe stub
        replyText = `🐕 [Cloudflare stub] I received: "${message}". Configure SYN_API_KEY or OPEN_API_KEY in the Worker env for real LLM replies.`;
      } else {
        // Try to call OpenAI-style chat completions
        // (Treat SYN_API_KEY as an OpenAI-compatible key if that's what you're using.)
        try {
          const payload = {
            model: "gpt-4.1-mini", // adjust if you like
            messages: [
              {
                role: "system",
                content:
                  "You are Alberto, a sassy but helpful code puppy. Be concise and practical.",
              },
              { role: "user", content: message },
            ],
          };

          const resp = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${apiKey}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
          });

          if (!resp.ok) {
            const errText = await resp.text();
            console.error("LLM backend error", resp.status, errText);
            replyText = `🐕 [Cloudflare backend error ${resp.status}] I couldn't talk to the model.`;
          } else {
            const data = await resp.json();
            replyText =
              data?.choices?.[0]?.message?.content?.trim() ||
              "🐕 [Cloudflare backend] The model didn't return any text.";
          }
        } catch (e) {
          console.error("LLM fetch exception", e);
          replyText =
            "🐕 [Cloudflare backend exception] Something went wrong talking to the model.";
        }
      }

      // Shape matches pup_sdk.types.ChatResponse as used in web/app.py
      const chatResponse = {
        success: true,
        response: replyText,
        execution_time: 0.1,
      };

      return json(chatResponse);
    }

    // Fallback 404 for everything else
    return json({ error: "Not found" }, 404);
  },
};
