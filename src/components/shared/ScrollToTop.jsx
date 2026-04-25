import { useEffect } from "react";

export default function ScrollToTop({ route }) {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [route]);
  return null;
}
