import { useState, useEffect } from "react";
import { COLORS } from "../data/quizData";

export function useMediaQuery(query) {
  const [matches, setMatches] = useState(() =>
    typeof window !== "undefined" ? window.matchMedia(query).matches : false
  );

  useEffect(() => {
    const mql = window.matchMedia(query);
    const handler = (e) => setMatches(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

export function useIsMobile() {
  return useMediaQuery("(max-width: 768px)");
}

export const ACCENT_GRADIENT = `linear-gradient(90deg, ${COLORS.bleu}, ${COLORS.rouge}, ${COLORS.or})`;

export const GLOBAL_KEYFRAMES = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600&display=swap');

  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  @keyframes barGrow {
    from { width: 0; }
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'DM Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
    color: ${COLORS.noir};
    background: ${COLORS.creme};
  }
  a { color: inherit; text-decoration: none; }
`;

export const sharedStyles = {
  eyebrow: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 11,
    letterSpacing: "3px",
    color: COLORS.or,
    fontWeight: 600,
    textTransform: "uppercase",
  },
  sectionPadding: {
    padding: "80px 24px",
    maxWidth: 1100,
    margin: "0 auto",
  },
  sectionPaddingMobile: {
    padding: "48px 16px",
  },
};
