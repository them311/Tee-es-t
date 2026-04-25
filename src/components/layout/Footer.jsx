import { COLORS } from "../../data/quizData";
import { useIsMobile } from "../../utils/styles";
import { FOOTER } from "../../data/siteContent";
import AccentBar from "../shared/AccentBar";

const NAV_LINKS = [
  { label: "Accueil", route: "accueil" },
  { label: "Le Quiz", route: "quiz" },
  { label: "Nos Profils", route: "profils" },
  { label: "Notre Histoire", route: "histoire" },
  { label: "Contact", route: "contact" },
];

export default function Footer() {
  const isMobile = useIsMobile();

  return (
    <footer style={{ background: COLORS.noir }}>
      <AccentBar height={4} />
      <div style={{
        maxWidth: 1100,
        margin: "0 auto",
        padding: isMobile ? "40px 24px" : "60px 24px",
        display: "flex",
        flexDirection: isMobile ? "column" : "row",
        gap: isMobile ? 32 : 60,
      }}>
        {/* Brand */}
        <div style={{ flex: 1 }}>
          <p style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 22,
            fontWeight: 700,
            color: COLORS.blanc,
            margin: "0 0 12px",
          }}>
            {FOOTER.brand}
          </p>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14,
            color: COLORS.gris,
            lineHeight: 1.6,
            margin: 0,
          }}>
            {FOOTER.tagline}
          </p>
        </div>

        {/* Navigation */}
        <div>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 11,
            letterSpacing: "2px",
            textTransform: "uppercase",
            color: COLORS.or,
            fontWeight: 600,
            margin: "0 0 16px",
          }}>
            Navigation
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {NAV_LINKS.map((link) => (
              <a
                key={link.route}
                href={`#${link.route}`}
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 14,
                  color: COLORS.cremeDark,
                  textDecoration: "none",
                }}
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>

        {/* Legal */}
        <div>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 11,
            letterSpacing: "2px",
            textTransform: "uppercase",
            color: COLORS.or,
            fontWeight: 600,
            margin: "0 0 16px",
          }}>
            Informations
          </p>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 13,
            color: COLORS.gris,
            lineHeight: 1.8,
            margin: 0,
          }}>
            {FOOTER.legal}
            <br />
            &copy; {new Date().getFullYear()} La Francaise des Sauces
          </p>
        </div>
      </div>
    </footer>
  );
}
