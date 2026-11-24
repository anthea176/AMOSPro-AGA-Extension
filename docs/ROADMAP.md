# Roadmap — AMOSPro AGA Extension

> **T06B L2b — Runtime PASS :** T06B Runtime PASS sur L2b : 12/12 cycles, 12 Pattern immédiatement après Swap réussi sans VBL préalable, BACK_OK=FRONT_OK=12, 36 swaps, 0 refus Swap, 12 reprises Fill et 12 Capture abouties, ERR 0, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. T06A et T06B qualifiés en Runtime ; fenêtre post-Swap exercée sans observation directe du drapeau interne Safe. Refus Safe absent/allocateur injectés couverts par Gate A, pas par WinUAE. Compiler reporté, D non testée. [Preuve](evidence/T06B_SAFE_RUNTIME_PASS_L2B_2026-11-24.TXT). L3 : commencer par T14A, mesure mémoire Open/DB/Close avec curseur ; T10/T11 banques et caches, T14 autres variantes (B8/End/C2P et timeout), T16 Copper restent ouverts. [T14A](../tests/proto/l3_resources/README.md).

> **T06A L2b — Runtime PASS :** T06A Runtime PASS sur L2b : TARGET BACK, PROBE_COMPLETE 1, back 64/128/192, ancien front 239/239/239, ERR 0, 3 swaps sans refus, CAP_RETRIES 0, FILL_RETRIES 1, CLOSE_RETURNED 1, CLOSED_MOUSE_X -1. Défaut FRONT AGA-011 corrigé dans le scénario stabilisé. T06B sans pré-VBL reste à exécuter ; Gates C/D non testées sur L2b. Le banc T06A et les deux Lib restent inchangés. [Preuve](evidence/T06_PATTERN_RUNTIME_PASS_L2B_2026-11-24.TXT) · [T06B](../tests/proto/t06_pattern_safe/README.md).

