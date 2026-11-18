# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 18 novembre 2026.** Cette page recense la référence installable, la priorité technique et les travaux suivants. **Ce n'est pas un journal de commits.** L'[ancien contenu intégral](ROADMAP_HISTORY_2026-11-17.md), les [preuves](NEXT_SESSION.md) et les [règles du projet](../EXTENSION_SOURCE_RULES.md) sont consultables séparément.

## 1. Référence actuelle

| Élément | État vérifié |
| --- | --- |
| **Bibliothèque de travail** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 P0j-b7-m1 — candidate de travail pour Gate B Runtime**, **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, **86 commandes / 181 entrées AP20**, quatre unités natives. Source reproductible via `tools/build_m19_p0j_end_lifecycle_in_memory.py::build_multiframe()`. |
| **Test AMOS actif unique** | [`M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) et [notice WinUAE](../tests/current/README.md). |
| **Validation de cette bibliothèque** | **Gate A B7-m1 MC68020 PASS (793 contrôles multiframe, 88 B7 historiques)**. Le scénario antérieur Draw/Swap/Close a été observé en compilé. **Ancien banc 120 frames : Gate B Runtime PASS**, quatre lancements sans traînée (journal et capture utilisateur). **Banc A/B/C à fond uni : Gate B PASS (720/720, A ≈25 FPS, C ≈49 FPS recalculés sur Timer)**, avec 719 retries VBL confondant le coût de copie et la synchronisation. [Résultats](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md). **Banc actif à décor texturé : 720 frames A/B/C, Gate B NON TESTÉE**, sans Compiler. [Nouveau protocole](M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md). Gate D NON TESTÉE. |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, sans nouvelle promotion. |

**API Bob :** `Aga Bob Blit` dessine immédiatement. `Aga Bob` et `Aga Bob Off` sont exposées, mais **leur cycle de vie persistant et leur utilisation complète ne sont pas qualifiés en Runtime/Compiler**. `Aga Bob Draw` est désormais **intégré dans B7-m1 comme fonction numérique sans argument** ; les bancs Runtime à quatre Bobs en fond uni sont PASS, mais **le rendu sur décor texturé doit encore passer Gate B**, et la parité Compiler C reste NON TESTÉE.

La **cinquième unité native** a été validée en Gates A/B/C pour son banc de sondes, puis ces sondes ont été retirées : la version installable reste à **quatre unités**. [Rapport de l'expérience](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md).

## 2. Priorité — M19 : afficher les Bobs persistants

**Objectif :** un rendu Blitter de **1 à 64 Bobs multi-banques**, dans le back buffer `Safe`, **sans projection temporaire de `bank_active_state`**, sans Swap implicite, sans mémoire Chip périmée et avec refus sûr d'une frame invalide.

**Jalon B4 : Gate A MC68020 PASS, 104 contrôles** ([CI renforcée 44179811049](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44179811049), initialement 60 contrôles). Le parcours Safe/WaitBlit de 64 Bobs utilise les banques d'origine sans shadow, dessine les masques en Chip, garde le front intact et n'effectue aucun Swap. Candidate privée AP20 **100 596 octets** (SHA256 `b6a318118d0f8c58ab839d905c4094b8de27b6f481d411c647626266d69a6a7b`). **Tests renforcés PASS :** masque corrompu refusé avant DMA, clipping pixel-exact, échec tardif SafePort avec back partiel constaté. **P0j-b5 source-only : Gate A MC68020 PASS (86 contrôles, [CI 44182795423](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44182795423))** : un Draw privé raté verrouille la présentation, le token existant `Aga Swap` est routé vers un garde de refus avant le vrai Swap AGA, et le Close natif P0c doit seul réinitialiser la barrière après fermeture réussie. **P0j-b7 : Gate A MC68020 PASS, 88 contrôles ; la candidate est maintenant installable pour la campagne B/C autorisée** ([CI 44185874211](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44185874211)). B7 corrige le callback End laissant le verrou DIRTY après fermeture, et maintient le verrou lors de réponses Safe/Disp en attente. Candidate en mémoire **102 072 octets**, SHA256 `f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b`, 86 commandes, 181 entrées, quatre unités, PC16 max 28 600. **Bascule de la seule Lib active + de l'ASC B7 autorisée, sans promotion LAST_GOOD ; B/C/D à exécuter et à documenter séparément.** [Rapport B7](M19_P0J_END_LIFECYCLE_GATE_A_2026-11-17.md). **B6 historique :** API numérique Draw, Gate A 52 contrôles ([rapport B6](M19_P0J_PUBLIC_DRAW_API_GATE_A_2026-11-17.md)), intégrée ensuite dans B7. . Gates B/C/D non engagées. **Gates B/C/D de B4 non réalisées**. [Contrat et preuves](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md).

| Ordre | Travail à faire | Critère de réussite |
| --- | --- | --- |
| **1** | **P0j-b2 : préparation Chip explicite — PASS source-only**. | **46 contrôles MC68020 PASS** ; deux banques distinctes, copie Chip contrôlée, cache sans recopie et zéro écriture du shadow. [Preuve](M19_P0J_EXPLICIT_BANK_STAGE_GATE_A_2026-11-17.md). |
| **2** | **P0j-b3/b4 : résolution et route Blitter explicites — PASS Gate A source-only**. | 64 Bobs banques 10/11, masques pixel-exacts, front intact, aucun shadow modifié, aucun Swap. |
| **3** | **Verrouiller la présentation après échec de frame**, y compris après un Blit réussi. | Refus avant DMA des images/masques corrompus ; échec tardif teste le back partiel ; garantir que `Aga Swap` ne puisse présenter une page invalide et définir la reconstruction. **B5 a PASS 86 contrôles Gate A sans changer la Lib installée ; Gates B/C encore nécessaires.** |
| **4** | Intégrer le rendu au registre des objets et **sécuriser Close/End**. | Identité de banque conservée après `Aga Bob Off`, allocations libérées une seule fois, pointeurs DMA invalidés, fermeture et réouverture sûres. |
| **5** | **B6 : API numérique Draw — Gate A source-only PASS ; aucune installation**. | 52 contrôles MC68020 : token `0`, modèle de dispatch interpréteur/Compiler, ABI 0/1, Swap gardé. **Restent** : choix de promotion vers l'unique Lib/ASC uniquement sur autorisation, Gate B Runtime puis Gate C vrai Compiler, End/Close Safe pending et Gate D séparée. |

**Acquis sans installation :** P0i (76 contrôles, mais shadow temporaire non réentrant), P0j-a (68 contrôles, préflight de 64 images), P0j-b1/b2/b3 (lookup/staging/résolution Chip explicites), puis **P0j-b4 (104 contrôles Gate A PASS)**. B4 retire la projection temporaire, **sans garantir l'atomicité complète ni empêcher un `Aga Swap` explicite après erreur**. **Ces résultats source-only ne prouvent pas les Gates B/C/D et ne changent pas la bibliothèque installée.**

## 3. Après M19 — pistes non engagées

| Sujet | Objectif |
| --- | --- |
| **M19 : animation et Bobs** | Décor reconstruit, ordre des objets, éventuelles API `Clear` / `Update`, double buffering, benchmarks de frames complètes 4/8/16 Bobs. |
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
