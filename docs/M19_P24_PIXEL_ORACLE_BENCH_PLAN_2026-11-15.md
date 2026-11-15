# M19 P2.4 — validation pixel WinUAE et mesure BASIC/Batch R87

Date : 15 novembre 2026. **NOUVEAU TEST EN PRÉPARATION**, aucune Gate B/C P2.4 ne peut être déclarée PASS avant les journaux WinUAE. Ce test valide la nouvelle R87 v0.13.32 sans diagnostic Probe. Ne change pas la R84 `LAST_GOOD`.

## Périmètre et prérequis

- **Nouveau candidat R87 v0.13.32**, généré directement dans `dist/AMOSPro_AGA.Lib` depuis R84 figée après Gate A, **77 commandes / 87 entrées AP20**, et aucune commande `Aga Bob Probe`. La R86 v0.13.31 (SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`) reste un jalon historique. **Pas de promotion.**
- Fichier **actif unique** : [`tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc`](../tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc).
- Le programme P2.3 déjà qualifié Runtime/Compiled est **archivé octet pour octet** dans [`tests/passed/M19_P23_BOBS_BATCH_01.asc`](../tests/passed/M19_P23_BOBS_BATCH_01.asc), Git blob `19ad2044252783454f4082c118e53b34a6b83478` ; [rapport P2.3](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md).
- Matériel de benchmark de référence : **WinUAE 68020 à 14 MHz, PAL, JIT désactivé**, comme le [benchmark M19 P2.1](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md). Exécuter le même programme en **Runtime** puis en **Compiled** et récupérer les deux TXT depuis `RAM:` avant reboot.
- Aucun fichier image, IFF ou ABK externe ; création autonome de deux captures AGAPIC v1/v2, d'un FICON8 indexé et des banques de descripteurs `BOB1` au démarrage.
- **Pas de nouveau code moteur**, de tri Z ou d'AMAL ; tous les appels de dessin s'exécutent en BASIC principal.

## Pixel oracle indépendant (19 points)

Les couleurs sont des **indices AGA 8 plans** : fond=1, AGAPIC v1=3, AGAPIC v2=4 et FICON8 intérieur=5, avec **index 0 transparent en mode 1**, index 0 **opaque en mode 0**.

Pour chaque point, la commande native `Aga Bank Image Capture(23,X,Y,1,1,-1,1)` crée une capture v1 d'un pixel. Le BASIC **vérifie réellement** magic/version/largeur/hauteur/profondeur/offset/contrôle RLE et reconstruit l'index de couleur en lisant le bit 15 des huit WORD de plans, puis le compare à la couleur attendue. Un retour de capture sans comparaison de pixel ne peut plus produire un PASS. Le modèle de test statique vérifie l'extracteur sur **les 256 indices**.

| Scénario | Points attendus | Contrôle |
|---|---|---|
| v1 → FICON → v2 | (116,116)=4 ; (110,110)=5 ; (100,100)=1 ; (130,130)=4 | Ordre Z et transparence |
| v2 forcée opaque | (110,110)=0 ; (116,116)=4 | Pen 0 visible, masquage désactivé |
| FICON forcée opaque | (105,105)=0 ; (106,106)=5 | Bordure 0 et intérieur 5 |
| Z inversé : v1 → v2 → FICON | (116,116)=5 ; (110,110)=5 | Priorité calculée |
| FICON à (-8,-8) | (0,0)=5 ; (7,7)=1 | Clipping négatif |
| FICON à (315,250) | (319,255)=5 ; (315,250)=1 | Clipping droite/bas |
| AGAPIC v1 (-8,-8), v2 (300,240) | (0,0)=3 ; (25,25)=1 ; (319,255)=4 ; (300,240)=1 | Clipping v1/v2 |
| Après le seul Swap explicite du scénario | (116,116)=1 | L'ancien front initialisé à 1 n'a pas été altéré par Batch |

**Si une capture échoue ou si un index diffère :** `RESULT=0`, `ERR` distinct, `PIXEL_BAD`, coordonnées, indice attendu/lu et numéro d'étape dans le journal. La sonde ne modifie pas la bibliothèque R86.

## Équivalence complète BASIC/Batch

Pour chacun des ensembles **4, 8 et 16 Bobs**, avec descripteurs préconstruits et ordre fixe, le programme :
1. Dessine les objets avec les commandes individuelles `Aga Bank Image Draw` et `Aga F Icon` sur un fond index 1.
2. Capture une zone **144×144** en AGAPIC v1 opaque, banque 27.
3. Reconstruit le même fond et appelle **une seule** commande `Aga Bob Batch(Bank,Count)`.
4. Capture la même zone en banque 28 et **compare tous les octets des deux données AGAPIC compressées** (contenu pixel, et pas seulement les retours des fonctions).

Les captures proviennent du même encodeur R84 et des mêmes dimensions ; leur représentation v1 est déterministe. `PARITY_OK=3`, `PARITY_BAD=0` et `PARITY_BYTES` attestent les comparaisons. Une divergence donne `ERR=49` ou `50`, ainsi que `PARITY_FIRST_OFFSET`/`PARITY_FIRST_CASE`.

## Benchmark ciblé — une seule campagne

- 4, 8 et 16 Bobs ; images et coordonnées identiques pour les deux méthodes.
- **64 itérations par cas, par méthode et par passage** ; deux passages avec ordre **BASIC puis Batch, ensuite Batch puis BASIC**. `BENCH_RUNS=12`, `BENCH_FRAMES=768`; **3 584 Bobs dessinés par méthode**.
- Mesure **draw-only** : aucun Swap, Wait VBL, capture, allocation, remplissage de fond ou tri Z **dans la zone chronométrée**. Le remplissage du fond identique est effectué **avant chaque mesure** ; aucune sélection de Z différente entre les deux méthodes.
- `Timer` mesure le temps en ticks, **pas les cycles CPU**. La configuration 68020 14 MHz/JIT OFF se règle dans WinUAE, et le fichier indique `CPU` / `CPU_ATTNFLAGS`, mais ne peut pas prouver la fréquence ni l'état JIT.
- Champs `BENCH_BOBS 4/8/16 BASIC_TICKS … BATCH_TICKS … SAVED_TICKS …`, détail `PASS0`/`PASS1`, `TOTAL_BASIC_TICKS` et `TOTAL_BATCH_TICKS`.
- Attention : ce benchmark **n'est pas directement comparable en valeur absolue** aux ~56,67 / 81,33 / 132 ms de P2.1, car il exclut volontairement les coûts de fond, présentation et tri Z. La comparaison pertinente est **BASIC contre Batch dans le même programme**.
- Aucun gain présumé. En cas de `Timer=0` ou de dessin refusé, le verdict est FAIL (pas un gain artificiel).

## Nettoyage prévu du code de test embarqué

**Nettoyage obligatoire avant toute version publiable après les essais P2.4 :** retirer du **binaire natif** la commande temporaire `Aga Bob Probe` (token public, stub AP20, routine `PROBE_CODE` et toutes références embarquées), sans supprimer le moteur `Aga Bob Batch`. Mettre à jour le générateur, les offsets et les références de groupe AP20, contrôler ABI/relocations/portée BSR.W et limite 65 534 octets, puis construire la **nouvelle candidate uniquement dans `dist/AMOSPro_AGA.Lib`**, sans toucher à R84 `LAST_GOOD`. Rejouer les tests statiques/MC68020 et obtenir de **nouveaux** résultats WinUAE Runtime et Compiled : les Gates R86 ne sont pas transférables automatiquement au binaire nettoyé. Les tests et rapports restent archivés dans `tests/passed/`, `tools/` et `docs/` pour la non-régression : seule la sonde de diagnostic embarquée doit disparaître. Aucun tag, release ou promotion sans validation explicite.

## Validation et états

**Gate statique P2.4** : [workflow dédié](../.github/workflows/m19-p24-bobs-pixels-static.yml) ; contrôle d'empreinte R84/R86, archive P2.3, unicité ASC, code des 19 probes, 256 indices capturés, géométrie et 4/8/16 descripteurs, AB/BA et fenêtres de chronométrage. **Gate statique PASS** — [CI 43701540717](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43701540717). Le validateur a contrôlé les 256 valeurs possibles de pixel 1×1, les 19 attentes géométriques, le témoin P2.3 archivé et la structure AB/BA. **Pas de Runtime/Compiled P2.4 exécutés.**

**Gates WinUAE P2.4** : **PENDING** — les anciens journaux P2.3 ne valident **pas** les nouveaux oracles ni ce benchmark. Quand les fichiers seront exécutés, récupérer :
- `RAM:M19_P24_RUNTIME.TXT`
- `RAM:M19_P24_COMPILED.TXT`

Critères de PASS fonctionnel : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `PIXEL_OK 19`, `PIXEL_BAD 0`, `PIX_CAPTURE_BAD 0`, `PARITY_OK 3`, `PARITY_BAD 0`, `BENCH_RUNS 12`, `DRAW_ERR 0`, `CLOSE_RETURNED 1`. Les temps se rapportent **séparément**, même en cas d'absence de gain.

**LAST_GOOD R84 non modifiée ; pas de branche, tag ou release.** La CI générale historique `Artifact integrity` est suivie séparément ; elle peut comporter des garde-fous anciens ne reconnaissant pas encore R86.

**Migration R87 du test P2.4 :** l'appel initial à `Aga Bob Probe` est supprimé, mais les 19 oracles, 3 parités et 12 fenêtres de timing sont conservés. **Les résultats P2.4 sur R86 n'ont jamais été exécutés** ; les validations seront effectuées uniquement sur la R87 sans Probe.
