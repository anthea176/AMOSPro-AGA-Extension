# Roadmap — AMOSPro AGA Extension

## 1. État actuel et objectif

**Socle protégé : 0.14.1 — Stability & Bug Fixes** (publication distincte). Développement repris : M19 Sprite, cible 0.15.0. [Checklist](releases/0.14.1_RELEASE_CHECKLIST.md) · [Qualification](releases/0.14.1_QUALIFICATION.md) · [Notes GitHub](releases/0.14.1_GITHUB_RELEASE.md) · [Notice Aminet](releases/0.14.1/AMOSProAGA.readme).

| Domaine | Statut |
| --- | --- |
| Lib de travail | [S1-P1f](../dist/AMOSPro_AGA.Lib), 142684 octets, SHA256 `dffe70c5550a4387b99901a2431892a2a7d6fe67328ab7cff8f69afd7ad91931`, 102 commandes / 208 AP20, MC68020+. [Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45466155974) PASS, B/C/D non testées. |
| LAST_GOOD | [P2d-L2b](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, protégée, distincte de S1-P1f ; promotion auteur le 24/11. [Rapport](M19_P2DL2B_LAST_GOOD_PROMOTION_2026-11-24.md). |
| ASC unique | [T06_PATTERN_TARGET.asc](../tests/current/T06_PATTERN_TARGET.asc), T06A/T06B Runtime PASS. Les sondes complémentaires restent dans tests/proto. [Campagne](../tests/current/README.md). |
| Reprise / preuves | [NEXT_SESSION.md](NEXT_SESSION.md) · [L2](AGA_L2_WINUAE_RESULTS_2026-11-24.md) · [L2b](AGA_L2B_PATTERN_SOURCE_GATE_A_2026-11-24.md) · [T10A](../tests/proto/l3_banks/README.md) · [T11A](../tests/proto/l3_cache/README.md) · [T14A](../tests/proto/l3_resources/README.md) · [L3 groupé](../tests/proto/l3_integrated/README.md). |

## 2. Clôture du socle 2D

- L0 : CI historiques/provenance à requalifier ; [rapport](AGA_L0_PROVENANCE_CI_2026-11-24.md).
- L1/L2 : corrections IFF / Back Fill Safe et premier Bind B8, Gate A PASS, Runtime B confirmé sur L2 selon preuves ; C limitée aux essais rapportés sur L2. EDGE sans pré-VBL, RPG, P2 intégrés PASS sur L2.
- L2b : Screen Pattern, échec FRONT L2 puis BACK PASS, Safe post-Swap PASS ; B/C/D ne sont jamais transférés entre binaires.
- L3 : T14A Open/Close/curseur, T11A FICON/FICHIP, T10A AGBO/B8, AGPC Fast/Chip/C2P/Copper PASS Runtime L2b ; mémoire stable sur chacun. [T14C End/Font](../tests/proto/l3_end/README.md) Runtime PASS ; ABA, BankFont et injections natives encore à disposer. Aucune anomalie nouvelle observée, pas de preuve exhaustive.
- L4 : [P2 ALL IN ONE](../tests/passed/M19_P2_ALL_IN_ONE.asc) Runtime PASS transmis sur L2b (journal identique à P2d historique, attribution contextuelle), B/C distinctes ; C manuelle reportée par l'auteur, D séparée. L5 : promotion interne L2b autorisée et effectuée ; publication distincte, CI post-promotion à requalifier. Aucune promotion automatique. [Audit et critères](AUDIT_AGA_BILAN_PLAN_CORRECTION_2026-11-24.md).

## 3. Sprites matériels AGA après levée du gel

S1-P1e (102 commandes / 208 AP20, historique Gate A PASS) reprise par accord auteur. **S1-P1f : réintégration source sur L2b**, Gate A PASS, Lib de travail livrée ; LAST_GOOD L2b inchangée. [Jalon](M19_S1_P1F_L2B_REBASE_2026-11-24.md). Sprite S0d B/C PASS historique, détachement DMA et D non prouvés. AGSP v1 : capture indexée RGB24, transparence explicite, S1 simple 3 couleurs opaques, S2 attaché 15 ; refus au-delà. DATA AGSP Save/Load B PASS, C délibérément sautée. Prochain essai : [capture AGSP Runtime](../tests/proto/agsp_capture/README.md) ; aucune DMA à ce stade. Avant activation DMA : palette, propriété canaux et arrêt sûr. [Audit S0](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md) · [AGSP](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [contrat S1](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md) · [preuves DATA](M19_S1_P1B_AGSP_DATA_AMOS_SAVELOAD_2026-11-22.md).

## 4. Après Sprite : M21 puis M20

M21 Dual Playfield avant M20 AGTM : plans indépendants, palettes, DB, défilement. Prototypes AGTM DATA Save/Load Runtime B PASS ; benchmark de tuiles B/C historique PASS, déplacement 16 px FULL/SCROLL 177/33 ticks Runtime, 140/31 ticks Compiler, pas de qualification scrolling 1px/multicouches. [Spécification](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md) · [preuves](AGTM_WINUAE_PROTOTYPES_2026-11-23.md). Après M21 et avant M20 : Aga Print, procédure IFF/fermeture, accès C2P simplifié. Puis input/joystick M22, C2P/Copper M23/M24 et optimisations mesurées.

## 5. Règles et historique

Un seul ASC actif, tests/passed protégés, prototypes uniquement tests/proto, exemples publics exclusivement examples. [Règles](../EXTENSION_SOURCE_RULES.md). [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive 23/11](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md) · [état détaillé avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7216b51960220d03561c1a6874849bdf104fec4/docs/ROADMAP.md). Les preuves datées restent dans les rapports et NEXT_SESSION.md ; ne pas recopier les journaux dans la roadmap.
