import { ACCENT_GRADIENT } from "../../utils/styles";

export default function AccentBar({ height = 5 }) {
  return <div style={{ height, background: ACCENT_GRADIENT, width: "100%" }} />;
}
