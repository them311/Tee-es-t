import { COLORS, PROFILES } from "../../data/quizData";
import { useIsMobile } from "../../utils/styles";
import SectionTitle from "../shared/SectionTitle";
import HoverButton from "../shared/HoverButton";

export default function ProfilsPage({ navigate }) {
  const isMobile = useIsMobile();
  const entries = Object.entries(PROFILES);

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
          title="Nos 5 Profils Gourmands"
          subtitle="Decouvrez les 5 identites gourmandes et trouvez celle qui vous ressemble."
        />

        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          {entries.map(([key, profile], i) => (
            <div
              key={key}
              style={{
                background: COLORS.blanc,
                borderRadius: 20,
                padding: isMobile ? "32px 24px" : "40px 40px",
                boxShadow: "0 8px 32px rgba(10,9,8,0.06)",
                display: "flex",
                flexDirection: isMobile ? "column" : (i % 2 === 0 ? "row" : "row-reverse"),
                alignItems: "center",
                gap: isMobile ? 24 : 40,
              }}
            >
              <div style={{
                width: 100,
                height: 100,
                borderRadius: "50%",
                border: `3px solid ${profile.color}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: COLORS.creme,
                flexShrink: 0,
              }}>
                <span style={{ fontSize: 48 }}>{profile.emoji}</span>
              </div>

              <div style={{ flex: 1, textAlign: isMobile ? "center" : "left" }}>
                <h3 style={{
                  fontFamily: "'Cormorant Garamond', Georgia, serif",
                  fontSize: 28,
                  fontWeight: 700,
                  color: profile.color,
                  margin: "0 0 12px",
                }}>
                  {profile.name}
                </h3>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 15,
                  color: COLORS.noirLight,
                  lineHeight: 1.65,
                  margin: "0 0 16px",
                }}>
                  {profile.description}
                </p>
                <p style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 14,
                  color: COLORS.gris,
                  fontStyle: "italic",
                  lineHeight: 1.6,
                  margin: 0,
                }}>
                  {profile.sauce_match}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Quiz */}
        <div style={{ textAlign: "center", marginTop: 48 }}>
          <p style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 26,
            fontWeight: 600,
            color: COLORS.noir,
            margin: "0 0 20px",
          }}>
            Quel profil etes-vous ?
          </p>
          <HoverButton
            onClick={() => navigate("quiz")}
            style={{
              background: COLORS.rouge,
              color: COLORS.blanc,
              borderRadius: 10,
              padding: "16px 40px",
              fontSize: 15,
              fontWeight: 600,
              letterSpacing: "0.5px",
            }}
          >
            Faire le quiz
          </HoverButton>
        </div>
      </section>
    </div>
  );
}
