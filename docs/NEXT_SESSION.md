# Reprise actuelle — AMOSPro AGA Extension

**NOUVEAU CHANTIER DOCUMENTÉ — SPRITES MATÉRIELS AGA (15/11/2026), PAS DE CODE NI DE TEST :** [contrat S0/S1/S2/S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md). Deux moteurs **séparés** : Bobs logiciels M19 (Blitter, banque multi-images 256 couleurs, priorité P0) versus **Sprites matériels AGA** (8 canaux DMA, largeur 16/32/64 via FMODE, 3 couleurs+transparent, paires attachées 15+transparent, choix de tranches de palette AGA, Chip/Copper/Intuition). **S0 audit** écran privé/ressources/ownership avant API ; **S1** Sprite 16 px ; **S2** attaché/largeurs/coordonnées/palettes ; **S3** multiplexage/AMAL facultatif/collisions. Les « 56 computed Sprites » du manuel AMOS OCS ne sont PAS 56 canaux AGA. Ne pas installer de nouvelle API sans vérification AP20/Compiler et Gates distinctes. R84 LAST_GOOD et R88 inchangées. Note de liaison ajoutée au [plan M19 historique](M19_SPRITES_BOBS_AMAL_PLAN.md) et au [contrat Bob](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md).

---

**FEUILLE DE ROUTE M19 P0/P1/P2 (15/11/2026) — DOCUMENTATION UNIQUEMENT :** le [contrat Bobs AGA](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md) contient désormais l'inventaire fonctionnel tiré des chapitres 7.01–7.04 du manuel AMOS. **P0 :** banques/capture/mask/Chip, objets persistants, `Aga Bob Off`, `Aga Bob Update`, `Aga Bob Clear`/`Aga Bob Draw` ; rendu dans le back buffer AGA, **pas de `Aga Swap` implicite**. **P1 :** lecture X/Y/image, hotspot, priorités, Paste, Limit, édition de banque. **P2 :** collisions, HREV/VREV/REV, Set Bob, intégration AMAL, automatisation éventuelle. Les nouveaux noms AGA sont des propositions **non implémentées** ; préflight/token AP20/Compiler avant codage. **R84 LAST_GOOD inchangée, R88 candidate inchangée ; aucune nouvelle Gate validée.**

---

**M19 Bobs AGA — CONTRAT UTILISATEUR MIS À JOUR (15/11/2026), CONCEPTION UNIQUEMENT :**
- **API cible** (non implémentée) : `Aga Bob Bank N`, `Get AGA Bob I,X1,Y1,X2,Y2` (**sans `To`**, bornes inclusives), `Make AGA Bob Mask I,C`, `No AGA Bob Mask I`, `Aga Bob N,X,Y,I`, `Aga Bob Bank Free N`. `Save`/`Load` AMOS natifs pour les ABK.
- **Banques multi-images 1..8 bitplanes/256 couleurs** : Bobs planaires **non compressés** et masques séparés ; pas de RLE dans les Bobs animés. **AGAPIC/RLE/Fast existant conservé pour les grandes images**, sans refonte.
- **Numéros de banques AMOS choisis par l'auteur** : `Aga Bob Bank N` sélectionne/crée la banque et prépare automatiquement les données DMA en **vraie Chip RAM** si nécessaire. `Load` AMOS peut rester en Fast : la préparation est déclenchée explicitement par `Aga Bob Bank N`, **sans commande AMCAF, copie manuelle ni seconde banque numérotée**.
- **Sécurité** : une entrée Chip associée par banque, réutilisable par plusieurs Bobs ; `Aga Bob Bank Free` libère seulement les ressources internes, invalide les Bobs dépendants. Après un `Load`/`Erase` natif qui remplace une banque, la resélection `Aga Bob Bank N` est contractuelle. Vérifier `MEMF_CHIP` réel, la durée de vie des pointeurs, `Safe`/`Swap`, la sauvegarde ABK, le Compiler.
- **État** : aucune nouvelle commande testée ni build produite ; R88 reste candidate, R84 `LAST_GOOD` protégée ; aucune promotion, branche, release ou modification du test ASC actif.
- [**Contrat complet M19 Bobs AGA**](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md).

---

## M19 P2.8 — diagnostic WinUAE du 15/11/2026 : banque AGPC en Fast RAM

**R88 v0.13.33 Gate A PASS (130 cas) ; WinUAE Runtime B FAIL sur le banc original, `ERR 12`**. Le journal `M19_P28_DIAG_RUNTIME.TXT` montre `B11/B13 LENGTH 360`, `AGPCACHE`, flags AGPC 3, mais `CHIP_AFTER_LOAD=CHIP_BEFORE=1 796 336` et `FAST_AFTER_LOAD-FAST_BEFORE=-768` : les deux banques de 384 octets (avec enveloppe AMOS) resident en Fast RAM. `Aga Cache Blit` renvoie 0 dans les deux modes sur les deux banques, conforme au refus `MEMF_CHIP` du coeur M18. **Diagnostic termine sans Guru : `DIAG_DONE 1`, `ERR 0`, `CLOSE_RETURNED 1`** ne constituent pas une Gate B PASS.

**ASC actif corrige (tests/courant)** : [`M19_P28_R88_CACHE_BLIT_FPS_01.asc`](../tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc), Git blob `001396551cad6fed57903b714bc374e0988f63ea`, staging AGPC en **vraies banques Chip Data 11/13** (via temp 20, copie exacte du payload 360 octets et du nom AGPCACHE, sans modifier les flags AMOS). **Correction PREPAREE uniquement** : nouvelle Gate B WinUAE attendue ; Gate C Compiler non testee. Les binaires R88 candidat, R87 archive et R84 `LAST_GOOD` sont inchanges. Pas de branche, promotion, tag ni release. [Rapport du diagnostic](M19_P28_R88_CHIP_BANK_DIAGNOSTIC_2026-11-15.md).

---

## CANDIDATE ACTIVE R88 — correction du chemin (15/11/2026)

