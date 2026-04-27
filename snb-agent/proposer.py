"""SNB Mission Hunter — Generation de propositions structurees (packaging complet) via Claude API.
NE JAMAIS mentionner S&B Consulting dans les propositions.

Chaque proposition est un PACKAGING complet : analyse besoin, phases, livrables,
timeline, prix, resultat attendu — pour faciliter la decision du client.
"""

import json
import logging
import re
from typing import Optional, Dict, Any
import anthropic
from models import RawMission, Proposal
from profile import PROFILE

logger = logging.getLogger("snb.proposer")


PACKAGING_PROMPT_FR = """Tu es {name}, consultant freelance independant base a Toulouse.

PROFIL :
{bio}

COMPETENCES CLES : {skills}
TARIFS : TJM {tjm} EUR/jour HT — Forfait disponible
LANGUES : Francais natif, Anglais courant, Espagnol courant
DISPONIBILITE : Immediate, 100% remote ou hybride

MISSION CLIENT :
Titre : {title}
Source : {source}
Type detecte : {mission_type}
Description : {description}

INSTRUCTIONS :
Genere un PACKAGING complet de proposition au format JSON strict, structure pour faciliter la decision du client. Le packaging doit montrer une comprehension precise du besoin, une approche professionnelle, et un cadre clair (phases, livrables, prix, resultat).

Retourne UNIQUEMENT un objet JSON valide avec cette structure exacte :
{{
  "intro": "1-2 phrases d'accroche montrant que tu as compris le besoin reel du client",
  "comprehension": "Reformulation du besoin client en 2-3 phrases (ce que tu as compris de leur enjeu)",
  "approach": "Approche methodologique en 2-3 phrases (comment tu vas y aller)",
  "phases": [
    {{"name": "Phase 1 - Cadrage & analyse", "duration": "1 semaine", "tasks": ["tache 1", "tache 2"], "deliverable": "Livrable de cette phase"}},
    {{"name": "Phase 2 - Developpement", "duration": "X semaines", "tasks": ["..."], "deliverable": "..."}},
    {{"name": "Phase 3 - Livraison & accompagnement", "duration": "...", "tasks": ["..."], "deliverable": "..."}}
  ],
  "timeline": "Duree totale estimee",
  "deliverables": ["Livrable final 1", "Livrable final 2", "Livrable final 3"],
  "expected_outcome": "Resultat optimal attendu pour le client en 1-2 phrases concretes",
  "pricing": {{"model": "forfait OU regie OU mixte", "amount": "Montant ou fourchette en EUR HT", "payment": "30% commande / 70% livraison ou autre"}},
  "next_step": "Proposition concrete pour la suite (RDV de cadrage 30 min, demo, etc.)",
  "signature": "Baptiste Thevenot, Consultant Web & IA"
}}

REGLES STRICTES :
- JAMAIS mentionner "S&B Consulting" ni "S&B"
- Adapter le contenu au type de mission ({mission_type})
- Etre concret, pas de bla-bla, pas de jargon inutile
- Phases adaptees a la complexite reelle (pas forcement 3 phases — peut etre 2 ou 4)
- Tarification realiste basee sur TJM 450 EUR/jour
- JSON strict valide, pas de texte avant/apres"""


PACKAGING_PROMPT_EN = """You are {name}, a freelance consultant based in Toulouse, France.

PROFILE:
{bio}

KEY SKILLS: {skills}
RATES: {tjm} EUR/day — Fixed-price available
LANGUAGES: French native, English fluent, Spanish fluent
AVAILABILITY: Immediate, 100% remote or hybrid

CLIENT MISSION:
Title: {title}
Source: {source}
Detected type: {mission_type}
Description: {description}

INSTRUCTIONS:
Generate a complete PROPOSAL PACKAGE in strict JSON format, structured to help the client make their decision. The package must show precise understanding of the need, a professional approach, and a clear framework (phases, deliverables, pricing, outcome).

Return ONLY a valid JSON object with this exact structure:
{{
  "intro": "1-2 hook sentences showing you understood the client's real need",
  "comprehension": "Reformulation of the client's need in 2-3 sentences",
  "approach": "Methodological approach in 2-3 sentences",
  "phases": [
    {{"name": "Phase 1 - Discovery & analysis", "duration": "1 week", "tasks": ["task 1", "task 2"], "deliverable": "Phase deliverable"}},
    {{"name": "Phase 2 - Development", "duration": "X weeks", "tasks": ["..."], "deliverable": "..."}},
    {{"name": "Phase 3 - Delivery & support", "duration": "...", "tasks": ["..."], "deliverable": "..."}}
  ],
  "timeline": "Total estimated duration",
  "deliverables": ["Final deliverable 1", "Final deliverable 2", "Final deliverable 3"],
  "expected_outcome": "Optimal outcome for the client in 1-2 concrete sentences",
  "pricing": {{"model": "fixed-price OR daily-rate OR mixed", "amount": "Amount or range in EUR", "payment": "30% upfront / 70% on delivery or other"}},
  "next_step": "Concrete next step proposal (30 min discovery call, demo, etc.)",
  "signature": "Baptiste Thevenot, Web & AI Consultant"
}}

STRICT RULES:
- NEVER mention "S&B Consulting" or "S&B"
- Adapt content to mission type ({mission_type})
- Be concrete, no fluff, no useless jargon
- Phases adapted to actual complexity (not necessarily 3 — could be 2 or 4)
- Realistic pricing based on EUR 450/day rate
- Valid strict JSON, no text before/after"""


