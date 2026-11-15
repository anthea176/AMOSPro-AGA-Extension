# M19 P2.5 — banc AMOS simplifié R87 (15/11/2026)

**Cible stricte :** `main`, `dist/AMOSPro_AGA.Lib` **R87 v0.13.32**, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. La R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` ne doit pas être modifiée, installée à la place de R87 ni promue.

## Pourquoi remplacer le P2.4 de 611 lignes

L'ancien `M19_P24_BOBS_PIXELS_BENCH_01.asc` avait été préparé et passé en CI statique sans essai AMOS/Compiler. Ce statut ne certifiait pas sa syntaxe réelle ni ses assertions de pixels. Il surchargeait le premier diagnostic avec des tableaux, des sous-routines, un décodeur RLE et plusieurs séquences de mesure. En cas d'erreurs dans AMOS, ce périmètre rendait la cause difficile à isoler. **Il n'a jamais reçu de Gates B/C sur R87.**

Son texte est archivé **sans changement d'octets** dans `tests/design/M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc` (Git blob `30c2e09f775ed2ad0b365aec8ef47fc741311ba1cb984a`). **Ce n'est pas un test PASS**, ni l'ASC actif. Le modèle Python historique ne vérifie plus que cette source *de conception* ; il ne certifie pas AMOS.

## Nouveau test actif : un seul programme

`tests/current/M19_P25_R87_BOBS_SMOKE_01.asc` — **209 lignes**, Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`.

Cette version reprend la structure du véritable témoin R86 `tests/passed/M19_P23_BOBS_BATCH_01.asc` (Gates B/C déjà obtenues sur ce *binaire R86*). Les modifications ont été limitées :
- Suppression de l'appel `Aga Bob Probe`, supprimé du binaire R87.
- Conservation du test de création AGAPIC v1/v2, de FICON8, de trois descripteurs BOB1 et de trois refus (Count nul, banque absente, Kind incorrect).
- Conservation de trois dessins Batch, d'une capture AGAPIC 1×1 **sans prétendre valider son index de pixel**, d'un essai de clipping et d'un Swap **explicite**.
- Suppression du benchmark 4 passes, trop court pour mesurer un gain, et des drapeaux `ORDER`/`CLIP`/`MASK` qui n'étaient pas des oracles de pixels.
- **Sécurité des banques corrigée :** `_BANKS_SAFE=1` uniquement après contrôle intégral de l'absence de banques 10..22 ; nettoyage `Erase` seulement avec cette garantie. Échec de détection AGA ou collision de banque : aucune banque préexistante effacée.
- Tous les chemins après `Aga Screen Open` passent par `Aga Screen Close` puis `Amos To Front`, avant journalisation.

Ce test **ne démontre pas** encore l'équivalence pixel par pixel entre BASIC et Batch, ni les performances 4/8/16. Ces essais seront ajoutés **progressivement après retour positif Runtime et Compiled** du programme minimal.

## Validation disponible et ce qu'elle ne prouve pas

- **Préflight du skill `amos-pro-aga-rules` exécuté sur le fichier exact** : `python -B tools/amos_preflight.py --strict-target --fail-on-warnings tests/current/M19_P25_R87_BOBS_SMOKE_01.asc`. Résultat attendu avant commit : `AMOS PREFLIGHT: PASS`. 21 tests du checker `tools/test_amos_preflight.py` déjà PASS localement.
- CI dédiée R87 : `tools/test_m19_p25_r87_smoke_static.py` verrouille SHA des binaires, l'archive R86, le brouillon P2.4 et le seul ASC actif, ainsi que les contrats de nettoyage de banque et de journalisation. Ce sont des contrôles **statiques**.
- **Gate A native R87 9/9 PASS** sur le moteur indépendamment du présent ASC : [GitHub Actions](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43719712637).
- **Gates B Runtime et C AMOS Compiler pour cet ASC R87 : NON TESTÉES.** Aucun résultat WinUAE ou vitesse inventés.

## Exécution sous WinUAE

Configuration de référence : **MC68020, 14 MHz, AGA PAL, JIT désactivé** ; AMOS Professional avec `AMOSPro_AGA.Lib` R87 installée dans le bon slot APSystem et Compiler V2 utilisé pour la seconde passe. Redémarrer AMOS après installation de la bibliothèque.

1. Ouvrir un programme vide dans AMOS ; **Project -> Merge ASCII** du fichier `tests/current/M19_P25_R87_BOBS_SMOKE_01.asc`. Ne pas utiliser `Load` pour charger cet ASCII.
2. Exécuter en **Runtime** ; vérifier `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `SWAPS 1`, `CLOSE_RETURNED 1`. Récupérer `RAM:M19_P25_RUNTIME.TXT`.
3. Compiler le **même programme**, exécuter l'exécutable ; vérifier les mêmes champs, l'absence de Guru/freeze et la fermeture. Récupérer `RAM:M19_P25_COMPILED.TXT`.
4. En cas d'erreur de l'éditeur, noter **le numéro de ligne AMOS, le texte du message et la commande exacte** ; en cas de plantage compilé, isoler l'étape en conservant le même ASC, plutôt que d'introduire des commandes au hasard.

**Aucun remplacement ni promotion de `LAST_GOOD`, aucune branche, aucun tag ni release.**