> **24/11/2026 — Bascule L2b :** P2d-L2b active, 136 708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`. [Gate A 45449139352](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449139352) PASS (184 Pattern, 172 writers, 10 suites Bob), seconde reconstruction [45449077283](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45449077283) même SHA256. Gate B T06A à établir, C reportée, D non testée. LAST_GOOD P2d intacte. [Test actif](../tests/current/README.md). Le statut ci-dessous est historique.

> **Objectif auteur : publication 0.14.1**, correctifs de stabilité du socle 2D. Finaliser L0, T06 et L3, puis qualification L4 et décision L5. Pas de nouveau Sprite/Tilemap ni de compilation intermédiaire imposée ; aucune promotion ou publication automatique. [Notes GitHub](releases/0.14.1_GITHUB_RELEASE.md) · [Aminet](releases/0.14.1/AMOSProAGA.readme) · [Checklist](releases/0.14.1_RELEASE_CHECKLIST.md).

> **Résultats du 24/11/2026 :** SafePort IFF / Back Fill / premier Bind B8 B/C PASS rapportés, P2 ALL IN ONE Runtime PASS rapporté (240/240, 252 swaps, 120 refus récupérés), EDGE SAFE 20x18 Runtime PASS (240/240, 0 refus), RPG V9 Runtime PASS (250 frames, 2 retries). Identité L2 confirmée par l'auteur. Les autres Gates C sont reportées par choix auteur ; D non testée. EDGE sans pré-VBL Runtime PASS (240/240, 241 swaps, 120 refus tous récupérés, 128 pixels de bord valides, ERR 0). T06 et L3 restent ouverts. LAST_GOOD intacte. Sprite gelé. [Rapport](AGA_L2_WINUAE_RESULTS_2026-11-24.md). Les statuts B/C antérieurs ci-dessous sont les états à la livraison.


> **24/11/2026 — Priorité absolue : correction du socle 2D P2d.** Lecture statique planifiée terminée : 21 passages, 102 commandes inventoriées (100 natives P2d), 19 scénarios, aucun nouvel essai WinUAE. [Bilan et plan L0–L5](AUDIT_AGA_BILAN_PLAN_CORRECTION_2026-11-24.md) · [Rapport transversal et index des passages](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Matrice commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) · [Cahier de tests](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).
>
> **L0 :** [corrections CI et provenance](AGA_L0_PROVENANCE_CI_2026-11-24.md), Artifact integrity et OPT020 PASS avant bascule. **L1 engagé :** [correctif source-only IFF Load / Back Fill SafePort](AGA_L1_SAFEPORT_SOURCE_GATE_A_2026-11-24.md) (AGA-001/010 P0), **Gate A PASS 172 cas**, candidate 136 248 octets uniquement en mémoire ; B/C/D non testées. **L2 engagé :** [premier Bind B8 et régression L1](AGA_L2_FIRST_BIND_SOURCE_GATE_A_2026-11-24.md) (AGA-002 P1), **Gate A PASS 172 cas + 10 suites Bob**, candidate 136332 octets active après accord auteur. [Campagne WinUAE](AGA_L2_WINUAE_CAMPAIGN_2026-11-24.md), B/C/D non testées. Screen Pattern reste VM de la cible OS (T06). L3 ressources, L4 régression B/C, L5 décision auteur. AGA-003 reste VM du contrat Clear → décor → Swap. **Sprite gelé, LAST_GOOD protégée, aucune promotion.** Les résultats historiques détaillés restent dans les rapports et NEXT_SESSION.md.

> **23/11/2026 — Distribution :** `examples/` est réservé aux exemples **livrés avec la Lib** ; [`tests/proto/`](../tests/proto/README.md) reçoit les prototypes non distribués (AGSP, AGTM, Sprite S0). L'ancien état détaillé est conservé dans [l'archive intégrale](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md).

## 1. État actuel

| Domaine | Statut |
| --- | --- |
| **Lib de travail** | **M19 P2d-L2**, 136 332 octets, SHA256 `b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1`, 100 commandes / 203 AP20. [Lib](../dist/AMOSPro_AGA.Lib), Gate A PASS ; SafePort B/C PASS rapportés ; autres scénarios Runtime L2 PASS, Compiler reporté ; D physique non testée. |
| **LAST_GOOD protégée** | **M19 P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 entrées AP20. [LAST_GOOD](../dist/AMOSPro_AGA_LAST_GOOD.Lib) non modifiée. |
| **Campagne courante** | [M19_P2D_L2_SAFEPORT_BC.asc](../tests/current/M19_P2D_L2_SAFEPORT_BC.asc), préflight PASS, B/C PASS rapportés. [P2 ALL IN ONE historique](../tests/passed/M19_P2_ALL_IN_ONE.asc) validé sur P2d, non transférable à L2. |
| **Source MC68020 P2d** | 268 modules, 122 602 octets d'instructions dans 131 734 octets classés ; aucune zone inconnue. [Bilan](M19_P2D_NATIVE_SOURCE_CLASSIFICATION_2026-11-22.md) · [Reprise](NEXT_SESSION.md). |
| **Historique et preuves** | [NEXT_SESSION.md](NEXT_SESSION.md) · [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive avant rangement](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md). Les Gates de candidats anciens ne sont pas transposables. |

**S1-P1e :** candidate précédente gelée, 102 commandes / 208 AP20, Gate A historique PASS. Les deux commandes Sprite ne font pas partie de L2 ; [ancien binaire](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e0de86ccfa61c573c505f8b9c42b890140c85d9b/dist/AMOSPro_AGA.Lib) et sources conservés. [Test AGSP historique](../tests/proto/agsp_capture/README.md), à reprendre seulement après validation du socle.

## 2. Sprites matériels AGA (M19 S0–S3)

**P0–P2 Bob avaient été clos historiquement sur P2d ; le socle est désormais en correction et le chantier Sprite gelé.** La sonde S0d a passé Runtime B et Compiler C : trois cycles, 108 mouvements, curseur et Copper ; **détachement DMA et Gate D physique non prouvés**. [Audit S0](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md).

**AGSP v1 adopté** : planches IFF indexées, palette RGB24 par image, transparence explicite ; **3 couleurs opaques maxi en S1 Sprite simple 2bpp**, puis 15 en S2 Sprite attaché 4bpp. Au-delà : refus. [Format](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [contrat API](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md).

**S1-P1/P1b : Gate A CPU partielle PASS** : capture MC68020, pont ScreenBuffer/GetRGB32 et repack AGSP (8+6+8 tests). [Détails](M19_S1_P1B_AGSP_REPACK_MC68020_2026-11-22.md). La [sonde ViewPort](../tests/proto/sprite_s0_viewport/README.md) reste un prototype non distribué. **La [sonde DATA AGSP](../tests/proto/agsp_bank/AGSP_BANK_SAVELOAD.asc) a obtenu Gate B Runtime PASS**, avec [journal et ABK exact](M19_S1_P1B_AGSP_DATA_AMOS_SAVELOAD_2026-11-22.md). **Gate C Compiler délibérément sautée par décision de l'auteur** : non testée, non bloquante pour la suite S1-P1c.

**Travail Sprite après levée du gel :** wrapper AP20, contrôles mémoire/ScreenBuffer Safe, publication transactionnelle de banques DATA AGSP, puis vérification Runtime de la **capture native**. Pas de Compiler demandé pour la sonde DATA. Avant activation matérielle : palette Sprite/BPLCON4, possession OS des canaux et arrêt sûr du DMA. Ne pas toucher à la Lib installable ni à LAST_GOOD sans accord spécifique.

## 3. M21 Dual Playfield, puis AGTM M20

**Ordre retenu : M21 Dual Playfield avant le développement natif de M20 AGTM.** M21 doit qualifier plans indépendants, palettes, double buffering et défilement. [Spécification RPG Engine AGTM](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md).

Les **prototypes WinUAE AGTM** ont désormais des résultats : banque DATA **Runtime B PASS** (`Save/Load`, 352 indices) ; benchmark de tuiles **Runtime B et Compiler C PASS**, `PIXEL_BAD=0` sur 81 920 octets. En déplacement de **16 pixels**, FULL/SCROLL : 177/33 ticks Runtime, 140/31 ticks Compiler. [Rapport et preuves](AGTM_WINUAE_PROTOTYPES_2026-11-23.md). Cela n'évalue **ni moteur natif M20, ni scrolling 1px, ni multicouches/acteurs**.

Pistes M20 après M21 : banque AGTM, tileset, scrolling natif, édition de cellules, invalidation de régions, deux pages indépendantes, intégration Bob et performances CPU/Blitter. Évaluer par Gates A/B/C distinctes, puis D physique.

## 4. Ergonomie et suite

Après M21 et avant M20 : **`Aga Print`** sur écran privé, procédure réutilisable `Aga Pic Info` / `Aga Iff Load` / fermeture sûre ; étudier éventuellement une API de haut niveau. Explorer ensuite un accès C2P chunky plus simple sans oublier le rendu AGA planaire.

Autres sujets : entrées AMOS/joystick M22, C2P et Copper M23/M24, stabilité Compiler et optimisations mesurées. Les détails, anciennes décisions et preuves conservées restent dans [l'archive](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md).

**Règles :** un seul ASC actif sous `tests/current/`, archives `tests/passed/` protégées, preuves sous `docs/evidence/`, prototypes sous `tests/proto/` et **uniquement des exemples de distribution sous `examples/`**.
