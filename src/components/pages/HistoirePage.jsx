import { COLORS } from "../../data/quizData";
import { useIsMobile } from "../../utils/styles";
import { HISTORY } from "../../data/siteContent";
import SectionTitle from "../shared/SectionTitle";
import Divider from "../shared/Divider";

export default function HistoirePage() {
  const isMobile = useIsMobile();

  return (
    <div style={{
      background: `linear-gradient(180deg, ${COLORS.creme} 0%, ${COLORS.cremeDark} 100%)`,
      minHeight: "100vh",
    }}>
      <section style={{
        padding: isMobile ? "48px 16px" : "80px 24px",
        maxWidth: 800,
        margin: "0 auto",
      }}>
        <SectionTitle
          eyebrow="La Francaise des Sauces"
          title={HISTORY.title}
          subtitle="L'art de la sauce, de la tradition a l'innovation."
        />

        {/* Stats */}
        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
          gap: 20,
          marginBottom: 60,
        }}>
          {HISTORY.stats.map((stat) => (
            <div key={stat.label} style={{
              background: COLORS.blanc,
              borderRadius: 16,
              padding: "32px 24px",
              textAlign: "center",
              boxShadow: "0 4px 16px rgba(10,9,8,0.05)",
            }}>
              <p style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: 52,
                fontWeight: 700,
                color: COLORS.or,
                margin: 0,
                lineHeight: 1,
              }}>
                {stat.value}
              </p>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 13,
                color: COLORS.gris,
                fontWeight: 500,
                margin: "8px 0 0",
                textTransform: "uppercase",
                letterSpacing: "1px",
              }}>
                {stat.label}
              </p>
            </div>
          ))}
        </div>

        {/* Timeline */}
        <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
          {HISTORY.sections.map((section, i) => (
            <div
              key={i}
              style={{
                background: COLORS.blanc,
                borderRadius: 20,
                padding: isMobile ? "32px 24px" : "40px 48px",
                boxShadow: "0 8px 32px rgba(10,9,8,0.06)",
                borderLeft: `4px solid ${COLORS.or}`,
              }}
            >
              <h3 style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: 24,
                fontWeight: 700,
                color: COLORS.noir,
                margin: "0 0 16px",
              }}>
                {section.title}
              </h3>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 15,
                color: COLORS.noirLight,
                lineHeight: 1.7,
                margin: 0,
              }}>
                {section.text}
              </p>
            </div>
          ))}
        </div>

        {/* Citation */}
        <div style={{
          marginTop: 60,
          borderLeft: `3px solid ${COLORS.or}`,
          paddingLeft: 28,
        }}>
          <p style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 24,
            fontStyle: "italic",
            color: COLORS.noirLight,
            lineHeight: 1.5,
            margin: 0,
          }}>
            "Bien manger n'est pas un luxe. C'est un art de vivre a la francaise."
          </p>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 13,
            color: COLORS.gris,
            marginTop: 12,
          }}>
            — La Francaise des Sauces
          </p>
        </div>
      </section>
    </div>
  );
}
