# Roadmap — AMOSPro AGA Extension

**26/11/2026 — P2l-c : ÉCHEC FONCTIONNEL de la relance sans reset (ERR10, SPRITE_RC=-123).** Gate A PASS ; les PASS Runtime phases 1/2 sont uniquement des PASS de scénario de quarantaine, pas une validation du cycle de vie. [Journaux et correctif P2m](M19_S1_P2M_FUNCTIONAL_LIFECYCLE_2026-11-26.md). P2m en qualification source, Lib/ASC actifs P2l-c inchangés, LAST_GOOD protégée. Ne plus relancer le test P2l-c.

## 1. État actuel et objectif

**Socle protégé : 0.14.1 — Stability & Bug Fixes** (publication distincte). Développement repris : M19 Sprite, cible 0.15.0. [Checklist](releases/0.14.1_RELEASE_CHECKLIST.md) · [Qualification](releases/0.14.1_QUALIFICATION.md) · [Notes GitHub](releases/0.14.1_GITHUB_RELEASE.md) · [Notice Aminet](releases/0.14.1/AMOSProAGA.readme).

| Domaine | Statut |
| --- | --- |
| Lib de travail | [S1-P2l-c](../dist/AMOSPro_AGA.Lib), 150056 octets, SHA256 `148b4d06702f84dd6de3eacd069a55c4759164bb4dd3c74f319f81e6f077f3f5`, 105 commandes / 214 AP20, MC68020+. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45877952385) ; 532 contrôles, [reconstruction exacte PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45880559895), Runtime quarantaine PASS / relance fonctionnelle FAIL, C reportée, D non testée. Diagnostic DMA seulement. [Rapport](M19_S1_P2L_C_IDLE_DETAIL_2026-11-26.md). |
| LAST_GOOD | [P2d-L2b](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, protégée, distincte de S1-P2l-c ; promotion auteur le 24/11. [Rapport](M19_P2DL2B_LAST_GOOD_PROMOTION_2026-11-24.md). |
| ASC unique | [SPRITE_PUBLIC.asc](../tests/current/SPRITE_PUBLIC.asc) + [AGSP_S1P1E_FINAL.ABK](../tests/current/AGSP_S1P1E_FINAL.ABK). Runtime P2l-c : deux phases quarantaine PASS, relance FAIL ; test suspendu ; [T06 conservé](../tests/proto/t06_pattern/T06_PATTERN_TARGET.asc). [Campagne](../tests/current/README.md). |
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
- [P2g](M19_S1_P2G_RECLAIM_2026-11-25.md) récupération expérimentale après vrai CloseScreen et garde Copper/OS ; r1 FAIL builder (8/6 octets), r2 [30 scénarios CPU PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45679517861). Persistance pending après unload, palette, producteur et API restent à qualifier. Aucun nouveau token/binaire, pas de debugger manuel.
- [P2h](M19_S1_P2H_PERSISTENT_ROOT_2026-11-25.md) registre Exec persistant source-only, suppression si vide, emprunt non bloquant ; [étape CPU PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45680011267), raccordement aux chemins Close/End et producteur à réaliser (marge UNIT142 504 octets).
- [P2i](M19_S1_P2I_INTEGRATED_SPRITE_2026-11-25.md) : intégration complète, [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45682158541), candidate livrée ; Runtime/Compiler/DMA réels à qualifier.
- [P2j](M19_S1_P2J_RUNTIME_REPAIR_2026-11-25.md) : P2i rejetée, reprise séquence P2b, erreurs détaillées et verrou DMA rétabli ; Gate A à relever avant nouvelle Lib.
- [P2l-c](M19_S1_P2L_C_IDLE_DETAIL_2026-11-26.md) : détail du refus -185, Gate A complète PASS, paire active, Runtime à effectuer ; réemploi DMA et validation multi-cycles encore bloqués.
- Historique détaillé : [roadmap avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/17d710693a3ae26a6ab94775c9af1b8bd5428232/docs/ROADMAP.md), rapports de jalon et NEXT_SESSION.md. Aucun transfert de PASS à la libération DMA, au Compiler ou au matériel.


## 4. Après Sprite : M21 puis M20

M21 Dual Playfield avant M20 AGTM : plans indépendants, palettes, DB, défilement. Prototypes AGTM DATA Save/Load Runtime B PASS ; benchmark de tuiles B/C historique PASS. Scrolling fin horizontal 1/8/16 px **B Runtime et C Compiler PASS** (26/11), 983 040 octets planaires sans écart par mode. [Preuves initiales](AGTM_WINUAE_PROTOTYPES_2026-11-23.md) · [preuves scrolling fin](AGTM_FINE_SCROLL_WINUAE_2026-11-26.md). [Prototype deux pages/scrolling 2D/édits/overlays](../tests/proto/agtm_prototype/AGTM_DB_DIRTY_BENCH.asc) : **Runtime B et Compiler C PASS** (26/11), gain global ×5,17 / ×4,68, [preuves](AGTM_DB_DIRTY_WINUAE_2026-11-26.md). [Comparatif CPU/Blitter/hybride](../tests/proto/agtm_prototype/AGTM_BACKEND_BENCH.asc) : préflight et modèle hôte PASS, Runtime/Compiler non testés. [Spécification](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md). Après M21 et avant M20 : Aga Print, procédure IFF/fermeture, accès C2P simplifié. Puis input/joystick M22, C2P/Copper M23/M24 et optimisations mesurées.

## 5. Règles et historique

Un seul ASC actif, tests/passed protégés, prototypes uniquement tests/proto, exemples publics exclusivement examples. [Règles](../EXTENSION_SOURCE_RULES.md). [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive 23/11](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md) · [état détaillé avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7216b51960220d03561c1a6874849bdf104fec4/docs/ROADMAP.md). Les preuves datées restent dans les rapports et NEXT_SESSION.md ; ne pas recopier les journaux dans la roadmap.
