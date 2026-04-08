"""LFDS Pricing Engine — Grille tarifaire et generation de devis La Francaise des Sauces.

Grille tarifaire centralisee par segment (Grossiste, GMS, Agent, Traiteur,
Epicerie Fine, B2C). Genere des devis professionnels HTML alignes Brand Bible V3.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

log = logging.getLogger("commercial-agent")

LIVRABLES_DIR = os.path.join(os.path.dirname(__file__), "..", "livrables")

# =============================================================================
# GRILLE TARIFAIRE LFDS — Source de verite
# =============================================================================

CATALOGUE = {
    "LFDS-001": {
        "nom": "Sauce Signature",
        "description": "La classique LFDS, polyvalente et raffinee",
        "volume": "290ml",
        "prix": {
            "grossiste": 4.20,
            "gms": 4.80,
            "agent": 4.50,
            "traiteur": 5.50,
            "epicerie_fine": 6.90,
            "b2c": 8.90,
        },
    },
    "LFDS-002": {
        "nom": "Sauce Truffe Noire",
        "description": "Truffe noire du Perigord, intensite et elegance",
        "volume": "190ml",
        "prix": {
            "grossiste": 7.50,
            "gms": 8.50,
            "agent": 8.00,
            "traiteur": 9.50,
            "epicerie_fine": 11.90,
            "b2c": 14.90,
        },
    },
    "LFDS-003": {
        "nom": "Sauce Poivre Sauvage",
        "description": "Poivre sauvage de Madagascar, puissance et finesse",
        "volume": "290ml",
        "prix": {
            "grossiste": 4.50,
            "gms": 5.20,
            "agent": 4.80,
            "traiteur": 5.90,
            "epicerie_fine": 7.50,
            "b2c": 9.50,
        },
    },
    "LFDS-004": {
        "nom": "Sauce Echalote & Vin Rouge",
        "description": "Echalotes confites, vin rouge de Bordeaux",
        "volume": "290ml",
        "prix": {
            "grossiste": 4.50,
            "gms": 5.20,
            "agent": 4.80,
            "traiteur": 5.90,
            "epicerie_fine": 7.50,
            "b2c": 9.50,
        },
    },
    "LFDS-005": {
        "nom": "Sauce Citron Confit & Herbes",
        "description": "Citron confit, herbes fraiches de Provence",
        "volume": "290ml",
        "prix": {
            "grossiste": 4.20,
            "gms": 4.80,
            "agent": 4.50,
            "traiteur": 5.50,
            "epicerie_fine": 6.90,
            "b2c": 8.90,
        },
    },
    "LFDS-006": {
        "nom": "Coffret Decouverte",
        "description": "3 sauces signatures en format decouverte",
        "volume": "3 x 100ml",
        "prix": {
            "grossiste": 9.00,
            "gms": 10.50,
            "agent": 9.80,
            "traiteur": 11.50,
            "epicerie_fine": 14.50,
            "b2c": 18.90,
        },
    },
}

SEGMENTS = {
    "grossiste": {
        "label": "Grossiste",
        "franco": 500,
        "paiement": "30 jours fin de mois",
        "moq": 48,
        "moq_label": "48 unites",
        "acompte": "30% a la commande",
    },
    "gms": {
        "label": "GMS (Grande Distribution)",
        "franco": 300,
        "paiement": "45 jours fin de mois",
        "moq": 24,
        "moq_label": "24 unites",
        "acompte": "Aucun",
    },
    "agent": {
        "label": "Agent Commercial",
        "franco": 200,
        "paiement": "30 jours",
        "moq": 12,
        "moq_label": "12 unites",
        "acompte": "Aucun",
    },
    "traiteur": {
        "label": "Traiteur / Restaurateur",
        "franco": 150,
        "paiement": "30 jours",
        "moq": 6,
        "moq_label": "6 unites",
        "acompte": "Aucun",
    },
    "epicerie_fine": {
        "label": "Epicerie Fine",
        "franco": 100,
        "paiement": "Comptant ou 15 jours",
        "moq": 6,
        "moq_label": "6 unites",
        "acompte": "Aucun",
    },
    "b2c": {
        "label": "Particulier (B2C)",
        "franco": 35,
        "paiement": "Comptant",
        "moq": 1,
        "moq_label": "1 unite",
        "acompte": "Aucun",
    },
}

TVA_RATE = 20  # %


# =============================================================================
# DEVIS TEMPLATE — LFDS Brand Bible V3
# =============================================================================

LFDS_DEVIS_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Inter', sans-serif;
    color: #1A1A1A;
    max-width: 800px;
    margin: 0 auto;
    padding: 0;
    background: #fff;
}}
.dv-header {{
    background: linear-gradient(135deg, #2C1810 0%, #4A2C2A 100%);
    color: #FAF7F2;
    padding: 2.5rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}}
.dv-brand h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}}
.dv-brand p {{
    font-size: 0.75rem;
    opacity: 0.7;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
.dv-ref {{
    text-align: right;
    font-size: 0.8rem;
}}
.dv-ref strong {{
    display: block;
    font-size: 1rem;
    color: #C5A47E;
    margin-bottom: 0.3rem;
}}
.dv-ref .validity {{
    color: #C5A47E;
    font-weight: 600;
    margin-top: 0.4rem;
}}
.dv-parties {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    padding: 2rem 3rem;
    background: #FAF7F2;
    border-bottom: 1px solid #E8E0D4;
}}
.dv-party h3 {{
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8B7355;
    margin-bottom: 0.5rem;
}}
.dv-party strong {{
    display: block;
    font-size: 0.95rem;
    margin-bottom: 0.2rem;
}}
.dv-party span {{
    font-size: 0.82rem;
    color: #666;
    display: block;
    line-height: 1.5;
}}
.dv-objet {{
    padding: 1.2rem 3rem;
    font-size: 0.9rem;
    border-bottom: 1px solid #E8E0D4;
}}
.dv-objet strong {{ color: #4A2C2A; }}
.dv-table {{
    padding: 0 3rem 1.5rem;
    margin-top: 1.5rem;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th {{
    background: #2C1810;
    color: #FAF7F2;
    padding: 0.7rem 1rem;
    text-align: left;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}}
th:last-child, td:last-child {{ text-align: right; }}
th:nth-child(3), td:nth-child(3) {{ text-align: right; }}
th:nth-child(2), td:nth-child(2) {{ text-align: center; }}
td {{
    padding: 0.7rem 1rem;
    border-bottom: 1px solid #F0EBE3;
    font-size: 0.82rem;
}}
tr:hover {{ background: #FAF7F2; }}
.td-ref {{ color: #8B7355; font-size: 0.72rem; }}
.total-section {{
    margin: 0 3rem 1.5rem;
    display: flex;
    justify-content: flex-end;
}}
.total-box {{
    background: #FAF7F2;
    border: 1px solid #E8E0D4;
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    min-width: 280px;
}}
.total-line {{
    display: flex;
    justify-content: space-between;
    padding: 0.3rem 0;
    font-size: 0.85rem;
    color: #666;
}}
.total-line.grand {{
    border-top: 2px solid #2C1810;
    margin-top: 0.5rem;
    padding-top: 0.6rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: #2C1810;
}}
.dv-conditions {{
    margin: 0 3rem 2rem;
    padding: 1.2rem 1.5rem;
    background: #FAF7F2;
    border-radius: 8px;
    border-left: 3px solid #C5A47E;
}}
.dv-conditions h4 {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8B7355;
    margin-bottom: 0.6rem;
}}
.dv-conditions li {{
    font-size: 0.8rem;
    color: #555;
    line-height: 1.6;
    margin-left: 1rem;
}}
.dv-footer {{
    background: #2C1810;
    color: #8B7355;
    text-align: center;
    padding: 1rem;
    font-size: 0.7rem;
    letter-spacing: 0.5px;
}}
.dv-footer strong {{ color: #C5A47E; }}
</style>
</head>
<body>
<div class="dv-header">
    <div class="dv-brand">
        <h1>La Francaise des Sauces</h1>
        <p>Artisan saucier depuis toujours</p>
    </div>
    <div class="dv-ref">
        <strong>DEVIS {numero}</strong>
        Date : {date}<br>
        <div class="validity">Valide jusqu'au {date_validite}</div>
    </div>
</div>
<div class="dv-parties">
    <div class="dv-party">
        <h3>Emetteur</h3>
        <strong>La Francaise des Sauces</strong>
        <span>Baptiste Thevenot<br>bp.thevenot@gmail.com</span>
    </div>
    <div class="dv-party">
        <h3>Client</h3>
        <strong>{client_name}</strong>
        <span>{client_company}<br>{client_email}{client_phone}</span>
    </div>
</div>
<div class="dv-objet">
    <strong>Objet :</strong> {objet} &mdash; <em>Segment : {segment_label}</em>
</div>
<div class="dv-table">
    <table>
        <thead>
            <tr>
                <th>Produit</th>
                <th>Qte</th>
                <th>Prix unit. HT</th>
                <th>Total HT</th>
            </tr>
        </thead>
        <tbody>
            {lignes}
        </tbody>
    </table>
</div>
<div class="total-section">
    <div class="total-box">
        <div class="total-line"><span>Total HT</span><span>{total_ht} &euro;</span></div>
        <div class="total-line"><span>TVA ({tva_rate}%)</span><span>{total_tva} &euro;</span></div>
        <div class="total-line grand"><span>Total TTC</span><span>{total_ttc} &euro;</span></div>
    </div>
</div>
<div class="dv-conditions">
    <h4>Conditions commerciales</h4>
    <ul>
        <li>Paiement : {conditions_paiement}</li>
        <li>Acompte : {acompte}</li>
        <li>Franco de port : {franco} &euro; HT minimum</li>
        <li>Quantite minimum par reference : {moq_label}</li>
        <li>Delai de livraison : {delai}</li>
        <li>Validite du devis : 30 jours</li>
    </ul>
</div>
<div class="dv-footer">
    <strong>La Francaise des Sauces</strong> &mdash; Document genere par Agent Commercial IA
</div>
</body>
</html>"""


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

