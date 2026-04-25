import { useState } from "react";
import { COLORS } from "../../data/quizData";

export default function HoverButton({ children, style, onClick, hoverBg = COLORS.noirLight, ...props }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      style={{
        fontFamily: "'DM Sans', sans-serif",
        cursor: "pointer",
        border: "none",
        transition: "all 0.25s ease",
        ...style,
        ...(hovered ? { background: hoverBg, transform: "translateY(-2px)" } : {}),
      }}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      {...props}
    >
      {children}
    </button>
  );
}
