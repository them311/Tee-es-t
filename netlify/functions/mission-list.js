import { getStore } from "@netlify/blobs";

export default async (req) => {
  const apiKey = req.headers.get("x-api-key") || "";
  const expected = Netlify.env.get("LFDS_API_KEY");
  if (expected && apiKey !== expected) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const indexStore = getStore("mission-email-index");
    const ids = (await indexStore.get("all", { type: "json" })) || [];

    const store = getStore("mission-emails");
    const missions = [];

    for (const id of ids.slice(-50).reverse()) {
      try {
        const data = await store.get(id, { type: "json" });
        if (data) {
          missions.push({
            id: data.id,
            to: data.to,
            subject: data.subject,
            mission_title: data.mission_title,
            platform: data.platform,
            budget: data.budget,
            delai: data.delai,
            status: data.status,
            created_at: data.created_at,
          });
        }
      } catch (e) {
        continue;
      }
    }

    return new Response(
      JSON.stringify({ count: missions.length, missions }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: "Internal error", message: err.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};

export const config = {
  path: "/api/missions",
};
