import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { api } from "../api";
import type { StudentMatch } from "../types";

/**
 * Top students ranked for a given mission.
 *
 * Data flow mirrors the student Matches page:
 *   1. `location.state.bootstrap` — inline candidates returned by POST /offers
 *      so the employer never stares at an empty list on submit.
 *   2. REST GET /offers/:id/matches — source of truth on refresh.
 */
export default function CompanyMatches() {
  const { offerId: rawId } = useParams();
  const location = useLocation() as {
    state?: { bootstrap?: StudentMatch[]; enriched?: string[] };
  };
  const offerId = rawId ?? localStorage.getItem("studentflow.offer_id") ?? "";
  const bootstrap = location.state?.bootstrap ?? null;
  const enriched = location.state?.enriched ?? null;

  const [matches, setMatches] = useState<StudentMatch[] | null>(bootstrap);
  const [loading, setLoading] = useState(bootstrap === null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!offerId) {
      setError("Aucune mission. Publie-en une d'abord.");
      setLoading(false);
      return;
    }
    api
      .listMatchesForOffer(offerId)
      .then((data) => {
        setMatches(data);
        setError(null);
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : String(err)),
      )
      .finally(() => setLoading(false));
  }, [offerId]);

  if (loading && matches === null) return <div className="loading">Chargement des candidats…</div>;

  if (error)
    return (
      <div>
        <div className="alert error">{error}</div>
        <Link to="/company">
          <button>Publier une mission</button>
        </Link>
      </div>
    );

  return (
    <div>
      <h2>Candidats pour ta mission</h2>
      <p style={{ color: "var(--fg-muted)" }}>
        Top étudiants scorés par StudentFlow. Chaque ligne affiche le pourcentage
        de match et les raisons derrière le score.
      </p>
      {enriched && enriched.length > 0 && (
        <div className="card" style={{ background: "rgba(66,153,225,0.08)", borderColor: "var(--accent)" }}>
          <strong>Compétences détectées automatiquement dans ton annonce :</strong>
          <div className="reasons" style={{ marginTop: "0.5rem" }}>
            {enriched.map((s) => (
              <span key={s} style={{ borderColor: "var(--accent)", color: "var(--accent)" }}>
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
      {matches && matches.length === 0 ? (
        <div className="empty">
          Aucun candidat pour l'instant. StudentFlow notifiera automatiquement
          les étudiants dès qu'un nouveau profil matchera ta mission.
        </div>
      ) : (
        matches?.map((m) => (
          <div key={m.student_id} className="card match">
            <div>
              <h3>{m.full_name || "Étudiant"}</h3>
              <div className="meta">
                <a href={`mailto:${m.email}`}>{m.email}</a>
                {m.city ? ` · ${m.city}` : ""}
                {typeof m.distance_km === "number" && <> · {Math.round(m.distance_km)} km</>}
              </div>
            </div>
            <span className="score">{Math.round(m.score * 100)}%</span>
            <div className="reasons">
              {m.reasons.map((r, i) => (
                <span key={i}>{r}</span>
              ))}
              {m.skills.slice(0, 6).map((s, i) => (
                <span key={`sk-${i}`} style={{ borderColor: "var(--accent)", color: "var(--accent)" }}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
