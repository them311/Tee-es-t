import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api";
import type { ContractType, StudentCreate } from "../types";

const CONTRACT_CHOICES: { value: ContractType; label: string }[] = [
  { value: "internship", label: "Stage" },
  { value: "apprenticeship", label: "Alternance" },
  { value: "cdd", label: "CDD" },
  { value: "cdi", label: "CDI" },
  { value: "part_time", label: "Temps partiel / job étudiant" },
  { value: "freelance", label: "Freelance" },
];

export default function Signup() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [city, setCity] = useState("");
  const [remoteOk, setRemoteOk] = useState(true);
  const [skills, setSkills] = useState("");
  const [contracts, setContracts] = useState<ContractType[]>(["internship", "apprenticeship"]);
  const [maxHours, setMaxHours] = useState(35);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleContract(c: ContractType) {
    setContracts((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c],
    );
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const payload: StudentCreate = {
      email,
      full_name: fullName,
      city,
      remote_ok: remoteOk,
      skills: skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      accepted_contracts: contracts,
      max_hours_per_week: maxHours,
    };
    try {
      const { id } = await api.createStudent(payload);
      // Stash locally so /matches can retrieve them without asking again.
      localStorage.setItem("studentflow.student_id", id);
      nav(`/matches/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h2>Créer mon profil</h2>
      {error && <div className="alert error">{error}</div>}
      <form onSubmit={onSubmit} className="card">
        <label>
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tonemail@exemple.fr"
          />
        </label>
        <label>
          Nom complet
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Prénom Nom"
          />
        </label>
        <label>
          Ville
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Paris"
          />
        </label>
        <label>
          Compétences (séparées par des virgules)
          <input
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            placeholder="react, javascript, python"
          />
        </label>
        <label>
          Heures max / semaine
          <input
            type="number"
            min={1}
            max={40}
            value={maxHours}
            onChange={(e) => setMaxHours(Number(e.target.value))}
          />
        </label>
        <label>
          <input
            type="checkbox"
            checked={remoteOk}
            onChange={(e) => setRemoteOk(e.target.checked)}
            style={{ width: "auto", marginRight: "0.5rem" }}
          />
          J'accepte le télétravail
        </label>
        <fieldset style={{ border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "1rem", marginBottom: "1rem" }}>
          <legend style={{ color: "var(--fg-muted)", fontSize: "0.9rem" }}>Types de contrat acceptés</legend>
          {CONTRACT_CHOICES.map((c) => (
            <label key={c.value} style={{ flexDirection: "row", alignItems: "center", marginBottom: "0.5rem" }}>
              <input
                type="checkbox"
                checked={contracts.includes(c.value)}
                onChange={() => toggleContract(c.value)}
                style={{ width: "auto", marginRight: "0.5rem" }}
              />
              {c.label}
            </label>
          ))}
        </fieldset>
        <button type="submit" disabled={submitting}>
          {submitting ? "Envoi…" : "Créer mon profil"}
        </button>
      </form>
    </div>
  );
}
