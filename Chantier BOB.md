# M19 — chantier BOB AGA

**LAST_GOOD reste P0 protégée** (117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`). **Lib active P1a de TEST** (118 816 octets, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`) : trois tokens numériques X/Y/I installés dans l'unique `dist/AMOSPro_AGA.Lib`, **Gate A PASS, Gate B Runtime PASS fonctionnel, Gates C/D NON TESTÉES**.

| Étape | Fonction | État exact |
| --- | --- | --- |
| P0 | `Aga Bob Clear` — restauration du fond | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Update` — mise à jour sans Swap implicite | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Bank Free N` — libération cache Chip | **Implémenté**, Gate A PASS / Runtime B fonctionnel ; Compiler C P0 non testé |
| **P1a** | `Aga X Bob(N)`, `Aga Y Bob(N)`, `Aga I Bob(N)` ; refus `-32769` | **Builder AP20 source-pinné + shims MC68020 Gate A PASS (110 contrôles)** ; **candidate active** 118 816 octets / 92 commandes / 188 entrées ; Gate B Runtime PASS fonctionnel ([2 journaux](docs/M19_P1A_RUNTIME_B_2026-11-21.md)), Gates C/D en attente |
| **P1b** | Hot Spot, origine propre à chaque image | Champs AGBO v1 existants ; `set_hotspot` hôte + tests **PASS** ; non appliqué par le dessin natif |
| P1c | Priorités d'affichage ID / Y / ordre inverse | Non implémenté |
| P1d | `Limit Bob` : clipping configurable au pixel | Non implémenté |
| P1e | `Del Bob` / `Ins Bob` : édition des images de banque | Non implémenté |
| P2 | Collisions Bob–Bob rectangles puis masques | Non implémenté |
| P2 | Retournements H/V sans altérer les sources partagées | Non implémenté |
| P2 | Modes avancés et animation automatique / AMAL | Non implémenté |
| Ensuite | Sprites matériels AGA | Non engagé |

**Preuves P1 :** [socle et Hot Spot](docs/M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md) ; [rapport P1a AP20](docs/M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md) ; [CI Gate A P1a PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430). **La syntaxe des tokens a été auditée en AP20 ; deux exécutions AMOS Runtime WinUAE P1a sont PASS fonctionnel. Le vrai Compiler P1a reste NON TESTÉ.**

**Prochaine action :** **P1b — appliquer les Hot Spots AGBO à la chaîne native Safe Blit**, avec vérification du cache Chip, de l'ordre Clear/Update/Swap, des masques et du clipping. D'abord **source-only + tests CPU020**, sans remplacer la Lib P1a ni promouvoir LAST_GOOD P0.
