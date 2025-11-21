#!/bin/bash
# Script pour créer une nouvelle release
# Usage: ./scripts/bump_version.sh 0.0.2

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.0.2"
    exit 1
fi

VERSION=$1
DATE=$(date +%Y-%m-%d)

# Vérifier que le CHANGELOG a été mis à jour
if ! grep -q "\[$VERSION\]" CHANGELOG.md; then
    echo "Erreur: La version $VERSION n'est pas dans le CHANGELOG.md"
    echo "Ajoutez d'abord les notes de version dans CHANGELOG.md"
    exit 1
fi

# Mettre à jour la version dans manifest.json
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" custom_components/zendure_tempo/manifest.json

echo "Version mise à jour dans manifest.json: $VERSION"

# Commit et tag
git add custom_components/zendure_tempo/manifest.json
git commit -m "Bump version to $VERSION"
git tag -a "v$VERSION" -m "Version $VERSION"

echo ""
echo "Version $VERSION préparée!"
echo "Pour publier la release:"
echo "  git push origin main"
echo "  git push origin v$VERSION"
