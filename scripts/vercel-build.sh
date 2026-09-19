#!/usr/bin/env bash
# One-origin static export: passenger chat at / and operations at /ops.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

rm -rf public
mkdir -p public/ops

(cd frontend-manager && npm install && EXPORT=1 npm run build)
cp -R frontend-manager/out/. public/ops/

(cd frontend && npm ci && EXPORT=1 NEXT_PUBLIC_OPS_URL=/ops npm run build)
cp -R frontend/out/. public/
