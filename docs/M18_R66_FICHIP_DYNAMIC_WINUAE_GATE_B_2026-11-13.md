# M18/R66 — Gate B WinUAE interprétée : PASS (rendu et mémoire)

**13 novembre 2026 — R66 v0.13.11, candidate NON PROMUE.**

## Provenance et périmètre

Deux **captures WinUAE transmises par l'auteur** dans la conversation le 13/11/2026, correspondant au programme `M18-R66-FICHIP-DYNAMIC-01` : (1) écran AGA 256 couleurs ; (2) console AMOS et valeurs de contrôle. Les captures ne sont pas archivées comme fichiers binaires dans ce dossier. Validation visuelle et des valeurs affichées, **pas** une lecture instrumentée de chaque pixel.

- Bibliothèque unique active : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **41 804 octets**, SHA256 `e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca`, **60 commandes / 67 entrées AP20**.
- [Test actif interprété](../tests/current/M18_R66_FICHIP_DYNAMIC_01.asc), chargé avec **Project → Merge ASCII** et exécuté sans AMOS Compiler.
- **Gate A CPU 68000 PASS : 122 cas** (dispositions interpréteur et Compiler V2 simulé), [régression complète sur dernier binaire et documents PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43454808422). Cette simulation n'est pas une Gate C réelle.
- Deux commandes mises à l'épreuve : `Aga F Chip Bank Create(CacheBank,Count)` et `Aga F Chip Stage(SourceBank,CacheBank,IconID)`.

## Rendu visuel — conforme

Fond **bleu** avec trois icônes de **16×16 pixels**, cadres **blancs**, diagonales **rouges et vertes** :

| Coordonnées (origine x) | Fonction | Résultat observé |
|---|---|---|
| **X=30** | `Aga F Icon(12,1,30,60,1)` — CPU masqué | Cadre et diagonales colorées ; pixels index zéro **bleus** (fond préservé) |
| **X=90** | `Aga F Blit(11,1,90,60,1)` — Blitter masqué | Rendu **identique** à celui du CPU, intérieur bleu |
| **X=150** | `Aga F Blit(11,2,150,60,0)` — Blitter opaque | Même cadre et diagonales, intérieur **noir** |
| **X=210** | Slot 3 jamais préparé | **Aucun dessin parasite**, fond bleu |

Pas d'anomalie graphique apparente ni de Guru sur les captures.

## Console WinUAE — valeurs relevées

| Champ | Observation | Analyse |
|---|---|---|
| `CREATE FICON/CHIP` | **`1 1`** | Source `FICON8` et cache `FICHIP8` créés |
| `DUP/BAD` | **`0 0 0`** | Collision et paramètres invalides rejetés |
| `CHIP DELTA` | **`1192` octets** | Allocation Chip du cache de 4 icônes (taille utile 1168 octets, surcoût AMOS inclus) |
| `LEN/COUNT` | **`1168 4`** | `12 + 4 × 289 = 1168` |
| `STAGE INITIAL/RESTAGE/ICON2` | **`1 1 1`** | Staging initial, actualisation et autre emplacement |
| `PUT0/1/2` | **`1 1 1`** | Sources chunky importées dans FICON8 |
| `OLD/STALE/NEW MASK` | **`65535 65535 49155`** | Source modifiée sans rafraîchissement automatique : cache initial inchangé, puis conversion après `Stage` |
| `PLANE1` | **`32771`** | Premier plan de la ligne de référence |
| `READY1/2/3` | **`1 1 0`** | Deux icônes prêtes ; icône 3 non préparée |
| `BAD ID0/5/ALIAS/SRC/DEST` | **`0 0 0 0 0`** | Erreurs refusées |
| `OPEN/DB/SHOW` | **`1 1 1`** | Ouverture écran, double tampon et présentation |
| `CPU/MASKED/OPAQUE/UNREADY` | **`1 1 1 0`** | Rendus réussis et slot non prêt refusé |
| `CHIP BEFORE/ERASE` | **`1801960 1801960`** | Chip Free revenue exactement au niveau initial après libération |
| `FAST BEFORE/ERASE` | **`138312256 138312256`** | Fast Free revenue exactement au niveau initial |
| `ABK BEFORE/AFTER` | **`1168 1168`** ; `READY 0 0` | Cycle **sur un cache vierge recréé** : sauvegarde/chargement ABK sans changement de longueur/validité ; ce test ne prouve pas à lui seul la persistance d'une icône déjà staged |
| `NOS/CLOSE` | **`0 -1`** | Appel Blitter sans écran rejeté ; fermeture correcte |
| Résultat | **`RESULT 1` puis `CLOSE RETURNED`** | **Gate B PASS** |

**Attention sur les ressources :** `CHIP/FAST AFTER RAM FILE` est une information relevée *après* écriture du fichier `RAM:` ; les fichiers en RAM peuvent consommer des allocations. Les comparaisons pertinentes pour la libération des banques sont `BEFORE/ERASE`, identiques pour Chip et Fast.

## Bilan

**Gate A native : PASS. Gate B interprétée WinUAE : PASS, rendu conforme.** Sont couverts : création de cache en Chip, rejet des collisions/erreurs, slots et marqueurs ready, conversion et re-staging, transparence/opaque CPU versus Blitter, mémoire AMOS libérée, ABK vierge sauvegardée/rechargée, et fermeture.

**Non validé par ces captures :** comportement réel du **nouveau programme compilé Gate C** (une seule compilation manuelle à la fin M18), tests **Gate D** sur Amiga physique, performance CPU/Blitter chronométrée, persistance après sauvegarde d'un **slot déjà prêt**, et capture directe d'une icône depuis l'écran (future commande R67).

**Aucune promotion automatique.** R66 `dist/AMOSPro_AGA.Lib` et son ASC restent inchangés. R63 `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste protégée (38 736 octets, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`). Prochaine fonction prévue et distincte : [`Aga F Icon Capture(Bank,IconID,X,Y)`](M18_FICON8_CAPTURE_DESIGN.md), lecture de 16×16 indices depuis le back buffer AGA directement dans un slot `FICON8`.
