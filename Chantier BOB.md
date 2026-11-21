# M19 — chantier BOB AGA

**LAST_GOOD reste P0 protégée** (117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`). **Lib active P1b de TEST** (119 176 octets, SHA256 `2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4`) : 92 commandes / 188 entrées AP20, fonctions getters P1a conservées, dessin Hot Spot intégré au Safe Blitter. **P1b Gates A et B Runtime PASS, Gates C/D à tester ; P1a Gate B Runtime PASS fonctionnel.**

| Étape | Fonction | État exact |
| --- | --- | --- |
| P0 | `Aga Bob Clear` — restauration du fond | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Update` — mise à jour sans Swap implicite | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Bank Free N` — libération cache Chip | **Implémenté**, Gate A PASS / Runtime B fonctionnel ; Compiler C P0 non testé |
| **P1a** | `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)` ; refus `-32769` | **Builder AP20 source-pinné + shims MC68020 Gate A PASS (110 contrôles)** ; **fonctionnalités conservées dans P1b**, 92 commandes / 188 entrées ; Gate B Runtime PASS fonctionnel ([2 journaux](docs/M19_P1A_RUNTIME_B_2026-11-21.md)), Gates C/D en attente |
| **P1b** | Hot Spot, origine propre à chaque image | **Raccord MC68020 au Safe Blitter installé**, 119 176 octets. **Gate A intégrée PASS (98 contrôles, 258 contrôles du helper)** ; **Gate B Runtime WinUAE PASS** sur deux lancements et contrôle visuel confirmé. Gates C/D à tester. [Rapport](docs/M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md) |
| **P1c** | `Aga Bob Priority(Mode)` : ID ou Y logique, normal ou inverse | Implémenté dans le builder MC68020 en mémoire. [Contrat et tests](docs/M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1c--priorité-daffichage-des-bobs). |
| P1d | `Limit Bob` : clipping configurable au pixel | Non implémenté |
| P1e | `Del Bob` / `Ins Bob` : édition des images de banque | Non implémenté |
| P2 | Collisions Bob–Bob rectangles puis masques | Non implémenté |
| P2 | Retournements H/V sans altérer les sources partagées | Non implémenté |
| P2 | Modes avancés et animation automatique / AMAL | Non implémenté |
| Ensuite | Sprites matériels AGA | Non engagé |

**Preuves P1 :** [socle et Hot Spot](docs/M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md) ; [rapport P1a AP20](docs/M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md) ; [CI Gate A P1a PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430). **La syntaxe des tokens a été auditée en AP20 ; deux exécutions AMOS Runtime WinUAE P1a sont PASS fonctionnel. Le vrai Compiler P1a reste NON TESTÉ.**

**Prochaine action** — Décider de la bascule de la Lib de travail P1c pour WinUAE et du moment de la campagne AMOS Compiler.
