import { getStore } from "@netlify/blobs";

export default async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type, x-api-key",
      },
    });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const apiKey = req.headers.get("x-api-key") || "";
  const expected = Netlify.env.get("LFDS_API_KEY");
  if (expected && apiKey !== expected) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const data = await req.json();
    const { to, subject, mission_title, platform, content, budget, delai } = data;

    if (!to || !subject || !content) {
      return new Response(
        JSON.stringify({ error: "Missing required fields: to, subject, content" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const gmailUser = Netlify.env.get("GMAIL_USER") || "bp.thevenot@gmail.com";
    const fromName = Netlify.env.get("GMAIL_FROM_NAME") || "Baptiste Thevenot";

    const htmlBody = buildEmailHTML({
      mission_title: mission_title || subject,
      platform: platform || "direct",
      content,
      budget: budget || "",
      delai: delai || "",
      fromName,
    });

    const store = getStore("mission-emails");
    const emailId = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    await store.setJSON(emailId, {
      id: emailId,
      to,
      from: `${fromName} <${gmailUser}>`,
      subject,
      mission_title: mission_title || subject,
      platform: platform || "direct",
      content,
      budget,
      delai,
      html: htmlBody,
      created_at: new Date().toISOString(),
      status: "queued",
    });

    const indexStore = getStore("mission-email-index");
    const existing = (await indexStore.get("all", { type: "json" })) || [];
    existing.push(emailId);
    await indexStore.setJSON("all", existing);

    console.log(`[send-mission] ${emailId} | to:${to} | ${mission_title || subject}`);

    return new Response(
      JSON.stringify({
        success: true,
        email_id: emailId,
        message: `Mission email queued for ${to}`,
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (err) {
    console.error("[send-mission] error:", err);
    return new Response(
      JSON.stringify({ error: "Internal error", message: err.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};

function buildEmailHTML({ mission_title, platform, content, budget, delai, fromName }) {
  const platformColors = {
    codeur: "#0066FF",
    malt: "#FC5757",
    "freelance-info": "#2D3748",
    upwork: "#14A800",
    direct: "#0ea5e9",
  };
  const color = platformColors[platform] || "#0ea5e9";

  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 16px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">

<tr><td style="background:#0f172a;padding:24px 32px">
  <div style="font-size:20px;font-weight:800;color:white;letter-spacing:-0.5px">SNB Consulting</div>
  <div style="font-size:12px;color:#94a3b8;margin-top:4px">Proposition de mission</div>
</td></tr>

<tr><td style="padding:32px">
  <div style="display:inline-block;padding:4px 12px;background:${color}15;color:${color};font-size:11px;font-weight:700;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:16px">${platform}</div>
  <h2 style="font-size:22px;font-weight:800;color:#0f172a;margin:0 0 8px;letter-spacing:-0.5px">${mission_title}</h2>
  ${budget ? `<div style="font-size:14px;color:#16a34a;font-weight:600;margin-bottom:4px">Budget : ${budget}</div>` : ""}
  ${delai ? `<div style="font-size:13px;color:#64748b;margin-bottom:20px">Delai : ${delai}</div>` : ""}
  <div style="border-top:1px solid #e2e8f0;margin:20px 0"></div>
  <div style="font-size:14px;color:#334155;line-height:1.8;white-space:pre-wrap">${content}</div>
</td></tr>

<tr><td style="background:#f8fafc;padding:20px 32px;border-top:1px solid #e2e8f0">
  <div style="font-size:13px;color:#0f172a;font-weight:700">${fromName}</div>
  <div style="font-size:12px;color:#64748b">SNB Consulting &mdash; Agents IA &amp; Automatisation</div>
  <div style="font-size:12px;color:#0ea5e9;margin-top:4px">bp.thevenot@gmail.com</div>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}

export const config = {
  path: "/api/mission/send",
};
