"""Livrables & Devis — generation automatique de documents commerciaux.

Genere des devis, propositions commerciales et livrables au format HTML/JSON
prets a etre convertis en PDF ou envoyes par email.
"""

import os
import json
import logging
from datetime import datetime, timedelta

log = logging.getLogger("commercial-agent")

# Directory for generated documents
LIVRABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "livrables")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


# --- Templates de devis ---

DEVIS_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; }}
.header {{ display: flex; justify-content: space-between; border-bottom: 3px solid #2c7be5; padding-bottom: 1rem; margin-bottom: 2rem; }}
.header h1 {{ color: #1a2a3a; font-size: 1.5rem; }}
.header .company {{ text-align: right; color: #666; font-size: 0.85rem; }}
.info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }}
.info-box {{ background: #f8f9fa; padding: 1rem; border-radius: 8px; }}
.info-box h3 {{ font-size: 0.8rem; text-transform: uppercase; color: #999; margin-bottom: 0.5rem; }}
table {{ width: 100%; border-collapse: collapse; margin: 1.5rem 0; }}
th {{ background: #1a2a3a; color: white; padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; }}
td {{ padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f8f9fa; }}
.amount {{ text-align: right; font-variant-numeric: tabular-nums; }}
.total-row {{ font-weight: bold; background: #f0f4ff; }}
.total-row td {{ border-top: 2px solid #2c7be5; }}
.footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; font-size: 0.8rem; color: #999; }}
.conditions {{ background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1.5rem; font-size: 0.82rem; }}
.conditions h4 {{ margin-bottom: 0.5rem; color: #1a2a3a; }}
.validity {{ color: #e53e3e; font-weight: 600; }}
.urgency-banner {{ background: linear-gradient(135deg, #ff6b35, #e53e3e); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.9rem; text-align: center; }}
.guarantee {{ background: #f0fff4; border: 1px solid #38a169; padding: 1rem; border-radius: 8px; margin-top: 1.5rem; }}
.guarantee h4 {{ color: #38a169; margin-bottom: 0.5rem; }}
.next-steps {{ background: linear-gradient(135deg, #ebf8ff, #f0f4ff); border: 2px solid #2c7be5; padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; }}
.next-steps h4 {{ color: #2c7be5; margin-bottom: 0.75rem; }}
.next-steps ol {{ margin: 0; padding-left: 1.2rem; }}
.next-steps li {{ margin-bottom: 0.4rem; }}
</style>
</head>
<body>
<div class="header">
    <div>
        <h1>DEVIS N&deg; {numero}</h1>
        <p>Date : {date}</p>
        <p class="validity">Offre valable jusqu'au : {date_validite}</p>
    </div>
    <div class="company">
        <strong>{company_name}</strong><br>
        {company_email}<br>
        {company_phone}
    </div>
</div>
<div class="urgency-banner">
    Tarif garanti jusqu'au {date_validite} — Demarrage possible sous 48h apres validation
</div>
<div class="info-grid">
    <div class="info-box">
        <h3>Emetteur</h3>
        <strong>{company_name}</strong><br>
        {company_email}
    </div>
    <div class="info-box">
        <h3>Client</h3>
        <strong>{client_name}</strong><br>
        {client_company}<br>
        {client_email}
    </div>
</div>
<h3>Objet : {objet}</h3>
<table>
    <thead>
        <tr>
            <th>Description</th>
            <th>Quantite</th>
            <th>Prix unitaire HT</th>
            <th class="amount">Total HT</th>
        </tr>
    </thead>
    <tbody>
        {lignes}
    </tbody>
    <tfoot>
        <tr class="total-row">
            <td colspan="3">Total HT</td>
            <td class="amount">{total_ht} &euro;</td>
        </tr>
        <tr class="total-row">
            <td colspan="3">TVA ({tva_rate}%)</td>
            <td class="amount">{total_tva} &euro;</td>
        </tr>
        <tr class="total-row" style="font-size: 1.1rem;">
            <td colspan="3">Total TTC</td>
            <td class="amount">{total_ttc} &euro;</td>
        </tr>
    </tfoot>
</table>
<div class="guarantee">
    <h4>Garanties incluses</h4>
    <ul>
        <li>Satisfait ou repris : ajustements inclus pendant 30 jours apres livraison</li>
        <li>Interlocuteur unique et dedie tout au long du projet</li>
        <li>Points d'avancement reguliers selon vos preferences</li>
    </ul>
</div>
<div class="conditions">
    <h4>Conditions</h4>
    <ul>
        <li>Paiement : {conditions_paiement}</li>
        <li>Validite de l'offre : {date_validite}</li>
        <li>Delai de realisation : {delai}</li>
    </ul>
</div>
<div class="next-steps">
    <h4>Pour demarrer</h4>
    <ol>
        <li>Repondez a cet email avec votre accord (ou vos questions)</li>
        <li>Nous planifions un appel de cadrage de 30 min</li>
        <li>Demarrage du projet sous 48h</li>
    </ol>
</div>
<div class="footer">
    <p>{company_name} — Proposition confidentielle</p>
</div>
</body>
</html>"""

PROPOSITION_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; }}
.cover {{ background: linear-gradient(135deg, #1a2a3a, #2c3e50); color: white; padding: 3rem; border-radius: 12px; margin-bottom: 2rem; }}
.cover h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
.cover p {{ opacity: 0.8; }}
.cover .meta {{ margin-top: 1.5rem; font-size: 0.85rem; opacity: 0.7; }}
section {{ margin: 2rem 0; }}
section h2 {{ color: #1a2a3a; border-bottom: 2px solid #2c7be5; padding-bottom: 0.5rem; margin-bottom: 1rem; }}
.highlight {{ background: #f0f4ff; border-left: 4px solid #2c7be5; padding: 1rem 1.5rem; border-radius: 0 8px 8px 0; margin: 1rem 0; }}
.pain-point {{ background: #fff5f5; border-left: 4px solid #e53e3e; padding: 1rem 1.5rem; border-radius: 0 8px 8px 0; margin: 1rem 0; }}
.solution {{ background: #f0fff4; border-left: 4px solid #38a169; padding: 1rem 1.5rem; border-radius: 0 8px 8px 0; margin: 1rem 0; }}
.testimonial {{ background: #f7fafc; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; font-style: italic; position: relative; }}
.testimonial::before {{ content: open-quote; font-size: 3rem; color: #2c7be5; position: absolute; top: -0.2rem; left: 0.75rem; }}
.testimonial .author {{ font-style: normal; font-weight: 600; color: #2c7be5; margin-top: 0.75rem; font-size: 0.9rem; }}
.deliverables {{ list-style: none; padding: 0; }}
.deliverables li {{ padding: 0.75rem 1rem; border-bottom: 1px solid #eee; display: flex; align-items: flex-start; gap: 0.75rem; }}
.deliverables li::before {{ content: "✓"; color: #2c7be5; font-weight: bold; flex-shrink: 0; }}
.pricing {{ background: #f8f9fa; padding: 1.5rem; border-radius: 12px; }}
.pricing table {{ width: 100%; border-collapse: collapse; }}
.pricing th {{ text-align: left; padding: 0.5rem; color: #666; font-size: 0.8rem; text-transform: uppercase; }}
.pricing td {{ padding: 0.5rem; border-bottom: 1px solid #eee; }}
.pricing .total {{ font-weight: bold; font-size: 1.2rem; color: #1a2a3a; }}
.roi-box {{ background: linear-gradient(135deg, #ebf8ff, #f0fff4); border: 2px solid #38a169; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; text-align: center; }}
.roi-box h3 {{ color: #38a169; margin-bottom: 0.5rem; }}
.roi-box .roi-value {{ font-size: 1.8rem; font-weight: bold; color: #1a2a3a; }}
.urgency-strip {{ background: linear-gradient(135deg, #ff6b35, #e53e3e); color: white; padding: 0.75rem 1.5rem; border-radius: 8px; margin: 1.5rem 0; text-align: center; font-weight: 600; }}
.cta-block {{ background: linear-gradient(135deg, #2c7be5, #1a56a8); color: white; padding: 2rem; border-radius: 12px; margin: 2rem 0; text-align: center; }}
.cta-block h3 {{ font-size: 1.3rem; margin-bottom: 1rem; }}
.cta-block .steps {{ text-align: left; max-width: 400px; margin: 0 auto; }}
.cta-block .steps li {{ margin-bottom: 0.5rem; opacity: 0.95; }}
.cta-block .cta-email {{ display: inline-block; background: white; color: #2c7be5; padding: 0.75rem 2rem; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 1rem; font-size: 1.1rem; }}
.footer {{ margin-top: 3rem; text-align: center; color: #999; font-size: 0.8rem; }}
</style>
</head>
<body>
<div class="cover">
    <h1>{titre}</h1>
    <p>{sous_titre}</p>
    <div class="meta">
        Proposition pour <strong>{client_name}</strong> | {date} | Ref: {reference}
    </div>
</div>
<section>
    <h2>Votre situation</h2>
    <div class="pain-point">
        <p>{contexte}</p>
    </div>
</section>
<section>
    <h2>Notre reponse</h2>
    <div class="solution">
        <p>{approche}</p>
    </div>
</section>
{social_proof_html}
<section>
    <h2>Ce que vous obtenez</h2>
    <ul class="deliverables">
        {livrables_html}
    </ul>
</section>
<section>
    <h2>Planning previsionnel</h2>
    {planning_html}
</section>
<section>
    <h2>Investissement</h2>
    <div class="pricing">
        <table>
            {pricing_html}
        </table>
    </div>
    {roi_html}
</section>
<div class="urgency-strip">
    Conditions tarifaires garanties jusqu'au {date_validite}
</div>
<div class="cta-block">
    <h3>Prochaines etapes</h3>
    <p>{prochaines_etapes}</p>
    <ol class="steps">
        <li>Repondez a cet email avec votre accord</li>
        <li>Appel de cadrage de 30 min pour affiner les details</li>
        <li>Demarrage du projet sous 48h</li>
    </ol>
    <a href="mailto:{company_email}" class="cta-email">Repondre maintenant</a>
</div>
<div class="footer">
    <p>{company_name} — Proposition commerciale confidentielle</p>
    <p>{company_email}</p>
</div>
</body>
</html>"""


# --- Tool definitions ---

LIVRABLES_TOOLS = [
    {
        "name": "livrables_create_devis",
        "description": "Generer un devis professionnel au format HTML avec urgence, garanties et CTA clair. IMPORTANT: Ne generer que pour les prospects qualifies (score BANT >= 70). Le fichier est sauve dans le dossier livrables/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Nom du client"},
                "client_company": {"type": "string", "description": "Entreprise du client"},
                "client_email": {"type": "string", "description": "Email du client"},
                "objet": {"type": "string", "description": "Objet du devis (ex: 'Developpement application web')"},
                "lignes": {
                    "type": "array",
                    "description": "Lignes du devis",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Description de la prestation"},
                            "quantite": {"type": "number", "description": "Quantite (jours, heures, unites)"},
                            "prix_unitaire": {"type": "number", "description": "Prix unitaire HT en euros"},
                        },
                        "required": ["description", "quantite", "prix_unitaire"],
                    },
                },
                "conditions_paiement": {
                    "type": "string",
                    "description": "Conditions de paiement (ex: '50% a la commande, 50% a la livraison')",
                    "default": "50% a la commande, 50% a la livraison",
                },
                "delai": {
                    "type": "string",
                    "description": "Delai de realisation (ex: '4 semaines', '2 mois')",
                    "default": "A definir lors du cadrage",
                },
                "tva_rate": {
                    "type": "number",
                    "description": "Taux de TVA en pourcentage (defaut: 20)",
                    "default": 20,
                },
                "bant_score": {
                    "type": "number",
                    "description": "Score BANT du prospect (0-100). Requis pour le tracking de conversion.",
                },
                "validity_days": {
                    "type": "number",
                    "description": "Nombre de jours de validite du devis (defaut: 15 pour creer de l'urgence)",
                    "default": 15,
                },
            },
            "required": ["client_name", "client_email", "objet", "lignes"],
        },
    },
    {
        "name": "livrables_create_proposition",
        "description": "Generer une proposition commerciale complete au format HTML avec preuve sociale, ROI, urgence et CTA fort. Inclut contexte, approche, livrables detailles, planning et pricing. Le fichier est sauve dans le dossier livrables/.",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Nom du client ou de l'entreprise"},
                "titre": {"type": "string", "description": "Titre de la proposition (ex: 'Refonte du site e-commerce')"},
                "sous_titre": {"type": "string", "description": "Sous-titre ou accroche orientee resultat"},
                "contexte": {"type": "string", "description": "Description du probleme CONCRET du client et son impact (chiffre si possible)"},
                "approche": {"type": "string", "description": "Description de la solution proposee et pourquoi elle repond au probleme"},
                "livrables": {
                    "type": "array",
                    "description": "Liste des livrables avec description",
                    "items": {
                        "type": "object",
                        "properties": {
                            "titre": {"type": "string", "description": "Nom du livrable"},
                            "description": {"type": "string", "description": "Description detaillee orientee benefice client"},
                        },
                        "required": ["titre"],
                    },
                },
                "planning": {
                    "type": "array",
                    "description": "Phases du planning avec durees",
                    "items": {
                        "type": "object",
                        "properties": {
                            "phase": {"type": "string", "description": "Nom de la phase"},
                            "duree": {"type": "string", "description": "Duree estimee"},
                            "livrables": {"type": "string", "description": "Livrables de cette phase"},
                        },
                        "required": ["phase", "duree"],
                    },
                },
                "pricing": {
                    "type": "array",
                    "description": "Lignes de tarification",
                    "items": {
                        "type": "object",
                        "properties": {
                            "poste": {"type": "string", "description": "Poste de cout"},
                            "montant": {"type": "number", "description": "Montant HT en euros"},
                        },
                        "required": ["poste", "montant"],
                    },
                },
                "prochaines_etapes": {
                    "type": "string",
                    "description": "Description des prochaines etapes avec action concrete (ex: 'Repondez OK a cet email et nous planifions le cadrage cette semaine.')",
                },
                "social_proof": {
                    "type": "string",
                    "description": "Temoignage client ou cas de reference (ex: 'Nous avons accompagne [entreprise similaire] qui a obtenu [resultat] en [delai].'). Laisser vide si pas de reference pertinente.",
                },
                "social_proof_author": {
                    "type": "string",
                    "description": "Auteur du temoignage (ex: 'Jean Dupont, CTO de TechCorp')",
                },
                "roi_estimate": {
                    "type": "string",
                    "description": "Estimation du ROI ou benefice chiffre pour le client (ex: 'Gain estime : 2h/jour par collaborateur, soit 15 000 EUR/an'). Laisser vide si pas quantifiable.",
                },
                "bant_score": {
                    "type": "number",
                    "description": "Score BANT du prospect (0-100). Requis pour le tracking de conversion.",
                },
            },
            "required": ["client_name", "titre", "contexte", "livrables"],
        },
    },
    {
        "name": "livrables_list",
        "description": "Lister tous les livrables generes (devis et propositions). Retourne la liste des fichiers avec leurs metadonnees et statut de conversion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "type_filter": {
                    "type": "string",
                    "enum": ["all", "devis", "proposition"],
                    "description": "Filtrer par type de livrable (defaut: all)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "livrables_update_status",
        "description": "Mettre a jour le statut de conversion d'un devis ou proposition. Utilise quand un prospect repond, signe, ou refuse. IMPORTANT: toujours mettre a jour le statut pour alimenter le tracking de conversion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reference": {
                    "type": "string",
                    "description": "Numero du devis (DEV-...) ou reference de la proposition (PROP-...)",
                },
                "status": {
                    "type": "string",
                    "enum": ["sent", "viewed", "responded", "negotiating", "won", "lost"],
                    "description": "Nouveau statut du livrable",
                },
                "followup_increment": {
                    "type": "boolean",
                    "description": "Incrementer le compteur de relances (defaut: false)",
                    "default": False,
                },
                "lost_reason": {
                    "type": "string",
                    "description": "Raison de la perte si statut = lost (ex: 'budget', 'timing', 'concurrent', 'silence', 'besoin_change')",
                },
            },
            "required": ["reference", "status"],
        },
    },
    {
        "name": "livrables_conversion_report",
        "description": "Generer un rapport de conversion des livrables. Analyse les taux de conversion par score BANT, type de livrable, et raisons de perte. Utilise dans l'audit hebdomadaire pour calibrer la strategie.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


# --- Tool Execution ---

def execute_livrables_tool(name: str, input_data: dict) -> str:
    """Execute a livrables tool and return the result as a string."""
    try:
        if name == "livrables_create_devis":
            return _create_devis(input_data)
        elif name == "livrables_create_proposition":
            return _create_proposition(input_data)
        elif name == "livrables_list":
            return _list_livrables(input_data)
        elif name == "livrables_update_status":
            return _update_status(input_data)
        elif name == "livrables_conversion_report":
            return _conversion_report(input_data)
        else:
            return f"Error: Unknown livrables tool '{name}'"
    except Exception as e:
        log.error(f"Livrables tool error: {e}")
        return f"Error executing {name}: {str(e)}"


def _create_devis(input_data: dict) -> str:
    """Generate a professional devis (quote) in HTML."""
    os.makedirs(LIVRABLES_DIR, exist_ok=True)

    now = datetime.now()
    numero = f"DEV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}"
    date = now.strftime("%d/%m/%Y")
    validity_days = input_data.get("validity_days", 15)
    date_validite = (now + timedelta(days=validity_days)).strftime("%d/%m/%Y")

    company_name = os.getenv("AGENT_OWNER_NAME", "SNB Consulting")
    company_email = os.getenv("AGENT_OWNER_EMAIL", "contact@snb-consulting.com")

    # Build line items
    lignes_html = ""
    total_ht = 0
    for ligne in input_data["lignes"]:
        qty = ligne["quantite"]
        price = ligne["prix_unitaire"]
        line_total = qty * price
        total_ht += line_total
        lignes_html += f"""        <tr>
            <td>{ligne['description']}</td>
            <td>{qty}</td>
            <td class="amount">{price:,.2f} &euro;</td>
            <td class="amount">{line_total:,.2f} &euro;</td>
        </tr>\n"""

    tva_rate = input_data.get("tva_rate", 20)
    total_tva = total_ht * tva_rate / 100
    total_ttc = total_ht + total_tva

    html = DEVIS_TEMPLATE.format(
        numero=numero,
        date=date,
        date_validite=date_validite,
        company_name=company_name,
        company_email=company_email,
        company_phone="",
        client_name=input_data["client_name"],
        client_company=input_data.get("client_company", ""),
        client_email=input_data["client_email"],
        objet=input_data["objet"],
        lignes=lignes_html,
        total_ht=f"{total_ht:,.2f}",
        tva_rate=tva_rate,
        total_tva=f"{total_tva:,.2f}",
        total_ttc=f"{total_ttc:,.2f}",
        conditions_paiement=input_data.get("conditions_paiement", "50% a la commande, 50% a la livraison"),
        delai=input_data.get("delai", "A definir lors du cadrage"),
    )

    filename = f"devis_{numero}.html"
    filepath = os.path.join(LIVRABLES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    # Save metadata with conversion tracking
    bant_score = input_data.get("bant_score", 0)
    meta = {
        "type": "devis",
        "numero": numero,
        "date": date,
        "date_validite": date_validite,
        "client": input_data["client_name"],
        "client_email": input_data.get("client_email", ""),
        "objet": input_data["objet"],
        "total_ht": total_ht,
        "total_ttc": total_ttc,
        "filename": filename,
        "created_at": now.isoformat(),
        "conversion": {
            "bant_score": bant_score,
            "status": "sent",
            "followups_sent": 0,
            "response_received": False,
            "converted": False,
            "converted_at": None,
            "lost_reason": None,
        },
    }
    meta_path = os.path.join(LIVRABLES_DIR, f"devis_{numero}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log.info(f"Devis {numero} cree: {filepath} ({total_ttc:.2f} EUR TTC) [BANT: {bant_score}]")

    return json.dumps({
        "status": "created",
        "type": "devis",
        "numero": numero,
        "filename": filename,
        "client": input_data["client_name"],
        "objet": input_data["objet"],
        "total_ht": f"{total_ht:,.2f} EUR",
        "total_ttc": f"{total_ttc:,.2f} EUR",
        "bant_score": bant_score,
        "validity": f"{validity_days} jours (jusqu'au {date_validite})",
        "path": filepath,
    }, ensure_ascii=False)


def _create_proposition(input_data: dict) -> str:
    """Generate a commercial proposal in HTML."""
    os.makedirs(LIVRABLES_DIR, exist_ok=True)

    now = datetime.now()
    reference = f"PROP-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}"
    date = now.strftime("%d/%m/%Y")
    date_validite = (now + timedelta(days=15)).strftime("%d/%m/%Y")

    company_name = os.getenv("AGENT_OWNER_NAME", "SNB Consulting")
    company_email = os.getenv("AGENT_OWNER_EMAIL", "contact@snb-consulting.com")

    # Build livrables list
    livrables_html = ""
    for liv in input_data.get("livrables", []):
        desc = f" — {liv['description']}" if liv.get("description") else ""
        livrables_html += f"        <li><strong>{liv['titre']}</strong>{desc}</li>\n"

    # Build planning table
    planning_html = '<table style="width:100%;border-collapse:collapse;margin:1rem 0;">'
    planning_html += '<tr><th style="text-align:left;padding:0.5rem;border-bottom:2px solid #2c7be5;">Phase</th>'
    planning_html += '<th style="text-align:left;padding:0.5rem;border-bottom:2px solid #2c7be5;">Duree</th>'
    planning_html += '<th style="text-align:left;padding:0.5rem;border-bottom:2px solid #2c7be5;">Livrables</th></tr>'
    for phase in input_data.get("planning", []):
        planning_html += f'<tr><td style="padding:0.5rem;border-bottom:1px solid #eee;">{phase["phase"]}</td>'
        planning_html += f'<td style="padding:0.5rem;border-bottom:1px solid #eee;">{phase["duree"]}</td>'
        planning_html += f'<td style="padding:0.5rem;border-bottom:1px solid #eee;">{phase.get("livrables", "")}</td></tr>'
    planning_html += '</table>'

    if not input_data.get("planning"):
        planning_html = '<p><em>Planning a definir lors du cadrage.</em></p>'

    # Build pricing table
    pricing_html = '<tr><th>Poste</th><th style="text-align:right;">Montant HT</th></tr>'
    total = 0
    for item in input_data.get("pricing", []):
        pricing_html += f'<tr><td>{item["poste"]}</td><td style="text-align:right;">{item["montant"]:,.2f} &euro;</td></tr>'
        total += item["montant"]
    if input_data.get("pricing"):
        pricing_html += f'<tr><td class="total" style="border-top:2px solid #2c7be5;padding-top:0.75rem;">Total HT</td>'
        pricing_html += f'<td class="total" style="text-align:right;border-top:2px solid #2c7be5;padding-top:0.75rem;">{total:,.2f} &euro;</td></tr>'
    else:
        pricing_html = '<tr><td colspan="2"><em>Tarification a definir apres cadrage.</em></td></tr>'

    # Build social proof section
    social_proof_html = ""
    if input_data.get("social_proof"):
        author = input_data.get("social_proof_author", "")
        author_html = f'<div class="author">— {author}</div>' if author else ""
        social_proof_html = f"""<section>
    <h2>Ils nous font confiance</h2>
    <div class="testimonial">
        <p>{input_data['social_proof']}</p>
        {author_html}
    </div>
</section>"""

    # Build ROI section
    roi_html = ""
    if input_data.get("roi_estimate"):
        roi_html = f"""<div class="roi-box">
        <h3>Retour sur investissement estime</h3>
        <p class="roi-value">{input_data['roi_estimate']}</p>
    </div>"""

    html = PROPOSITION_TEMPLATE.format(
        titre=input_data["titre"],
        sous_titre=input_data.get("sous_titre", "Proposition commerciale"),
        client_name=input_data["client_name"],
        date=date,
        date_validite=date_validite,
        reference=reference,
        contexte=input_data["contexte"],
        approche=input_data.get("approche", "Notre approche sera definie lors du cadrage initial."),
        livrables_html=livrables_html,
        planning_html=planning_html,
        pricing_html=pricing_html,
        social_proof_html=social_proof_html,
        roi_html=roi_html,
        prochaines_etapes=input_data.get("prochaines_etapes",
            "Repondez OK a cet email et nous planifions un appel de cadrage de 30 minutes "
            "cette semaine. Demarrage possible sous 48h."),
        company_name=company_name,
        company_email=company_email,
    )

    filename = f"proposition_{reference}.html"
    filepath = os.path.join(LIVRABLES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    # Save metadata with conversion tracking
    bant_score = input_data.get("bant_score", 0)
    meta = {
        "type": "proposition",
        "reference": reference,
        "date": date,
        "date_validite": date_validite,
        "client": input_data["client_name"],
        "titre": input_data["titre"],
        "total_ht": total,
        "nb_livrables": len(input_data.get("livrables", [])),
        "has_social_proof": bool(input_data.get("social_proof")),
        "has_roi_estimate": bool(input_data.get("roi_estimate")),
        "filename": filename,
        "created_at": now.isoformat(),
        "conversion": {
            "bant_score": bant_score,
            "status": "sent",
            "followups_sent": 0,
            "response_received": False,
            "converted": False,
            "converted_at": None,
            "lost_reason": None,
        },
    }
    meta_path = os.path.join(LIVRABLES_DIR, f"proposition_{reference}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log.info(f"Proposition {reference} creee: {filepath} [BANT: {bant_score}]")

    return json.dumps({
        "status": "created",
        "type": "proposition",
        "reference": reference,
        "filename": filename,
        "client": input_data["client_name"],
        "titre": input_data["titre"],
        "total_ht": f"{total:,.2f} EUR" if total > 0 else "A definir",
        "nb_livrables": len(input_data.get("livrables", [])),
        "bant_score": bant_score,
        "validity": f"15 jours (jusqu'au {date_validite})",
        "path": filepath,
    }, ensure_ascii=False)


def _list_livrables(input_data: dict) -> str:
    """List all generated livrables."""
    if not os.path.exists(LIVRABLES_DIR):
        return json.dumps({"total": 0, "livrables": []}, ensure_ascii=False)

    type_filter = input_data.get("type_filter", "all")
    livrables = []

    for filename in sorted(os.listdir(LIVRABLES_DIR), reverse=True):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(LIVRABLES_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if type_filter != "all" and meta.get("type") != type_filter:
                continue
            livrables.append(meta)
        except (json.JSONDecodeError, IOError):
            continue

    return json.dumps({
        "total": len(livrables),
        "livrables": livrables,
    }, ensure_ascii=False)


def _update_status(input_data: dict) -> str:
    """Update conversion status of a devis or proposition."""
    if not os.path.exists(LIVRABLES_DIR):
        return json.dumps({"error": "Aucun livrable trouve"}, ensure_ascii=False)

    reference = input_data["reference"]
    new_status = input_data["status"]

    # Find the matching JSON metadata file
    meta_path = None
    for filename in os.listdir(LIVRABLES_DIR):
        if not filename.endswith(".json"):
            continue
        if reference in filename:
            meta_path = os.path.join(LIVRABLES_DIR, filename)
            break

    if not meta_path:
        return json.dumps({"error": f"Livrable '{reference}' non trouve"}, ensure_ascii=False)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Initialize conversion tracking if missing (backwards compatibility)
    if "conversion" not in meta:
        meta["conversion"] = {
            "bant_score": 0,
            "status": "sent",
            "followups_sent": 0,
            "response_received": False,
            "converted": False,
            "converted_at": None,
            "lost_reason": None,
        }

    old_status = meta["conversion"]["status"]
    meta["conversion"]["status"] = new_status

    if new_status in ("responded", "negotiating", "won"):
        meta["conversion"]["response_received"] = True

    if new_status == "won":
        meta["conversion"]["converted"] = True
        meta["conversion"]["converted_at"] = datetime.now().isoformat()

    if new_status == "lost":
        meta["conversion"]["lost_reason"] = input_data.get("lost_reason", "non_specifie")

    if input_data.get("followup_increment"):
        meta["conversion"]["followups_sent"] += 1

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log.info(f"Livrable {reference}: {old_status} -> {new_status}")

    return json.dumps({
        "status": "updated",
        "reference": reference,
        "old_status": old_status,
        "new_status": new_status,
        "conversion": meta["conversion"],
    }, ensure_ascii=False)


def _conversion_report(input_data: dict) -> str:
    """Generate a conversion analytics report."""
    if not os.path.exists(LIVRABLES_DIR):
        return json.dumps({"error": "Aucun livrable trouve"}, ensure_ascii=False)

    all_livrables = []
    for filename in sorted(os.listdir(LIVRABLES_DIR), reverse=True):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(LIVRABLES_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                meta = json.load(f)
            all_livrables.append(meta)
        except (json.JSONDecodeError, IOError):
            continue

    if not all_livrables:
        return json.dumps({"total": 0, "message": "Aucun livrable genere"}, ensure_ascii=False)

    # Overall stats
    total = len(all_livrables)
    with_conversion = [l for l in all_livrables if "conversion" in l]
    won = [l for l in with_conversion if l["conversion"].get("converted")]
    lost = [l for l in with_conversion if l["conversion"].get("status") == "lost"]
    responded = [l for l in with_conversion if l["conversion"].get("response_received")]
    pending = [l for l in with_conversion if l["conversion"].get("status") in ("sent", "viewed")]

    # Revenue stats
    total_won_ht = sum(l.get("total_ht", 0) for l in won)
    total_pipeline_ht = sum(l.get("total_ht", 0) for l in with_conversion if l["conversion"].get("status") not in ("lost",))

    # BANT correlation
    bant_buckets = {"chaud_70_100": [], "tiede_40_69": [], "froid_0_39": []}
    for l in with_conversion:
        score = l["conversion"].get("bant_score", 0)
        if score >= 70:
            bant_buckets["chaud_70_100"].append(l)
        elif score >= 40:
            bant_buckets["tiede_40_69"].append(l)
        else:
            bant_buckets["froid_0_39"].append(l)

    bant_analysis = {}
    for bucket_name, bucket_items in bant_buckets.items():
        if bucket_items:
            bucket_won = [l for l in bucket_items if l["conversion"].get("converted")]
            bant_analysis[bucket_name] = {
                "total": len(bucket_items),
                "won": len(bucket_won),
                "conversion_rate": f"{len(bucket_won)/len(bucket_items)*100:.0f}%",
                "avg_followups": sum(l["conversion"].get("followups_sent", 0) for l in bucket_items) / len(bucket_items),
            }

    # Lost reasons breakdown
    lost_reasons = {}
    for l in lost:
        reason = l["conversion"].get("lost_reason", "non_specifie")
        lost_reasons[reason] = lost_reasons.get(reason, 0) + 1

    # Type breakdown
    devis_items = [l for l in with_conversion if l.get("type") == "devis"]
    prop_items = [l for l in with_conversion if l.get("type") == "proposition"]
    devis_won = len([l for l in devis_items if l["conversion"].get("converted")])
    prop_won = len([l for l in prop_items if l["conversion"].get("converted")])

    report = {
        "periode": f"Depuis le debut — {total} livrables analyses",
        "kpis": {
            "total_livrables": total,
            "taux_reponse": f"{len(responded)/total*100:.0f}%" if total > 0 else "0%",
            "taux_conversion": f"{len(won)/total*100:.0f}%" if total > 0 else "0%",
            "ca_signe_ht": f"{total_won_ht:,.2f} EUR",
            "pipeline_ht": f"{total_pipeline_ht:,.2f} EUR",
            "en_attente": len(pending),
        },
        "par_score_bant": bant_analysis,
        "par_type": {
            "devis": {"total": len(devis_items), "convertis": devis_won, "taux": f"{devis_won/len(devis_items)*100:.0f}%" if devis_items else "N/A"},
            "propositions": {"total": len(prop_items), "convertis": prop_won, "taux": f"{prop_won/len(prop_items)*100:.0f}%" if prop_items else "N/A"},
        },
        "raisons_perte": lost_reasons if lost_reasons else "Aucune perte enregistree",
        "recommandations": _generate_recommendations(bant_analysis, lost_reasons, responded, total),
    }

    return json.dumps(report, ensure_ascii=False, indent=2)


def _generate_recommendations(bant_analysis: dict, lost_reasons: dict, responded: list, total: int) -> list:
    """Generate actionable recommendations based on conversion data."""
    recs = []

    if total == 0:
        return ["Aucune donnee disponible. Les recommandations seront generees apres les premiers livrables."]

    response_rate = len(responded) / total if total > 0 else 0
    if response_rate < 0.3:
        recs.append("Taux de reponse faible (<30%). Verifier la pertinence du ciblage et la qualite des objets d'email.")

    # Check BANT effectiveness
    cold = bant_analysis.get("froid_0_39", {})
    if cold and cold.get("total", 0) > 2 and cold.get("won", 0) == 0:
        recs.append("Les prospects froids (BANT < 40) ne convertissent pas. Arreter de generer des devis pour ce segment et concentrer l'effort sur la qualification.")

    hot = bant_analysis.get("chaud_70_100", {})
    if hot and hot.get("total", 0) > 0:
        hot_rate = hot.get("won", 0) / hot["total"]
        if hot_rate < 0.4:
            recs.append("Meme les prospects chauds (BANT >= 70) convertissent peu. Revoir la proposition de valeur, le pricing, ou le delai de reponse.")

    # Lost reasons analysis
    if lost_reasons:
        top_reason = max(lost_reasons, key=lost_reasons.get)
        if top_reason == "budget":
            recs.append("Principale raison de perte : budget. Proposer des offres modulaires ou un MVP a prix reduit.")
        elif top_reason == "timing":
            recs.append("Principale raison de perte : timing. Mettre en place un systeme de relance a 30/60/90 jours pour les prospects 'pas maintenant'.")
        elif top_reason == "concurrent":
            recs.append("Principale raison de perte : concurrent. Renforcer la preuve sociale et les elements differenciants dans les propositions.")
        elif top_reason == "silence":
            recs.append("Principale raison de perte : silence radio. Augmenter la frequence des relances a valeur ajoutee et varier les canaux (email + LinkedIn).")

    if not recs:
        recs.append("Donnees insuffisantes pour des recommandations precises. Continuer a tracker les conversions.")

    return recs