LFDS_PRICING_TOOLS = [
    {
        "name": "lfds_get_catalogue",
        "description": "Obtenir le catalogue complet LFDS avec les prix par segment. Utile pour repondre a une demande de tarifs ou presenter l'offre produit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment": {
                    "type": "string",
                    "enum": ["grossiste", "gms", "agent", "traiteur", "epicerie_fine", "b2c", "all"],
                    "description": "Segment tarifaire. 'all' pour afficher tous les prix.",
                },
            },
            "required": ["segment"],
        },
    },
    {
        "name": "lfds_create_devis",
        "description": "Generer un devis LFDS professionnel. Applique automatiquement la grille tarifaire selon le segment du client. Produit un HTML conforme Brand Bible V3.",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string", "description": "Nom du client"},
                "client_company": {"type": "string", "description": "Entreprise ou enseigne"},
                "client_email": {"type": "string", "description": "Email du client"},
                "client_phone": {"type": "string", "description": "Telephone (optionnel)"},
                "segment": {
                    "type": "string",
                    "enum": ["grossiste", "gms", "agent", "traiteur", "epicerie_fine", "b2c"],
                    "description": "Segment tarifaire du client",
                },
                "lignes": {
                    "type": "array",
                    "description": "Lignes de commande",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ref": {
                                "type": "string",
                                "description": "Reference produit (ex: LFDS-001)",
                            },
                            "quantite": {
                                "type": "number",
                                "description": "Quantite commandee",
                            },
                        },
                        "required": ["ref", "quantite"],
                    },
                },
                "objet": {
                    "type": "string",
                    "description": "Objet du devis (ex: 'Commande initiale sauces LFDS')",
                },
                "delai": {
                    "type": "string",
                    "description": "Delai de livraison (defaut: '5 a 10 jours ouvrés')",
                },
            },
            "required": ["client_name", "client_email", "segment", "lignes"],
        },
    },
    {
        "name": "lfds_get_conditions",
        "description": "Obtenir les conditions commerciales pour un segment specifique (franco de port, paiement, MOQ, acompte).",
        "input_schema": {
            "type": "object",
            "properties": {
                "segment": {
                    "type": "string",
                    "enum": ["grossiste", "gms", "agent", "traiteur", "epicerie_fine", "b2c"],
                    "description": "Segment a consulter",
                },
            },
            "required": ["segment"],
        },
    },
]


