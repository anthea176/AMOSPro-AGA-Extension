> **Checkpoint 10/11/2026 :** M8/R19 0.8.3 est la candidate `Aga Mouse X/Y` ; Gate A CPU PASS 76 cas, Gate B WinUAE non testée. Les dernières archives validées sont M7/R18 et M6/R15. Voir [R19](M8_MOUSE_R19.md) et [statut M8](M8_STATUS.md). Le `LAST_GOOD` global R10 demeure protégé. Les anciennes mentions R18 « candidate courante » ci-dessous sont historiques.

# Construire, tester et conserver une bibliothèque AGA

**Règle durable :** `dist/AMOSPro_AGA.Lib` est **le candidat à installer/tester** ; `dist/experimental/` conserve les archives identifiées par version, et `dist/AMOSPro_AGA_LAST_GOOD.Lib` est un point de repli **protégé**.

Ne jamais déduire le numéro de build courant depuis ce fichier : consulter [`NEXT_SESSION.md`](NEXT_SESSION.md), le [STATUS du jalon actif](M7_STATUS.md), le HEAD de `main` et les empreintes réelles.

## Avant un nouvel essai

1. Partir d'une **archive validée explicitement** ; identifier le builder reproductible et comparer le SHA256.
2. Générer l'archive versionnée et, seulement pour un candidat à présenter, la bibliothèque `dist/AMOSPro_AGA.Lib` à contenu identique.
3. Vérifier HUNK/AP20, table de tokens, ABI AMOS, SHA, reproductibilité, conservation des segments déjà validés.
4. Un test de CPU/CI **ne valide pas** la présence d'une fonction en interprété WinUAE. Suivre les Gates A (statique), B (interprété), C (Compiler), D (Amiga réel).
5. Tester un seul nouvel incrément, conserver intact le programme exact validé dans `tests/passed/` ; diagnostics rejetés dans `tests/historical/`.
6. **Ne jamais promouvoir `LAST_GOOD` sans décision explicite**.

Pour M7 Copper : le préflight Python **n'est pas** un binaire. Les références de build et de statut figurent dans [`M7_STATUS.md`](M7_STATUS.md), avec les validations [R16 Clear](M7_COPPER_R16.md) et [R17 On/Off](M7_COPPER_R17.md). R18 est un **raster validé sur le scénario AMOS interprété/WinUAE** ([spécification](M7_COPPER_R18.md)). Gate A CPU 26 scénarios **PASS** et **CI complète PASS** ([#42870412601](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42870412601)) ; **test AMOS/WinUAE PASS** sur les captures du rendu et de la fermeture (10/11/2026, ligne 95) ; [test corrigé archivé](../tests/passed/M7_R18_COPPER_RASTER_01.asc). Compiler, matériel réel, stress/fuites restent non testés. Les archives R16/R15 et `LAST_GOOD` restent protégées.
