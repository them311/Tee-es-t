# Tee-es-t

SNB Consulting — site vitrine statique (`docs/`) et agent commercial IA autonome (`commercial-agent/`).

## Démarrage rapide

```bash
# Installation des dépendances (live-server uniquement, en dev)
npm install

# Développement (hot reload front)
npm run dev

# Production (tout en 1, port 3001)
npm run start
```

### `npm run dev`
Lance `live-server` sur `http://localhost:3000` avec rechargement automatique
des fichiers de `docs/`. Idéal pour itérer sur le front.

### `npm run start`
Lance `server.js` (Node natif, zéro dépendance prod) sur `http://localhost:3001`.
C'est le mode "tout en 1" qui sert :

| Route          | Description                                            |
|----------------|--------------------------------------------------------|
| `/`            | Site statique depuis `docs/`                           |
| `/api/health`  | Healthcheck JSON (`status`, `uptime`, `node`, …)       |
| `/api/status`  | Contenu de `docs/status.json` avec ETag + 304          |
| `/<route>`     | Fallback SPA vers `index.html` si la ressource n'existe pas |

Variables d'environnement :
- `PORT` (défaut `3001`)
- `HOST` (défaut `0.0.0.0`)

### `npm test`
Smoke tests des endpoints (utilise `node:test`, intégré à Node 20+).

## Structure

- `docs/` — site statique (déployé sur Netlify)
- `server.js` — serveur Node natif "tout en 1" pour la production
- `test/` — tests Node natifs
- `commercial-agent/` — agent commercial Python autonome (HubSpot, Gmail, Notion)
- `netlify.toml` — configuration de déploiement Netlify
