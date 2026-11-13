# M18/R61 v0.13.6 — Fast Icon AGA, Gates B et C WinUAE

**13 novembre 2026 — Gate A CPU/CI PASS, Gate B AMOS interprété PASS et Gate C nouvel exécutable compilé WinUAE PASS, pour le scénario R61 testé. Gate D matérielle non effectuée.**

## Binaire et ressources contrôlés

- Bibliothèque de travail unique : [dist/AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib), **36 816 octets**, SHA256 `ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f`, R61 v0.13.6, 55 commandes / 62 entrées AP20.
- `LAST_GOOD` distincte, **R60 v0.13.5**, 35 056 octets, conservée dans [dist/AMOSPro_AGA_LAST_GOOD.Lib](../dist/AMOSPro_AGA_LAST_GOOD.Lib). **Aucune promotion R61.**
- [ASC R61 exact](../tests/current/M18_R61_FICON_01.asc) et [banque FICON8](../tests/current/M18_FICON8_SAMPLE_BANK10.abk) de 1 184 octets : quatre icônes AGA 16×16×8 plans.
- [CI intégrité et Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43420547089) : **226 cas CPU M68000**, dispositions interprétée et Compiler V2 simulées. Cette CI ne remplace pas les essais WinUAE.

## Résultats constatés sur trois captures fournies par l'auteur

La première capture montre cinq carrés à l'écran AGA : un carré noir, un carré blanc et trois motifs multicolores dont un décalé en X ; les autres motifs partiellement visibles témoignent des tests de clipping. Les deux autres captures sont les sorties du mode interprété et du mode compilé, ce dernier étant désigné par l'annotation manuscrite « compilé ». **Le bandeau `R61 AGA 256 / V2 COMPILER` est imprimé par l'ASC dans les deux modes et n'est pas une preuve autonome de compilation.**

| Contrôle | Interprété (Gate B) | Compilé (Gate C) |
|---|---|---|
| OPEN / DB / SW0 / SAFE | 1 / 1 / 1 / 1 | 1 / 1 / 1 / 1 |
| ICON (quatre) / SHIFT | 1 1 1 1 / 1 | 1 1 1 1 / 1 |
| CLIP (quatre bords) / OUT | 1 1 1 1 / 1 | 1 1 1 1 / 1 |
| BAD BANK / ID / MODE | 0 / 0 / 0 | 0 / 0 / 0 |
| R60 REJECT / SWAP / NOS / CLOSE | 0 / 1 / 0 / -1 | 0 / 1 / 0 / -1 |
| CHIP BEFORE / END | **1 797 840 / 1 797 840** | **1 861 944 / 1 861 944** |
| RESULT | **1** | **1** |
| Fin | CLOSE RETURNED | CLOSE RETURNED |

**Écran Program interrupted at line 141 (interprété) :** `Wait Vbl` se trouve dans la boucle de maintien finale `Do / Wait Vbl / Loop`, après `RESULT 1` et `CLOSE RETURNED`. L'interruption de ce programme de test après sa fin utile n'est pas un plantage de la routine native.

Les valeurs Chip Free diffèrent entre exécutions, mais **ne changent pas pendant chaque essai**. Le résultat et le rendu sont cohérents avec les cas de test ; aucune comparaison automatique pixel à pixel de la capture WinUAE n'a été réalisée.

## Limites et suites

**Gates A/B/C PASS sur ce scénario uniquement.** Pas de mesure du placement effectif Fast de la banque FICON8 ; pas de benchmark Fast Icon natif huit plans ; pas encore de cache Chip ni backend Blitter masqué ; pas de Gate D sur Amiga physique. La CI d'intégrité R61 n'est pas une régression complète de pré-publication sur matériel.

Conserver R61 dans la seule bibliothèque de travail et ne pas toucher à la R60 `LAST_GOOD` avant accord exprès de l'auteur sur une promotion. L'ASC actif validé reste inchangé.
