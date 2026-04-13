import type { Match } from "../types";

interface Props {
  match: Match;
}

export default function MatchCard({ match }: Props) {
  const pct = Math.round(match.score * 100);
  return (
    <div className="card">
      <div className="match">
        <div>
          <h3>{match.title || "(sans titre)"}</h3>
          <div className="meta">
            {match.company || "—"} · {match.city || "lieu non précisé"}
          </div>
        </div>
        <span className="score">{pct}%</span>
        {match.reasons.length > 0 && (
          <div className="reasons">
            {match.reasons.map((r, i) => (
              <span key={i}>{r}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
