// ─────────────────────────────────────────────────────────
// QUIZ DATA — La Française des Sauces
// Questions, profils, couleurs et configuration
// ─────────────────────────────────────────────────────────

export const COLORS = {
  noir: "#0A0908",
  creme: "#F8F5EF",
  bleu: "#0055A4",
  rouge: "#EF4135",
  or: "#C4A35A",
  cremeDark: "#EDE8DC",
  noirLight: "#2A2826",
  gris: "#8A8580",
  blanc: "#FFFFFF",
  vertDoux: "#6B8E5A",
  mauve: "#9B6B9E",
};

export const QUESTIONS = [
  {
    id: "cuisine_freq",
    question: "Vous rentrez du travail. Ce soir, c\u2019est\u2026",
    dataLabel: "Fr\u00e9quence cuisine maison",
    category: "habitudes",
    options: [
      { text: "Un plat mijot\u00e9 maison, m\u00eame si \u00e7a prend du temps", value: "quotidien", icon: "\uD83C\uDF72", profile: { artisan: 3, epicurien: 2 } },
      { text: "Quelque chose de rapide mais fait maison", value: "regulier", icon: "\uD83C\uDF73", profile: { pragmatique: 2, curieux: 1 } },
      { text: "Un bon produit tout pr\u00eat, bien choisi", value: "occasionnel", icon: "\uD83D\uDED2", profile: { pragmatique: 3 } },
      { text: "On commande, pas d\u2019inspiration ce soir", value: "rare", icon: "\uD83D\uDCF1", profile: { social: 2 } },
    ],
  },
  {
    id: "critere_achat",
    question: "Au rayon sauces, qu\u2019est-ce qui attire votre \u0153il en premier ?",
    dataLabel: "Crit\u00e8re d\u2019achat dominant",
    category: "achat",
    options: [
      { text: "La liste d\u2019ingr\u00e9dients \u2014 courte et claire", value: "ingredients", icon: "\uD83D\uDD0D", profile: { artisan: 2, epicurien: 2 } },
      { text: "L\u2019origine fran\u00e7aise, le terroir", value: "origine", icon: "\uD83C\uDDEB\uD83C\uDDF7", profile: { epicurien: 3, artisan: 1 } },
      { text: "Le packaging \u2014 s\u2019il est beau, je regarde", value: "packaging", icon: "\u2728", profile: { curieux: 2, social: 1 } },
      { text: "Le prix, soyons honn\u00eates", value: "prix", icon: "\uD83D\uDCB0", profile: { pragmatique: 3 } },
    ],
  },
  {
    id: "decouverte",
    question: "Comment d\u00e9couvrez-vous un nouveau produit alimentaire ?",
    dataLabel: "Canal de d\u00e9couverte",
    category: "marketing",
    options: [
      { text: "Recommandation d\u2019un proche", value: "bouche_a_oreille", icon: "\uD83D\uDCAC", profile: { social: 3 } },
      { text: "R\u00e9seaux sociaux / influenceurs", value: "reseaux", icon: "\uD83D\uDCF2", profile: { curieux: 2, social: 1 } },
      { text: "En magasin, au hasard du rayon", value: "magasin", icon: "\uD83C\uDFEA", profile: { curieux: 3 } },
      { text: "Articles, blogs, \u00e9missions culinaires", value: "media", icon: "\uD83D\uDCF0", profile: { epicurien: 2, artisan: 1 } },
    ],
  },
  {
    id: "reception",
    question: "Vous recevez des amis samedi. Votre approche ?",
    dataLabel: "Comportement r\u00e9ception",
    category: "habitudes",
    options: [
      { text: "Menu \u00e9labor\u00e9, rien n\u2019est laiss\u00e9 au hasard", value: "elabore", icon: "\uD83C\uDFA9", profile: { artisan: 3, epicurien: 1 } },
      { text: "Un beau plat principal et de bons produits autour", value: "equilibre", icon: "\uD83C\uDF7D\uFE0F", profile: { epicurien: 2, pragmatique: 1 } },
      { text: "Ap\u00e9ro d\u00eenatoire \u2014 convivial et sans prise de t\u00eate", value: "convivial", icon: "\uD83E\uDD42", profile: { social: 3 } },
      { text: "Je commande chez un traiteur de qualit\u00e9", value: "traiteur", icon: "\uD83D\uDCE6", profile: { pragmatique: 2, social: 1 } },
    ],
  },
  {
    id: "sauce_usage",
    question: "Une sauce dans un plat, pour vous c\u2019est\u2026",
    dataLabel: "Rapport \u00e0 la sauce",
    category: "produit",
    options: [
      { text: "L\u2019\u00e9l\u00e9ment qui fait toute la diff\u00e9rence", value: "essentiel", icon: "\u2B50", profile: { epicurien: 3, artisan: 1 } },
      { text: "Un plus appr\u00e9ciable quand elle est bonne", value: "important", icon: "\uD83D\uDC4D", profile: { curieux: 2, pragmatique: 1 } },
      { text: "J\u2019en fais moi-m\u00eame la plupart du temps", value: "fait_maison", icon: "\uD83D\uDC68\u200D\uD83C\uDF73", profile: { artisan: 3 } },
      { text: "Pas indispensable, \u00e7a d\u00e9pend du plat", value: "occasionnel", icon: "\uD83E\uDD37", profile: { pragmatique: 2 } },
    ],
  },
  {
    id: "budget",
    question: "Pour un produit alimentaire de qualit\u00e9, vous \u00eates pr\u00eat(e) \u00e0\u2026",
    dataLabel: "Sensibilit\u00e9 prix",
    category: "achat",
    options: [
      { text: "Mettre le prix sans h\u00e9siter si c\u2019est bon", value: "premium", icon: "\uD83D\uDC8E", profile: { epicurien: 3 } },
      { text: "Payer un peu plus cher si \u00e7a se justifie", value: "raisonne", icon: "\u2696\uFE0F", profile: { artisan: 2, curieux: 1 } },
      { text: "Comparer et choisir le meilleur rapport qualit\u00e9-prix", value: "compare", icon: "\uD83D\uDCCA", profile: { pragmatique: 3 } },
      { text: "Craquer de temps en temps pour un produit d\u2019exception", value: "plaisir", icon: "\uD83C\uDF81", profile: { curieux: 2, social: 1 } },
    ],
  },
  {
    id: "valeurs",
    question: "Quelle valeur compte le plus dans votre alimentation ?",
    dataLabel: "Valeur alimentaire prioritaire",
    category: "valeurs",
    options: [
      { text: "Le go\u00fbt avant tout", value: "gout", icon: "\uD83D\uDE0B", profile: { epicurien: 3 } },
      { text: "Le naturel \u2014 pas d\u2019additifs, pas de conservateurs", value: "naturel", icon: "\uD83C\uDF3F", profile: { artisan: 3 } },
      { text: "La praticit\u00e9 au quotidien", value: "praticite", icon: "\u26A1", profile: { pragmatique: 3 } },
      { text: "Le partage et la convivialit\u00e9", value: "partage", icon: "\u2764\uFE0F", profile: { social: 3 } },
    ],
  },
  {
    id: "lieu_achat",
    question: "O\u00f9 faites-vous principalement vos courses alimentaires ?",
    dataLabel: "Canal d\u2019achat",
    category: "achat",
    options: [
      { text: "Grandes surfaces (Carrefour, Leclerc, Auchan\u2026)", value: "gms", icon: "\uD83C\uDFEC", profile: { pragmatique: 2 } },
      { text: "March\u00e9s, producteurs locaux, \u00e9piceries fines", value: "epicerie", icon: "\uD83E\uDDFA", profile: { artisan: 2, epicurien: 2 } },
      { text: "En ligne \u2014 livraison ou drive", value: "online", icon: "\uD83D\uDCBB", profile: { pragmatique: 2, curieux: 1 } },
      { text: "Un mix de tout selon l\u2019envie et le produit", value: "mix", icon: "\uD83D\uDD04", profile: { curieux: 2, social: 1 } },
    ],
  },
];

