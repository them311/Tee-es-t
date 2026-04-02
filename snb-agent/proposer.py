"""SNB Mission Hunter — Generation de propositions via Claude API.
NE JAMAIS mentionner S&B Consulting dans les propositions.
"""

import logging
from typing import Optional
import anthropic
from models import RawMission, Proposal
from profile import PROFILE, get_proposal_prompt

logger = logging.getLogger("snb.proposer")


TEMPLATES = {
    "ia": "Expert en intelligence artificielle et automatisation (Claude API, OpenAI, agents IA, chatbots). Mets l'accent sur tes projets IA : systeme multi-agents, Chef IA, integration Claude API.",
    "web": "Developpeur web fullstack (React.js, Next.js, Shopify, Node.js). Mets l'accent sur tes projets web : La Francaise des Sauces (Shopify), landing pages, UI/UX Figma.",
    "data": "Specialiste data et automatisation (Python, scraping, dashboards, analytics). Mets l'accent sur tes projets data : SNB Mission Hunter, audit cybersecurite, pipelines automatises.",
    "consulting": "Consultant en strategie digitale et transformation (Master 2 TBS, experience internationale). Mets l'accent sur ta formation et ton approche strategique.",
    "design": "Consultant UX/UI et branding (Figma, charte graphique, identite visuelle). Mets l'accent sur tes competences design et tes projets de branding.",
    "other": "Consultant polyvalent Web & IA. Adapte ta proposition au besoin specifique du client.",
}


class Proposer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, mission: RawMission, mission_type: str = "other", **kwargs) -> Optional[Proposal]:
        """Generate a personalized proposal, adapted to mission type."""
        prompt = get_proposal_prompt(
            mission_title=mission.title,
            mission_desc=mission.description or "",
            mission_source=mission.source,
            mission_type=mission_type,
        )

        text_sample = f"{mission.title} {(mission.description or '')[:200]}"
        lang = self._detect_language(text_sample)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            text = text.replace("S&B Consulting", "").replace("S&B", "")

            return Proposal(
                mission_id="",
                text=text,
                language=lang,
                template_used=f"profile_v2_{mission_type}",
                status="ready",
            )
        except Exception as e:
            logger.error(f"Erreur generation proposition: {e}")
            return None

    @staticmethod
    def _detect_language(text: str) -> str:
        text_lower = text.lower()
        fr = ["developpeur", "recherche", "projet", "entreprise", "nous", "besoin"]
        en = ["developer", "looking", "project", "company", "need", "team"]
        fc = sum(1 for m in fr if m in text_lower)
        ec = sum(1 for m in en if m in text_lower)
        return "en" if ec > fc else "fr"