# =============================================================================
# TOOL EXECUTION
# =============================================================================

def execute_lfds_tool(name: str, input_data: dict) -> str:
    """Execute an LFDS pricing tool."""
    try:
        if name == "lfds_get_catalogue":
            return _get_catalogue(input_data)
        elif name == "lfds_create_devis":
            return _create_lfds_devis(input_data)
        elif name == "lfds_get_conditions":
            return _get_conditions(input_data)
        else:
            return f"Error: Unknown LFDS tool '{name}'"
    except Exception as e:
        log.error(f"LFDS tool error: {e}")
        return f"Error executing {name}: {str(e)}"


def _get_catalogue(input_data: dict) -> str:
    """Return the full LFDS product catalogue with prices for a given segment."""
    segment = input_data["segment"]

    produits = []
    for ref, prod in CATALOGUE.items():
        item = {
            "ref": ref,
            "nom": prod["nom"],
            "description": prod["description"],
            "volume": prod["volume"],
        }
        if segment == "all":
            item["prix"] = prod["prix"]
        else:
            item["prix_ht"] = prod["prix"].get(segment, "N/A")
            item["segment"] = SEGMENTS.get(segment, {}).get("label", segment)
        produits.append(item)

    result = {"catalogue": produits, "tva": TVA_RATE}
    if segment != "all" and segment in SEGMENTS:
        result["conditions"] = SEGMENTS[segment]

    return json.dumps(result, ensure_ascii=False, indent=2)


