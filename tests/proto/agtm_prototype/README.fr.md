# AGTM — prototypes AMOS pour WinUAE

**Statut 23/11/2026 : banque AGTM Runtime B PASS ; benchmark tuiles Runtime B et vrai Compiler C PASS.** [Rapport, journaux d'origine et ABK](../../../docs/AGTM_WINUAE_PROTOTYPES_2026-11-23.md). **Prototypes non distribués avec la Lib.**

Ces deux fichiers sont des **prototypes autonomes** pour étudier AGTM sans modifier l'extension installée. Ils emploient des instructions AMOS et des commandes AGA **déjà existantes dans M19 P2d**, sans nouveau token, moteur ASM ou format graphique natif. Le lancement du chantier natif M20 reste prévu **après Dual Playfield M21**.

Version de référence : `dist/AMOSPro_AGA.Lib` **M19 P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` ; `LAST_GOOD` identique et protégée. Les chaînes `LIBRARY_EXPECTED` des logs indiquent une attente, **pas une preuve du binaire réellement installé**.

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

Les deux fichiers `.asc` sont en ASCII pur, **préflight strict `amos_preflight.py --strict-target --fail-on-warnings` PASS localement**. Les **21 tests du préflight** passent. Un modèle de pixels Python indépendant a également confirmé l'équivalence logique du décalage 16 px avant exécution Amiga, sans prouver le comportement de `BltBitMap`.

**Gates par source :** banque DATA AGTM `AGTM_BANK_ROUNDTRIP.asc` : B Runtime PASS, C Compiler non testée. Benchmark `AGTM_TILE_BENCH.asc` : B Runtime PASS et C vrai Compiler PASS. **Aucun moteur natif M20 testé ; D physique non testée.** La version binaire P2d installée reste à vérifier indépendamment de `LIBRARY_EXPECTED`. `tests/current/`, `tests/passed/`, `dist/`, `LAST_GOOD`, tokens et sources ASM inchangés.

[Spécification AGTM v1](../../../docs/RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md) · [Roadmap](../../../docs/ROADMAP.md).
