# Roadmap — AMOSPro AGA Extension

> **24/11/2026 — Priorité absolue : correction du socle 2D P2d.** Lecture statique planifiée terminée : 21 passages, 102 commandes inventoriées (100 natives P2d), 19 scénarios, aucun nouvel essai WinUAE. [Bilan et plan L0–L5](AUDIT_AGA_BILAN_PLAN_CORRECTION_2026-11-24.md) · [Rapport transversal et index des passages](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Matrice commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) · [Cahier de tests](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).
>
> **L0 :** [corrections CI et provenance](AGA_L0_PROVENANCE_CI_2026-11-24.md), qualification globale restante. **L1 engagé :** [correctif source-only IFF Load / Back Fill SafePort](AGA_L1_SAFEPORT_SOURCE_GATE_A_2026-11-24.md) (AGA-001/010 P0), **Gate A PASS 172 cas**, candidate 136 248 octets uniquement en mémoire ; B/C/D non testées. Ensuite qualification Screen Pattern et L2 amorçage B8 (AGA-002 P1). L3 ressources, L4 régression B/C, L5 décision auteur. AGA-003 reste VM du contrat Clear → décor → Swap. **Sprite gelé, aucun remplacement de Lib ou promotion.** Les résultats historiques détaillés restent dans les rapports et NEXT_SESSION.md.

> **23/11/2026 — Distribution :** `examples/` est réservé aux exemples **livrés avec la Lib** ; [`tests/proto/`](../tests/proto/README.md) reçoit les prototypes non distribués (AGSP, AGTM, Sprite S0). L'ancien état détaillé est conservé dans [l'archive intégrale](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md).

## 1. État actuel

| Domaine | Statut |
| --- | --- |
| **Lib de travail** | **M19 S1-P1e Get AGA Sprite candidate**, 142 000 octets, SHA256 `1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106`, 102 commandes / 208 entrées AP20. [Lib](../dist/AMOSPro_AGA.Lib), Gate A PASS ; B/C/D non testées. |
| **LAST_GOOD protégée** | **M19 P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 entrées AP20. [LAST_GOOD](../dist/AMOSPro_AGA_LAST_GOOD.Lib) non modifiée. |
| **Régression courante** | Un ASC unique : [`M19_P2_ALL_IN_ONE.asc`](../tests/current/M19_P2_ALL_IN_ONE.asc) (25 056 octets), Gates B Runtime et C vrai Compiler PASS pour ce banc P2a–P2e. [Rapport](M19_P2_ALL_IN_ONE_2026-11-21.md). |
| **Source MC68020 P2d** | 268 modules, 122 602 octets d'instructions dans 131 734 octets classés ; aucune zone inconnue. [Bilan](M19_P2D_NATIVE_SOURCE_CLASSIFICATION_2026-11-22.md) · [Reprise](NEXT_SESSION.md). |
| **Historique et preuves** | [NEXT_SESSION.md](NEXT_SESSION.md) · [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive avant rangement](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md). Les Gates de candidats anciens ne sont pas transposables. |

**S1-P1e :** candidate de travail désormais dans `dist/AMOSPro_AGA.Lib` avec autorisation expresse ; API AP20 `Aga Sprite Bank N` / `Get AGA Sprite I,X1,Y1,X2,Y2,TransparentPen`, 102 commandes / 208 entrées, **Gate A MC68020 simulée PASS**. [Test Runtime et IFF](../tests/proto/agsp_capture/README.md) : utiliser la Lib du dépôt pour un test WinUAE isolé ; Gate B de la nouvelle commande non exécutée. Aucun test Compiler demandé pour la sonde DATA.

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
