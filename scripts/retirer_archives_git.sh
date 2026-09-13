#!/usr/bin/env bash
# scripts/retirer_archives_git.sh
#
# Purge de l'HISTORIQUE Git le gabarit « archive » des portraits
# (portraits/<nn>-<slug>.webp sans suffixe, ~140 Ko × 170 ≈ 24 Mo), non
# référencé par aucun livrable. Les suppressions dans le dernier commit ne
# suffisent pas : les blobs restent dans l'historique, d'où ce script.
#
# Les gabarits conservés (-web.webp, -vignette.webp) et la planche contact ne
# sont PAS touchés.
#
# ⚠ Opération destructive : réécriture de l'historique → à coordonner avec
# tous les collaborateurs, puis « git push --force-with-lease » sur chaque
# branche concernée. Les clones existants doivent être re-clonés ou
# « git pull --rebase ».
#
# Prérequis :
#   python3 -m pip install git-filter-repo   (ou le paquet git-filter-repo)
#
# Usage :
#   bash scripts/retirer_archives_git.sh
#
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✘ À lancer depuis la racine du dépôt." >&2
  exit 1
fi
if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "✘ git-filter-repo introuvable :" >&2
  echo "  python3 -m pip install git-filter-repo" >&2
  exit 1
fi
if ! grep -q -- '/portraits/\*.webp' .gitignore; then
  echo "✘ .gitignore ne contient pas encore la règle des archives ; annulation." >&2
  exit 1
fi

echo "→ Analyse des archives présentes dans l'historique…"
git filter-repo --invert-paths \
  --path-regex '^portraits/[0-9]+[a-z0-9-]*(?<!-web)(?<!-vignette)\.webp$' \
  --dry-run 2>/dev/null || true

read -rp "Réécrire l'historique pour supprimer ces blobs ? (oui/non) " reponse
if [ "$reponse" != "oui" ]; then
  echo "Annulé."
  exit 0
fi

git filter-repo --force --invert-paths \
  --path-regex '^portraits/[0-9]+[a-z0-9-]*(?<!-web)(?<!-vignette)\.webp$'

echo
echo "✔ Historique réécrit. Vérification du poids :"
git count-objects -vH
echo
echo "Étapes suivantes :"
echo "  1. git remote add origin <url>   (filter-repo retire l'origine)"
echo "  2. git push --force-with-lease --all"
echo "  3. git push --force-with-lease --tags"
echo "  4. Prévenir les collaborateurs (re-clonage recommandé)."
