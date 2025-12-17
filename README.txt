 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/ready_to_paste/README.txt b/ready_to_paste/README.txt
new file mode 100644
index 0000000000000000000000000000000000000000..17266f2a1cddc12af82932921428caf59cef6fc1
--- /dev/null
+++ b/ready_to_paste/README.txt
@@ -0,0 +1,8 @@
+Copies des fichiers essentiels de l'intégration Zendure Tempo, prêts à être collés dans votre configuration Home Assistant.
+Chaque sous-dossier reprend la structure complète :
+- custom_components/zendure_tempo/ (__init__.py, const.py, manifest.json)
+- services.yaml
+- README.md
+- CHANGELOG.md
+
+Copiez ces fichiers et dossiers dans votre installation Home Assistant (ou repo) en conservant la même arborescence.
 
EOF
)