export const PROFILES = {
  epicurien: {
    name: "L\u2019\u00C9picurien Exigeant",
    emoji: "\uD83C\uDF77",
    color: COLORS.rouge,
    description:
      "Le go\u00fbt est votre boussole. Vous ne transigez pas sur la qualit\u00e9 et savez reconna\u00eetre un produit d\u2019exception au premier regard. Pour vous, bien manger n\u2019est pas un luxe \u2014 c\u2019est un art de vivre.",
    sauce_match:
      "La Sauce Beurre & Herbes Fra\u00eeches by LFDS a \u00e9t\u00e9 con\u00e7ue pour des palais comme le v\u00f4tre : des ingr\u00e9dients nobles, z\u00e9ro compromis.",
    cta_url: "https://l-fds.com/epicurien",
  },
  artisan: {
    name: "L\u2019Artisan du Quotidien",
    emoji: "\uD83D\uDC68\u200D\uD83C\uDF73",
    color: COLORS.bleu,
    description:
      "Vous aimez mettre la main \u00e0 la p\u00e2te et ma\u00eetriser ce que vous mangez. La liste d\u2019ingr\u00e9dients n\u2019a pas de secrets pour vous, et le fait-maison est votre terrain de jeu favori.",
    sauce_match:
      "Avec 70% d\u2019ingr\u00e9dients fran\u00e7ais, sans additifs ni conservateurs, notre sauce parle votre langue : celle de l\u2019authenticit\u00e9.",
    cta_url: "https://l-fds.com/artisan",
  },
  pragmatique: {
    name: "Le Pragmatique Malin",
    emoji: "\u26A1",
    color: COLORS.or,
    description:
      "Vous cherchez l\u2019efficacit\u00e9 sans sacrifier la qualit\u00e9. Votre temps est pr\u00e9cieux et vous savez exactement o\u00f9 mettre votre argent pour un maximum de satisfaction.",
    sauce_match:
      "Un produit pr\u00eat en 2 minutes qui \u00e9l\u00e8ve n\u2019importe quel plat ? C\u2019est exactement ce que LFDS vous propose.",
    cta_url: "https://l-fds.com/pragmatique",
  },
  curieux: {
    name: "Le Curieux Gourmand",
    emoji: "\uD83D\uDD0D",
    color: COLORS.vertDoux,
    description:
      "Toujours \u00e0 l\u2019aff\u00fbt d\u2019une nouvelle saveur, d\u2019un produit qu\u2019on ne conna\u00eet pas encore. Vous aimez sortir des sentiers battus et raconter vos d\u00e9couvertes.",
    sauce_match:
      "LFDS, c\u2019est la p\u00e9pite que vous allez adorer faire d\u00e9couvrir \u00e0 votre entourage.",
    cta_url: "https://l-fds.com/curieux",
  },
  social: {
    name: "Le Convive G\u00e9n\u00e9reux",
    emoji: "\uD83E\uDD42",
    color: COLORS.mauve,
    description:
      "Pour vous, la cuisine est avant tout un moment de partage. Ce qui compte, c\u2019est le sourire autour de la table, et vous savez cr\u00e9er ces moments.",
    sauce_match:
      "Impressionnez vos invit\u00e9s sans effort : LFDS transforme un plat simple en moment m\u00e9morable.",
    cta_url: "https://l-fds.com/social",
  },
};

export const PROFILE_KEYS = Object.keys(PROFILES);
