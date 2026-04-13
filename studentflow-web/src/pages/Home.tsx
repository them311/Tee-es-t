import { Link } from "react-router-dom";

export default function Home() {
  return (
    <section className="hero">
      <h1>Le bon job étudiant, envoyé au bon étudiant, en temps réel.</h1>
      <p>
        StudentFlow scanne en continu France Travail, Adzuna, HelloWork et Jooble, score
        chaque offre contre ton profil, et te notifie dès qu'une correspondance dépasse 60 %.
        Zéro chasse, zéro perte de temps.
      </p>
      <div style={{ marginTop: "2rem", display: "flex", gap: "1rem", justifyContent: "center" }}>
        <Link to="/signup">
          <button>Créer mon profil</button>
        </Link>
        <Link to="/stats">
          <button style={{ background: "transparent", border: "1px solid var(--border)" }}>
            Voir les stats
          </button>
        </Link>
      </div>
    </section>
  );
}
