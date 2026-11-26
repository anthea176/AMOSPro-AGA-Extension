# AGTM — prototypes AMOS pour WinUAE

**Statut 23/11/2026 : banque AGTM Runtime B PASS ; benchmark tuiles Runtime B et vrai Compiler C PASS.** [Rapport, journaux d'origine et ABK](../../../docs/AGTM_WINUAE_PROTOTYPES_2026-11-23.md). **Prototypes non distribués avec la Lib.**

Ces fichiers sont des **prototypes autonomes** pour étudier AGTM sans modifier l'extension installée. Ils emploient des instructions AMOS et des commandes AGA **déjà existantes dans M19 P2d**, sans nouveau token, moteur ASM ou format graphique natif. Le lancement du chantier natif M20 reste prévu **après Dual Playfield M21**.

Version de référence historique des deux premiers bancs (23/11) : **M19 P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Pour le nouveau banc de scrolling fin, voir la référence L2b en section 4. Ne pas assimiler la Lib de travail courante à l'ancienne P2d. Les chaînes `LIBRARY_EXPECTED` des logs indiquent une attente, **pas une preuve du binaire réellement installé**.

## 1. Prototypes disponibles

### [AGTM_BANK_ROUNDTRIP.asc](AGTM_BANK_ROUNDTRIP.asc)

**But :** valider sous le vrai AMOS Professional la représentation AGTM dans une **banque DATA**, la sauvegarde `Save` au format `.ABK`, l'effacement, le rechargement `Load` et la comparaison des indices.

- Banque **26 obligatoirement libre** ; créera `RAM:AGTM_V1_TEST.ABK`, qui peut remplacer le fichier de même nom dans `RAM:`. Ne touche pas aux autres banques.
- Carte : **22×16**, **une couche**, **4 indices de tuiles 0..3**, données 352 octets + en-tête AGTM de 64 octets = **416 octets**.
- Après rechargement : signature, version, offsets, tailles, octets réservés et **toutes les 352 cellules** vérifiés.
- Résultats attendus : `RESULT 1`, `ERR 0`, `SAVE_ERROR 0`, `LOAD_ERROR 0`, `BYTE_MISMATCH 0`.
- Journaux : `RAM:AGTM_BANK_INTERPRETED.TXT`, `RAM:AGTM_BANK_RUNTIME.TXT` ou `RAM:AGTM_BANK_COMPILED.TXT`, selon `Prg State`.

Ce premier test **n'utilise pas l'écran AGA**, ne mesure pas les performances graphiques et ne prouve pas encore le fonctionnement d'un lecteur AGTM natif.

### [AGTM_TILE_BENCH.asc](AGTM_TILE_BENCH.asc)

**But :** mesurer sur le vrai MC68020/Blitter la différence entre le redessin intégral d'un décor et son décalage avec réparation de la bande découverte.

- **AMOS Professional + bibliothèque P2d ; AGA PAL, MC68020 minimum.**
- **Banques 20, 21, 22, 23, 24 obligatoirement libres**. Toutes sont libérées en sortie normale ou erreur gérée.
- Pas d'IFF, pas d'ABK externe : banque 20 chunky 16×16, banque 21 AGTM 22×16 (416 octets), banque 22 FICON8 (quatre tuiles), banques 23 et 24 pour les captures comparatives.
- **Indices AGTM 0..3**, convertis en identifiants **FICON8 1..4 uniquement lors du dessin**, mode opaque 0 (couleur 0 visible).
- Image : une couche de **20×16 tuiles 16×16**, soit **320×256 pixels, 8 plans**.
- **Méthode A — FULL :** 320 appels `Aga F Icon` pour la caméra décalée d'une tuile.
- **Méthode B — SCROLL :** un `Aga Blit Copy(16,0,0,0,304,256)` chevauchant dans le back buffer, puis 16 appels `Aga F Icon` pour la dernière colonne.
- Avant chaque mesure, le même décor avec caméra à zéro est redessiné **hors `Timer`**. Ordre de comparaison : **A/B puis B/A**, quatre répétitions par méthode et par passe.
- **Vérification réelle prévue** : `Aga C Block Capture` sur la même page back après chaque méthode ; comparaison **octet par octet des 81 920 octets planaires** capturés. Les captures, le contrôle, `Aga Swap` et les VBL sont **hors chronométrage**.
- Sur réussite : affichage quelques instants de la carte, fermeture AGA et retour AMOS.
- Résultats attendus : `RESULT 1`, `ERR 0`, `BENCH_RUNS 4`, `PIXELS_OK 81920`, `PIXEL_BAD 0`, `SWAPS 1`, `CLOSE_RETURNED 1`.
- Journaux : `RAM:AGTM_BENCH_INTERPRETED.TXT`, `RAM:AGTM_BENCH_RUNTIME.TXT`, `RAM:AGTM_BENCH_COMPILED.TXT`.

Les `PASSx_FULL` et `PASSx_SCROLL` sont des **ticks bruts AMOS `Timer`**. Leur résolution est nominalement 20 ms/tick en PAL. Un résultat à 0 tick est **sous la résolution**, pas un coût nul. Si nécessaire, augmenter `_REPS` dans le programme et refaire les **deux méthodes**.

Ce banc ne teste **ni le scrolling de 1 pixel non aligné, ni plusieurs couches, ni les acteurs**, ni le double buffering animé frame par frame. Il constitue une première mesure native discriminante et un test d'équivalence planaire.

## 2. Exécution WinUAE

1. Configuration de référence : **68020 à 14 MHz, AGA PAL, JIT OFF**, Chip RAM et Fast RAM disponibles. Vérifier le binaire P2d réellement installé sous `APSystem`, puis redémarrer AMOS Professional.
2. Dans un **programme vide**, faire **Project → Merge ASCII** sur `AGTM_BANK_ROUNDTRIP.asc` et l'exécuter. Vérifier `RESULT 1` et récupérer le journal `RAM:AGTM_BANK_...TXT`.
3. Ouvrir **un autre programme vide**, importer `AGTM_TILE_BENCH.asc` par **Merge ASCII**, exécuter et vérifier le rendu : un quadrillage de tuiles colorées, sans bord décalé ni déchirure. Après fermeture, relever les ticks et le résultat `PIXEL_BAD`.
4. **Si le Runtime fonctionne**, compiler **le même ASC** avec AMOS Compiler V2 et lancer le nouvel exécutable. Récupérer un **second journal** ; une Gate Compiler ne découle jamais d'une Gate Runtime.
5. Conserver les valeurs de `PASS0_FULL/SCROLL` et `PASS1_FULL/SCROLL`, les erreurs, les compteurs, une capture d'écran du banc et la configuration WinUAE. Ne calculer de gain qu'avec `RESULT 1`, `PIXEL_BAD 0` et des ticks positifs significatifs.

**À transmettre pour analyse :** `RAM:AGTM_BANK_RUNTIME.TXT`, `RAM:AGTM_BENCH_RUNTIME.TXT` puis `RAM:AGTM_BENCH_COMPILED.TXT` si la compilation a été tentée ; préciser fréquence/JIT/Chip/Fast réels et présence ou non d'un Guru/freezing. Les journaux doivent refléter les fichiers source exacts de ce dossier.

## 3. Provenance et limites de validation

Les deux premiers fichiers `.asc` sont en ASCII pur, **préflight strict `amos_preflight.py --strict-target --fail-on-warnings` PASS localement**. Les **21 tests du préflight** passent. Un modèle de pixels Python indépendant a également confirmé l'équivalence logique du décalage 16 px avant exécution Amiga, sans prouver le comportement de `BltBitMap`.

**Gates par source :** banque DATA AGTM `AGTM_BANK_ROUNDTRIP.asc` : B Runtime PASS, C Compiler non testée. Benchmark `AGTM_TILE_BENCH.asc` : B Runtime PASS et C vrai Compiler PASS. **Aucun moteur natif M20 testé ; D physique non testée.** La version binaire P2d installée reste à vérifier indépendamment de `LIBRARY_EXPECTED`. `tests/current/`, `tests/passed/`, `dist/`, `LAST_GOOD`, tokens et sources ASM inchangés.

[Spécification AGTM v1](../../../docs/RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md) · [Roadmap](../../../docs/ROADMAP.md).

## 4. Scrolling fin : nouveau prototype AMOS du 24/11/2026

**[AGTM_FINE_SCROLL_BENCH.asc](AGTM_FINE_SCROLL_BENCH.asc)** — **PREFLIGHT PASS + modèle hôte PASS ; Runtime B et Compiler C PASS (journaux reçus le 26/11/2026).** [Rapport et preuves](../../../docs/AGTM_FINE_SCROLL_WINUAE_2026-11-26.md). Aucun changement de Lib, aucun token AGTM.

### Référence et lancement

- Cible recommandée : socle protégé **P2d-L2b**, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, [LAST_GOOD](../../../dist/AMOSPro_AGA_LAST_GOOD.Lib), promu le 24/11. Le chantier Sprite utilise une candidate distincte : utiliser de préférence une installation WinUAE/AMOS séparée, sans modifier la Lib du dépôt ni perturber les essais Sprite. Indiquer le binaire réellement installé ; le texte `LIBRARY_EXPECTED` est une référence, non une preuve.
- Configuration recommandée : AGA PAL, MC68020 14 MHz, JIT OFF. Préciser la configuration réellement utilisée et la version du Compiler. Pour comparer avec les anciens résultats P2d, conserver les différences de version et de protocole explicites.
- Nouveau programme vierge, **Project → Merge ASCII**, banques **20 à 24 libres**. Pas de fichier externe ; les banques de travail sont générées à l'exécution, puis effacées sur sortie normale ou erreur gérée.
- Exécuter d'abord en Runtime, puis compiler le même ASC si le premier essai passe. Ne pas relancer les tests historiques par défaut.

### Géométrie et protocole

Carte AGTM 64×16 (1 088 octets), 16 tuiles FICON8 16×16, une couche opaque, écran 320×256×8 plans. Toutes les données chunky originales restent en banque 20 pour l'oracle de pixels.

1. **Conformité avant chronométrage :** pour chaque pas 1, 8, 16 px, deux déplacements dans chaque sens. La caméra 1 px commence à X=14 pour franchir une limite de tuile (14→15→16→15→14). Les pas 8 et 16 commencent à X=0. Après chaque mise à jour incrémentale, capture des huit plans puis redessin complet et seconde capture : 12 comparaisons intégrales, **983 040 octets comparés**, plus **1 008 pixels** relus directement dans les bitplanes et confrontés à la source chunky. Le moindre écart bloque la mesure et la présentation.
2. **Mesure :** FULL = toutes les tuiles visibles, y compris celles partiellement visibles aux bords ; SCROLL = copie chevauchante dans la page back, puis redessin des tuiles touchant la bande découverte. Deux passes A/B puis B/A par pas. Quatre déplacements dans chaque sens par série, soit **12 séries, 96 mises à jour chronométrées**. Une seule différence de `Timer` par série, avec initialisation du décor, captures de conformité, VBL, Swap et fermeture hors mesure.
3. **Affichage final :** un seul Swap, après les mesures, puis retour AMOS. Ce n'est **pas** encore un test d'animation alternant les pages physiques. Les pixels réécrits sur la bande incluent éventuellement un recouvrement avec la zone conservée ; aucune affirmation de trafic DMA exact.

Compteurs attendus par série de huit mises à jour (`_STEPS=4`), calculés et vérifiés sur hôte :

| Pas horizontal | FULL_ICONS | SCROLL_ICONS | SCROLL_COPIES |
|---:|---:|---:|---:|
| 1 px | 2 656 | 128 | 8 |
| 8 px | 2 624 | 128 | 8 |
| 16 px | 2 560 | 128 | 8 |

**Critères de réception :** `RESULT 1`, `ERR 0`, `CHECKS 12`, `COMPARE_BYTES 983040`, `BYTE_MISMATCH 0`, `ORACLE_CHECKS 1008`, `ORACLE_BAD 0`, `BENCH_RUNS 12`, `SWAPS 1`, `CLOSE_RETURNED 1`. Vérifier les compteurs par série et la mémoire avant/après. Pour les mesures de vitesse, `LOW_TICK_RUNS 0` est souhaitable ; un temps de moins de cinq ticks est trop grossier pour une comparaison robuste. En cas de faible résolution, adapter la répétition dans une nouvelle révision documentée et retester les deux méthodes, sans modifier la source déjà mesurée.

Les journaux à transmettre sont **`RAM:AGTM_FINE_RUNTIME.TXT`** et **`RAM:AGTM_FINE_COMPILED.TXT`** (ou `RAM:AGTM_FINE_INTERPRETED.TXT` en interprété strict). Les champs STAGE/CASE/CAM/DIR/METHOD/PASS, les premiers offsets divergents et les valeurs du premier pixel divergent permettent de localiser un échec. Les anciens fichiers AGTM_BANK/BENCH ne sont pas écrasés.

### Preuves de préparation

- ASC 11 102 octets, ASCII LF, Git blob `678b97867cfdd4485ea2a0517ab6c882150324f6`, SHA256 `a2d2de907f69e70a1dc86d0e7550dc5312d65a8a5ba6d6e648458be7ce70c3d6`.
- Préflight strict PASS ; 21 tests du préflight PASS localement.
- [Test hôte](test_agtm_fine_scroll_model.py) : `python -B tests/proto/agtm_prototype/test_agtm_fine_scroll_model.py` depuis la racine. **3 tests PASS**, dont empreinte exacte ASC, 24 transitions continues du parcours chronométré comparées à un oracle monde pixel par pixel, vérification des compteurs et des 12 captures logiques/1 008 pixels échantillonnés. Le modèle simule une copie chevauchante correcte ; il ne teste pas les instructions du chipset, les Safe réels ni le Compiler.
- **Runtime B et Compiler C PASS** : 12 contrôles, 983 040 octets planaires sans écart, 1 008 pixels de l'oracle conformes ; gains FULL/SCROLL pour 1, 8, 16 px de 5,59/5,30/5,42 en Runtime et 4,63/4,34/4,47 en Compiler. La configuration effective et la SHA installée restent non attestées par les logs. [Rapport détaillé](../../../docs/AGTM_FINE_SCROLL_WINUAE_2026-11-26.md). La source est conservée à l'identique.

## 5. Deux pages physiques, scrolling 2D et modifications — prototype du 26/11/2026

**[AGTM_DB_DIRTY_BENCH.asc](AGTM_DB_DIRTY_BENCH.asc) — PREPARE, PREFLIGHT PASS, modèle hôte 3/3 PASS. WinUAE Runtime B / Compiler C NON TESTÉS.**

### Lancement

- Cible recommandée identique au banc précédent : **P2d-L2b LAST_GOOD**, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`. Utiliser une installation AMOS de test séparée pour ne pas perturber le chantier Sprite. Indiquer le binaire et la configuration WinUAE réellement utilisés (CPU, fréquence, JIT, mémoire, PAL/NTSC, Compiler).
- Programme vierge : Project → Merge ASCII, sélectionner le nouvel ASC. Banques 20 à 24 libres, aucun fichier externe. Lancer Runtime puis, s'il passe, le même ASC compilé. Ne pas modifier les tests antérieurs.
- Journaux : **`RAM:AGTM_DB_RUNTIME.TXT`** et **`RAM:AGTM_DB_COMPILED.TXT`** ; variante INTERPRETED si Prg State=0. Transmettre les logs même en cas d'échec.

### Scène et séquence

Écran 320×256×8 plans. Carte AGTM 64×32, deux couches de 2 048 octets (payload complet 4 160 octets). Seize tuiles FICON8 16×16 : fond opaque mode 0, overlay non vide mode 1 et pen 0 transparent. Banque 20 : pixels chunky d'origine ; 21 : carte ; 22 : FICON8 ; 23 et 24 : captures planaires.

Chaque série réinitialise carte et deux pages (deux Swap hors chrono). Une révision et une caméra par page ; le rôle logique BACK change uniquement après réussite de Swap. Douze frames avec trajectoire horizontale, verticale, diagonale, retours, déplacement nul pour une page et un edit par frame. Six edits du fond (dont un hors écran), trois suppressions et trois insertions d'overlay. Le scrolling copie dans **la même page back**, répare les bandes en dessinant les tuiles qui les touchent (coins éventuellement redondants), puis repeint les cellules visibles modifiées depuis la révision propre à la page. Les cellules sont recomposées du fond à l'overlay. Aucun acteur/Bob dans ce banc.

- **Validation hors chronométrage (12 frames)** : capture du back incrémental, redessin complet sur la même page, comparaison de tous les octets planaires ; 6 pixels par frame relus indépendamment depuis la capture incrémentale et comparés à la carte et aux pixels chunky, notamment autour des edits visibles. Le redessin de référence rétablit un fond identique avant présentation ; une erreur interdit Swap.
- **Mesure sans captures de validation** : quatre séries de 12 frames, FULL/SCROLL puis SCROLL/FULL ; carte et deux pages remises à zéro hors chrono. `DRAW_TICKS` somme des différences Timer par frame autour du dessin uniquement (résolution grossière, quantification à chaque frame). `FRAME_TICKS` différence Timer sur toute la série, inclut edits, dessin, bookkeeping, Swap, reprises Swap et un VBL explicite après chaque présentation. Cette deuxième mesure est la référence la plus robuste du coût complet dans ce protocole. Aucun résultat de vitesse Amiga n'est préjugé.
- Initialisation Safe avec Fill et reprises bornées ; chaque Swap a des reprises bornées. Après Swap, attente VBL explicite. Un retour de dessin 0 après cette attente est un échec journalisé, pas une validation ni une reprise aveugle d'une frame potentiellement partielle.

### Réception

| Champ | Attendu |
|---|---:|
| RESULT / ERR | 1 / 0 |
| CHECKS / COMPARE_BYTES / BYTE_MISMATCH | 12 / 983040 / 0 |
| ORACLE_CHECKS / ORACLE_BAD | 72 / 0 |
| BENCH_RUNS / FRAMES_PER_RUN | 4 / 12 |
| SWAPS (10 init + 60 frames) | 70 |
| CLOSE_RETURNED | 1 |

Compteurs par série de 12 frames, déterminés par le modèle hôte :

| Méthode | GROUND | OVER | COPIES | PATCHES |
|---|---:|---:|---:|---:|
| FULL (0) | 4116 | 1011 | 0 | 0 |
| SCROLL (1) | 480 | 127 | 11 | 21 |

Contrôler aussi mémoire Chip/Fast, temps bruts et attentes de Swap. La comparaison ne démontre ni une cadence 50 FPS ni une performance A1200 standard. Pas de gros saut, historique perdu, gestion générique de dirty rects, Bobs, scrolling matériel ou moteur M20 natif.

### Provenance

ASC 12 012 octets ASCII LF, Git blob `8aa8776e15b4f071c7c5d3069e028f922d80155c`, SHA256 `5a2749c931cb3317a39de478b4c0d1bb0dcbf19d1a30414cc3ecd632fbcee80e`. Préflight strict local PASS, 21 tests du préflight PASS. [Modèle hôte et tests](test_agtm_db_dirty_model.py), 3 tests PASS ; vérification de la SHA source, 12 frames par méthode comparées à l'oracle monde pixel par pixel et préservation de l'autre page du modèle, compteurs et éditions transparentes. La simulation n'est pas un test réel de Safe/Disp, du Blitter ou de la compilation.

Depuis la racine du dépôt :

~~~sh
python -B tests/proto/agtm_prototype/test_agtm_db_dirty_model.py
~~~

M20 natif reste prévu après M21. Aucun nouveau token, binaire, ASC actif ni changement de LAST_GOOD.
