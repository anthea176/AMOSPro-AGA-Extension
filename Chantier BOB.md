# M19 — chantier BOB AGA

Référence active **P0 promue LAST_GOOD** (20/11/2026), 117 896 octets, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`. P1 commencée **source-only**, pas de nouvelle commande publique ni changement de `.Lib`.

| Étape | Fonction | État exact |
| --- | --- | --- |
| P0 | `Aga Bob Clear` — restauration du fond | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Update` — mise à jour sans Swap implicite | **Implémenté**, Gate A PASS et Runtime B P0 fonctionnel |
| P0 | `Aga Bob Bank Free N` — libération cache Chip | **Implémenté**, Gate A PASS / Runtime B fonctionnel ; Compiler C P0 non testé |
| **P1a** | Lecture X/Y/image, équivalents AGA de `X Bob`, `Y Bob`, `I Bob` | `object_read` privé MC68020 **testé** ; API publique à définir/implémenter |
| **P1b** | Hot Spot, origine propre à chaque image | Champs AGBO v1 existants ; `set_hotspot` hôte + tests **PASS** ; non appliqué par le dessin natif |
| P1c | Priorités d'affichage ID / Y / ordre inverse | Non implémenté |
| P1d | `Limit Bob` : clipping configurable au pixel | Non implémenté |
| P1e | `Del Bob` / `Ins Bob` : édition des images de banque | Non implémenté |
| P2 | Collisions Bob–Bob rectangles puis masques | Non implémenté |
| P2 | Retournements H/V sans altérer les sources partagées | Non implémenté |
| P2 | Modes avancés et animation automatique / AMAL | Non implémenté |
| Ensuite | Sprites matériels AGA | Non engagé |

**Preuves P1 :** [rapport de jalon](docs/M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md) et [CI source-only PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44827972362). Gates B/C/D **P1 non testées** ; aucune validation d'API P1 revendiquée.

**Prochaine décision :** signatures publiques et politique de refus des getters, avant ajout de tokens AP20 ou nouvelle `.Lib`.
