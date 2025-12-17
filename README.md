# Zendure Tempo

Intégration Home Assistant pour piloter automatiquement les batteries Zendure Hyper 2000 selon les tarifs RTE Tempo.

## Fonctionnalités

- **Pilotage automatique** charge/décharge selon la couleur Tempo et les heures creuses/pleines
- **Support multi-batteries** : créez une instance par batterie avec réglages indépendants
- **Activation sélective** par couleur : choisissez quels types de jours piloter automatiquement
- **Charge préventive** la veille des jours Rouges avec optimisation solaire
- **Prévision solaire** : réduction intelligente de la charge si bonne production prévue
- **Détection automatique** de la saison Tempo (basée sur les jours restants)
- **Configuration complète** via l'interface Home Assistant (aucun fichier YAML)
- **Notification automatique** avant les jours Rouges
- **Persistance** de l'état activé/désactivé après redémarrage

## Prérequis

- Home Assistant
- [Intégration Zendure](https://github.com/Zendure/Zendure-HA) configurée
- [Intégration RTE Tempo](https://github.com/hekmon/rtetempo) configurée

## Installation

### HACS (recommandé)

1. Ouvrir HACS
2. Cliquer sur les 3 points → "Dépôts personnalisés"
3. Ajouter `https://github.com/GevaudanBeast/ha-zendure-tempo`
4. Installer "Zendure Tempo"
5. Redémarrer Home Assistant

### Manuel

1. Copier le dossier `custom_components/zendure_tempo` dans votre dossier `config/custom_components/`
2. Redémarrer Home Assistant

## Configuration

### Configuration simple (une batterie)

1. Aller dans **Paramètres → Appareils et services → Ajouter une intégration**
2. Chercher "Zendure Tempo"
3. Donner un nom à l'instance (optionnel) : `Zendure Tempo` ou laissez par défaut
4. Sélectionner vos entités :
   - **Obligatoires** :
     - Couleur Tempo actuelle : `sensor.rte_tempo_couleur_actuelle`
     - Couleur Tempo demain : `sensor.rte_tempo_prochaine_couleur`
     - Heures creuses : `binary_sensor.rte_tempo_heures_creuses`
     - Limite d'entrée : `number.hyper_2000_input_limit`
     - Limite de sortie : `number.hyper_2000_output_limit`
     - SOC cible : `number.hyper_2000_soc_set`
   - **Optionnelles** :
     - Jours rouges restants : `sensor.rte_tempo_cycle_jours_restants_rouge`
     - Jours blancs restants : `sensor.rte_tempo_cycle_jours_restants_blanc`
     - Prévision solaire demain : `sensor.solcast_pv_forecast_today` (ou autre)

### Configuration multi-batteries

Si vous avez **plusieurs batteries Hyper 2000**, vous pouvez créer une instance par batterie :

1. **Première batterie** :
   - Ajouter l'intégration "Zendure Tempo"
   - Nom : `Zendure Tempo - Batterie 1`
   - Sélectionner les entités : `number.hyper_2000_input_limit`, `number.hyper_2000_output_limit`, etc.

2. **Deuxième batterie** :
   - Ajouter à nouveau l'intégration "Zendure Tempo"
   - Nom : `Zendure Tempo - Batterie 2`
   - Sélectionner les entités : `number.hyper_2000_2_input_limit`, `number.hyper_2000_2_output_limit`, etc.

3. **Troisième batterie, etc.** : Répéter le processus

**Avantages** : Chaque batterie peut avoir ses propres réglages (SOC cible, limites, activation par couleur, etc.)

## Options

Dans les options de l'intégration (Paramètres → Appareils et services → Zendure Tempo → Configurer), vous pouvez configurer :

### Activation par couleur

| Option | Description | Défaut |
|--------|-------------|--------|
| Activer jours rouges | Active le pilotage automatique pour les jours rouges | ✅ Activé |
| Activer jours blancs | Active le pilotage automatique pour les jours blancs | ✅ Activé |
| Activer jours bleus | Active le pilotage automatique pour les jours bleus | ❌ Désactivé |

*Décochez une case pour désactiver le pilotage automatique pour ce type de jour et utiliser le mode normal.*

### Niveaux de charge

| Option | Description | Défaut |
|--------|-------------|--------|
| SOC cible jour Rouge | Niveau de charge cible pour les jours rouges | 100% |
| SOC cible jour Rouge avec soleil | Niveau de charge réduit si bonne production solaire prévue | 80% |
| SOC cible normal | Niveau de charge cible normal | 90% |

### Limites de puissance

| Option | Description | Défaut |
|--------|-------------|--------|
| Limite charge max | Puissance de charge maximale | 1200W |
| Limite décharge max | Puissance de décharge maximale | 1200W |

### Prévision solaire

| Option | Description | Défaut |
|--------|-------------|--------|
| Seuil production solaire | Production minimale (kWh) pour réduire la charge préventive | 3.0 kWh |

## Stratégie

| Situation | Action |
|-----------|--------|
| **Rouge HP** (6h-22h) | Décharge max, pas de charge réseau |
| **Rouge HC** (22h-6h) | Charge max pour le lendemain |
| **Blanc HP** | Décharge |
| **Blanc HC** | Normal |
| **Veille Rouge** | Charge préventive + notification |
| **Bleu** | Mode normal |

## Entités créées

### Contrôle
- `switch.zendure_tempo_pilotage_tempo` : Activer/désactiver le pilotage

### Informations
- `sensor.zendure_tempo_mode_actuel` : Mode actif actuellement

### Boutons de test

Pour vérifier le bon fonctionnement du pilotage, vous disposez de boutons de test :

- `button.test_rouge_hp` : Tester le mode Rouge HP (décharge max)
- `button.test_rouge_hc` : Tester le mode Rouge HC (charge max)
- `button.test_blanc_hp` : Tester le mode Blanc HP (décharge)
- `button.test_blanc_hc` : Tester le mode Blanc HC (normal)
- `button.test_veille_rouge` : Tester le mode Veille Rouge (charge préventive)
- `button.test_bleu` : Tester le mode Bleu (normal)
- `button.reinitialiser_mode_automatique` : Revenir au pilotage automatique

**Utilisation** : Appuyez sur un bouton de test pour forcer temporairement un mode spécifique et vérifier que les valeurs de batterie changent correctement. Utilisez le bouton "Réinitialiser" pour revenir au pilotage automatique.

## Licence

MIT
