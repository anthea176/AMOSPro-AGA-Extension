# Roadmap — AMOSPro AGA Extension

> **23/11/2026 — Distribution :** `examples/` est réservé aux exemples **livrés avec la Lib** ; [`tests/proto/`](../tests/proto/README.md) reçoit les prototypes non distribués (AGSP, AGTM, Sprite S0). L'ancien état détaillé est conservé dans [l'archive intégrale](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md).

## 1. État actuel

| Domaine | Statut |
| --- | --- |
| **Lib active et LAST_GOOD** | **M19 P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. [Lib](../dist/AMOSPro_AGA.Lib) et [LAST_GOOD](../dist/AMOSPro_AGA_LAST_GOOD.Lib) identiques, protégées. Aucun remplacement ou promotion automatique. |
| **Régression courante** | Un ASC unique : [`M19_P2_ALL_IN_ONE.asc`](../tests/current/M19_P2_ALL_IN_ONE.asc) (25 056 octets), Gates B Runtime et C vrai Compiler PASS pour ce banc P2a–P2e. [Rapport](M19_P2_ALL_IN_ONE_2026-11-21.md). |
| **Source MC68020 P2d** | 268 modules, 122 602 octets d'instructions dans 131 734 octets classés ; aucune zone inconnue. [Bilan](M19_P2D_NATIVE_SOURCE_CLASSIFICATION_2026-11-22.md) · [Reprise](NEXT_SESSION.md). |
| **Historique et preuves** | [NEXT_SESSION.md](NEXT_SESSION.md) · [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive avant rangement](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md). Les Gates de candidats anciens ne sont pas transposables. |

## 2. Sprites matériels AGA (M19 S0–S3)

**Les Bobs P0–P2 sont clos sur P2d.** La sonde S0d a passé Runtime B et Compiler C : trois cycles, 108 mouvements, curseur et Copper ; **détachement DMA et Gate D physique non prouvés**. [Audit S0](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md).

**AGSP v1 adopté** : planches IFF indexées, palette RGB24 par image, transparence explicite ; **3 couleurs opaques maxi en S1 Sprite simple 2bpp**, puis 15 en S2 Sprite attaché 4bpp. Au-delà : refus. [Format](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [contrat API](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md).

**S1-P1/P1b : Gate A CPU partielle PASS** : capture MC68020, pont ScreenBuffer/GetRGB32 et repack AGSP (8+6+8 tests). [Détails](M19_S1_P1B_AGSP_REPACK_MC68020_2026-11-22.md). La [sonde ViewPort](../tests/proto/sprite_s0_viewport/README.md) reste un prototype non distribué. **La [sonde DATA AGSP](../tests/proto/agsp_bank/AGSP_BANK_SAVELOAD.asc) a obtenu Gate B Runtime PASS**, avec [journal et ABK exact](M19_S1_P1B_AGSP_DATA_AMOS_SAVELOAD_2026-11-22.md). **Gate C Compiler délibérément sautée par décision de l'auteur** : non testée, non bloquante pour la suite S1-P1c.

**Prochain travail Sprite :** wrapper AP20, contrôles mémoire/ScreenBuffer Safe, publication transactionnelle de banques DATA AGSP, puis vérification Runtime de la **capture native**. Pas de Compiler demandé pour la sonde DATA. Avant activation matérielle : palette Sprite/BPLCON4, possession OS des canaux et arrêt sûr du DMA. Ne pas toucher à la Lib installable ni à LAST_GOOD sans accord spécifique.

## 3. M21 Dual Playfield, puis AGTM M20

**Ordre retenu : M21 Dual Playfield avant le développement natif de M20 AGTM.** M21 doit qualifier plans indépendants, palettes, double buffering et défilement. [Spécification RPG Engine AGTM](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md).

Les **prototypes WinUAE AGTM** ont désormais des résultats : banque DATA **Runtime B PASS** (`Save/Load`, 352 indices) ; benchmark de tuiles **Runtime B et Compiler C PASS**, `PIXEL_BAD=0` sur 81 920 octets. En déplacement de **16 pixels**, FULL/SCROLL : 177/33 ticks Runtime, 140/31 ticks Compiler. [Rapport et preuves](AGTM_WINUAE_PROTOTYPES_2026-11-23.md). Cela n'évalue **ni moteur natif M20, ni scrolling 1px, ni multicouches/acteurs**.

Pistes M20 après M21 : banque AGTM, tileset, scrolling natif, édition de cellules, invalidation de régions, deux pages indépendantes, intégration Bob et performances CPU/Blitter. Évaluer par Gates A/B/C distinctes, puis D physique.

## 4. Ergonomie et suite

Après M21 et avant M20 : **`Aga Print`** sur écran privé, procédure réutilisable `Aga Pic Info` / `Aga Iff Load` / fermeture sûre ; étudier éventuellement une API de haut niveau. Explorer ensuite un accès C2P chunky plus simple sans oublier le rendu AGA planaire.

Autres sujets : entrées AMOS/joystick M22, C2P et Copper M23/M24, stabilité Compiler et optimisations mesurées. Les détails, anciennes décisions et preuves conservées restent dans [l'archive](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md).

**Règles :** un seul ASC actif sous `tests/current/`, archives `tests/passed/` protégées, preuves sous `docs/evidence/`, prototypes sous `tests/proto/` et **uniquement des exemples de distribution sous `examples/`**.
