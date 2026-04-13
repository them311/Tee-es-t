import { NavLink, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Matches from "./pages/Matches";
import Signup from "./pages/Signup";
import Stats from "./pages/Stats";

export default function App() {
  return (
    <>
      <nav className="nav">
        <span className="brand">StudentFlow</span>
        <NavLink to="/" end>
          Accueil
        </NavLink>
        <NavLink to="/signup">Inscription</NavLink>
        <NavLink to="/matches">Mes matches</NavLink>
        <NavLink to="/stats">Stats</NavLink>
        <span className="spacer" />
      </nav>
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/matches" element={<Matches />} />
          <Route path="/matches/:studentId" element={<Matches />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </main>
    </>
  );
}