def _get_conditions(input_data: dict) -> str:
    """Return commercial conditions for a specific segment."""
    segment = input_data["segment"]
    if segment not in SEGMENTS:
        return json.dumps({"error": f"Segment inconnu: {segment}"})

    return json.dumps({
        "segment": segment,
        "conditions": SEGMENTS[segment],
        "tva": TVA_RATE,
    }, ensure_ascii=False, indent=2)


def _create_lfds_devis(input_data: dict) -> str:
    """Generate a professional LFDS quote using the pricing grid."""
    os.makedirs(LIVRABLES_DIR, exist_ok=True)

    now = datetime.now()
    numero = f"LFDS-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}"
    date = now.strftime("%d/%m/%Y")
    date_validite = (now + timedelta(days=30)).strftime("%d/%m/%Y")

    segment = input_data["segment"]
    seg_info = SEGMENTS.get(segment, SEGMENTS["b2c"])

    # Build line items from catalogue
    lignes_html = ""
    total_ht = 0.0
    lignes_meta = []

    for ligne in input_data["lignes"]:
        ref = ligne["ref"]
        qty = ligne["quantite"]

        if ref not in CATALOGUE:
            lignes_html += f"""        <tr>
            <td>{ref} <span class="td-ref">(reference inconnue)</span></td>
            <td>{qty}</td>
            <td>--</td>
            <td>--</td>
        </tr>\n"""
            continue

        prod = CATALOGUE[ref]
        prix = prod["prix"].get(segment, prod["prix"]["b2c"])
        line_total = qty * prix
        total_ht += line_total

        lignes_html += f"""        <tr>
            <td>{prod['nom']} <span class="td-ref">{ref} &mdash; {prod['volume']}</span></td>
            <td>{qty}</td>
            <td>{prix:,.2f} &euro;</td>
            <td>{line_total:,.2f} &euro;</td>
        </tr>\n"""

        lignes_meta.append({
            "ref": ref,
            "nom": prod["nom"],
            "quantite": qty,
            "prix_unitaire": prix,
            "total": line_total,
        })

    total_tva = total_ht * TVA_RATE / 100
    total_ttc = total_ht + total_tva

    client_phone = input_data.get("client_phone", "")
    if client_phone:
        client_phone = f"<br>{client_phone}"

    html = LFDS_DEVIS_TEMPLATE.format(
        numero=numero,
        date=date,
        date_validite=date_validite,
        client_name=input_data["client_name"],
        client_company=input_data.get("client_company", ""),
        client_email=input_data["client_email"],
        client_phone=client_phone,
        objet=input_data.get("objet", "Commande sauces La Francaise des Sauces"),
        segment_label=seg_info["label"],
        lignes=lignes_html,
        total_ht=f"{total_ht:,.2f}",
        tva_rate=TVA_RATE,
        total_tva=f"{total_tva:,.2f}",
        total_ttc=f"{total_ttc:,.2f}",
        conditions_paiement=seg_info["paiement"],
        acompte=seg_info["acompte"],
        franco=seg_info["franco"],
        moq_label=seg_info["moq_label"],
        delai=input_data.get("delai", "5 a 10 jours ouvres"),
    )

    filename = f"devis_{numero}.html"
    filepath = os.path.join(LIVRABLES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    # Save metadata
    meta = {
        "type": "devis_lfds",
        "numero": numero,
        "date": date,
        "client": input_data["client_name"],
        "company": input_data.get("client_company", ""),
        "email": input_data["client_email"],
        "segment": segment,
        "segment_label": seg_info["label"],
        "objet": input_data.get("objet", "Commande LFDS"),
        "lignes": lignes_meta,
        "total_ht": total_ht,
        "total_tva": total_tva,
        "total_ttc": total_ttc,
        "conditions": {
            "paiement": seg_info["paiement"],
            "franco": seg_info["franco"],
            "acompte": seg_info["acompte"],
            "moq": seg_info["moq_label"],
        },
        "filename": filename,
        "created_at": now.isoformat(),
    }
    meta_path = os.path.join(LIVRABLES_DIR, f"devis_{numero}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    log.info(f"Devis LFDS {numero} cree: {filepath} ({total_ttc:.2f} EUR TTC)")

    return json.dumps({
        "status": "created",
        "type": "devis_lfds",
        "numero": numero,
        "filename": filename,
        "client": input_data["client_name"],
        "segment": seg_info["label"],
        "total_ht": f"{total_ht:,.2f} EUR",
        "total_ttc": f"{total_ttc:,.2f} EUR",
        "nb_lignes": len(lignes_meta),
        "path": filepath,
    }, ensure_ascii=False)
