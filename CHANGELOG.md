 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/ready_to_paste/README.md b/ready_to_paste/README.md
new file mode 100644
index 0000000000000000000000000000000000000000..96d082e3a42f742b1f67265ba8bf5b10942619fc
--- /dev/null
+++ b/ready_to_paste/README.md
@@ -0,0 +1,98 @@
+# Zendure Tempo
+
+Intégration Home Assistant pour piloter automatiquement les batteries Zendure Hyper 2000 selon les tarifs RTE Tempo.
+
+## Version
+
+- Version actuelle : **0.0.5**
+
+> ℹ️ Les mises à jour sont livrées sur la branche `work` de ce dépôt. Si vous ne voyez pas les derniers commits, exécutez `git fetch && git checkout work && git pull` dans votre clone ou vérifiez que votre installation HACS pointe bien sur cette branche.
+
+## Fonctionnalités
+
+- Pilotage automatique charge/décharge selon la couleur Tempo et les heures creuses/pleines
+- Charge préventive la veille des jours Rouges
+- Configuration via l'interface Home Assistant
+- Notification automatique avant les jours Rouges
+
+## Prérequis
+
+- Home Assistant
+- [Intégration Zendure](https://github.com/Zendure/Zendure-HA) configurée
+- [Intégration RTE Tempo](https://github.com/hekmon/rtetempo) configurée
+
+## Installation
+
+### HACS (recommandé)
+
+1. Ouvrir HACS
+2. Cliquer sur les 3 points → "Dépôts personnalisés"
+3. Ajouter `https://github.com/GevaudanBeast/ha-zendure-tempo`
+4. Installer "Zendure Tempo"
+5. Redémarrer Home Assistant
+
+### Manuel
+
+1. Copier le dossier `custom_components/zendure_tempo` dans votre dossier `config/custom_components/`
+2. Redémarrer Home Assistant
+
+## Configuration
+
+1. Aller dans **Paramètres → Appareils et services → Ajouter une intégration**
+2. Chercher "Zendure Tempo"
+3. Sélectionner vos entités :
+   - Couleur Tempo actuelle : `sensor.rte_tempo_couleur_actuelle`
+   - Couleur Tempo demain : `sensor.rte_tempo_prochaine_couleur`
+   - Heures creuses : `binary_sensor.rte_tempo_heures_creuses`
+   - Limite d'entrée : `number.hyper_2000_input_limit`
+   - Limite de sortie : `number.hyper_2000_output_limit`
+   - SOC cible : `number.hyper_2000_soc_set`
+
+## Options
+
+Dans les options de l'intégration, vous pouvez configurer :
+
+| Option | Description | Défaut |
+|--------|-------------|--------|
+| SOC cible jour Rouge | Niveau de charge cible pour les jours rouges | 100% |
+| SOC cible normal | Niveau de charge cible normal | 90% |
+| Limite charge max | Puissance de charge maximale | 1200W |
+| Limite décharge max | Puissance de décharge maximale | 1200W |
+
+## Stratégie
+
+| Situation | Action |
+|-----------|--------|
+| **Rouge HP** (6h-22h) | Décharge max, pas de charge réseau |
+| **Rouge HC** (22h-6h) | Charge max pour le lendemain |
+| **Blanc HP** | Décharge |
+| **Blanc HC** | Normal |
+| **Veille Rouge** | Charge préventive + notification |
+| **Bleu** | Mode normal |
+
+### Commande manuelle pour tests
+
+Un service Home Assistant `zendure_tempo.apply_mode` permet de forcer l'application d'un mode sans attendre le calcul automatique. Pratique pour vérifier rapidement que la communication avec la batterie fonctionne :
+
+- `mode` : `Auto` par défaut (applique le mode détecté) ou l'un des modes disponibles (Rouge/Blanc/Bleu, veille rouge, désactivé).
+- `config_entry_id` : optionnel si vous n'avez qu'une seule instance ; renseignez-le sinon.
+
+L'appel applique immédiatement les consignes de charge/décharge et met à jour l'état interne de l'intégration. Le service est documenté dans l'onglet **Développeur → Services** grâce au fichier `services.yaml`.
+
+### Vérifier que la mise à jour est bien chargée
+
+Pour confirmer que votre instance Home Assistant embarque bien la dernière version :
+
+- Ouvrez **Paramètres → Intégrations → Zendure Tempo** et vérifiez que la version indiquée est **0.0.5** (ou plus).
+- Dans **Développeur → Services**, la fiche `zendure_tempo.apply_mode` doit proposer les sélecteurs `mode` et `config_entry_id`, preuve que `services.yaml` est pris en compte.
+
+Si ces éléments n'apparaissent pas, forcez le rechargement de l'intégration ou redémarrez Home Assistant pour récupérer les fichiers mis à jour.
+
+## Entités créées
+
+- `switch.zendure_tempo_pilotage_tempo` : Activer/désactiver le pilotage
+- `sensor.zendure_tempo_mode_actuel` : Mode actif actuellement
+
+## Licence
+
+MIT
 
EOF
)
