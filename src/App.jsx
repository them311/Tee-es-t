import useHashRouter from "./hooks/useHashRouter";
import { GLOBAL_KEYFRAMES } from "./utils/styles";
import Header from "./components/layout/Header";
import Footer from "./components/layout/Footer";
import ScrollToTop from "./components/shared/ScrollToTop";
import HomePage from "./components/pages/HomePage";
import QuizPage from "./components/pages/QuizPage";
import ProfilsPage from "./components/pages/ProfilsPage";
import HistoirePage from "./components/pages/HistoirePage";
import ContactPage from "./components/pages/ContactPage";

const PAGES = {
  accueil: HomePage,
  quiz: QuizPage,
  profils: ProfilsPage,
  histoire: HistoirePage,
  contact: ContactPage,
};

export default function App() {
  const { route, navigate } = useHashRouter();
  const Page = PAGES[route] || HomePage;
  const showLayout = route !== "quiz";

  return (
    <>
      <style>{GLOBAL_KEYFRAMES}</style>
      {showLayout && <Header currentRoute={route} navigate={navigate} />}
      <ScrollToTop route={route} />
      <main>
        <Page navigate={navigate} />
      </main>
      {showLayout && <Footer />}
    </>
  );
}
