import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api";
import MatchCard from "../components/MatchCard";
import type { Match } from "../types";

export default function Matches() {
  const params = useParams();
  const initialId =
    params.studentId ?? localStorage.getItem("studentflow.student_id") ?? "";

  const [studentId, setStudentId] = useState(initialId);
  const [matches, setMatches] = useState<Match[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load(id: string) {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.listMatchesForStudent(id);
      setMatches(data);
      localStorage.setItem("studentflow.student_id", id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setMatches(null);
    } finally {
      setLoading(false);
    }
  }

  // Auto-load if we had a saved id.
  useEffect(() => {
    if (initialId) void load(initialId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialId]);

  return (
    <div>
      <h2>Mes matches</h2>
      <div className="card">
        <label>
          ID étudiant
          <input
            type="text"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="collez votre id reçu à l'inscription"
          />
        </label>
        <button onClick={() => load(studentId)} disabled={!studentId || loading}>
          {loading ? "Chargement…" : "Rafraîchir"}
        </button>
      </div>

      {error && <div className="alert error">{error}</div>}
      {loading && <div className="loading">Chargement des matches…</div>}
      {matches && matches.length === 0 && (
        <div className="empty">
          Aucun match pour l'instant. Les agents tournent toutes les 15 min —
          reviens bientôt.
        </div>
      )}
      {matches && matches.length > 0 && (
        <div>
          {matches.map((m) => (
            <MatchCard key={m.offer_id} match={m} />
          ))}
        </div>
      )}
    </div>
  );
}
