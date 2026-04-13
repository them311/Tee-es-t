# Tee-es-t

SNB Consulting — site vitrine statique (`docs/`) et agent commercial IA autonome (`commercial-agent/`).

## Démarrage rapide

```bash
# Installation des dépendances
npm install

# Développement (hot reload front)
npm run dev

# Production (tout en 1, port 3001)
npm run start
```

- `npm run dev` lance `live-server` sur `http://localhost:3000` avec rechargement automatique des fichiers de `docs/`.
- `npm run start` lance `http-server` sur `http://localhost:3001` pour servir le site en mode production.

## Structure

- `docs/` — site statique (déployé sur Netlify)
- `commercial-agent/` — agent commercial Python autonome (HubSpot, Gmail, Notion)
- `netlify.toml` — configuration de déploiement Netlify
