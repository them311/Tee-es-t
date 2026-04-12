# CLAUDE.md

Ce fichier guide les sessions Claude Code ouvertes dans ce repo. Garde-le à jour
quand tu modifies l'architecture.

## Vue d'ensemble

`them311/tee-es-t` est un monorepo d'expérimentations regroupant plusieurs
sous-projets indépendants :

| Dossier             | Stack               | Description                                         |
| ------------------- | ------------------- | --------------------------------------------------- |
| `studentflow/`      | Python 3.11 + FastAPI | Matching temps-réel jobs ↔ étudiants (multi-agents) |
| `commercial-agent/` | Python              | Agent CRM / Notion / Gmail / GitHub                 |
| `docs/`             | HTML statique       | Pages publiées via Netlify                          |
| `daleme-scoop-2.html` | HTML + CSS         | Article "journal vintage" autonome                  |

La racine ne contient PAS de projet — chaque sous-dossier est autonome avec sa
propre toolchain.

## StudentFlow — projet actif

C'est le projet sur lequel tu vas probablement passer le plus de temps. Il y a
un `studentflow/CLAUDE.md` dédié avec l'architecture détaillée. Lis-le avant
toute modification dans `studentflow/`.

**Commandes fréquentes** (depuis `studentflow/`) :

```bash
make install        # pip install -e .[dev]
make test           # pytest
make lint           # ruff check
make run-api        # lance l'API FastAPI en local
make run-agents     # lance les 3 agents en boucle
```

## Conventions

- **Python** : 3.11+, type hints partout, `pydantic` v2 pour les modèles, `ruff`
  pour lint/format.
- **Tests** : `pytest`, fixtures dans `tests/conftest.py` ou `tests/fixtures.py`.
- **Commits** : style conventionnel (`feat:`, `fix:`, `docs:`, `refactor:`…).
- **Branches** : `claude/<slug>` pour le travail piloté par Claude Code.
- **Secrets** : jamais commiter de `.env`, toujours passer par `.env.example`.

## Pièges connus

- Le repo contient plusieurs sous-projets historiques (quiz LFDS sur la branche
  `claude/data-collection-component-LqGjM`, agent commercial). Ne pas les mixer
  avec StudentFlow.
- Le déploiement Netlify (`netlify.toml`) concerne uniquement `docs/`, pas les
  apps Python.
