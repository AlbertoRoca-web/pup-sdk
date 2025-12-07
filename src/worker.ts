// src/worker.ts
//
// Minimal Cloudflare Worker backend for Pup SDK.
// Implements the endpoints that PupClient expects:
//
//   GET  /health
//   GET  /api/v1/status
//   POST /api/v1/chat
//
// Everything else returns 404 JSON.

interface Capability {
  name: string;
  enabled: boolean;
  description?: string;
}

function jsonResponse(body: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(body), {
    status: init?.status ?? 200,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
}

export default {
  async fetch(
    request: Request,
    env: Record<string, unknown>,
    ctx: ExecutionContext,
  ): Promise<Response> {
    const url = new URL(request.url);
    const { pathname } = url;

    // Root – simple stub
    if (pathname === "/") {
      return jsonResponse({
        status: "ok",
        message: "Cloudflare Pup backend is running (stub)",
      });
    }

    // Simple health check used by PupClient.test_connection()
    if (pathname === "/health") {
      return jsonResponse({ status: "ok" });
    }

    // PupClient.get_status() → /api/v1/status (GET)
    if (pathname === "/api/v1/status" && request.method === "GET") {
      const capabilities: Capability[] = [
        {
          name: "chat",
          enabled: true,
          description: "Basic chat via Cloudflare Worker backend",
        },
      ];

      return jsonResponse({
        available: true,
        version: "0.1.0",
        message: "Cloudflare Pup backend is ready",
        capabilities,
      });
    }

    // PupClient.chat() → /api/v1/chat (POST)
    if (pathname === "/api/v1/chat" && request.method === "POST") {
      let payload: any = {};
      try {
        payload = await request.json();
      } catch {
        // leave payload as {}
      }

      const msg =
        typeof payload?.message === "string" ? payload.message : "(no message)";

      const start = Date.now();
      const replyText =
        `🐕 Cloudflare backend stub replying to: "${msg}". ` +
        `This is coming from pup-sdk.alroca308.workers.dev.`;
      const executionTime = (Date.now() - start) / 1000.0;

      // Shape matches ChatResponse in pup_sdk.types (success/response/execution_time)
      return jsonResponse({
        success: true,
        response: replyText,
        execution_time: executionTime,
      });
    }

    // Optional: let you test POST /api/v1/chat from a browser as GET
    if (pathname === "/api/v1/chat" && request.method === "GET") {
      return jsonResponse(
        { error: "Use POST for /api/v1/chat" },
        { status: 405 },
      );
    }

    // Everything else → JSON 404
    return jsonResponse({ error: "Not found" }, { status: 404 });
  },
};
