# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 18 novembre 2026.** Cette page recense la référence installable, la priorité technique et les travaux suivants. **Ce n'est pas un journal de commits.** L'[ancien contenu intégral](ROADMAP_HISTORY_2026-11-17.md), les [preuves](NEXT_SESSION.md) et les [règles du projet](../EXTENSION_SOURCE_RULES.md) sont consultables séparément.

## 1. Référence actuelle

| Élément | État vérifié |
| --- | --- |
| **Bibliothèque de travail** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 P0j-b7-m1 — candidate de travail validée en Runtime sur le scénario Bob**, **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, **86 commandes / 181 entrées AP20**, quatre unités natives. Source reproductible via `tools/build_m19_p0j_end_lifecycle_in_memory.py::build_multiframe()`. |
| **Dernier test actif, conservé pour régression** | [`M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), [notice WinUAE](../tests/current/README.md). Pas de nouveau benchmark prévu. |
| **Validation** | **Gate A MC68020 PASS** (793 contrôles multiframe + **194 contrôles cycle de vie B7-m1**, [rapport](M19_B7M1_BOB_LIFECYCLE_GATE_A_2026-11-18.md)). **Gate B Runtime PASS** : Bobs 120 frames, puis A/B/C 720 frames sur fond uni et décor texturé. Décor : **A/B 25,05 FPS**, **C 48,98 FPS**, avec **719 retries VBL** (temps de synchronisation inclus). [Rapport décor](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md) · [Fond uni](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md). **Gate C Compiler / D matériel NON TESTÉES**. |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, sans nouvelle promotion. |

**API Bob :** `Aga Bob Blit` dessine immédiatement ; `Aga Bob _N,_X,_Y,_I`, `Aga Bob Off _N` et `_OK=Aga Bob Draw` sont disponibles. **Le rendu de quatre Bobs est validé en Runtime B ; Off/réactivation et 1/4/8/16/64 Bobs sont maintenant Gate A PASS sur la Lib exacte, mais leur Gate B reste à effectuer**. Gate C Compiler de B7-m1 NON TESTÉE.

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

**Procédure :** **Gate A MC68020 de ce jalon PASS** ([CI 44404123651](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44404123651)). Étape suivante : **un seul nouveau test fonctionnel Runtime**, sans benchmark. Aucun nouvel AP20, changement de Lib, test Compiler ni promotion `LAST_GOOD` sans décision distincte.

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