class Proposer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, mission: RawMission, mission_type: str = "other", **kwargs) -> Optional[Proposal]:
        """Generate a structured packaging proposal."""
        text_sample = f"{mission.title} {(mission.description or '')[:200]}"
        lang = self._detect_language(text_sample)

        prompt_template = PACKAGING_PROMPT_FR if lang == "fr" else PACKAGING_PROMPT_EN
        prompt = prompt_template.format(
            name=PROFILE["name"],
            bio=PROFILE["bio_full"],
            skills=", ".join(PROFILE["skills_primary"][:6]),
            tjm=PROFILE["tjm"],
            title=mission.title,
            description=(mission.description or "")[:2000],
            source=mission.source,
            mission_type=mission_type,
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text.strip()
            raw_text = raw_text.replace("S&B Consulting", "").replace("S&B", "")

            # Extract JSON (sometimes Claude wraps in ```json ... ```)
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not json_match:
                logger.error(f"No JSON found in response for {mission.title[:40]}")
                return None

            try:
                package = json.loads(json_match.group(0))
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error for {mission.title[:40]}: {e}")
                return None

            # Generate human-readable text version too
            text = self._render_text(package, lang)

            return Proposal(
                mission_id="",
                text=text,
                language=lang,
                template_used=f"packaging_v3_{mission_type}",
                status="ready",
            )
        except Exception as e:
            logger.error(f"Erreur generation proposition: {e}")
            return None

    @staticmethod
    def _render_text(pkg: Dict[str, Any], lang: str) -> str:
        """Render the JSON package as a structured plain-text proposal."""
        lines = []
        lines.append(pkg.get("intro", ""))
        lines.append("")
        if pkg.get("comprehension"):
            lines.append("VOTRE BESOIN" if lang == "fr" else "YOUR NEED")
            lines.append(pkg["comprehension"])
            lines.append("")
        if pkg.get("approach"):
            lines.append("MON APPROCHE" if lang == "fr" else "MY APPROACH")
            lines.append(pkg["approach"])
            lines.append("")
        if pkg.get("phases"):
            lines.append("PHASES" if lang == "fr" else "PHASES")
            for i, p in enumerate(pkg["phases"], 1):
                lines.append(f"{p.get('name', f'Phase {i}')} — {p.get('duration', '')}")
                for t in p.get("tasks", []):
                    lines.append(f"  - {t}")
                if p.get("deliverable"):
                    lines.append(f"  Livrable: {p['deliverable']}" if lang == "fr" else f"  Deliverable: {p['deliverable']}")
                lines.append("")
        if pkg.get("timeline"):
            lines.append(("DUREE TOTALE: " if lang == "fr" else "TOTAL DURATION: ") + pkg["timeline"])
        if pkg.get("deliverables"):
            lines.append("")
            lines.append("LIVRABLES FINAUX" if lang == "fr" else "FINAL DELIVERABLES")
            for d in pkg["deliverables"]:
                lines.append(f"  - {d}")
        if pkg.get("expected_outcome"):
            lines.append("")
            lines.append("RESULTAT ATTENDU" if lang == "fr" else "EXPECTED OUTCOME")
            lines.append(pkg["expected_outcome"])
        if pkg.get("pricing"):
            lines.append("")
            lines.append("TARIFICATION" if lang == "fr" else "PRICING")
            pr = pkg["pricing"]
            lines.append(f"  Modele: {pr.get('model', '')}")
            lines.append(f"  Montant: {pr.get('amount', '')}")
            lines.append(f"  Paiement: {pr.get('payment', '')}")
        if pkg.get("next_step"):
            lines.append("")
            lines.append("PROCHAINE ETAPE" if lang == "fr" else "NEXT STEP")
            lines.append(pkg["next_step"])
        if pkg.get("signature"):
            lines.append("")
            lines.append(pkg["signature"])

        # Store JSON in a special marker for the dashboard to parse
        text = "\n".join(lines)
        text += f"\n\n<!--PACKAGE_JSON:{json.dumps(pkg, ensure_ascii=False)}-->"
        return text

    @staticmethod
    def _detect_language(text: str) -> str:
        text_lower = text.lower()
        fr = ["developpeur", "developpement", "recherche", "projet", "entreprise", "nous", "besoin", "freelance"]
        en = ["developer", "development", "looking", "project", "company", "need", "team", "freelance"]
        fc = sum(1 for m in fr if m in text_lower)
        ec = sum(1 for m in en if m in text_lower)
        return "en" if ec > fc else "fr"
