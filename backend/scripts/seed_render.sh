#!/usr/bin/env bash
# Seed the Render production database from your laptop (Render Shell needs a paid plan).
# Reads RENDER_DATABASE_URL from backend/.env.render.local, which is git-ignored.
#
#   scripts/seed_render.sh           # create the demo accounts and data
#   scripts/seed_render.sh --reset   # delete the demo rows and recreate them
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_FILE=.env.render.local
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing backend/$ENV_FILE — copy .env.render.example and paste Render's External Database URL." >&2
  exit 1
fi
set -a
source "$ENV_FILE"
set +a
: "${RENDER_DATABASE_URL:?RENDER_DATABASE_URL is not set in $ENV_FILE}"

source venv/bin/activate
# The throwaway SECRET_KEY only satisfies the production startup guard; demo logins use
# bcrypt hashes, so they work on the live site regardless of this key.
DATABASE_URL="$RENDER_DATABASE_URL" ENVIRONMENT=production \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  python scripts/seed.py --allow-production "$@"
