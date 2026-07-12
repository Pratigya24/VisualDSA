#!/usr/bin/env bash
# Generates an RS256 keypair for local development / CI.
# Production keys are provisioned via the platform secret manager, never via this script.
set -euo pipefail

KEYS_DIR="$(dirname "$0")/../keys"
mkdir -p "$KEYS_DIR"

if [[ -f "$KEYS_DIR/private.pem" ]]; then
  echo "Keys already exist at $KEYS_DIR — skipping."
  exit 0
fi

openssl genrsa -out "$KEYS_DIR/private.pem" 2048
openssl rsa -in "$KEYS_DIR/private.pem" -pubout -out "$KEYS_DIR/public.pem"

echo "Generated $KEYS_DIR/private.pem and $KEYS_DIR/public.pem"
