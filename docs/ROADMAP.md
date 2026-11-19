# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 19 novembre 2026.** Cette page recense la référence installable, la priorité technique et les travaux suivants. **Ce n'est pas un journal de commits.** L'[ancien contenu intégral](ROADMAP_HISTORY_2026-11-17.md), les [preuves](NEXT_SESSION.md) et les [règles du projet](../EXTENSION_SOURCE_RULES.md) sont consultables séparément.

## 1. Référence actuelle

| Élément | État vérifié |
| --- | --- |
| **Bibliothèque de travail** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 B7-m2 — candidate de travail validée sur le scénario Bob Lifecycle en Runtime et Compiler**, **102 400 octets**, SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`, **86 commandes / 181 entrées AP20**, quatre unités natives. Source reproductible via `tools/build_m19_b7m2_close_reset_in_memory.py::build_close_reset()`. |
| **Test fonctionnel actif (Gates B/C PASS)** | [`M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc`](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc), **10911 octets**, SHA256 `a5b5325b677984fd18114e6983df1bebb3f04e3ce626a482fb4ef5a50665cdec`, [notice WinUAE](../tests/current/README.md). Off/On, 2→1→0→2→4→8→16→64→16, sans FPS ; [ancien benchmark](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/cb3d97aec357bc726ea26047b6d3cb2c90b82247/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) conservé dans Git. |
| **Validation** | **Gate A PASS** MC68020 (75 groupes). **Gate B PASS** : deux lancements Runtime consécutifs, 405/405 frames et 9/9 étapes, sans `Erase All` ni redémarrage. **Gate C fonctionnelle PASS** : un exécutable AMOS Compiler, 405/405 frames, 9/9 étapes, `ERR 0`, `PATH_OK`. **Gate D NON TESTÉE** ; pas de relance compilée ni de contrôle complet des pixels du binaire compilé. [Rapport des preuves B/C](M19_B7M2_GATES_BC_2026-11-19.md). B7-m1 reste FAIL à la seconde exécution (`ERR 14`). |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, sans nouvelle promotion. |

**API Bob :** `Aga Bob Blit` dessine immédiatement ; `Aga Bob _N,_X,_Y,_I`, `Aga Bob Off _N` et `_OK=Aga Bob Draw` sont disponibles. **B7-m2 corrige le défaut de relance B7-m1 sur le scénario Off/On/64 Bobs : Gates A/B/C PASS** ([preuves](M19_B7M2_GATES_BC_2026-11-19.md)). Ce résultat n'autorise pas de nouvelle API ni de promotion `LAST_GOOD`.

La **cinquième unité native** a été validée en Gates A/B/C pour son banc de sondes, puis ces sondes ont été retirées : la version installable reste à **quatre unités**. [Rapport de l'expérience](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md).

## 2. Priorité — M19 : Clear/Update P0 après validation du cycle de vie

**Nouveau checkpoint B8 (19/11/2026)** — Candidate AP20 **source-only** de `Aga Bob Clear` et `Aga Bob Update` : **115 744 octets**, SHA256 `00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae`, 88 commandes / 184 entrées, PC16 29 962. Premier Update B7/B8 intégré **Gate A MC68020 PASS** ([CI 44635843744](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44635843744), 59 contrôles, deux placements), avec AmigaOS/Blitter simulés. Bootstrap End sans dessin par le premier SET Bob ; si aucun SET n'a eu lieu, premier Update refusé et rollback. **B8 n'est pas installée ; Gates WinUAE/Compiler non testées.** Prochaines actions : traiter le contrat du cas 0 Bob/absence de SET et ABA, demander une bascule explicite de l'unique Lib pour exécuter B/C. [Rapport](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).


**Acquis :** B7-m2 a validé le scénario Off/On, réactivation, masques, banques mixtes et 64 Bobs en **Gate A native, Gate B Runtime (deux relances) et Gate C Compiler (une exécution)**. La correction Close élimine le refus `ERR 14` de B7-m1 dans ce scénario. Le retour `End` sans Close et la relance compilée demeurent à qualifier séparément. Les anciennes recherches B4/B5/B6 sont détaillées dans [les rapports techniques](M19_P0J_NO_SHADOW_DRAW_GATE_A_2026-11-17.md), sans confondre leur Gate A avec la candidate installée.

**M19 B8 — Clear/Update source-only : transaction et Update atomique enregistré Gate A PASS.** Le gestionnaire de deux snapshots et la chaîne `Safe/WaitBlit/Close/End` restent source-pinnés. [**80 contrôles de transaction MC68020 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44628023301), plus [**48 contrôles Update atomique + 36 intégrés vrai B7 préflight/Draw/Close et copie B8 + 60 régressions B7 PASS**](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44628948845). **Candidate mémoire 115 180 octets**, SHA256 `62b9d3236197d5b7340237278719d3caa17b0b3df456c4bbe300c03d801dcae2`, **86 commandes, 182 AP20, cinq unités** `[142,153,156,177,181]`, portée PC16 max **29 558**. `Clear` restaure les fonds physiques Safe, `Update` enchaîne atomiquement `Prepare → vrai Draw B7 → Finish`, ou `Abort` DIRTY. **BLOQUANT : premier Update sans callback End B7 déjà enregistré (bootstrap), génération Open/Close ABA, tokens publics et Gates B/C.** Aucun nouveau token, aucune installation ni changement B7-m2/ASC/`LAST_GOOD`. [Rapport technique](M19_B8_CLEAR_UPDATE_MODEL_2026-11-19.md).

**Arrêt des benchmarks :** le dernier test de 720 frames sur décor texturé est documenté et conservé comme référence. L'[exemple public interactif](../examples/bob_local_restore/README.fr.md) en extrait le seul parcours **restauration locale + quatre Bobs** ; nouvel ASC autonome **PREFLIGHT PASS**, Runtime de cette variante encore à vérifier.

**Développement suivant :** [cycle de vie des Bobs](M19_NEXT_BOB_LIFECYCLE_2026-11-18.md), sans mesure FPS :

| Ordre | Fonction à qualifier | Résultat attendu |
| --- | --- | --- |
| **1** | `Aga Bob Off _N` puis réactivation — **Gates A/B/C PASS sur ce banc** | Un contrôle visuel de chaque étape en mode Compiler reste hors preuve |
| **2** | Plusieurs banques, IDs 1..64 — **Gates A/B/C PASS sur ce banc** | Palier 64 visible dans la capture Runtime ; pas d'oracle pixel complet du compilé |
| **3** | Erreurs de banque/masque et Safe/Disp — **Gate A partielle** | Source active périmée et verrou DIRTY prouvés ; rendre visibles les erreurs sans présenter de frame partielle |
| **4** | Close / réouverture — **Runtime B PASS en relance ; Compiler C PASS une fois** | `End` sans Close et seconde relance Compiler : **NON TESTÉS** |

**Suivi :** [Gate A B7-m2](M19_B7M2_CLOSE_RESET_GATE_A_2026-11-18.md) et [Gates B/C WinUAE PASS](M19_B7M2_GATES_BC_2026-11-19.md). Le [test actif](../tests/current/M19_B7M1_BOB_LIFECYCLE_RUNTIME_01.asc) reste inchangé, sans benchmark. Aucun nouvel AP20, changement de Lib, test supplémentaire ou promotion `LAST_GOOD` décidé par ce compte rendu.

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
