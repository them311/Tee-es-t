import { COLORS } from "../../data/quizData";
import Divider from "./Divider";

export default function SectionTitle({ eyebrow, title, subtitle, light = false }) {
  return (
    <div style={{ textAlign: "center", marginBottom: 48 }}>
      {eyebrow && (
        <p style={{
          fontFamily: "'DM Sans', sans-serif",
          fontSize: 11,
          letterSpacing: "3px",
          color: COLORS.or,
          fontWeight: 600,
          textTransform: "uppercase",
          margin: "0 0 16px",
        }}>
          {eyebrow}
        </p>
      )}
      <h2 style={{
        fontFamily: "'Cormorant Garamond', Georgia, serif",
        fontSize: 40,
        fontWeight: 700,
        color: light ? COLORS.blanc : COLORS.noir,
        lineHeight: 1.15,
        margin: 0,
      }}>
        {title}
      </h2>
      <Divider />
      {subtitle && (
        <p style={{
          fontFamily: "'DM Sans', sans-serif",
          fontSize: 16,
          color: light ? COLORS.cremeDark : COLORS.gris,
          lineHeight: 1.6,
          maxWidth: 540,
          margin: "0 auto",
        }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}
