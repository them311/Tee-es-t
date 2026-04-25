import { COLORS } from "../../data/quizData";

export default function Card({ children, style, maxWidth = 560 }) {
  return (
    <div
      style={{
        background: COLORS.blanc,
        borderRadius: 20,
        maxWidth,
        width: "100%",
        boxShadow: "0 12px 48px rgba(10,9,8,0.08)",
        overflow: "hidden",
        ...style,
      }}
    >
      {children}
    </div>
  );
}