**`dist/AMOSPro_AGA.Lib` contient R88 v0.13.33** (**75 040 octets**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`). La **R87 v0.13.32 précédente** est archivée sans changement dans `dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib` (**73 184 octets**). Les quatre banques P2.8 restent dans `tests/fixtures/m19_p28/`, l'unique ASC dans `tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc`. **Gate A native R88 PASS ; Gates WinUAE B/C NON TESTÉES.** R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` intacte et non remplacée. Aucun tag, release, promotion ni branche. [Contrat du changement](M19_P28_R88_ACTIVE_CANDIDATE_2026-11-15.md).

---

## ARCHIVAGE R88 GATE A SUR GITHUB — uniquement expérimental

La bibliothèque **R88 v0.13.33 (75 040 octets, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`)** est conservée sur `main` sous [`dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib`](../dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib). Les **quatre banques ABK v1/v2** du banc sont également conservées durablement sous [`tests/fixtures/m19_p28/`](../tests/fixtures/m19_p28/). [Vérificateur SHA/taille](../tools/verify_p28_archive.py) et [CI de génération](../.github/workflows/m19-p28-agapic-planar-cache-gate-a.yml) : Gate A PASS. **R87 candidate active et R84 `LAST_GOOD` restent intactes, WinUAE Runtime et Compiler R88 non testés, aucun binaire promu.**

---

## CHANTIER ACTUEL — P2.8 R88 expérimental : Gate A native PASS, banc WinUAE préparé

**R88 v0.13.33 est construite en mémoire uniquement** : **75 040 octets**, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`. 78 commandes / 88 entrées AP20 ; nouvelle commande tentative `Aga Cache Blit(CacheBank,X,Y,Mode)`, **16×16×8 seulement, cache AGPC en Chip RAM**, alpha 1-bit indépendant des couleurs, v1/v2. **Gate A 68020 PASS : 130 cas Interpreter + Compiler V2 emulé**, en complément des 288 oracles host et 48 cas M18 core. L'ancien échec d'oracle venait d'un stride physique de 18 octets contre 10 attendus à tort par le test ; correction et rerun PASS [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43730486672). **Ce n'est PAS WinUAE/AMOS Compiler réel.**

**Nouveau seul ASC actif** : `tests/current/M19_P28_R88_CACHE_BLIT_FPS_01.asc` (350 lignes, Git blob `a9ee1aaa64d9b588e5b2d6e6134d63ec848e6181`, préflight AMOS strict PASS). **Quatre banques sources** v1/v2 AGAPIC/AGPC générées par `tools/m19_p28_winuae_bundle.py`, même motif et masque indépendant. La CI fournit une archive séparée **`M19_P28_R88_GATE_A_ONLY_WINUAE_BUNDLE`** avec la **bibliothèque expérimentale R88**, l'ASC, les quatre ABK et les consignes d'installation. **Pas d'écriture dans dist, aucune promotion.**

L'ASC compare **8 captures complètes** avant 12 séries de dessin seul (4/8/16, 64 répétitions AB/BA) et 12 séries de **frames complètes** (4/8/16, 24 frames par série, 288 Swap), incluant fond, Wait Vbl et Swap. Récupérer **`RAM:M19_P28_RUNTIME.TXT` / `RAM:M19_P28_COMPILED.TXT`**, puis analyser gains de dessin et FPS réels séparément. **Gates B/C R88 NON TESTÉES, aucun gain P2.8 encore démontré.**

**R87 active inchangée** `dist/AMOSPro_AGA.Lib` (73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`), **R84 `LAST_GOOD` inchangée**. main exclusivement, pas de branche, tag, release ou promotion.

---

## CHANTIER EN COURS — M19 P2.8 P0 (alpha independant)

**Sources nouvelles sur `main` :** `tools/m19_p28_agapic_planar_cache.py` et `tools/test_m19_p28_agapic_planar_cache.py` ; [contrat P2.8](M19_P28_AGAPIC_PLANAR_CHIP_ALPHA_2026-11-15.md) ; [workflow Gate A](../.github/workflows/m19-p28-agapic-planar-cache-gate-a.yml). Convertir AGAPIC v1/v2 en snapshot planaire **avec alpha independant des indices couleur**, garder l'ownership en banque DATA et rejeter les buffers/preparations incomplets. Cas 16×16×8 : bloc 288 octets compatible avec le **coeur M18/P5 natif existant**, mais **PAS avec l'ancien wrapper AP20**, qui imposait `alpha == OR des plans couleur` et doit etre remplace avant toute API publique AGPC. **Gate A native a executer en CI** ; **AUCUN nouveau binaire R88, AUCUNE Gate B/C P2.8, AUCUN FPS mesure pour P2.8**.

**Priorite suivante apres Gate A :** pont AGPC/AP20 pour une vraie banque Chip verifiee `TypeOfMem`, puis images hors 16×16, un benchmark complet avec fond, double buffering, Swap et cout de staging inclus. R87 et R84 `LAST_GOOD` restent identiques ; main exclusivement, aucune promotion.

---

## PRIORITÉ ACTUELLE — M19 P2.8 : cache AGAPIC planaire et vrai rendu masqué

**Constat P2.7 (WinUAE réel, 15/11/2026)** : le rendu AGAPIC RLE coûte **553 contre 225 ticks FICON8** en Runtime, **522 contre 198** en Compiled (somme 4/8/16 Bobs), soit **−59,31 % / −62,07 %**. La copie Blitter **opaque, pré-stagée** économise **41,67 % / 45,90 %** par rapport au CPU opaque. **Les neuf captures comparées sont identiques en Runtime et Compiled** (`PARITY_OK 9`, `PARITY_BAD 0`), `RESULT 1`, `ERR 0`, mémoire stable, fermeture réussie. **P2.7 Gate B Runtime PASS / Gate C Compiled PASS**. [Résultats détaillés](../benchmarks/RESULTATS_M19_P27_R87_CPU_RLE_FICON_BLITTER_2026-11-15.md), [log Runtime](../benchmarks/M19_P27_RUNTIME.TXT), [log Compiled](../benchmarks/M19_P27_COMPILED.TXT).

**Étape à développer :** cache AGAPIC pré-décodé, **sans perte du masque alpha indépendant** (y compris couleur zéro opaque), préparation hors frame, propriété AMOS de la mémoire, validité après Erase/Load et Blitter masqué Chip→Chip (reprendre M18 pour ABI, Safe et WaitBlit). Benchmarker **cache CPU vs vrai cache Chip/Blitter**, staging inclus/amorti, puis la frame complète avec Swap, décor et FPS. **P2.8 reste NON IMPLÉMENTÉ / NON TESTÉ.** Pas de modifications de l'actuel binaire R87 avant nouveaux tests natifs, aucune promotion automatique, branche `main` uniquement, R84 `LAST_GOOD` protégée.

**Source P2.7 archivée** `tests/passed/M19_P27_R87_CACHE_CPU_BLITTER_01.asc` **inchangée** (Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`). Une copie reste dans `tests/current/` comme référence unique jusqu'à la préparation du prochain ASC ; ne pas l'interpréter comme un nouveau test à refaire.

---

## HISTORIQUE — M19 P2.7, préparation du banc cache et Blitter

**Un seul ASC actif** : `tests/current/M19_P27_R87_CACHE_CPU_BLITTER_01.asc` (Git blob `e1062818abdfeb2d7e699d8c1dc9e9696250af65`). R87 v0.13.32 inchangée, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. Le programme crée le **même motif** 16×16 en AGAPIC v1/v2 et FICON8, vérifie **9 comparaisons intégrales** (opaque, masqué, X décalé, clipping, copie Blitter), puis chronomètre 4/8/16 Bobs masqués et un transfert opaque Blitter 8 Bobs. **Ne pas confondre copie Blitter opaque déjà stagée et rendu AGAPIC masqué natif**. **Gate A nouveau modèle/préflight local : PASS ; Gate B/C P2.7 NON TESTÉES.** WinUAE demandé : MC68020 14 MHz, PAL, JIT OFF, même ASC en Runtime et AMOS Compiler V2. Journaux `RAM:M19_P27_RUNTIME.TXT` et `RAM:M19_P27_COMPILED.TXT`. [Contrat P2.7](M19_P27_AGAPIC_CACHE_BACKENDS_2026-11-15.md).

**P2.6 désormais qualifié** : Runtime et Compiled `RESULT 1 / ERR 0 / VERDICT PASS` dans les journaux transmis ; gains Batch **2,42 % / 0,43 %** cumulés. ASC **archivé octet pour octet** dans `tests/passed/M19_P26_R87_DRAW_BENCH_01.asc`. [Résultats](../benchmarks/RESULTATS_M19_P26_R87_DRAW_2026-11-15.md). **Ne pas refaire le smoke ou le Batch pour P2.7.** R84 `LAST_GOOD` intangible. main seulement, pas de branche/tag/release/promotion.

---

## HISTORIQUE — M19 P2.6 R87 : préparation du banc BASIC vs Batch (15/11/2026)

**À tester maintenant :** `tests/current/M19_P26_R87_DRAW_BENCH_01.asc` (**267 lignes**, Git blob `c6c03b24bb273027492776ba24e53193ec52198b`). Uniquement **4/8/16 Bobs**, 64 répétitions, passes AB puis BA, **12 séries draw-only**, sans Z-sort, Fill, Swap, VBL ou allocation *pendant les chronos*. Le programme journalise les ticks bruts `BASIC_TICKS`, `BATCH_TICKS`, `PASS0_N` et `PASS1_N` dans `RAM:M19_P26_RUNTIME.TXT` puis `RAM:M19_P26_COMPILED.TXT`. **P2.6 Runtime/Compiled NON TESTÉ**, aucun gain présumé. Configuration WinUAE 68020/14 MHz/PAL/JIT OFF. [Protocole](M19_P26_R87_DRAW_PERFORMANCE_2026-11-15.md).

**Le smoke P2.5 R87 a déjà PASS en Runtime et Compiled** (`RESULT=1`, `ERR=0`, `VERDICT=PASS`, `DRAW=3`, `REJECT=3`, mémoire Chip/Fast stable). Son fichier source est maintenant archivé **sans modification** : `tests/passed/M19_P25_R87_BOBS_SMOKE_01.asc`, Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`. Les journaux P2.5 ne sont **pas** des benchmarks ; ne pas relancer un nouveau smoke à la place de P2.6. Le brouillon P2.4 reste en `tests/design/` non validé.

**Candidate R87 v0.13.32 inchangée** : `dist/AMOSPro_AGA.Lib`, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. R84 `LAST_GOOD` intouchable. **main uniquement**, pas de tag, branche supplémentaire, release ou promotion.

---

## HISTORIQUE — M19 P2.5 R87, smoke AMOS après audit du skill

Le nouveau **seul test actif** est `tests/current/M19_P25_R87_BOBS_SMOKE_01.asc` (Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`, 209 lignes) : base du véritable test R86 P2.3 PASS, retrait du Probe R87, des fausses validations pixel et du benchmark non qualifié. Vérification des banques **avant tout Erase** via `_BANKS_SAFE`. Préflight strict `amos-pro-aga-rules` **PASS**, 21 tests du checker **PASS** en local ; nouvelle CI dédiée à contrôler. **Gates B/C R87 NON TESTÉES.**

L'ancien `M19_P24_BOBS_PIXELS_BENCH_01.asc` est déplacé **octet pour octet** dans `tests/design/M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc`. Il comportait 611 lignes et n'a jamais été validé en Runtime/Compiler ; il n'est plus l'ASC actif ni un test `passed`. Ses travaux de pixel oracle et de benchmark reprendront une fois le smoke R87 validé sous AMOS.

**Fichiers attendus WinUAE pour le test actuel :** `RAM:M19_P25_RUNTIME.TXT` puis `RAM:M19_P25_COMPILED.TXT` (68020/14 MHz/PAL/JIT OFF). Résultat ciblé : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `CLOSE_RETURNED 1`. [Guide et problèmes corrigés](M19_P25_R87_AMOS_SMOKE_REVIEW_2026-11-15.md).

La candidate `dist/AMOSPro_AGA.Lib` **R87 v0.13.32 est inchangée** ; R84 `LAST_GOOD` reste intouchable. Pas de branche, tag, release ou promotion.

---

## CHANTIER ACTIF — M19 P2.5 R87 : suppression du témoin BOBS (15/11/2026)

**Branche `main` uniquement.** Le nouveau constructeur `tools/build_m19_p25_no_probe.py` retire définitivement **du candidat R87** le token `Aga Bob Probe`, son stub et la routine `PROBE_CODE` ; `Aga Bob Batch` reste identique, indice AP20 **82**, groupe BOBS **85**, 77 commandes et 87 entrées AP20. Le nouveau test natif MC68020 `tools/test_m19_p25_no_probe.py` vérifie ABI, absence de Probe, contenu moteur, portée BSR.W, pixels, sécurité du front, erreurs et R84 historique. Le workflow R86 obsolète est désactivé en push pour éviter un retour arrière automatique.

**État validé du chantier :** candidate R87 v0.13.32 enregistrée dans `dist/AMOSPro_AGA.Lib` (**73 184 octets**, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`) ; **CI native MC68020 Gate A 9/9 PASS** ([run 43719479059](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43719479059)), P2.4 statique PASS. Aucun binaire R86 ne reste actif, ses preuves demeurent historiques. **R84 `LAST_GOOD` absolument inchangée.** Le seul ASC actif `tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc` est ciblé **R87** (plus d'appel au Probe). Les anciens logs R86 P2.3 **ne valident pas** R87. **Gates B/C R87 NON TESTÉES**, aucun gain de performance présumé. Nouvelle validation sous WinUAE 68020/14 MHz/JIT OFF via `RAM:M19_P24_RUNTIME.TXT` et `RAM:M19_P24_COMPILED.TXT`. Aucune branche/tag/release ou promotion.

[Contrat R87](M19_P25_R87_NO_PROBE_2026-11-15.md) · [Test actuel](../tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc).

---

## HISTORIQUE — M19 P2.4, banc pixels + benchmark non validé (15/11/2026)

**Nettoyage obligatoire avant toute version publiable après les essais P2.4 :** retirer du **binaire natif** la commande temporaire `Aga Bob Probe` (token public, stub AP20, routine `PROBE_CODE` et toutes références embarquées), sans supprimer le moteur `Aga Bob Batch`. Mettre à jour le générateur, les offsets et les références de groupe AP20, contrôler ABI/relocations/portée BSR.W et limite 65 534 octets, puis construire la **nouvelle candidate uniquement dans `dist/AMOSPro_AGA.Lib`**, sans toucher à R84 `LAST_GOOD`. Rejouer les tests statiques/MC68020 et obtenir de **nouveaux** résultats WinUAE Runtime et Compiled : les Gates R86 ne sont pas transférables automatiquement au binaire nettoyé. Les tests et rapports restent archivés dans `tests/passed/`, `tools/` et `docs/` pour la non-régression : seule la sonde de diagnostic embarquée doit disparaître. Aucun tag, release ou promotion sans validation explicite.

- **Branche main uniquement** ; aucun tag, aucune release, aucune promotion. Binaire **R86 v0.13.31** dans `dist/AMOSPro_AGA.Lib` : 73 232 octets, SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`. **R84 LAST_GOOD** reste figée : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.
- **Test actif unique** : `tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc`. **L'ancien ASC P2.3 archivé sans changement** : `tests/passed/M19_P23_BOBS_BATCH_01.asc`, blob Git `19ad2044252783454f4082c118e53b34a6b83478`. Le P2.3 dispose déjà de **Gates A/B/C PASS** ; son rapport demeure [M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md).
- **Nouveau P2.4** : 19 indices de couleur vérifiés par décodage d'une capture AGAPIC v1 1×1 (pas de faux flag `CLIP`/`MASK`/`ORDER`), front contrôlé après Swap explicite, parité d'images complètes BASIC/Batch 144×144 sur **4/8/16 Bobs**, comparaison de tous les octets RLE.
- **Mesure unique prévue** : draw-only, **64 itérations × 2 passages AB/BA** pour 4/8/16 Bobs ; **12 sous-runs et 3 584 dessins par méthode**. Aucun Swap, Wait VBL, fond, capture, tri Z ou allocation dans les plages chronométrées. `Timer` en ticks ; ne pas comparer directement les ms P2.1, périmètres différents. WinUAE cible 68020/14 MHz/PAL/JIT OFF.
- **Gates P2.4 WinUAE B Runtime/C Compiled : PENDING**, nouveaux journaux attendus `RAM:M19_P24_RUNTIME.TXT` et `RAM:M19_P24_COMPILED.TXT`. Ne pas annoncer de gain sans mesures réelles. **Gate statique P2.4 PASS** ([run 43701540717](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43701540717) : 19 points, 256 indices et 3 cas de parité modélisés). Cette validation est distincte des Gates WinUAE.
- **CI générale historique** : dernier diagnostic `build_aga_r84_agapic.py` refuse encore le SHA de la candidate R86 lors d'un test de reconstruction R84 ; chantier d'outillage séparé, aucune modification de la bibliothèque R84.

[Contrat de validation P2.4](M19_P24_PIXEL_ORACLE_BENCH_PLAN_2026-11-15.md).

---

## HISTORIQUE — M19 P2.3 R86 : Gates A/B/C PASS, pas de promotion (15/11/2026)

**Branche `main` uniquement**, aucun tag, release ou changement de branche. **Candidate active** `dist/AMOSPro_AGA.Lib` R86 v0.13.31 : **73 232 octets**, SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`, **78 commandes / 88 entrées AP20**, blocs C2P 5 558 / IFF 2 508 / BOBS 5 226 / AGA 56 580. `Aga Bob Batch(DescriptorBank,Count)` fonctionne dans le scénario livré, `Aga Bob Probe` est conservée. **R84 `dist/AMOSPro_AGA_LAST_GOOD.Lib` toujours figée** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`).

**Gates :** A native MC68020 **8/8 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700178749)), **B WinUAE Runtime PASS** (`PRG_STATE 1`, `RESULT 1`, `ERR 0`), **C WinUAE Compiled PASS** (`PRG_STATE -1`, `RESULT 1`, `ERR 0`). Les deux journaux fournis établissent `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `CLOSE_RETURNED 1`, mémoire Chip/Fast revenue au point initial dans chaque exécution. **BASIC_TICKS 13 / BATCH_TICKS 13 dans les deux modes : aucun gain démontré** sur quatre itérations avec fond inclus.

**Périmètre réel :** les flags `ORDER`/`CLIP`/`MASK` de cet ASC sont mis à 1 après retour positif et ne vérifient pas indépendamment les pixels WinUAE ; les comparaisons de pixels sont celles de la Gate A native. Les logs affichent la chaîne de version ASC, **pas le SHA256 du binaire chargé**. Gate D Amiga physique non exécutée ; ne pas promouvoir `LAST_GOOD`.

**Seul test actif** : `tests/current/M19_P23_BOBS_BATCH_01.asc` ; blob Git `19ad2044252783454f4082c118e53b34a6b83478`, **ne pas modifier le test couvert par ces journaux**. Ancien témoin P2.2 déjà archivé octet pour octet dans `tests/passed/M19_P22_4UNIT_PROBE_01.asc`. Si un nouveau test est décidé, archiver d'abord le P2.3 sans le modifier puis ne garder qu'un ASC dans `tests/current/`.

**Suite recommandée** : nouveau banc ciblé avec oracles de pixels WinUAE pour transparence, chevauchement et clipping ; comparaison BASIC/Batch sur durée suffisante et sans confondre le coût du fond ou le cache Z. **Aucune campagne supplémentaire n'a encore été exécutée.** Le contrôle général `Artifact integrity` peut rester en échec pour des tests historiques/expérimentaux sans remettre en cause la CI ciblée ; vérifier sa cause exacte au besoin.

**État CI générale au 15/11/2026 : FAIL**, [run 43700905076](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700905076). La vérification **R86 à quatre unités** dans `test_generate_current_native_source.py` passe désormais (`STRICT R86 FOUR-UNIT SOURCE PROVENANCE PASS`), mais l'étape suivante réexécute le constructeur historique `build_aga_r84_agapic.py` qui refuse encore le SHA de la R86 active (`AssertionError: Unknown active dist binary during historical R84 rebuild`). **C'est un garde-fou de compatibilité des outils historiques, pas un échec du moteur R86 ou des Gates A/B/C**. Adapter ce contrôle de façon ciblée lors d'un chantier CI dédié, sans altérer la R84 figée et sans contourner la validation d'origine.

**Rapport signé par les deux journaux** : [M19 P2.3 R86 Runtime / Compiled](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md) · [Contrat API](M19_P23_BOBS_BATCH_CONTRACT.md).

---

## HISTORIQUE — M19 P2.3 R86 avant les journaux WinUAE (15/11/2026)

Sur `main` exclusivement, deux nouvelles commandes actuelles : `Aga Bob Batch(DescriptorBank,Count)` et témoin `Aga Bob Probe`. R86 v0.13.31: 78 commandes publiques, 88 entrées AP20, quatre unités natives. Le constructeur `tools/build_m19_p23_bob_batch.py` produit **uniquement** `dist/AMOSPro_AGA.Lib` avec `--write-dist` ; `LAST_GOOD` R84 reste intouchable (67904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). CI dédiée : `.github/workflows/m19-p23-bobs-batch-gate-a.yml`. Ne pas annoncer un PASS sans le résultat d'exécution de la nouvelle CI.

**Test actif unique** : `tests/current/M19_P23_BOBS_BATCH_01.asc`. Ancien témoin R85 à archiver dans `tests/passed/` avec les mêmes octets. Le Batch dessine en groupe sur le back buffer, ne fait pas Swap/Wait VBL, et peut laisser un frame partiel en cas d'erreur sur un Bob tardif : **si résultat 0, ne pas Swap**. Tests WinUAE Runtime et Compiled **en attente des vrais journaux** `RAM:M19_P23_RUNTIME.TXT` et `RAM:M19_P23_COMPILED.TXT` ; performance pas encore mesurée.

**Point CI préexistant** : `Artifact integrity` échoue déjà sur le jalon expérimental `Experimental Compiler V2 68000 bridge Gate A` (run 43698493395), indépendamment du test spécifique BOBS R85. [Contrat API](M19_P23_BOBS_BATCH_CONTRACT.md).

---


## ÉTAT ACTUEL — M19 P2.2 R85, témoin quatrième bloc PASS (15/11/2026)

**Correction de l'organisation : seul ASC actif = [`tests/current/M19_P22_4UNIT_PROBE_01.asc`](../tests/current/M19_P22_4UNIT_PROBE_01.asc)**, déplacé sans modification depuis `tests/design/`. **Ne plus chercher le nouveau test dans `tests/design/`.** Précédent P2.1 PASS archivé exactement dans [`tests/passed/M19_P21_ZCACHE_BENCH_01.asc`](../tests/passed/M19_P21_ZCACHE_BENCH_01.asc), blob Git `f75af1a84b4c658d5f1cb330d58d248413e72cc7`. Le source P2.2 correspond au blob Git `cd564aa660f8927b1c4d0b63456de58b5535fae0`.

**Journaux fournis** `M19_P22_4UNIT_RUNTIME.TXT` (`PRG_STATE 1`) et `M19_P22_4UNIT_COMPILED.TXT` (`PRG_STATE -1`) : **RESULT 1, VERDICT PASS, ERR 0, AGA_DETECT -1, BOB_PROBE 1, CLOSE_RETURNED 1** pour chacun. **Gate B Runtime du témoin PASS ; Gate C Compiled du témoin PASS.** [Rapport avec logs bruts](M19_P22_4UNIT_WINUAE_RUNTIME_COMPILED_2026-11-15.md). Ce résultat atteste le routage du quatrième groupe, pas `Aga Bob Batch`, pas un rendu d'images.

**Binaire de travail :** `dist/AMOSPro_AGA.Lib` R85 v0.13.30 (67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`). **R84 `LAST_GOOD`** protégée dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucune promotion. `main` exclusivement, aucune autre branche.

