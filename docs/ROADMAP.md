# Roadmap — AMOSPro AGA Extension

**26/11/2026 — P2m clôture fonctionnelle acceptée, B PASS, C fonctionnelle 2/2 (strict 1/2), D non testée.** [Résultats](M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md). S2a engagé en sources seulement ; Lib et ASC inchangés, LAST_GOOD protégée.

## 1. État actuel et objectif

**Socle protégé : 0.14.1 — Stability & Bug Fixes** (publication distincte). Développement repris : M19 Sprite, cible 0.15.0. [Checklist](releases/0.14.1_RELEASE_CHECKLIST.md) · [Qualification](releases/0.14.1_QUALIFICATION.md) · [Notes GitHub](releases/0.14.1_GITHUB_RELEASE.md) · [Notice Aminet](releases/0.14.1/AMOSProAGA.readme).

| Domaine | Statut |
| --- | --- |
| Lib de travail | [S1-P2m](../dist/AMOSPro_AGA.Lib), 149400 octets, SHA256 `5ee0c4bf7ec526085a97287ca04ded97778bd60761a3247f969c9c045440b0be`, 105 commandes / 214 AP20, MC68020+. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891037257), [reconstruction et préflight PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45891360197). B fonctionnelle PASS ; C fonctionnelle 2/2, stricte 1/2 ; D non testée. [Rapport](M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md). |
| LAST_GOOD | [P2d-L2b](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, protégée, distincte de S1-P2m ; promotion auteur le 24/11. [Rapport](M19_P2DL2B_LAST_GOOD_PROMOTION_2026-11-24.md). |
| ASC unique | [SPRITE_PUBLIC.asc](../tests/current/SPRITE_PUBLIC.asc) + [AGSP_S1P1E_FINAL.ABK](../tests/current/AGSP_S1P1E_FINAL.ABK). P2m : 100 cycles et 10 fermetures par lancement, trois lancements sans reset. [Campagne](../tests/current/README.md). |
| Reprise / preuves | [NEXT_SESSION.md](NEXT_SESSION.md) · [L2](AGA_L2_WINUAE_RESULTS_2026-11-24.md) · [L2b](AGA_L2B_PATTERN_SOURCE_GATE_A_2026-11-24.md) · [T10A](../tests/proto/l3_banks/README.md) · [T11A](../tests/proto/l3_cache/README.md) · [T14A](../tests/proto/l3_resources/README.md) · [L3 groupé](../tests/proto/l3_integrated/README.md). |

## 2. Clôture du socle 2D

- L0 : CI historiques/provenance à requalifier ; [rapport](AGA_L0_PROVENANCE_CI_2026-11-24.md).
- L1/L2 : corrections IFF / Back Fill Safe et premier Bind B8, Gate A PASS, Runtime B confirmé sur L2 selon preuves ; C limitée aux essais rapportés sur L2. EDGE sans pré-VBL, RPG, P2 intégrés PASS sur L2.
- L2b : Screen Pattern, échec FRONT L2 puis BACK PASS, Safe post-Swap PASS ; B/C/D ne sont jamais transférés entre binaires.
- L3 : T14A Open/Close/curseur, T11A FICON/FICHIP, T10A AGBO/B8, AGPC Fast/Chip/C2P/Copper PASS Runtime L2b ; mémoire stable sur chacun. [T14C End/Font](../tests/proto/l3_end/README.md) Runtime PASS ; ABA, BankFont et injections natives encore à disposer. Aucune anomalie nouvelle observée, pas de preuve exhaustive.
- L4 : [P2 ALL IN ONE](../tests/passed/M19_P2_ALL_IN_ONE.asc) Runtime PASS transmis sur L2b (journal identique à P2d historique, attribution contextuelle), B/C distinctes ; C manuelle reportée par l'auteur, D séparée. L5 : promotion interne L2b autorisée et effectuée ; publication distincte, CI post-promotion à requalifier. Aucune promotion automatique. [Audit et critères](AUDIT_AGA_BILAN_PLAN_CORRECTION_2026-11-24.md).

## 3. Sprites matériels AGA

S1 : banque AGSP v1 DATA multi-images, capture RGB24 avec transparence explicite, Sprite 16px/3 couleurs, cycle de vie P2m fonctionnel. [Format](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) · [Historique et résultats](M19_S1_P2M_RUNTIME_COMPILER_2026-11-26.md) · [Contrat S0–S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md). Réserve Fast transitoire documentée, pas de promotion.

- **S2a en cours :** [S2a — staging et contrat](M19_S2A_FRAME_STAGE_2026-11-26.md). Préparation de l'image suivante dans un slot inactif, sans nouveau token. [Intégration publique S2a-P1](M19_S2A_PUBLIC_FRAME_CHANGE_2026-11-26.md) en sources, Gate A à relever ; publication réelle à qualifier. UNIT142 à préserver (110 octets libres), travail UNIT207.
- S2b : plusieurs objets, propriété des canaux et palettes ; S2c : attaché 15 couleurs ; S2d : largeur 32/64 via mode global ; ensuite coordonnées/hotspots, priorité/clipping, ergonomie et benchmarks.
- S3 : multiplexage vertical, collisions, animation multi-objets, AMAL facultatif après validation du moteur classique.
- Les jalons P2a–P2l-c, leurs preuves et refus sont conservés dans [NEXT_SESSION.md](NEXT_SESSION.md), leurs rapports et [la roadmap avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/57a1a9d2085e5d887a1fccc5300a0de5eaeef709/docs/ROADMAP.md).

## 4. Après Sprite : M21 puis M20

M21 Dual Playfield avant M20 AGTM : plans indépendants, palettes, DB, défilement. Prototypes AGTM DATA Save/Load Runtime B PASS ; benchmark de tuiles B/C historique PASS. Scrolling fin horizontal 1/8/16 px **B Runtime et C Compiler PASS** (26/11), 983 040 octets planaires sans écart par mode. [Preuves initiales](AGTM_WINUAE_PROTOTYPES_2026-11-23.md) · [preuves scrolling fin](AGTM_FINE_SCROLL_WINUAE_2026-11-26.md). [Prototype deux pages/scrolling 2D/édits/overlays](../tests/proto/agtm_prototype/AGTM_DB_DIRTY_BENCH.asc) : **Runtime B et Compiler C PASS** (26/11), gain global ×5,17 / ×4,68, [preuves](AGTM_DB_DIRTY_WINUAE_2026-11-26.md). [Comparatif CPU/Blitter/hybride](../tests/proto/agtm_prototype/AGTM_BACKEND_BENCH.asc) : préflight et modèle hôte PASS, Runtime/Compiler non testés. [Spécification](RPG_ENGINE_AGTM_V1_SPEC_DRAFT.md). Après M21 et avant M20 : Aga Print, procédure IFF/fermeture, accès C2P simplifié. Puis input/joystick M22, C2P/Copper M23/M24 et optimisations mesurées.

## 5. Règles et historique

Un seul ASC actif, tests/passed protégés, prototypes uniquement tests/proto, exemples publics exclusivement examples. [Règles](../EXTENSION_SOURCE_RULES.md). [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) · [archive 23/11](history/ROADMAP_BEFORE_PROTOTYPE_SPLIT_2026-11-23.md) · [état détaillé avant condensation](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7216b51960220d03561c1a6874849bdf104fec4/docs/ROADMAP.md). Les preuves datées restent dans les rapports et NEXT_SESSION.md ; ne pas recopier les journaux dans la roadmap.
