import { useState } from "react";
import { COLORS } from "../../data/quizData";
import { useIsMobile } from "../../utils/styles";
import { CONTACT } from "../../data/siteContent";
import SectionTitle from "../shared/SectionTitle";
import HoverButton from "../shared/HoverButton";

export default function ContactPage() {
  const isMobile = useIsMobile();
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });

  function handleSubmit(e) {
    e.preventDefault();
    const subject = encodeURIComponent(form.subject || "Contact via le site");
    const body = encodeURIComponent(
      `Nom : ${form.name}\nEmail : ${form.email}\n\n${form.message}`
    );
    window.location.href = `mailto:${CONTACT.email}?subject=${subject}&body=${body}`;
  }

  const inputStyle = {
    padding: "14px 18px",
    border: `1.5px solid ${COLORS.cremeDark}`,
    borderRadius: 10,
    fontSize: 15,
    fontFamily: "'DM Sans', sans-serif",
    outline: "none",
    color: COLORS.noir,
    width: "100%",
    background: COLORS.blanc,
    transition: "border-color 0.2s ease",
  };

  return (
    <div style={{
      background: `linear-gradient(180deg, ${COLORS.creme} 0%, ${COLORS.cremeDark} 100%)`,
      minHeight: "100vh",
    }}>
      <section style={{
        padding: isMobile ? "48px 16px" : "80px 24px",
        maxWidth: 900,
        margin: "0 auto",
      }}>
        <SectionTitle
          eyebrow="La Francaise des Sauces"
          title={CONTACT.title}
          subtitle={CONTACT.subtitle}
        />

        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "3fr 2fr",
          gap: 32,
        }}>
          {/* Form */}
          <div style={{
            background: COLORS.blanc,
            borderRadius: 20,
            padding: isMobile ? "28px 20px" : "40px 36px",
            boxShadow: "0 8px 32px rgba(10,9,8,0.06)",
          }}>
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div>
                <label style={labelStyle}>Votre nom</label>
                <input
                  type="text"
                  placeholder="Jean Dupont"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  style={inputStyle}
                  required
                />
              </div>
              <div>
                <label style={labelStyle}>Votre email</label>
                <input
                  type="email"
                  placeholder="jean@exemple.fr"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  style={inputStyle}
                  required
                />
              </div>
              <div>
                <label style={labelStyle}>Sujet</label>
                <select
                  value={form.subject}
                  onChange={(e) => setForm({ ...form, subject: e.target.value })}
                  style={{ ...inputStyle, cursor: "pointer" }}
                >
                  <option value="">-- Choisir un sujet --</option>
                  {CONTACT.fields[2].options.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Message</label>
                <textarea
                  placeholder="Votre message..."
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  style={{ ...inputStyle, minHeight: 140, resize: "vertical" }}
                  required
                />
              </div>
              <HoverButton
                style={{
                  background: COLORS.noir,
                  color: COLORS.blanc,
                  borderRadius: 10,
                  padding: "16px 40px",
                  fontSize: 15,
                  fontWeight: 600,
                  letterSpacing: "0.5px",
                  width: "100%",
                }}
              >
                Envoyer
              </HoverButton>
            </form>
          </div>

          {/* Info card */}
          <div style={{
            background: COLORS.noir,
            borderRadius: 20,
            padding: isMobile ? "28px 20px" : "40px 36px",
            color: COLORS.blanc,
          }}>
            <h3 style={{
              fontFamily: "'Cormorant Garamond', Georgia, serif",
              fontSize: 24,
              fontWeight: 700,
              margin: "0 0 24px",
            }}>
              Parlons de vos projets
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 11,
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                  color: COLORS.or,
                  fontWeight: 600,
                  margin: "0 0 6px",
                }}>
                  Email
                </p>
                <a
                  href={`mailto:${CONTACT.email}`}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: 15,
                    color: COLORS.cremeDark,
                    textDecoration: "none",
                  }}
                >
                  {CONTACT.email}
                </a>
              </div>
              <div>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 11,
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                  color: COLORS.or,
                  fontWeight: 600,
                  margin: "0 0 6px",
                }}>
                  Horaires
                </p>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 14,
                  color: COLORS.gris,
                  lineHeight: 1.6,
                  margin: 0,
                }}>
                  Lundi — Vendredi
                  <br />
                  9h00 — 18h00
                </p>
              </div>
              <div>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 11,
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                  color: COLORS.or,
                  fontWeight: 600,
                  margin: "0 0 6px",
                }}>
                  Localisation
                </p>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 14,
                  color: COLORS.gris,
                  lineHeight: 1.6,
                  margin: 0,
                }}>
                  France
                </p>
              </div>
            </div>

            <div style={{
              marginTop: 32,
              padding: "20px 0 0",
              borderTop: `1px solid ${COLORS.noirLight}`,
            }}>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 12,
                color: COLORS.gris,
                lineHeight: 1.6,
                margin: 0,
              }}>
                Conforme RGPD · Donnees hebergees en France · Aucune revente a des tiers
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

const labelStyle = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: 13,
  fontWeight: 600,
  color: "#2A2826",
  display: "block",
  marginBottom: 6,
};
