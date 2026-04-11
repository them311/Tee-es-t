"""Autonomous Commercial Agent — runs unattended on a schedule.

This script performs a full morning routine:
1. Check unread emails → identify real prospects → draft responses
2. Check HubSpot tasks due today
3. Follow up on stale prospects
4. Log activity summary
"""

import os
import json
import logging
from datetime import datetime, timezone

import anthropic
from dotenv import load_dotenv

from config.system_prompt import get_system_prompt
from tools import ALL_TOOLS, execute_tool

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("commercial-agent")

ROUTINES = {
    "morning": """Effectue la routine du matin :

1. EMAILS : Utilise gmail_search_messages pour chercher les emails non-lus (is:unread) recus dans les dernieres 24h.
   - Ignore les newsletters, spam, notifications automatiques (Uber, Bolt, Apple, Indeed, Nickel, Adobe, etc.)
   - Pour chaque email d'un vrai prospect ou client : lis le thread complet avec gmail_read_thread.

2. QUALIFICATION : Pour chaque nouveau prospect identifie :
   - Evalue le score BANT (Budget, Autorite, Besoin, Timing) sur 100 points.
   - Cherche/cree le contact dans HubSpot.
   - Ajoute une note HubSpot avec le detail du score : "BANT: B=X A=X N=X T=X | Total=XX/100"
   - Mets a jour hs_lead_status selon le score (>= 70: IN_PROGRESS, 40-69: OPEN, < 40: NEW).

3. REPONSES ADAPTEES AU SCORE :
   - Score >= 70 (CHAUD) : Genere un devis detaille (livrables_create_devis avec bant_score) + proposition si projet complexe (livrables_create_proposition). Utilise le template email "Prospect CHAUD". Mentionne la validite limitee (15 jours).
   - Score 40-69 (TIEDE) : Utilise le template email "Prospect TIEDE" avec questions de qualification. Genere une proposition legere SANS pricing detaille si pertinent.
   - Score < 40 (FROID) : Utilise le template email "Prospect FROID" — email de decouverte uniquement. PAS de devis ni proposition.
   - Cree un brouillon Gmail adapte (gmail_create_draft).

4. SUIVI REPONSES : Verifie les reponses aux propositions/devis envoyes precedemment.
   - Si un prospect a repondu positivement → livrables_update_status avec status "responded" ou "negotiating".
   - Si un prospect a decline → livrables_update_status avec status "lost" et la raison (budget, timing, concurrent, silence).

5. CRM : Verifie les contacts IN_PROGRESS et OPEN dont la derniere interaction date de plus de 2 jours.

6. RESUME : Donne un resume structure :
   - Nombre d'emails traites et scores BANT attribues
   - Nombre de brouillons crees (par segment chaud/tiede/froid)
   - Nombre de devis/propositions generes (uniquement pour score >= 40)
   - Conversions detectees (reponses positives, signatures)
   - Actions prioritaires

IMPORTANT : Tu dois TOUJOURS creer des brouillons (gmail_create_draft), JAMAIS envoyer directement. Baptiste validera ensuite.""",

    "followup": """Effectue la routine de relance intelligente :

1. TRACKING : Utilise livrables_list pour voir tous les livrables en cours.
   - Pour chaque livrable avec statut "sent", verifie dans Gmail si le prospect a repondu.
   - Mets a jour le statut via livrables_update_status (responded, won, lost, etc.).

2. RELANCES PAR SEGMENT :
   Cherche dans HubSpot les contacts OPEN et IN_PROGRESS. Pour chacun :

   a) Prospects CHAUDS (notes BANT >= 70 ou hs_lead_status = IN_PROGRESS) :
      - Relance a J+2 si pas de reponse. Template : rappel de la proposition + deadline de validite.
      - Relance a J+5 : partage d'un cas client similaire ou resultat concret.
      - Relance a J+10 : "derniere relance" — pas insistant, porte ouverte.
      - Apres 3 relances : marquer ATTEMPTED_TO_REACH + livrables_update_status status="lost" lost_reason="silence"

   b) Prospects TIEDES (notes BANT 40-69 ou hs_lead_status = OPEN) :
      - Relance a J+4 : apport de valeur (cas client, article, conseil).
      - Relance a J+8 : proposition de call de 15 min.
      - Relance a J+14 : derniere relance.
      - Apres 3 relances : marquer ATTEMPTED_TO_REACH.

   c) Prospects FROIDS (notes BANT < 40) :
      - Relance a J+7 uniquement : email de valeur (pas de proposition commerciale).
      - Si pas de reponse : marquer ATTEMPTED_TO_REACH. Pas de 2eme relance.

3. CHAQUE RELANCE DOIT :
   - Apporter de la VALEUR (cas client, conseil, ressource) — jamais un simple "je relance".
   - Utiliser livrables_update_status avec followup_increment=true pour tracker le nombre de relances.
   - Mentionner les livrables existants et leur date de validite si pertinent.

4. RESUME : Actions effectuees, relances envoyees par segment, conversions detectees.""",

    "weekly_audit": """Effectue l'audit hebdomadaire du CRM et du pipeline de conversion :

1. CRM : Liste tous les contacts actifs (hs_lead_status != UNQUALIFIED).
   Identifie :
   - Contacts sans activite depuis plus de 7 jours
   - Deals sans montant defini
   - Contacts sans email
   - Doublons potentiels

2. CONVERSION REPORT : Utilise livrables_conversion_report pour obtenir les KPIs de conversion.
   Analyse :
   - Taux de reponse et taux de conversion global
   - Performance par segment BANT (chaud/tiede/froid)
   - Raisons de perte principales
   - CA signe vs pipeline en cours

3. RECOMMANDATIONS : Base-toi sur le rapport de conversion pour proposer des ajustements :
   - Si taux de conversion des chauds < 50% : le probleme est dans la proposition de valeur ou le pricing.
   - Si taux de reponse < 30% : le probleme est dans le ciblage ou la qualite des emails.
   - Si la raison de perte principale est "budget" : proposer des offres plus modulaires.
   - Si la raison de perte principale est "timing" : mettre en place des relances longues (30/60/90 jours).
   - Si la raison de perte principale est "concurrent" : renforcer la preuve sociale.

4. ACTIONS CORRECTIVES :
   - Pour chaque probleme identifie, propose une action concrete.
   - Mets a jour les contacts CRM si necessaire.

5. RAPPORT FINAL avec KPIs :
   - Contacts actifs et repartition par statut
   - Deals en cours et valeur totale
   - Taux de conversion par segment
   - CA signe cette semaine vs objectif
   - Top 3 actions prioritaires pour la semaine prochaine""",
}


