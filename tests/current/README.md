# Test AMOS actif — M16/R48 token/ABI (diagnostic uniquement)

**Unique test actif :** [`M16_R48_TOKEN_ABI_PROBE_01.asc`](M16_R48_TOKEN_ABI_PROBE_01.asc). Il correspond à la bibliothèque **R48** actuellement dans [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib).

Importer avec **Project → Merge ASCII** dans un programme vide, puis lancer **en interprété**, dans la configuration WinUAE de test. Aucun écran ni banque n'est nécessaire. Résultat attendu : `AFTER R48 CALL 1` puis `RESULT 1`.

**R48 n'effectue aucune capture** : elle vérifie uniquement la reconnaissance de `Aga Image Capture(11,16,16,16,16,-1)` et l'ABI des arguments. Gate B sous WinUAE encore non validée ; ne pas compiler ni promouvoir. La R46 C1 reste [`LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib).

L'ancien test de capture R47 est conservé dans [`tests/diagnostics`](../diagnostics/M16_R47_IMAGE_CAPTURE_01.asc), **non actif et non compatible avec la sonde R48**.
