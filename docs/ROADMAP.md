# Roadmap — AMOSPro AGA Extension

## 1. État actuel et objectif

**Socle protégé : 0.14.1 — Stability & Bug Fixes** (publication distincte). Développement repris : M19 Sprite, cible 0.15.0. [Checklist](releases/0.14.1_RELEASE_CHECKLIST.md) · [Qualification](releases/0.14.1_QUALIFICATION.md) · [Notes GitHub](releases/0.14.1_GITHUB_RELEASE.md) · [Notice Aminet](releases/0.14.1/AMOSProAGA.readme).

| Domaine | Statut |
| --- | --- |
| Lib de travail | [S1-P1i](../dist/AMOSPro_AGA.Lib), 142968 octets, SHA256 `2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3`, 102 commandes / 208 AP20, MC68020+. [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492646401) ; B capture AGSP PASS, C/D non testées. |
| LAST_GOOD | [P2d-L2b](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, protégée, distincte de S1-P1i ; promotion auteur le 24/11. [Rapport](M19_P2DL2B_LAST_GOOD_PROMOTION_2026-11-24.md). |
| ASC unique | [T06_PATTERN_TARGET.asc](../tests/current/T06_PATTERN_TARGET.asc), T06A/T06B Runtime PASS. Les sondes complémentaires restent dans tests/proto. [Campagne](../tests/current/README.md). |
| Reprise / preuves | [NEXT_SESSION.md](NEXT_SESSION.md) · [L2](AGA_L2_WINUAE_RESULTS_2026-11-24.md) · [L2b](AGA_L2B_PATTERN_SOURCE_GATE_A_2026-11-24.md) · [T10A](../tests/proto/l3_banks/README.md) · [T11A](../tests/proto/l3_cache/README.md) · [T14A](../tests/proto/l3_resources/README.md) · [L3 groupé](../tests/proto/l3_integrated/README.md). |

## 2. Clôture du socle 2D

- L0 : CI historiques/provenance à requalifier ; [rapport](AGA_L0_PROVENANCE_CI_2026-11-24.md).
- L1/L2 : corrections IFF / Back Fill Safe et premier Bind B8, Gate A PASS, Runtime B confirmé sur L2 selon preuves ; C limitée aux essais rapportés sur L2. EDGE sans pré-VBL, RPG, P2 intégrés PASS sur L2.
- L2b : Screen Pattern, échec FRONT L2 puis BACK PASS, Safe post-Swap PASS ; B/C/D ne sont jamais transférés entre binaires.
- L3 : T14A Open/Close/curseur, T11A FICON/FICHIP, T10A AGBO/B8, AGPC Fast/Chip/C2P/Copper PASS Runtime L2b ; mémoire stable sur chacun. [T14C End/Font](../tests/proto/l3_end/README.md) Runtime PASS ; ABA, BankFont et injections natives encore à disposer. Aucune anomalie nouvelle observée, pas de preuve exhaustive.
- L4 : [P2 ALL IN ONE](../tests/passed/M19_P2_ALL_IN_ONE.asc) Runtime PASS transmis sur L2b (journal identique à P2d historique, attribution contextuelle), B/C distinctes ; C manuelle reportée par l'auteur, D séparée. L5 : promotion interne L2b autorisée et effectuée ; publication distincte, CI post-promotion à requalifier. Aucune promotion automatique. [Audit et critères](AUDIT_AGA_BILAN_PLAN_CORRECTION_2026-11-24.md).

## 3. Sprites matériels AGA après levée du gel

S1-P1e (102 commandes / 208 AP20, historique Gate A PASS) reprise par accord auteur. **S1-P1f : réintégration sur L2b**, Gate A native PASS mais échec syntaxe AMOS. **S1-P1g : correction AP20**, Gate A ciblée PASS, Lib livrée ; LAST_GOOD L2b inchangée. [Correctif](M19_S1_P1G_AP20_SYNTAX_FIX_2026-11-24.md), rejet Runtime ERR 7. **S1-P1h : correction Cur_Banks, Runtime ERR 9. S1-P1i : contrats Safe et banque corrigés, Gate A complète PASS, candidate livrée puis Runtime capture AGSP PASS.** [Rapport](M19_S1_P1H_CUR_BANKS_FIX_2026-11-24.md). Sprite S0d B/C PASS historique, détachement DMA et D non prouvés. AGSP v1 : capture indexée RGB24, transparence explicite, S1 simple 3 couleurs opaques, S2 attaché 15 ; refus au-delà. DATA AGSP Save/Load B PASS, C délibérément sautée. [Preuves capture AGSP Runtime](M19_S1_P1I_RUNTIME_PASS_2026-11-24.md) ; S1-P2a préparation Chip source-only : [44 scénarios MC68020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45497634775). Prochaine étape : [sonde palette GET](../tests/proto/sprite_s1_palette/README.md), puis preuve d'arrêt sûr ; aucune DMA S1 à ce stade. Avant activation DMA : palette, propriété canaux et arrêt sûr. [Audit S0](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md) · [AGSP](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [contrat S1](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md) · [preuves DATA](M19_S1_P1B_AGSP_DATA_AMOS_SAVELOAD_2026-11-22.md).

## 4. Après Sprite : M21 puis M20

M21 Dual Playfield avant M20 AGTM : plans indépendants, palettes, DB, défilement. Prototypes AGTM DATA Save/Load Runtime B PASS ; benchmark de tuiles B/C historique PASS, déplacement 16 px FULL/SCROLL 177/33 ticks Runtime, 140/31 ticks Compiler, pas de qualification scrolling 1px/multicouches. [Spécification](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md) · [preuves](AGTM_WINUAE_PROTOTYPES_2026-11-23.md). Après M21 et avant M20 : Aga Print, procédure IFF/fermeture, accès C2P simplifié. Puis input/joystick M22, C2P/Copper M23/M24 et optimisations mesurées.

## 5. Règles et historique

Un seul ASC actif, tests/passed protégés, prototypes uniquement tests/proto, exemples publics exclusivement examples. [Règles](../EXTENSION_SOURCE_RULES.md). [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive 23/11](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md) · [état détaillé avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7216b51960220d03561c1a6874849bdf104fec4/docs/ROADMAP.md). Les preuves datées restent dans les rapports et NEXT_SESSION.md ; ne pas recopier les journaux dans la roadmap.

### S1-P2 — 25 novembre 2026

Sonde palette Runtime PASS, [preuve originale](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/main/docs/evidence/M19_S1P2_PALETTE_RUNTIME_2026-11-25.TXT). [S1-P2b](M19_S1_P2B_AGSP_DISPLAY_PROBE_2026-11-25.md) sonde visuelle préparée sur P1i ; non testée. P2a reste source-only. Retrait DMA non prouvé, aucune bascule de Lib ni promotion. 

**25/11/2026 — Gate B Runtime P2b PASS, scénario d'affichage/retrait visuel uniquement.** [Journal original](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/main/docs/evidence/M19_S1P2B_AGSP_RUNTIME_2026-11-25.TXT) : 379 octets, 14 CRLF, SHA256 `ed3d5be70927342eabf6cca6915eda8fe153cd5648296d21d1915d0f24028d5d`, blob `bda744907449d40819ba6f02dc44258a2c3712d0`. PRG_STATE 1, RESULT 1, ERR 0, SOURCE_ERASED 1, PALETTE_OK 1, MOVES 100, BLANK_SET 1, BLANK_VBL 150, FREES 2, CLOSE_RETURNED 1, CHIP_HELD 244, DMA_FREE_PROVEN 0. L'auteur confirme oralement dans la conversation (réponse « oui ») le déplacement visible à droite, la disparition et le retour AMOS ; aucune capture fournie. Lib P1i attribuée par le contexte, SHA installé non mesuré. Aucun transfert de PASS au détachement DMA, au natif P2a, au Compiler ou au matériel. ASC P2b blob `8927457a659d16a25d4f63138eeefe75dece1a84` conservé. P2c autorisée par « go! » : audit DMA et Copper, aucune nouvelle Lib ni promotion.
