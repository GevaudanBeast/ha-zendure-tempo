 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/ready_to_paste/CHANGELOG.md b/ready_to_paste/CHANGELOG.md
new file mode 100644
index 0000000000000000000000000000000000000000..7cc8036f80eb8f8561834711e4dca61c2b45ec92
--- /dev/null
+++ b/ready_to_paste/CHANGELOG.md
@@ -0,0 +1,29 @@
+# Changelog
+
+Toutes les modifications notables de ce projet seront documentées dans ce fichier.
+
+Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
+et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).
+
+## [0.0.5] - 2025-12-17
+
+### Ajouté
+- Service manuel `zendure_tempo.apply_mode` pour déclencher un mode Tempo à la demande
+  et faciliter les tests de communication avec la batterie.
+- Déclaration du service `apply_mode` dans `services.yaml` pour bénéficier de l'aide
+  intégrée dans l'UI Home Assistant.
+
+## [0.0.1] - 2025-11-21
+
+### Ajouté
+- Première version de l'intégration
+- Configuration via l'interface Home Assistant
+- Pilotage automatique charge/décharge selon Tempo
+- Support des jours Rouge, Blanc, Bleu
+- Charge préventive la veille des jours Rouges
+- Notification automatique avant les jours Rouges
+- Switch pour activer/désactiver le pilotage (activé par défaut)
+- Sensor affichant le mode actuel
+- Traductions français et anglais
+- Détection automatique de la saison Tempo (basée sur les jours restants)
+- Persistance de l'état activé/désactivé après redémarrage
 
EOF
)
