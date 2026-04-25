import { COLORS } from "../../data/quizData";

export default function Divider() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, justifyContent: "center", margin: "24px 0" }}>
      <div style={{ height: 1, width: 60, background: COLORS.cremeDark }} />
      <span style={{ color: COLORS.or, fontSize: 12 }}>{"✦"}</span>
      <div style={{ height: 1, width: 60, background: COLORS.cremeDark }} />
    </div>
  );
}