def run_autonomous(routine: str) -> str:
    """Run an autonomous routine."""
    if routine not in ROUTINES:
        log.error(f"Unknown routine: {routine}. Available: {list(ROUTINES.keys())}")
        return f"Error: unknown routine '{routine}'"

    prompt = ROUTINES[routine]
    log.info(f"Starting routine: {routine}")

    client = anthropic.Anthropic()
    system_prompt = get_system_prompt()

    messages = [{"role": "user", "content": prompt}]

    max_iterations = 25
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        log.info(f"  Iteration {iteration}/{max_iterations}")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=16000,
                system=system_prompt,
                tools=ALL_TOOLS,
                messages=messages,
            )
        except Exception as e:
            log.error(f"  API error: {e}")
            return f"API Error: {e}"

        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            log.info(f"Routine '{routine}' completed in {iteration} iterations")
            log.info(f"Result:\n{final_text[:500]}")
            return final_text

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        for block in text_blocks:
            if block.text.strip():
                log.info(f"  Agent: {block.text[:200]}")

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool in tool_use_blocks:
            log.info(f"  Tool: {tool.name}")
            try:
                result = execute_tool(tool.name, tool.input)
                if len(result) > 5000:
                    result = result[:5000] + "... (truncated)"
            except Exception as e:
                result = f"Error: {e}"
                log.error(f"  Tool error: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    log.warning(f"Routine '{routine}' hit max iterations ({max_iterations})")
    return "Agent stopped: maximum iterations reached."


def main():
    """Entry point — determines which routine to run based on args or time."""
    import sys

    if len(sys.argv) > 1:
        routine = sys.argv[1]
    else:
        # Auto-select based on time of day
        hour = datetime.now().hour
        weekday = datetime.now().weekday()

        if weekday == 4 and hour >= 16:  # Friday afternoon
            routine = "weekly_audit"
        elif hour < 12:
            routine = "morning"
        else:
            routine = "followup"

    log.info(f"=== AUTONOMOUS AGENT — {routine.upper()} — {datetime.now().isoformat()} ===")
    result = run_autonomous(routine)

    # Save report
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(
        report_dir,
        f"{routine}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
    )
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"=== {routine.upper()} — {datetime.now().isoformat()} ===\n\n")
        f.write(result)

    log.info(f"Report saved: {report_file}")


if __name__ == "__main__":
    main()
