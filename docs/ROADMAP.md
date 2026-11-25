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

**S1-P1i** : capture AGSP Runtime PASS, Gate A complète PASS. P1e–P1h historiques : voir [correctif P1i](M19_S1_P1I_CONTRACT_AUDIT_2026-11-24.md) et [preuves](M19_S1_P1I_RUNTIME_PASS_2026-11-24.md). AGSP v1 DATA multi-images Save/Load, 3 opaques S1, 15 S2, transparence explicite, RGB24. [Format](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [Contrat S1](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md).

- P2a préparation Chip source-only, Gate A composant PASS ; palette GET V40 et [P2b affichage/mouvements/retrait visuel](M19_S1_P2B_AGSP_DISPLAY_PROBE_2026-11-25.md) Runtime PASS.
- [P2c](M19_S1_P2C_DMA_OBSERVATION_2026-11-25.md) séquence Runtime PASS, DMA INCONCLUSIVE (pas de debugger manuel).
- [P2d r2](M19_S1_P2D_OS_AUDIT_2026-11-25.md) : six snapshots valides, références copinit et SimpleSprites retirées, contrôle positif réévalué hors ligne ; journal brut INCONCLUSIVE conservé. DMA_FREE_PROVEN 0.
- [P2e](M19_S1_P2E_NATIVE_RETIRE_2026-11-25.md) retrait natif logique, [Gate A composant PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45674243613) (OS simulé).
- [P2f](M19_S1_P2F_CLOSE_END_GUARD_2026-11-25.md) garde Close/End source-only, [40 scénarios CPU PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45675885915).
- [P2g](M19_S1_P2G_RECLAIM_2026-11-25.md) récupération expérimentale après vrai CloseScreen et garde Copper/OS ; r1 FAIL builder (8/6 octets), r2 corrigée, CI à relever. Persistance pending après unload, palette, producteur et API restent à qualifier. Aucun nouveau token/binaire, pas de debugger manuel.
- [P2h](M19_S1_P2H_PERSISTENT_ROOT_2026-11-25.md) registre Exec persistant source-only, suppression si vide, emprunt non bloquant ; CI à relever, raccordement aux chemins Close/End et producteur à réaliser.
- Historique détaillé : [roadmap avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/17d710693a3ae26a6ab94775c9af1b8bd5428232/docs/ROADMAP.md), rapports de jalon et NEXT_SESSION.md. Aucun transfert de PASS à la libération DMA, au Compiler ou au matériel.


## 4. Après Sprite : M21 puis M20

M21 Dual Playfield avant M20 AGTM : plans indépendants, palettes, DB, défilement. Prototypes AGTM DATA Save/Load Runtime B PASS ; benchmark de tuiles B/C historique PASS, déplacement 16 px FULL/SCROLL 177/33 ticks Runtime, 140/31 ticks Compiler, pas de qualification scrolling 1px/multicouches. [Spécification](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md) · [preuves](AGTM_WINUAE_PROTOTYPES_2026-11-23.md). Après M21 et avant M20 : Aga Print, procédure IFF/fermeture, accès C2P simplifié. Puis input/joystick M22, C2P/Copper M23/M24 et optimisations mesurées.

## 5. Règles et historique

Un seul ASC actif, tests/passed protégés, prototypes uniquement tests/proto, exemples publics exclusivement examples. [Règles](../EXTENSION_SOURCE_RULES.md). [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive 23/11](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md) · [état détaillé avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7216b51960220d03561c1a6874849bdf104fec4/docs/ROADMAP.md). Les preuves datées restent dans les rapports et NEXT_SESSION.md ; ne pas recopier les journaux dans la roadmap.
