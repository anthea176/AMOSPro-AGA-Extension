# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 18 novembre 2026.** Cette page recense la référence installable, la priorité technique et les travaux suivants. **Ce n'est pas un journal de commits.** L'[ancien contenu intégral](ROADMAP_HISTORY_2026-11-17.md), les [preuves](NEXT_SESSION.md) et les [règles du projet](../EXTENSION_SOURCE_RULES.md) sont consultables séparément.

## 1. Référence actuelle

| Élément | État vérifié |
| --- | --- |
| **Bibliothèque de travail** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 B7-m2 — candidate de travail pour relance WinUAE**, **102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`, **86 commandes / 181 entrées AP20**, quatre unités natives. Source reproductible via `tools/build_m19_b7m2_close_reset_in_memory.py::build_close_reset()`. |
| **Test fonctionnel actif (Gate C à réaliser)** | [`M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc`](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10911 octets**, SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`, [notice WinUAE](../tests/current/README.md). Off/On, 2→1→0→2→4→8→16→64→16, sans FPS ; [ancien benchmark](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) conservé dans Git. |
| **Validation** | **Gate A B7-m2 PASS** (75 groupes MC68020 après 194 contrôles B7-m1). **Gate B B7-m1 : premier lancement 405/405 PASS, deuxième lancement FAIL ERR 14**. **Gate B B7-m2 relance : PASS sur deux lancements Runtime sans Erase All. Gate C : banc corrigé, essai Compiler à refaire**. Benchmarks B7-m1 précédents conservés comme preuves historiques ([rapport décor](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md)). Gate C Compiler / D matériel **NON TESTÉES**. |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, sans nouvelle promotion. |

**API Bob :** `Aga Bob Blit` dessine immédiatement ; `Aga Bob _N,_X,_Y,_I`, `Aga Bob Off _N` et `_OK=Aga Bob Draw` sont disponibles. **B7-m1 a validé visuellement les neuf étapes à la première exécution mais a échoué au deuxième lancement (ERR 14). B7-m2 corrige le reset : Gate A PASS, Gate B Runtime PASS en relance. Le banc est désormais ouvert à Prg State=-1 pour qualifier Gate C (non testée).** Gate C Compiler de B7-m2 NON TESTÉE.

La **cinquième unité native** a été validée en Gates A/B/C pour son banc de sondes, puis ces sondes ont été retirées : la version installable reste à **quatre unités**. [Rapport de l'expérience](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md).

## 2. Priorité — M19 : cycle de vie des Bobs persistants

**Acquis :** B7-m1 dispose d'un Draw explicite, de la barrière DIRTY/Swap, de la gestion Safe/Disp et du callback End ; **Gate A native PASS, incluant désormais Off/On et 64 Bobs sur deux placements MC68020**. Les quatre Bobs multi-banques et la restauration de fond ont **PASS Gate B Runtime**. Les anciennes recherches B4/B5/B6 sont détaillées dans [les rapports techniques](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md), sans confondre leur Gate A avec la candidate installée.

**Arrêt des benchmarks :** le dernier test de 720 frames sur décor texturé est documenté et conservé comme référence. L'[exemple public interactif](../examples/bob_local_restore/README.fr.md) en extrait le seul parcours **restauration locale + quatre Bobs** ; nouvel ASC autonome **PREFLIGHT PASS**, Runtime de cette variante encore à vérifier.

**Développement suivant :** [cycle de vie des Bobs](M19_NEXT_BOB_LIFECYCLE_2026-11-18.md), sans mesure FPS :

| Ordre | Fonction à qualifier | Résultat attendu |
| --- | --- | --- |
| **1** | `Aga Bob Off _N` puis réactivation — **Gate A PASS** | Gate B : vérifier la disparition visuelle et le réemploi du même ID/bank, sans Swap implicite |
| **2** | Plusieurs banques, IDs 1..64 — **Gate A PASS** | Gate B : vérifier les paliers 1/4/8/16/64 et le rendu masqué/opaque sur écran |
| **3** | Erreurs de banque/masque et Safe/Disp — **Gate A partielle** | Source active périmée et verrou DIRTY prouvés ; rendre visibles les erreurs sans présenter de frame partielle |
| **4** | Close/End — **Gate A PASS** ; réexécution à contrôler | Pas de libération double en modèle CPU ; retour AMOS et seconde exécution à qualifier en Gate B |

**Procédure :** **Gate A MC68020 PASS** ([CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44404123651)). **Nouveau test fonctionnel Runtime préparé et préflight PASS** ([source](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc)), **Gate B NON TESTÉE**, sans benchmark. Aucun nouvel AP20, changement de Lib, test Compiler ni promotion `LAST_GOOD` sans décision distincte.

## 3. Après M19 — pistes non engagées

| Sujet | Objectif |
| --- | --- |
| **M19 : animation et Bobs** | Décor reconstruit, ordre des objets, éventuelles API `Clear` / `Update` et cohérence du double buffering. Pas de nouveau benchmark FPS prévu. |
| **M19 : sprites matériels AGA / AMAL** | Chantier distinct : slots, DMA, priorités, palettes et intégration éventuelle à AMAL. |
| **M20 : tilemaps / scrolling** | Tilesets, caméra, dirty rectangles et gestion Fast/Chip. |
| **M21 : dual playfield** | Deux plans de jeu, palettes et défilements indépendants. |
| **M22 : joystick** | Tester d'abord `Joy(0)` / `Joy(1)` natifs en Runtime, Compiler et physique ; pas d'API AGA décidée. |
| **M23 : C2P direct** | Étudier la conversion chunky→planar dans le back buffer AGA, sans présumer des gains. |
| **M24 : Copper avancé** | Étudier les commandes au-delà des usages actuels. |
| **Autres études** | P2C, PNG indexé natif et optimisations justifiées par mesures reproductibles. |

**Backlog ≠ engagement.** Aucune signature nouvelle, échéance ni publication n'est approuvée par la seule présence d'une ligne.

## 4. Méthode de suivi et historique

- **`main` uniquement** ; pas de branche, release ou promotion sans demande explicite. Une seule Lib dans `dist/AMOSPro_AGA.Lib` et un seul ASC actif sous `tests/current/` ; préserver `LAST_GOOD`, `tests/passed/` et les archives.
- CPU natif **MC68020/68EC020 minimum**. Gates **A** (CPU/ABI), **B** (WinUAE Runtime), **C** (vrai Compiler) et **D** (matériel) distinctes ; le résultat ne vaut que pour sa version et son scénario. WinUAE fonctionnel : 68030/JIT ON ; benchmarks : 68020/JIT OFF.
- **Ne plus empiler les comptes rendus dans cette page.** Les détails datés, échecs, SHA des candidats privés et anciennes Gates appartiennent aux [rapports techniques](NEXT_SESSION.md), à l'[historique des versions](LIBRARY_TEST_HISTORY.md) ou à l'[archive intégrale de l'ancienne roadmap](ROADMAP_HISTORY_2026-11-17.md).
- Mettre à jour cette roadmap **par remplacement ciblé** lors d'un changement de bibliothèque, de blocage, de décision ou de prochaine étape — **jamais** en ajoutant un nouveau chapitre de checkpoint en tête.
