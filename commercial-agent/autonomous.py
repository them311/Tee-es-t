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
   - Pour chaque email d'un vrai prospect ou client : lis le thread complet avec gmail_read_thread, puis cree un brouillon de reponse adapte avec gmail_create_draft.

2. CRM : Utilise hubspot_search_contacts pour lister les contacts avec hs_lead_status = OPEN ou IN_PROGRESS.
   - Pour chaque contact dont la derniere interaction date de plus de 3 jours, prepare un brouillon de relance.

3. TACHES : Utilise hubspot_search_contacts pour verifier s'il y a des taches en retard.

4. RESUME : A la fin, donne un resume structure :
   - Nombre d'emails traites
   - Nombre de brouillons crees
   - Contacts a relancer
   - Actions prioritaires

IMPORTANT : Tu dois TOUJOURS creer des brouillons (gmail_create_draft), JAMAIS envoyer directement. Baptiste validera ensuite.""",

    "followup": """Effectue la routine de relance :

1. Cherche dans HubSpot tous les contacts avec hs_lead_status = OPEN.
2. Pour chacun, verifie dans Gmail s'il y a eu une reponse recente (gmail_search_messages from:email_du_contact).
3. Si pas de reponse depuis plus de 3 jours : cree un brouillon de relance personnalise.
4. Si pas de reponse depuis plus de 7 jours : cree un brouillon de derniere relance.
5. Si pas de reponse depuis plus de 14 jours : mets le statut a ATTEMPTED_TO_REACH dans HubSpot.
6. Resume les actions effectuees.""",

    "weekly_audit": """Effectue l'audit hebdomadaire du CRM :

1. Liste tous les contacts actifs (hs_lead_status != UNQUALIFIED).
2. Identifie :
   - Contacts sans activite depuis plus de 7 jours
   - Deals sans montant defini
   - Contacts sans email
   - Doublons potentiels
3. Pour chaque probleme, propose une action corrective.
4. Genere un rapport complet avec KPIs :
   - Nombre total de contacts actifs
   - Nombre de deals en cours et valeur totale
   - Taux de reponse estime
   - Actions prioritaires pour la semaine""",
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
