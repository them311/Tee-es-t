import { useState } from "react";
import { COLORS } from "../../data/quizData";
import { ACCENT_GRADIENT, useIsMobile } from "../../utils/styles";
import AccentBar from "../shared/AccentBar";

const NAV_ITEMS = [
  { label: "Accueil", route: "accueil" },
  { label: "Le Quiz", route: "quiz" },
  { label: "Nos Profils", route: "profils" },
  { label: "Notre Histoire", route: "histoire" },
  { label: "Contact", route: "contact" },
];

export default function Header({ currentRoute, navigate }) {
  const isMobile = useIsMobile();
  const [menuOpen, setMenuOpen] = useState(false);
  const [hoveredLink, setHoveredLink] = useState(null);

  return (
    <header style={{ position: "sticky", top: 0, zIndex: 100, background: COLORS.blanc }}>
      <AccentBar height={4} />
      <div style={{
        maxWidth: 1100,
        margin: "0 auto",
        padding: "0 24px",
        height: 64,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <a
          href="#accueil"
          style={{
            fontFamily: "'Cormorant Garamond', Georgia, serif",
            fontSize: 20,
            fontWeight: 700,
            color: COLORS.noir,
            textDecoration: "none",
            whiteSpace: "nowrap",
          }}
        >
          La Francaise des Sauces
        </a>

        {isMobile ? (
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu"
            style={{
              background: "none",
              border: "none",
              fontSize: 24,
              cursor: "pointer",
              color: COLORS.noir,
              padding: 8,
            }}
          >
            {menuOpen ? "✕" : "☰"}
          </button>
        ) : (
          <nav style={{ display: "flex", gap: 28, alignItems: "center" }}>
            {NAV_ITEMS.map((item) => {
              const isActive = currentRoute === item.route;
              const isHovered = hoveredLink === item.route;
              return (
                <a
                  key={item.route}
                  href={`#${item.route}`}
                  onMouseEnter={() => setHoveredLink(item.route)}
                  onMouseLeave={() => setHoveredLink(null)}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: 14,
                    fontWeight: isActive ? 600 : 450,
                    color: isActive ? COLORS.noir : COLORS.gris,
                    textDecoration: "none",
                    paddingBottom: 4,
                    borderBottom: isActive
                      ? `2px solid ${COLORS.or}`
                      : isHovered
                        ? `2px solid ${COLORS.cremeDark}`
                        : "2px solid transparent",
                    transition: "all 0.2s ease",
                  }}
                >
                  {item.label}
                </a>
              );
            })}
          </nav>
        )}
      </div>

      {/* Mobile menu */}
      {isMobile && menuOpen && (
        <nav style={{
          background: COLORS.blanc,
          borderTop: `1px solid ${COLORS.cremeDark}`,
          boxShadow: "0 8px 24px rgba(10,9,8,0.08)",
          padding: "16px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 4,
        }}>
          {NAV_ITEMS.map((item) => (
            <a
              key={item.route}
              href={`#${item.route}`}
              onClick={() => setMenuOpen(false)}
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 16,
                fontWeight: currentRoute === item.route ? 600 : 400,
                color: currentRoute === item.route ? COLORS.noir : COLORS.gris,
                textDecoration: "none",
                padding: "12px 0",
                borderBottom: `1px solid ${COLORS.creme}`,
              }}
            >
              {item.label}
            </a>
          ))}
        </nav>
      )}
    </header>
  );
}
