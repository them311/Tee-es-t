#!/usr/bin/env bash
## Deploy the snb API + scheduler to Fly.io.
## Requires: flyctl on PATH, FLY_API_TOKEN in env OR `flyctl auth login` done.
##
## First run only:
##   ./scripts/deploy-snb.sh init
##   ./scripts/deploy-snb.sh secrets
##
## Normal deploy:
##   ./scripts/deploy-snb.sh          # build + deploy
##   ./scripts/deploy-snb.sh status   # show app + machines
##   ./scripts/deploy-snb.sh logs     # stream logs
set -euo pipefail

APP="snb-api"
CONFIG="fly.snb.toml"

command -v flyctl >/dev/null 2>&1 || {
    echo "flyctl not found. Install: curl -L https://fly.io/install.sh | sh" >&2
    exit 1
}

case "${1:-deploy}" in
    init)
        flyctl launch --config "$CONFIG" --copy-config --no-deploy --name "$APP"
        flyctl volumes create snb_data --config "$CONFIG" --region cdg --size 1
        ;;
    secrets)
        if [[ ! -f .env ]]; then
            echo ".env not found — copy from .env.example and fill in first" >&2
            exit 1
        fi
        echo "Setting secrets on $APP from .env (non-empty keys only)..."
        while IFS='=' read -r key value; do
            [[ -z "$key" || "$key" =~ ^# || -z "$value" ]] && continue
            flyctl secrets set --config "$CONFIG" --stage "$key=$value"
        done < <(grep -E '^[A-Z_]+=.+' .env | grep -v '^PORT=' | grep -v '^ENV=')
        flyctl secrets deploy --config "$CONFIG"
        ;;
    deploy|"")
        flyctl deploy --config "$CONFIG" --remote-only
        ;;
    status)
        flyctl status --config "$CONFIG"
        ;;
    logs)
        flyctl logs --config "$CONFIG"
        ;;
    open)
        flyctl open --config "$CONFIG"
        ;;
    scale-scheduler)
        flyctl scale count scheduler=1 --config "$CONFIG"
        ;;
    *)
        echo "Usage: $0 [init|secrets|deploy|status|logs|open|scale-scheduler]" >&2
        exit 1
        ;;
esac
