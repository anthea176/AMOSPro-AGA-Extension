# M19 — chantier BOB AGA

**LAST_GOOD reste P0.** La Lib active est P1d (121 432 octets, SHA256 `47fc7c5d056211a62a50b5405b8952db0bb715ace72a8dc257c4a90def2eb785`), 94 commandes, 192 entrées AP20, MC68020 minimum. [Gate A P1d PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44888685052).

| Étape | Fonction | État exact |
| --- | --- | --- |
| P0 | `Aga Bob Clear` — restauration du fond | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Update` — mise à jour sans Swap implicite | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Bank Free N` — libération cache Chip | **Implémenté**, Gate A PASS / Runtime B fonctionnel ; Compiler C P0 non testé |
| **P1a** | `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)` ; refus `-32769` | **Builder AP20 source-pinné + shims MC68020 Gate A PASS (110 contrôles)** ; **fonctionnalités conservées dans P1b**, 92 commandes / 188 entrées ; Gate B Runtime PASS fonctionnel ([2 journaux](docs/M19_P1A_RUNTIME_B_2026-11-21.md)), Gates C/D en attente |
| **P1b** | Hot Spot, origine propre à chaque image | Intégré au Safe Blitter. Gate A et Gate B Runtime PASS sur P1b. [Rapport](docs/M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md) |
| **P1c** | `Aga Bob Priority(Mode)` | Gate A PASS, B Runtime et C Compiler PASS sur les mesures. [Résultats](docs/M19_P1C_PRIORITY_GATES_BC_2026-11-21.md). |
| **P1d** | `Aga Limit Bob(N,X,Y,W,H)` | Lib active et Gate A PASS. [Banc WinUAE](tests/current/README.md). |
| P1e | `Del Bob` / `Ins Bob` : édition des images de banque | Non implémenté |
| P2 | Collisions Bob–Bob rectangles puis masques | Non implémenté |
| P2 | Retournements H/V sans altérer les sources partagées | Non implémenté |
| P2 | Modes avancés et animation automatique / AMAL | Non implémenté |
| Ensuite | Sprites matériels AGA | Non engagé |

**Preuves P1 :** [socle et Hot Spot](docs/M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md) ; [rapport P1a AP20](docs/M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md) ; [CI Gate A P1a PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430). **La syntaxe des tokens a été auditée en AP20 ; deux exécutions AMOS Runtime WinUAE P1a sont PASS fonctionnel. Le vrai Compiler P1a reste NON TESTÉ.**

**Prochaine action** — Exécuter P1d sous WinUAE et sauvegarder les deux journaux Runtime.