**Suite technique :** implémenter un véritable rendu groupé dans le quatrième bloc BOBS, puis valider cette fonctionnalité séparément. Les anciens états et liens cités plus bas sont des **notes historiques** et ne changent pas le test actif.

---


## HISTORIQUE — M19 P2.2, avant essais Runtime et Compiled (15/11/2026)

**Consigne explicite :** le binaire de travail est directement **[`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib)**, **pas dans `build/` ni un sous-dossier**. Version expérimentale **R85 v0.13.30** : 67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`, 77 commandes, 87 entrées AP20, quatre blocs C2P 5 558 / IFF 2 508 / BOBS 40 / AGA 56 580. **[`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib)** reste R84 v0.13.29, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, conservée **octet pour octet**, jamais écrasée.

**État technique :** **Gate A native/MC68020 PASS** (CI [43696972204](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43696972204)). Routage des 4 groupes : entrée publique `Aga Bob Probe` (index 82), groupes C2P=83, IFF=84, BOBS=85, AGA=86. Le témoin renvoie 1, **aucun rendu de Bob/BATCH encore** ; **Gates B WinUAE et C Compiler R85 NON TESTÉES**. Le constructeur `tools/build_m19_p22_fourth_unit_probe.py --write-dist` ne modifie que la Lib active après contrôle SHA de LAST_GOOD ; `--emit-base64` sert à constituer exactement le blob Git.

**Suite :** importer [`tests/design/M19_P22_4UNIT_PROBE_01.asc`](../tests/design/M19_P22_4UNIT_PROBE_01.asc) avec le **candidat R85**, jamais avec R84. Contrôler Gate B Runtime 68020 puis Gate C Compiler avant l'API de dessin groupé `Aga Bob Batch`. Un seul test actif reste `tests/current/M19_P21_ZCACHE_BENCH_01.asc` (P2.1 PASS) ; le témoin est volontairement dans `tests/design`. `main` seulement, ni nouvelle branche ni promotion LAST_GOOD.

[Contrat et historique du quatrième bloc](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md).

---


## M19 P2.2 — QUATRIÈME GROUPE NATIF BOBS, témoignage AP20 isolé (15/11/2026)

**Accord de l'auteur : « on se lance »** pour le quatrième bloc natif. Le premier incrément est volontairement **une preuve d'infrastructure** : `tools/build_m19_p22_fourth_unit_probe.py` reconstruit en mémoire une **bibliothèque expérimentale à quatre groupes** à partir de R84 v0.13.29 `LAST_GOOD`, conserve les 76 commandes R84 et les trois corps C2P/IFF/AGA, ajoute seulement `Aga Bob Probe` (témoin qui renvoie 1, **aucun dessin de Bob**). Le véritable `Aga Bob Batch(Bank,Count)` n'est **pas** encore implémenté et ne doit pas être présenté comme disponible.

**Gate A :** `tools/test_m19_p22_fourth_unit_probe.py` utilise l'émulateur Unicorn MC68020 pour l'interpréteur, le dispatcher V2, l'exécution du témoin et les retours ABI. [Workflow dédié](../.github/workflows/m19-p22-fourth-unit-gate-a.yml) : en cas de succès, dépose un fichier **expérimental téléchargeable** `M19_P22_4UNIT_PROBE_GATE_A_ONLY`. **En attendant le résultat CI, les Gates A/B/C P2.2 sont non validées.** Témoin AMOS volontairement placé sous `tests/design/M19_P22_4UNIT_PROBE_01.asc` ; **ne pas l'utiliser avec R84 seule**.

**Protection :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent strictement inchangés, tout comme l'unique ASC actif `tests/current/M19_P21_ZCACHE_BENCH_01.asc` (P2.1 PASS). `main` seulement, aucune branche/tag/release. [Contrat et statut](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md). Prochaine étape si Gate A PASS : Gate B WinUAE et Gate C Compiler avec binaire expérimental, puis étude de la boucle Batch AGAPIC/FICON8 et de ses appels inter-unités.

---


## M19 P2.1 — DERNIER BENCHMARK TERMINÉ : Gate B Runtime 68020 PASS (15/11/2026)

**Journal utilisateur :** `M19_P21_ZCACHE_RUNTIME.TXT`, `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68020`, `CPU_ATTNFLAGS 3`, `RESULT 1`, `VERDICT PASS`, `ERR 0` ; profil 14 MHz/JIT OFF précisé par l'auteur (non enregistré par le programme). **240 frames, 9 088 dessins, cinq invalidations, douze séries complètes**, `SORT_CALLS_TOTAL 1225`, `CACHE_BUILDS_TOTAL 17`, `CACHE_HITS_TOTAL 1188`, erreurs Sort/Fill/Draw/Swap 0/0/0/0, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, deltas Chip/Fast 0, `CLOSE_RETURNED 1`.

**Résultats (moyenne P0/P1, Timer PAL nominal 20 ms/tick) :** temps de composition BASE → CACHE : **4 Bobs 60,17 → 56,67 ms/frame (−5,8 %)** ; **8 Bobs 96,33 → 81,33 (−15,6 %)** ; **16 Bobs 189,67 → 132,00 (−30,4 %)**. Présentation VBL/Swap compris : 4 Bobs 80 → 61 ms, 8 Bobs 101 → 100 ms, 16 Bobs 200,5 → 140 ms.

**Conclusion :** le cache de l'ordre `(Z, ID)` avec invalidation explicite est recommandé dans le gestionnaire BASIC ; aucun changement de production n'est autorisé par ce test. Le dessin et le fond demeurent coûteux à 16 Bobs. **Fin du dernier essai demandé ; ne pas proposer une nouvelle campagne de benchmark.** Aucune API native décidée, R84 v0.13.29 `LAST_GOOD` intacte, `main` uniquement. Gates Compiler M19 et matériel physique non testées.

**Rapport officiel :** [Résultats M19 P2.1 Z-cache 68020/noJIT](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md). Seul ASC actif inchangé : [M19_P21_ZCACHE_BENCH_01.asc](../tests/current/M19_P21_ZCACHE_BENCH_01.asc).

---


## M19 P2.1 — dernier essai Z BASE vs CACHE, profil 68020 sans JIT (15/11/2026)

**Décision auteur :** « dernier essai », directement sous profil **WinUAE MC68020 14 MHz, PAL, JIT OFF**. **Un seul ASC actif** : [tests/current/M19_P21_ZCACHE_BENCH_01.asc](../tests/current/M19_P21_ZCACHE_BENCH_01.asc). L'ancien banc [M19_P2_BENCH_BOBS_01.asc](../tests/passed/M19_P2_BENCH_BOBS_01.asc) est **archivé avec son blob Git identique** (`4345d8728af1d6dba29a5936463219ac49b3b109`), et son [rapport 68020 PASS](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) reste la référence.

**P2.1 PRET, AUCUN LOG WinUAE ENCORE :** même source AGAPIC/FICON8 que P2 (4,8,16 objets) ; `BASE` trie à chaque frame, `CACHE` conserve l'ordre jusqu'à modification Z/visibilité/compte. Cinq contrôles d'invalidation avant mesure ; deux passages inversés BASE→CACHE puis CACHE→BASE. Chaque mode × N × passage : 120 demandes d'ordre, 60 compositions fond+Bobs (sans Swap) et 20 VBL+Swap. 120 Fill séparés ; résultat attendu `FRAME_OK 240`, `DRAW_OK 9088`, `SORT_CALLS_TOTAL 1225`, `CACHE_BUILDS_TOTAL 17`, `CACHE_HITS_TOTAL 1188`, `CACHE_INVALID_TESTS 5`, `BENCH_CASES 12`, `RESULT 1`, `ERR 0`. **Gate B de P2.1 à recevoir**, ne pas assimiler au précédent PASS.

**Journal attendu :** `RAM:M19_P21_ZCACHE_RUNTIME.TXT`, voir [instructions tests/current](../tests/current/README.md) et [protocole détaillé](../benchmarks/README_M19_P21_ZCACHE_68020_NOJIT.md). Échap signale `ERR 41`. `Timer` PAL nominal 20 ms/tick, aucune mesure de cycles CPU directe. Toute attente Safe en phase COMP invalide l'interprétation « temps CPU pur ». Pas d'AMOS Compiler ni de matériel physique testé pour P2.1.

**Aucun changement de bibliothèque :** R84 v0.13.29 `LAST_GOOD` protégée ; `main` uniquement, **aucune branche ni commande AP20 native nouvelle**. Le résultat du dernier A/B doit guider la décision sur le tri BASIC, pas déclencher automatiquement une nouvelle API.

---


## M19 P2 — benchmark MC68020/14 MHz/JIT OFF PASS ; analyse et prochaines optimisations (15/11/2026)

**Nouveau journal utilisateur :** `M19_P2_BENCH_BOBS_RUNTIME 68020 14Mhz noJIT.TXT`. `RUN_MODE RUNTIME`, `PRG_STATE 1`, `CPU 68020`, `CPU_ATTNFLAGS 3`, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK 240`, `DRAW_OK 9088`, erreurs Sort/Fill/Draw/Swap `0/0/0/0`, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, Chip/Fast delta 0, `CLOSE_RETURNED 1`. **14 MHz et JIT OFF déclarés par l'auteur, non auto-journalisés.** Bibliothèque R84 `LAST_GOOD` et source benchmark intactes.

**Deux passages, ticks bruts** (800 tris / 120 fonds / 120 compositions / 40 présentations par charge) :
- **4 Bobs :** tri 162/163 ; fond 188/188 ; comp 360/361 ; disp 160/160.
- **8 Bobs :** tri 604/604 ; fond 188/188 ; comp 578/577 ; disp 202/201.
- **16 Bobs :** tri 2347/2347 ; fond 188/188 ; comp 1137/1137 ; disp 401/401.

**PAL nominal 20 ms/tick :** composition ~**60,08 / 96,25 / 189,50 ms/frame** ; présentation ~**80,00 / 100,75 / 200,50 ms/frame** ; tri BASIC ~**4,06 / 15,10 / 58,68 ms/appel** (4/8/16). Fond constant ~31,33 ms/frame ; reste de dessin estimé ~6,2 ms par Bob, selon soustraction de séries indépendantes. À 16 objets, le tri représente ~31 % du temps de composition, avec des Z pourtant fixes.

**Comparaison :** 68030 avec JIT activé (test précédent PASS) composait ~23,25 / 23,42 / 23,83 ms/frame, non extrapolable au 68020 sans JIT. [Rapport 68020 et analyse détaillée](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) · [Rapport 68030/JIT](../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md). Les deux benchmarks sont qualifiés **Runtime WinUAE**, pas Compiler ou matériel.

**Suite recommandée, non engagée :** benchmark A/B **cache d'ordre Z en BASIC** (trier uniquement si Z, création, suppression, visibilité changent), puis mesure isolée des formats AGAPIC opaque/masqué et FICON8 et de la stratégie de fond. **Ne pas créer d'API native sans preuve d'un gain ciblé.** Le test actif reste `tests/current/M19_P2_BENCH_BOBS_01.asc`, seul ASC. P2.0 fonctionnel archivé, R84 `LAST_GOOD` inchangée, `main` uniquement.

---


## M19 P2 — benchmark complet 68030/JIT PASS, 68020 sans JIT attendu (15/11/2026)

**Second journal utilisateur `M19_P2_BENCH_BOBS_RUNTIME(1).TXT` :** WinUAE Runtime, `CPU 68030`, **JIT activé selon l'auteur (non enregistré dans le log)**, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK 240`, `DRAW_OK 9088`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, `SAFE_RETRIES 1` global, `COMP_SAFE_RETRIES 0` sur les six séries, Chip/Fast delta 0, fermeture 1.

**Ticks P0/P1 (800 tris / 120 fonds / 120 compositions / 40 présentations) :** N4 tri 0/0, fond 139/140, comp 140/139, disp 80/80 ; N8 tri 1/1, fond 140/139, comp 140/141, disp 80/80 ; N16 tri 6/6, fond 139/139, comp 143/143, disp 80/80. `Timer` PAL 20 ms/tick nominal : composition ≈ 23,25 / 23,42 / 23,83 ms/frame. **Ne pas extrapoler cette exécution JIT au MC68020 physique.**

**Rapport de référence :** [68030 JIT PASS](../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md) ; [premier run interrompu](../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md) conservé. Source `tests/current/M19_P2_BENCH_BOBS_01.asc` inchangée, seul ASC actif, bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée.

**Suite annoncée :** nouvel essai du même ASC en **MC68020 à 14 MHz, JIT OFF, PAL** ; conserver le journal distinct. Aucune API native approuvée.

---


## M19 P2 — premier journal benchmark 4/8/16, arrêt Échap (15/11/2026)

**Source active inchangée :** [tests/current/M19_P2_BENCH_BOBS_01.asc](../tests/current/M19_P2_BENCH_BOBS_01.asc) (SHA blob `4345d8728af1d6dba29a5936463219ac49b3b109`). Bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée. CI [`6138657` Artifact integrity PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43691301111).

**Journal utilisateur `M19_P2_BENCH_BOBS_RUNTIME.TXT` :** `RUN_MODE RUNTIME`, CPU annoncé `68030`, `RESULT 0`, `VERDICT FAIL`, **`ERR 20` = `Aga Key` a retourné 69 (Échap)**, `FRAME_OK 41/240`, `DRAW_OK 1736` (arithmétique des phases cohérente), `DRAW_FAIL 0`, `SWAP_FAIL 0`, `SAFE_RETRIES 0`, `SWAP_RETRIES 0`, `CHIP_DELTA 0`, `FAST_DELTA 0`, `CLOSE_RETURNED 1`.

**Mesures partielles P0 :** 4 Bobs : tri `0` tick/800, fond `139` ticks/120, composition `140` ticks/120, présentation `80` ticks/40 ; 8 Bobs : tri `1`, fond `140`, composition `140`, présentation **non terminée**. **16 Bobs et second passage totalement non mesurés**, les cases zéro sont des valeurs par défaut. Timer PAL nominal 20 ms/tick ; 4/8 composition ≈ 23,33 ms/frame, surtout liée au fond, mais la précision du timer et le mode Runtime interdisent d'en déduire une accélération ou une conclusion native. [Rapport détaillé](../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md).

**Prochaine action :** refaire l'ASC **inchangé** sans presser Échap, laisser 240 frames, conserver le fichier RAM: avant tout nouvel essai. Si `ERR 20` survient sans appui Échap, instrumenter le clavier au lieu de présumer une erreur d'utilisateur. Pour l'analyse cible, exécuter ensuite 68020/14MHz, PAL/JIT OFF, séparément du 68030. **Gate B benchmark non acquise ; aucune API native décidée.**

---


## M19 P2 — benchmark 4, 8 et 16 Bobs PRÊT, WinUAE à exécuter (15/11/2026)

**Accord utilisateur « ok » pour le benchmark proposé après le PASS P2.0.** Bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée, `main` uniquement. Aucune nouvelle instruction native, API AP20, branche ou release.

**Seul ASC actif :** [tests/current/M19_P2_BENCH_BOBS_01.asc](../tests/current/M19_P2_BENCH_BOBS_01.asc). Le P2.0 validé Runtime est archivé **octet pour octet** dans [tests/passed/M19_P2_OBJECTS_01.asc](../tests/passed/M19_P2_OBJECTS_01.asc) ; son [rapport PASS](M19_P2_WINUAE_RUNTIME_2026-11-15.md) reste la preuve, **pas** le benchmark qui n'a pas encore été testé.

**Protocole :** [benchmarks/README_M19_P2_BOBS_4_8_16.md](../benchmarks/README_M19_P2_BOBS_4_8_16.md). 4/8/16 objets, sources partagées générées avant chrono (1/4 AGAPIC masqués, 1/4 AGAPIC opaques, 1/2 FICON8 masqués), deux passages `P0/P1`. `Timer` PAL : **800 tris BASIC**, **120 Fill seuls**, **120 compositions sans Swap**, **40 frames VBL+Swap** par charge et passage. `Safe` contrôlé avec retries bornés, `Aga Swap` explicite, zéro dessin en interruption. Le banc **n'inclut pas AMAL**, afin d'isoler tri + dessin.

**Attendu :** exécution AMOS Runtime sous WinUAE AGA PAL / 68020 14MHz / JIT OFF (68030 possible pour contrôle séparé), banques 11..23 libres, rapport `RAM:M19_P2_BENCH_BOBS_RUNTIME.TXT`. `RESULT 1`, `ERR 0`, 16 objets préparés, `FRAME_OK 240`, `DRAW_OK 9088`, aucun échec Draw/Swap. Les champs `N4/N8/N16_P0/P1_*_TICKS` contiennent les **mesures à recevoir**. Attention : `Timer` donne un temps écoulé, pas des cycles CPU ; retries Safe/Swap à conserver.

**Statut : source construite et contrôlée statiquement, mais Gate B benchmark / chiffres WinUAE NON VALIDÉS.** Compiler M19 et Amiga physique non testés. La décision d'implémenter un gestionnaire natif n'est pas prise.

---


## M19 P2.0 — Gate B Runtime WinUAE PASS (journal reçu le 15/11/2026)

**Source de référence :** `tests/current/M19_P2_OBJECTS_01.asc` (sous-routines à préfixe `_`), bibliothèque R84 v0.13.29 `LAST_GOOD` inchangée. L'auteur a transmis `M19_P2_OBJECTS_RUNTIME.TXT`. **Gate B du prototype P2.0 PASS dans ce scénario** (`RUN_MODE RUNTIME`, `PRG_STATE 1`, CPU déclaré 68030, `RESULT 1`, `VERDICT PASS`, `ERR 0`).

**Mesures :** 240 frames, sources AGAPIC/FICON8 `6/4`, cinq objets créés et un supprimé, ID périmé/frame invalide/banque absente refusés `1/1/1`, masquage et réapparition `1/1`, priorité Z `2`, égalité stable `1`, sonde de superposition `PROBE_OK 1`/`PIXEL_DIFF 1`, 4 cas de clipping, 2 objets intégralement hors écran, 217 frames avec quatre objets dessinés, mouvements AMAL `239/239`, changements de frames `15/10`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, Chip/Fast delta `0/0`, `CLOSE_RETURNED 1`. [Rapport complet](M19_P2_WINUAE_RUNTIME_2026-11-15.md).

**Qualification limitée :** WinUAE Runtime 68030, 320×256, 256 couleurs/8 plans, banc P2.0 uniquement. **Ni AMOS Compiler M19 (Gate C), ni `PRG_STATE 0`, ni Amiga AGA physique (Gate D), ni cadence 50 FPS ne sont établis** par ce journal. La sonde RLE porte sur un seul pixel. Aucun développement d'API native approuvé.

**CI sur le commit préexistant `c65c820` :** [Artifact integrity PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337384) et [R84 Gate A ciblée PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43690337256). La validation Runtime ci-dessus est **indépendante** de cette CI. Le journal utilisateur ne comprend pas les valeurs affichées `LOG OPEN ERR` / `LOG CLOSE ERR`.

**Suite conseillée :** mesurer d'abord le coût CPU/Chip du gestionnaire BASIC avec des charges croissantes, puis décider si des commandes AP20 natives sont réellement justifiées. L'étude des sprites matériels AGA reste le volet P3 distinct. Conserver la bibliothèque et le banc P2.0 validé sans modification.

---


## M19 P2.0 — correction du nom des sous-routines et préflight (15/11/2026)

**Retour WinUAE de l'auteur :** capture AMOS Professional avec `Syntax error` à `Gosub Sort _OBJECTS`. Cause vérifiée : `SORT` est un mot-clé AMOS et le nom source `SORT_OBJECTS` était séparé en deux tokens. Le commit source déjà présent sur `main`, [`18b01a6`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/18b01a6976b9ac61a2c2bf676e69da558f8571b2), préfixe les 7 sous-routines et tous leurs `Gosub` par `_` (dont `_SORT_OBJECTS`), sans changer leurs traitements ni la bibliothèque R84.

**Régression CI identifiée :** le test historique `tools/test_current_ram_log.py` imposait `End` comme dernière instruction physique. Le P2.0 utilise **`End` puis les sous-routines `Gosub` terminées par `Return`**, syntaxe normale. Le contrôle est adapté pour accepter ce cas **sans autoriser un programme sans End ni boucle infinie terminale**. `tools/test_current_amos_blocks.py` signale désormais les noms commençant par une commande réservée (`SORT_`, `MOVE_`, etc.) et inclut un test de régression pour `Gosub SORT_OBJECTS`.

**Statut :** correction structurelle / source uniquement ; **un nouvel essai AMOS/WinUAE reste nécessaire** avant de prétendre P2.0 Gate B PASS. P1 archived unchanged, `LAST_GOOD` inchangée, aucun nouveau token/AP20. [Test actif](../tests/current/M19_P2_OBJECTS_01.asc) · [Consignes](../tests/current/README.md).

---


## M19 P2.0 — prototype BASIC, un seul ASC actif (15/11/2026)

**Accord auteur : « ok go » pour commencer le prototype P2.0**, pas d'autorisation d'ajouter un token/une API native. R84 v0.13.29 `LAST_GOOD` protegee, 68020 minimum. L'experience AP20 V3 parallele du commit `a36c8ed` est hors du perimetre M19 ; aucun de ses fichiers n'est modifie.

**Unique test actif :** [tests/current/M19_P2_OBJECTS_01.asc](../tests/current/M19_P2_OBJECTS_01.asc). Le banc P1 WinUAE-PASS a ete **archive octet pour octet** dans [tests/passed/M19_P1_AGAPIC_BOBS_01.asc](../tests/passed/M19_P1_AGAPIC_BOBS_01.asc). Ne pas annoncer P2.0 PASS sans journal WinUAE.

**Contenu :** gestionnaire AMOS BASIC par `Dim` et `Gosub/Return` : 4 objets initiaux (2 AGAPIC AMAL manuel + 1 FICON8 BASIC + 1 AGAPIC opaque BASIC), masquage/retour, changements de frames cadences, tri stable Z/ID, sondes 1x1 de priorite, quatre clips et culling, suppression ID4 puis nouveau ID5, refus d'ID mort et de frame/banque invalides. Fond complet sur back buffer Safe, `Aga Swap` explicite, journal `RAM:M19_P2_OBJECTS_RUNTIME.TXT`. Dimension 320x256x256, sources generees par le test, banques 11..23 libres.

**Qualification :** controles structurels de source et simulation de compteurs de 240 frames, **pas une compilation ni une execution AMOS**. Gate B P2.0 Runtime WinUAE EN ATTENTE ; C Compiler, D materiel et mode interprete strict non testes. Voir [instructions](../tests/current/README.md) et [contrat P2](M19_P2_OBJECT_MANAGER_CONTRACT.md). Reprendre directement avec le log WinUAE, puis decider si la gestion native est vraiment necessaire.

---


## M19 P2 — contrat d'objets proposé, pas d'API nouvelle (15/11/2026)

**Nouvelle référence de conception :** [M19_P2_OBJECT_MANAGER_CONTRACT.md](M19_P2_OBJECT_MANAGER_CONTRACT.md). L'auteur a autorisé l'étude P2. Proposition de **prototype d'abord en AMOS BASIC**, réutilisant AGAPIC v1/v2 et FICON8, avec objets logiques (ID, source/frame, X/Y et hotspot, Z stable, visibilité), mouvement BASIC ou AMAL manuel, composition uniquement sur back buffer Safe, zéro rendu en interruption et Swap explicite.

**Historique avant feu vert P2.0 :** proposition de contrat ; la version actuelle de reprise est en tête du fichier. Aucune signature AP20 native approuvée ; le P1 WinUAE PASS est maintenant archivé. R84 v0.13.29 `LAST_GOOD` et archives intactes.

**CI du commit P1-documentation :** les marqueurs de version EN/FR sont désormais validés dans le contrôle README ; un ancien préflight `tools/test_opt020_p1e_benchmark_static.py` rejette encore `M19_P1_AGAPIC_BOBS_01.asc` parce que sa liste de noms possibles s'arrête à R84. Le garde est limité au **benchmark historique hors tests/current** + **unique ASC actif** dans cette mise à jour. Pas de modification des formules du benchmark ni du binaire. **CI complète à revérifier**.

**Suite :** validation du contrat P2, puis un ASC P2.0 BASIC en remplaçant/archivant proprement le P1 courant ; Gate B Runtime sur le nouveau scénario, avant toute décision d'API native. Aucun sprite matériel : sujet P3.

---


## M19 P1 — Gate B Runtime WinUAE PASS (journal reçu le 15/11/2026)

**Source testée :** `tests/current/M19_P1_AGAPIC_BOBS_01.asc`, R84 v0.13.29 `LAST_GOOD` intacte. Journal auteur `M19_P1_AGAPIC_BOBS_RUNTIME.TXT` et capture WinUAE.

**Résultats :** `PRG_STATE 1`, `CPU 68030`, `RESULT 1`, `VERDICT PASS`, `ERR 0`, `CAP_OK 6`, `META_OK 6`, `PROBE_OK 1`, `PIXEL_DIFF 1`, `FRAME_OK 240`, déplacements 239/239, 15/10 changements d'image, 3 inversions de priorité, 46 frames avec chevauchement, 240 clips, 0 échecs de dessin/Swap, delta Chip/Fast 0, fermeture 1. **P1 Gate B PASS** sur le scénario Runtime 68030, 8 plans. [Rapport](M19_P1_WINUAE_RUNTIME_2026-11-15.md).

**Limites :** aucune validation M19 Compiler Gate C, interprété strict ni Amiga physique Gate D ; aucun nouvel objet matériel ni API.

**CI GitHub :** échec antérieur dans `tools/test_readme_api_coverage.py` en raison des marqueurs exacts de version absents des deux README, sans relation avec le rendu P1. Libellés ajustés dans ce commit documentaire, **nouvelle CI à vérifier**.

**Suite :** concevoir et faire valider le contrat d'objets P2 avant toute signature d'API ou implémentation native.

---


## M19 P1 EN COURS — multi-Bobs AGAPIC v1/v2 (14/11/2026)

**Unique ASC actif** : [tests/current/M19_P1_AGAPIC_BOBS_01.asc](../tests/current/M19_P1_AGAPIC_BOBS_01.asc). P0 archivé à [tests/passed/M19_P0_AMAL_BOBS_01.asc](../tests/passed/M19_P0_AMAL_BOBS_01.asc). Bibliothèque R84 v0.13.29 `LAST_GOOD` intacte ; `main` uniquement.

**Historique avant la validation Runtime P1 : prototype préparé** : six images AGAPIC 24×24, v1/v2, masquées et opaques, deux canaux AMAL en synchronisation manuelle, animation d'image contrôlée toutes les 16/24 frames, ordre de rendu alterné, comparaison de deux captures RLE 1×1 avec ordre de dessin inversé, quatre clips et redessin du fond dans le back buffer Safe avant Swap.

**Essai attendu :** AMOS Runtime, 320×256×256, banques 11..19 libres, puis journal `RAM:M19_P1_AGAPIC_BOBS_RUNTIME.TXT` et observation visuelle. `CAP_OK 6`, `META_OK 6`, `PIXEL_DIFF 1`, `FRAME_OK >= 180`, mouvements, frames, priorités, `DRAW_FAIL 0`, `SWAP_FAIL 0`, fermeture correcte. Gate B P1 maintenant attestée (voir première section) ; Gates C/D non testées. [Consignes](../tests/current/README.md) · [Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md).

---


## M19 P0 — résultat WinUAE et suppression du clignotement (14/11/2026)

**Validation reçue :** `M19_P0_AMAL_BOBS_RUNTIME.TXT` : `PRG_STATE 1` (Runtime), `CPU 68030`, `RESULT 1`, `ERR 0`, 211 frames, déplacements X/Y = 210/210, aucun refus Draw/Swap, mémoire Chip/Fast à delta 0, `CLOSE_RETURNED 1`. Le rendu des deux Bobs a été confirmé. **Gate B M19 P0 PASS dans ce scénario** ; aucune extrapolation au mode strictement interprété, Compiler ou matériel physique.

**Diagnostic visuel :** le clignotement était lié aux expressions AMAL `Let A=3-A` et `Let A=7-A` (alternance d'image à chaque frame), pas à une erreur observée de dessin/Swap. L'auteur confirme qu'il disparaît en retirant ces expressions. Source `tests/current/M19_P0_AMAL_BOBS_01.asc` mise à jour pour conserver les images fixes 1 et 3. **Nouveau journal de la version corrigée non reçu** ; le PASS chiffré correspond à la version initiale.

**Suite engagée :** P1 a désormais son banc actif ; voir la première section. Conserver R84 `LAST_GOOD` et ne pas ajouter d'API sans contrat approuvé. [Rapport](M19_P0_RUNTIME_DIAGNOSTIC_2026-11-14.md) · [Plan](M19_SPRITES_BOBS_AMAL_PLAN.md).

---


## Chantier M19 P0 ENGAGE — 14/11/2026 (apres R84 promue)

**Plan de référence approuvé :** [M19 sprites matériels, Bobs et AMAL](M19_SPRITES_BOBS_AMAL_PLAN.md). Première étape : AMAL manuel (`Synchro Off`, deux programmes `Amal ... To adresse`, `Synchro` dans la boucle BASIC), deux Bobs logiciels via `Aga F Icon` dans le back buffer AGA privé, sans dessin en interruption. **Aucune nouvelle commande native** ; R84 et `LAST_GOOD` restent identiques et protégées.

**Test AMOS courant unique :** `tests/current/M19_P0_AMAL_BOBS_01.asc` (remplace comme banc actif l'ancien R84 déjà figé dans `tests/passed/AGAPIC_R84_V1_V2_01.asc`). Ce P0 est un prototype source et doit être contrôlé sous AMOS/WinUAE ; **Gate B M19 P0 Runtime désormais attestée sur le scénario initial ; Gate C et mode strictement interprété non attestés**. Rapport attendu `RAM:M19_P0_AMAL_BOBS_<RUN_MODE>.TXT`. Suivre [tests/current/README.md](../tests/current/README.md). Un seul ASC courant et aucun binaire M19.

---


## R84 v0.13.29 — PROMUE `LAST_GOOD` le 14/11/2026 (autorisation explicite)

**Circuit unique sur `main` :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **76 commandes / 85 entrées AP20**, trois modules C2P/IFF/AGA (5 558 / 2 508 / 56 580 octets). **R83 historique** : SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, 64 188 octets, reconstruite par `tools/build_aga_r83_modular.py` et conservée dans Git.

**Validation :** Gate A CPU native/CI PASS (44 cas Info + 47 captures) ; **Gate C AMOS Compiler PASS** sur WinUAE 68030 avec une banque incluse lors de la compilation, 4/8 plans, `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 2`, Chip 0 et Fast **−11 920 octets**. **Gate B Runtime corrigée : NON attestée séparément**, ce que l’auteur accepte en autorisant la promotion, sans nouvel essai. Quatre fichiers ABK restent dans `RAM:` au moment de la mesure Fast ; aucune fuite native n'est établie par ce delta. `PRG_STATE 0` strict et Amiga physique Gate D non testés.

**Test actif unique :** `tests/current/AGAPIC_R84_V1_V2_01.asc`, copie identique figée dans `tests/passed/`. Pas de branche ni binaire parallèle, aucun tag, release GitHub ou publication Aminet. [Rapport de promotion](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Journal compilé](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md).

Les états R84 candidate, R83 et antérieurs ci-dessous sont **historiques**.

---

## HISTORIQUE — R84 v0.13.29 avant promotion (14/11/2026)

- **Unique binaire de travail :** `dist/AMOSPro_AGA.Lib`, R84 **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, 76 commandes / 85 entrées AP20 ; unités C2P 5 558, IFF 2 508, AGA/AGAPIC 56 580 (marge 8 954 octets).
- **`LAST_GOOD` R83 protégée :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, ses Gates A/B/C validées. **R84 candidate NON PROMUE.**
- Nouveaux points d’entrée : `Aga Bank Image Info(Bank,Champ)` (5 champs, v1 palette/ModeID absents=0, échec=-1) et `Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` (v1 ou v2). Ancienne `Aga Image Capture` préservée.
- **Gate A native CPU/CI R84 PASS** : 44 cas d'Info v1/v2, 47 captures v1/v2 sur vrai 68020 émulé, structure AP20/ABI, métadonnées/flux RLE, palette/ModeID, banque occupée, mémoire, dispatch.
- **Gates B Runtime WinUAE et C AMOS Compiler EN ATTENTE.** Test unique actif : `tests/current/AGAPIC_R84_V1_V2_01.asc`. Le test R83 est déjà dans `tests/passed`. Exécuter les 2 modes, collecter `RAM:AGAPIC_R84_RUNTIME.TXT` et `RAM:AGAPIC_R84_COMPILED.TXT`. Ne pas déduire une Gate D physique ni `PRG_STATE 0`.
- Pas de nouvelle branche, pas de tag/release/Aminet, pas de binaire parallèle. Ne promouvoir que sur nouvelle autorisation explicite.

[Roadmap](ROADMAP.md) · [Contrat](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Rapport Gate A](AGAPIC_R84_GATE_A_2026-11-14.md).

Les sections R83 et antérieures ci-dessous sont **historiques**.

---

## ÉTAT COURANT — R83 v0.13.28 PROMUE LAST_GOOD (14/11/2026)