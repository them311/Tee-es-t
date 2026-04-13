import type { Match, OfferCreate, Stats, StudentCreate, StudentMatch } from "./types";

/**
 * Base URL of the StudentFlow API.
 *
 * Configured via the `VITE_API_BASE_URL` build-time env var. Defaults to
 * `/api` so that the Vite dev proxy (see vite.config.ts) forwards requests
 * to http://localhost:8000 during development.
 *
 * In production, set VITE_API_BASE_URL to the Railway URL of the
 * studentflow-api service, e.g. `https://studentflow-api.up.railway.app`.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText}: ${text}`);
  }
  // Some endpoints return 204 No Content.
  if (resp.status === 204) {
    return undefined as T;
  }
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<{ status: string; version: string }>("/health"),

  createStudent: (payload: StudentCreate) =>
    request<{ id: string }>("/students", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listMatchesForStudent: (studentId: string) =>
    request<Match[]>(`/students/${encodeURIComponent(studentId)}/matches`),

  getStats: () => request<Stats>("/stats"),

  createOffer: (payload: OfferCreate) =>
    request<{ id: string }>("/offers", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listMatchesForOffer: (offerId: string) =>
    request<StudentMatch[]>(`/offers/${encodeURIComponent(offerId)}/matches`),
};
