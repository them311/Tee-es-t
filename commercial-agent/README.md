# Commercial Agent - L-FDS

Agent commercial autonome pour la gestion CRM HubSpot, l'envoi d'emails et la strategie de prospection.

## Prerequisites

1. **Python 3.10+**
2. **Cle API Anthropic** : Creer un compte sur [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key
3. **Cle API HubSpot** : Settings → Integrations → Private Apps → Create private app
4. **Credentials Gmail API** : [Google Cloud Console](https://console.cloud.google.com) → APIs → Gmail API → Credentials

## Installation

```bash
cd commercial-agent
pip install -r requirements.txt
```

## Configuration

Copier le fichier `.env.example` en `.env` et remplir les valeurs :

```bash
cp .env.example .env
```

## Lancement

```bash
python main.py
```

## Structure

```
commercial-agent/
├── main.py              # Point d'entree - boucle agent
├── config/
│   └── system_prompt.py # Prompt systeme de l'agent
├── tools/
│   ├── __init__.py
│   ├── hubspot.py       # Outils CRM HubSpot
│   └── gmail.py         # Outils Gmail
├── requirements.txt
└── .env.example
```
