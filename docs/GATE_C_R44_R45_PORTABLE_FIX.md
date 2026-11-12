# Gate C — correction relogeable candidate R44, transposition contrôlée R45

**Date : 12/11/2026. Statut : candidate expérimentale R44, uniquement contrôle structurel/statique en attente de CI ; ni PASS WinUAE ni correctif validé.**

**Important : M16/R45 n'est pas terminée.** La bibliothèque R45 active, son archive, R44 `LAST_GOOD`, les sources R44 et tous les tests courants restent **inchangés**. Aucune promotion ni changement de branche.

## Pourquoi cette correction

Le test **compilé sur la R45 installée par l'utilisateur** a affiché :

- `01 BEFORE AGA PROBE` puis `02 AGA PROBE RETURNED` : extension joignable.
- `03 BEFORE AGA SCREEN OPEN` puis **`04 OPEN RETURNED 1`** : `Aga Screen Open` retourne normalement.
- **`05 BEFORE AGA SCREEN CLOSE`** puis Guru AmigaOS **`80000004`** avant `06` : défaut sur le chemin de `Aga Screen Close` ou son retour.

[Trace originale](../tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc) : son nom contient R44, mais le programme emploie **la bibliothèque effectivement installée**, R45 lors du test. La **Gate C R44 historique n'a pas encore été essayée**. La cause précise n'a pas été capturée avec le PC fautif.

**Cause technique candidate très sérieuse :** dans R44 et R45 (R45 reprend les segments R44), quatre `BSR.w` bruts des segments 0/8/17/18 pointent directement vers l'intérieur du segment 54 (nettoyage du curseur), dans une autre routine AP20. AMOS Compiler recopie les routines de bibliothèque séparément : les déplacements inter-routines calculés dans la bibliothèque originale deviennent invalides. Le manuel source [`+Music.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BMusic.s) précise de remplacer ces appels par les marqueurs **`Rbsr`**.

## Candidate préparée (R44 seulement)

**Fichier expérimental, NON LAST_GOOD :** [`dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R44_CANDIDATE.Lib`](../dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R44_CANDIDATE.Lib).

**Générateur unique :** [`tools/build_aga_compiler_compat.py`](../tools/build_aga_compiler_compat.py). **Contrôle statique R44/R45 :** [`tools/test_aga_compiler_compat.py`](../tools/test_aga_compiler_compat.py). Le générateur n'écrit **aucun fichier** sans `--output` explicite, et ne peut écrire que dans `dist/experimental/` avec un nom de candidate.

Correction minimale autour de l'ancienne routine curseur #54 :

1. Remplacer son accès direct aux 8 octets d'état du curseur par **`Rbsr` vers un nouveau getter interne** (retour adresse en A2). Ce getter possède désormais le stockage unique, accessible après relocation.
2. Reprendre le hook de `CloseWindow` identique dans une **nouvelle routine interne autonome**, avec sauvegarde/restauration de tous les registres. Le hook demande l'adresse d'état au getter via `Rbsr` ; aucun pointeur absolu ou déplacement vers une autre routine.
3. Remplacer les quatre `BSR.w` inter-routines du nettoyage R44 (segments 0/8/17/18) par des **`Rbsr`** pointant sur le nouveau hook.
4. Ne changer **aucun token AMOS ni API publique**. Les autres segments de R44, le binaire R44 LAST_GOOD et les archives sont inchangés.

| Baseline | Segments avant | Getter ajouté | Hook ajouté | Fonctions publiques | Déploiement |
|---|---:|---:|---:|---:|---|
| R44 v0.11.5 | 55 | 55 | 56 | 49, inchangées | **Fichier candidate séparé** |
| R45 v0.12.0 | 56 | 56 | 57 | 50, inchangées | **Simulation en mémoire uniquement** |

Le même code `patch()` sert aux deux baselines, les numéros de routines sont calculés à partir de la table AP20 et les **SHA256 sources sont verrouillés**. La transposition R45 préserve octet pour octet sa routine `Aga Image Draw` (#55) et le `GetP` de son curseur (#54). Le code ne dérive pas un index fixe R44 qui entrerait en conflit avec l'image R45.

**Après de nouveaux changements M16**, le builder refuse un SHA inconnu : relecture des modifications et nouvelle validation avant transposition vers la version finale (R45, R46 ou ultérieure). C'est intentionnel pour éviter d'appliquer aveuglément un patch sur un binaire modifié.

## Limites et ordre de validation

- **Ce correctif n'est pas encore validé sous WinUAE.** Gate A exécution CPU native, Gate B AMOS interprété, Gate C AMOS Compiler, Gate D machine AGA réelle restent des vérifications distinctes. Les tests statiques ne suffisent pas à annoncer une Gate C PASS.
- Il existe **d'autres `BSR.w` inter-segments hérités de versions antérieures**, notamment 8→48, 17/18→33, 48→49. Ils ne sont **pas couverts par la présente correction minimale**. La Gate C complète pourra encore échouer sur un autre chemin ; il faudra les inventorier et les corriger sans casser le comportement interprété.
- Avant toute utilisation réelle, vérifier l'ABI du getter et du hook, la libération des 72 octets Chip au masquage/fermeture, absence d'interaction avec Workbench, reset/cleanup, double buffering, `Safe` et retour à AMOS.
- **R45 n'est pas interrompue.** Le test de cette candidate R44 est optionnel et séparé du développement M16. Pour le moment ne pas remplacer la bibliothèque R45 active par cette candidate sans organiser l'essai.
- Pour la future Gate C : compiler la [trace à six étapes](../tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc) avec la bibliothèque candidate réellement installée, puis comparer à la capture précédente. Le critère minimal est **`06 AFTER AGA SCREEN CLOSE`** sans Guru, puis tests double buffer et nettoyage souris.

## Provenance

- [Analyse initiale et captures](GATE_C_R44_COMPILER_DIAGNOSTIC.md).
- [Sources AMOS Compiler `+APComp.s`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s) et [macros `Rbsr`](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BCEqu.s).
- [R44 Mouse Cursor](../tools/m15bis_cursor_r44_emit.py) et [M16/R45 non terminée](M16_R45_IMAGE_DRAW_CONTRACT.md).

**Aucun résultat de CPU Gate A ni de WinUAE Gate C n'est inventé.**
