# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [0.0.4] - 2025-12-03

### Ajouté
- Cases à cocher pour activer/désactiver le pilotage par couleur (rouge/blanc/bleu)
- Chaque type de jour peut maintenant être piloté indépendamment
- Configuration plus granulaire du comportement de l'intégration

### Corrigé
- Erreur 500 lors de la réédition de la configuration (accès sécurisé à config_entry.options)
- Protection contre les options manquantes ou nulles via propriété _options

## [0.0.1] - 2025-11-21

### Ajouté
- Première version de l'intégration
- Configuration via l'interface Home Assistant
- Pilotage automatique charge/décharge selon Tempo
- Support des jours Rouge, Blanc, Bleu
- Charge préventive la veille des jours Rouges
- Notification automatique avant les jours Rouges
- Switch pour activer/désactiver le pilotage (activé par défaut)
- Sensor affichant le mode actuel
- Traductions français et anglais
- Détection automatique de la saison Tempo (basée sur les jours restants)
- Persistance de l'état activé/désactivé après redémarrage
