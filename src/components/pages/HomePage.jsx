import { COLORS, PROFILES } from "../../data/quizData";
import { useIsMobile } from "../../utils/styles";
import { HERO, BRAND_PROMISES, PRODUCT_HIGHLIGHT, QUIZ_CTA } from "../../data/siteContent";
import SectionTitle from "../shared/SectionTitle";
import HoverButton from "../shared/HoverButton";
import Divider from "../shared/Divider";
import Card from "../shared/Card";

export default function HomePage({ navigate }) {
  const isMobile = useIsMobile();

  return (
    <div>
      {/* ── HERO ── */}
      <section style={{
        minHeight: "80vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `linear-gradient(180deg, ${COLORS.creme} 0%, ${COLORS.cremeDark} 100%)`,
        padding: isMobile ? "60px 20px" : "80px 24px",
        textAlign: "center",
      }}>
        <div style={{ maxWidth: 680 }}>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 11,
            letterSpacing: "3px",
            color: COLORS.or,
            fontWeight: 600,
            textTransform: "uppercase",
            margin: "0 0 20px",
          }}>
            {HERO.eyebrow}
          </p>
          <h1 style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: isMobile ? 38 : 56,
            fontWeight: 700,
            color: COLORS.noir,
            lineHeight: 1.1,
            margin: "0 0 24px",
          }}>
            {HERO.title}
          </h1>
          <Divider />
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: isMobile ? 16 : 18,
            color: COLORS.noirLight,
            lineHeight: 1.7,
            margin: "0 0 40px",
          }}>
            {HERO.subtitle}
          </p>
          <div style={{
            display: "flex",
            gap: 16,
            justifyContent: "center",
            flexDirection: isMobile ? "column" : "row",
          }}>
            <HoverButton
              onClick={() => navigate("quiz")}
              style={{
                background: COLORS.noir,
                color: COLORS.blanc,
                borderRadius: 10,
                padding: "16px 40px",
                fontSize: 15,
                fontWeight: 600,
                letterSpacing: "0.5px",
              }}
            >
              {HERO.cta}
            </HoverButton>
            <HoverButton
              onClick={() => navigate("histoire")}
              hoverBg={COLORS.cremeDark}
              style={{
                background: "transparent",
                color: COLORS.noir,
                border: `1.5px solid ${COLORS.cremeDark}`,
                borderRadius: 10,
                padding: "16px 32px",
                fontSize: 15,
                fontWeight: 500,
              }}
            >
              {HERO.ctaSecondary}
            </HoverButton>
          </div>
        </div>
      </section>

      {/* ── PROMESSES MARQUE ── */}
      <section style={{
        padding: isMobile ? "48px 16px" : "80px 24px",
        maxWidth: 1100,
        margin: "0 auto",
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
          gap: 20,
        }}>
          {BRAND_PROMISES.map((item) => (
            <Card key={item.title} maxWidth="100%" style={{ padding: "36px 28px", textAlign: "center" }}>
              <span style={{ fontSize: 40, display: "block", marginBottom: 16 }}>{item.icon}</span>
              <h3 style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: 22,
                fontWeight: 700,
                color: COLORS.noir,
                margin: "0 0 12px",
              }}>
                {item.title}
              </h3>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 14,
                color: COLORS.gris,
                lineHeight: 1.65,
                margin: 0,
              }}>
                {item.text}
              </p>
            </Card>
          ))}
        </div>
      </section>

      {/* ── PRODUIT PHARE ── */}
      <section style={{
        padding: isMobile ? "48px 16px" : "80px 24px",
        background: COLORS.blanc,
      }}>
        <div style={{
          maxWidth: 720,
          margin: "0 auto",
          textAlign: "center",
        }}>
          <SectionTitle
            eyebrow="Produit signature"
            title={PRODUCT_HIGHLIGHT.name}
          />
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 16,
            color: COLORS.noirLight,
            lineHeight: 1.7,
            margin: "0 0 28px",
            fontStyle: "italic",
          }}>
            {PRODUCT_HIGHLIGHT.description}
          </p>
          <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
            {PRODUCT_HIGHLIGHT.badges.map((badge) => (
              <span key={badge} style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 12,
                fontWeight: 600,
                color: COLORS.or,
                background: `${COLORS.or}12`,
                padding: "8px 18px",
                borderRadius: 999,
                letterSpacing: "0.5px",
              }}>
                {badge}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── QUIZ CTA ── */}
      <section style={{
        background: COLORS.noir,
        padding: isMobile ? "60px 20px" : "80px 24px",
        textAlign: "center",
      }}>
        <SectionTitle
          title={QUIZ_CTA.title}
          subtitle={QUIZ_CTA.subtitle}
          light
        />
        <HoverButton
          onClick={() => navigate("quiz")}
          hoverBg={COLORS.noirLight}
          style={{
            background: COLORS.rouge,
            color: COLORS.blanc,
            borderRadius: 10,
            padding: "18px 48px",
            fontSize: 16,
            fontWeight: 600,
            letterSpacing: "0.5px",
            marginTop: 8,
          }}
        >
          {QUIZ_CTA.cta}
        </HoverButton>
      </section>

      {/* ── PREVIEW PROFILS ── */}
      <section style={{
        padding: isMobile ? "48px 16px" : "80px 24px",
        maxWidth: 1100,
        margin: "0 auto",
      }}>
        <SectionTitle
          eyebrow="5 profils gourmands"
          title="Lequel etes-vous ?"
          subtitle="Decouvrez les identites gourmandes identifiees par La Francaise des Sauces."
        />
        <div style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "repeat(2, 1fr)" : "repeat(5, 1fr)",
          gap: 16,
        }}>
          {Object.entries(PROFILES).map(([key, profile]) => (
            <a
              key={key}
              href="#profils"
              style={{
                background: COLORS.blanc,
                borderRadius: 16,
                padding: "28px 16px",
                textAlign: "center",
                textDecoration: "none",
                boxShadow: "0 4px 16px rgba(10,9,8,0.05)",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-4px)";
                e.currentTarget.style.boxShadow = "0 8px 28px rgba(10,9,8,0.1)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 4px 16px rgba(10,9,8,0.05)";
              }}
            >
              <div style={{
                width: 64,
                height: 64,
                borderRadius: "50%",
                border: `2px solid ${profile.color}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 12px",
                background: COLORS.creme,
              }}>
                <span style={{ fontSize: 28 }}>{profile.emoji}</span>
              </div>
              <p style={{
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: 15,
                fontWeight: 700,
                color: profile.color,
                margin: 0,
                lineHeight: 1.3,
              }}>
                {profile.name}
              </p>
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
