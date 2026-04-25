import { useState, useEffect, useCallback } from "react";

const ROUTES = ["accueil", "quiz", "profils", "histoire", "contact"];

function getRoute() {
  const hash = window.location.hash.replace("#", "");
  return ROUTES.includes(hash) ? hash : "accueil";
}

export default function useHashRouter() {
  const [route, setRoute] = useState(getRoute);

  useEffect(() => {
    const onHashChange = () => setRoute(getRoute());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const navigate = useCallback((name) => {
    window.location.hash = name;
  }, []);

  return { route, navigate };
}
