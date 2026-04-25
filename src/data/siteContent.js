export const HERO = {
  eyebrow: "LA FRANCAISE DES SAUCES",
  title: "L'art de la sauce, reinvente",
  subtitle:
    "70% d'ingredients francais. Sans additifs ni conservateurs. Des sauces qui elevent chaque plat.",
  cta: "Decouvrir mon profil",
  ctaSecondary: "Notre histoire",
};

export const BRAND_PROMISES = [
  {
    icon: "🌿",
    title: "Ingredients nobles",
    text: "70% d'ingredients d'origine francaise, selectionnes pour leur qualite et leur gout authentique.",
  },
  {
    icon: "🇫🇷",
    title: "Savoir-faire francais",
    text: "Un heritage culinaire transmis de generation en generation, reinvente avec passion.",
  },
  {
    icon: "✨",
    title: "Zero compromis",
    text: "Sans additifs, sans conservateurs, sans colorants. Que du bon, rien que du bon.",
  },
];

export const PRODUCT_HIGHLIGHT = {
  name: "Sauce Beurre & Herbes Fraiches",
  description:
    "Notre sauce signature. Un beurre onctueux releve d'herbes fraiches cueillies en France. Elle transforme n'importe quel plat du quotidien en moment d'exception.",
  badges: ["100% naturelle", "Prete en 2 min", "Made in France"],
};

export const QUIZ_CTA = {
  title: "Quel epicurien etes-vous ?",
  subtitle: "8 questions — 2 minutes — un profil qui vous ressemble.",
  cta: "Commencer le quiz",
};

export const HISTORY = {
  title: "Notre Histoire",
  sections: [
    {
      title: "L'heritage francais",
      text: "La France est le berceau de la gastronomie mondiale. Nos sauces perpetuent cette tradition d'excellence, en mariant les recettes classiques aux attentes d'aujourd'hui.",
    },
    {
      title: "Notre engagement",
      text: "Chaque pot contient au minimum 70% d'ingredients francais. Nous travaillons en circuit court avec des producteurs locaux pour garantir fraicheur et tracabilite.",
    },
    {
      title: "Le savoir-faire",
      text: "Nos recettes sont elaborees par des chefs passionnes. Chaque sauce est cuite lentement, en petits lots, pour preserver toute la richesse des saveurs.",
    },
    {
      title: "Notre promesse",
      text: "Zero additif, zero conservateur, zero colorant. Nous prouvons chaque jour qu'une sauce d'exception peut etre simple, saine et accessible.",
    },
  ],
  stats: [
    { value: "70%", label: "Ingredients francais" },
    { value: "0", label: "Additifs" },
    { value: "5", label: "Profils gourmands" },
  ],
};

export const CONTACT = {
  title: "Contactez-nous",
  subtitle:
    "Une question, une suggestion, un partenariat ? Nous sommes a votre ecoute.",
  email: "contact@l-fds.com",
  fields: [
    { id: "name", label: "Votre nom", type: "text", placeholder: "Jean Dupont" },
    { id: "email", label: "Votre email", type: "email", placeholder: "jean@exemple.fr" },
    {
      id: "subject",
      label: "Sujet",
      type: "select",
      options: [
        "Question sur nos produits",
        "Partenariat / distribution",
        "Presse / media",
        "Autre",
      ],
    },
    { id: "message", label: "Message", type: "textarea", placeholder: "Votre message..." },
  ],
};

export const FOOTER = {
  brand: "La Francaise des Sauces",
  tagline: "70% d'ingredients francais, sans additifs ni conservateurs.",
  legal: "Conforme RGPD · Donnees hebergees en France",
};
