# M18/R67 — Gate B WinUAE interprétée : PASS (console et confirmation auteur)

**13 novembre 2026 — R67 v0.13.12, candidate NON PROMUE.**

## Provenance et limites des preuves

L'auteur a transmis une **capture de la console AMOS sous WinUAE**, issue du test `M18-R67-FICON8-CAPTURE-01`, puis confirmé explicitement **« ça passe »** au sujet du **rendu de l'écran graphique**. Il précise ne pas avoir eu le temps de faire une capture de cet écran graphique. **Aucune image du rendu graphique n'est donc disponible comme preuve archivée.** Le rendu est validé ici sur confirmation de l'auteur, pas sur inspection visuelle indépendante ni comparaison instrumentée des couleurs à l'écran.

- Candidate testée : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **43 180 octets**, SHA256 `ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5`, **61 commandes / 68 entrées AP20**.
- Programme exact : [`tests/passed/M18_R67_FICON8_CAPTURE_01.asc`](../tests/passed/M18_R67_FICON8_CAPTURE_01.asc), exécuté en **AMOS interprété** selon le protocole M18, sans passage Compiler.
- Nouvelle commande : `Aga F Icon Capture(Bank,IconID,X,Y)`, lecture du **back buffer AGA privé 8 plans** et copie de 288 octets dans un slot `FICON8` existant ; aucun staging Chip implicite.
- **Gate A : PASS**, 240 cas CPU 68000 et CI complète [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43456641279). La disposition Compiler simulée n'est pas une Gate C WinUAE réelle.

## Relevés de la capture console

| Indicateur | Résultat affiché | Interprétation |
|---|---|---|
| `BANK FICON/CHIP`, `PUT` | `1 1`, `1` | Banques source/cache créées, icône source remplie |
| `OPEN/DB/SWAPS` | `1 1 1 1` | Écran, double tampon et deux swaps réussis |
| `DRAW SOURCE NONALIGN/ALIGN` | `1 1` | Motif source dessiné aux deux positions |
| `CAPTURE NONALIGN/ALIGN` | `1 1` | Captures à X=31,Y=44 et X=16,Y=80 acceptées |
| `PIXELS 288 BYTE EQ2/EQ3` | `1 1` | 288 octets des slots capturés égaux au modèle source |
| `BAD X/Y/NEG/ID/BANK/0` | `0 0 0 0 0 0` | Six erreurs détectées sans succès parasite |
| `CHIP BEFORE/AFTER CAPTURE` | Identiques | Pas de variation de Chip Free entre les deux relevés |
| `FAST BEFORE/AFTER CAPTURE` | Identiques | Pas de variation de Fast Free entre les deux relevés |
| `ABK SAVE/LOAD LEN` | `1164 1164` | Banque remplie sauvegardée et rechargée |
| `ABK RELOADED EQ2/EQ3` | `1 1` | Conservation des deux slots après rechargement |
| `STAGE2/3 READY2/3/4` | `1 1 1 1 0` | Deux slots Chip préparés, quatrième non prêt |
| `CPU/MASKED/OPAQUE/UNREADY` | `1 1 1 0` | Retours CPU/Blitter attendus ; slot non prêt refusé |
| `NOS/CLOSE` | `0 -1` | Capture refusée après fermeture, écran fermé |
| Résultat final | **`RESULT 1` et `CLOSE RETURNED`** | Tests internes et retour à AMOS réussis |

## Rendu AGA

Le programme affiche normalement trois icônes de 16×16 pixels (cadre blanc, diagonales rouge/verte) sur fond bleu : X=30 en CPU masqué, X=90 en Blitter masqué (fond bleu conservé), X=150 en Blitter opaque (intérieur noir), et aucun dessin à X=210. **L'auteur confirme que le rendu passe, sans capture graphique disponible.** Il n'est pas possible de documenter davantage les pixels effectivement vus.

## Décision

- **Gate B AMOS interprété / WinUAE : PASS sur le scénario R67**, à partir de la capture console et de la confirmation visuelle de l'auteur (sans image graphique).
- **Gate C Compiler : EN ATTENTE**, un seul passage manuel prévu à la clôture de l'ensemble de M18. Aucune validation compilée R67 n'est revendiquée.
- **Gate D Amiga AGA physique : NON TESTÉE.**
- **R67 non promue** ; `dist/AMOSPro_AGA.Lib` reste candidate unique. **R63 `LAST_GOOD` inchangée et protégée.**
- Test ASC archivé octet pour octet dans `tests/passed/` ; aucun nouvel ASC n'est créé dans `tests/current/`. Prochaine étude M18 : contrat CBlock, sans implémentation anticipée.
