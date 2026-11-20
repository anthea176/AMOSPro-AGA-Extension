# M20 P0 — oracle tilemaps / scrolling sur deux buffers

**Statut : développement hôte Python uniquement, aucun moteur natif installé.** La base reste M19 B8 S1 : deux journaux Runtime fournis, tous deux avec 405/405 frames, 9/9 étapes, 403 Clear et 405 Update, ERR 0 / PATH_OK. Gate C AMOS Compiler reportée à la demande de l'auteur. LAST_GOOD R84 inchangée.

## But

Établir une référence pixel par pixel avant d'écrire un moteur 68020 : caméra, scrolling, bandes découvertes, édition dynamique de tuiles et superposition de Bobs sur les **deux pages physiques indépendantes**.

Le prototype [m20_tilemap_model.py](../tools/m20_tilemap_model.py) utilise des pixels **chunky 8 bits pour l'oracle uniquement**, pas un écran ou moteur AGA planaire. Il n'ajoute ni commande AMOS, ni format de banque de production, ni accès DMA ou Blitter.

### Contrat de rendu simulé

1. Sur le back buffer physique, restaurer le snapshot du décor de la dernière frame de cette page (équivalent logique de Clear ; impossible avant le premier snapshot).
2. Déplacer le décor selon la caméra **précédente de cette même page**, puis repeindre les bandes exposées. Si le déplacement dépasse un écran, redessiner la totalité.
3. Repeindre les tuiles éditées depuis la révision propre à cette page. L'historique des éditions est borné à 128 changements : s'il n'est plus disponible, redessin complet plutôt qu'image obsolète.
4. Capturer le décor propre et superposer jusqu'à 64 rectangles Bob opaques (simple oracle, pas les vrais Bobs AGAPIC). Pen 0 est une couleur visible, pas une transparence implicite.
5. **Swap explicite uniquement après READY**. Une prévalidation refusée met le modèle en DIRTY et interdit Swap. Pas de modification de l'autre page.

**Écart connu avec B8 S1 réel :** le modèle accepte un premier Update vide tandis que la Lib native exige actuellement un premier setter Bob réussi pour amorcer End. La future intégration devra résoudre ou contractualiser ce cas. Les pixels chunky et rectangles Bob ne prouvent pas la copie planaire, le clipping bitplane, les SafePorts ni les coûts mémoire réels.

## Calculs géométriques à 320×256×8

| Élément | Capacité théorique |
| --- | ---: |
| Page planaire AGA | 81 920 octets |
| Deux snapshots plein écran | 163 840 octets |
| Tuile planaire opaque 16×16×8 | 256 octets |
| 256 tuiles opaques | 65 536 octets |
| Carte 64×64 avec indices sur un octet | 4 096 octets |

Ces volumes ne donnent aucune preuve sur l'emplacement Fast/Chip RAM, la taille des structures système ou les FPS.

## Résultats du prototype

**13 tests hôtes PASS**, [workflow M20 P0](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44789691639). Ils couvrent : caméra par page, bandes horizontales/verticales/diagonales, grands sauts, modifications visibles et hors champ, historique de révisions dépassé, pen 0 opaque, Bobs déplacés sans fantôme, refus et fermeture, géométrie pleine résolution 320×256 et **405 frames simulées** avec caméra et tuiles dynamiques.

- [Modèle hôte](../tools/m20_tilemap_model.py)
- [Tests automatisés](../tools/test_m20_tilemap_model.py)
- [Workflow CI](../.github/workflows/m20-tilemap-p0-host.yml)

Commande locale : python -B tools/test_m20_tilemap_model.py.

## Suite technique — sans changer B8 S1

Valider la conception de la banque de tuiles, la représentation planaire opaque/masquée, la copie source/destination lors des scrollings non alignés, les allocations Chip/Fast, le clipping et la synchronisation Safe/Disp. Ensuite seulement : **briques privées MC68020 avec tests Gate A**, puis contrat explicite avant toute nouvelle commande AMOS.

M20 P0 n'a **aucune Gate A native, B Runtime, C Compiler ou D matériel** : la CI ne prouve que la géométrie du modèle hôte. Ne pas présenter le test Python de 405 frames comme un test WinUAE.

Sources de cadrage : [roadmap](ROADMAP.md), [architecture](ARCHITECTURE.md), [audit documentaire AGE](AUDIT_AGE_V1_01_TILEMAP_C2P.md). Aucun code de AGE.lib n'est utilisé.
