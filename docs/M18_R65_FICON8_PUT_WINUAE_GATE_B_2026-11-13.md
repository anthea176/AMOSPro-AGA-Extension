# M18/R65 — FICON8 Bank Put — Gate B WinUAE interprétée PASS

**13 novembre 2026 — R65 v0.13.10, candidate NON PROMUE.** Preuves : **deux captures fournies par l'auteur dans la conversation**, une capture graphique WinUAE et une capture de la console AMOS intitulée `M18-R65-FICON8-PUT-01`. La méthode de test demandée était **AMOS interprété**, sans Compiler ; les captures attestent le résultat de ce protocole. Les images ne sont pas déposées en fichiers dans ce répertoire. La validation **ne vaut pas Gate C**.

## Identité du binaire et du test

- [Seule candidate](../dist/AMOSPro_AGA.Lib) : **40 116 octets**, SHA256 `6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2`, 58 commandes / 65 entrées AP20, R65 v0.13.10.
- [ASC unique actif](../tests/current/M18_R65_FICON8_PUT_01.asc) : `M18_R65_FICON8_PUT_01.asc` ; deux banques AMOS DATA 12 (`FICON8`) et 13 (256 pixels chunky).
- [Gate A 68000 / régression sur le binaire exact : PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43445143595), dont **98 cas natifs**, et **44 cas du modèle hôte**.
- [Contrat R65](M18_FICON8_BANK_PUT_DESIGN.md). R64 Create hérité, [Gate B précédente](M18_R64_FICON8_WINUAE_GATE_B_2026-11-13.md).

## Capture écran : résultat visuel conforme

L'écran AGA présente un **fond bleu**, deux motifs **16×16** à **contour blanc** et **diagonales rouges et vertes** :

| Position | Mode | Constat visuel |
|---|---|---|
| `X=30, Y=60` | `Aga F Icon(12,1,30,60,1)`, transparence index 0 | Cadre blanc et diagonales colorées ; **intérieur bleu**, le fond reste visible |
| `X=90, Y=60` | `Aga F Icon(12,2,90,60,0)`, opaque | Cadre blanc et diagonales colorées ; **intérieur noir** sur les pixels de couleur 0 |
| `X=150, Y=60` | `Aga F Icon(12,3,150,60,1)`, icône vide | Fond bleu inchangé, sans dessin parasite |

La capture montre aussi le pointeur souris, sans anomalie graphique évidente. La conformité est **visuelle** : pas de lecture automatique de pixels ou de chronométrage.

## Capture console : valeurs constatées

| Champ du programme de test | Résultat visible | Évaluation |
|---|---|---|
| `CREATE` et doublon | `1 1` / `DUP 0` ; `SRC LEN 256` | Créations de banques, refus de collision, taille source corrects |
| `PUT 1/2/3/4` | `1 1 1 1` | Import des icônes avant et après recréation de la banque |
| `SIZE/COUNT` et `LOAD` | `1164 4` / `1164 4` | `Save / Erase / Load` ABK préserve la structure |
| `MASK FIRST/ROW1` | `0 16380` | Masques 16 pixels conformes au motif ;
| `P0` | `65535 32771` | Premier plan de couleur exact sur deux lignes |
| `EMPTY MASK/PLANE` | `65535 0` | Slot 3 non touché |
| `SOURCE 0/17/30` | `255 4 5` | Données chunky source inchangées |
| `BAD ID0/5/OFF/ALIAS/BANK` | `0 0 0 0 0` | Cinq rejets non destructifs |
| `CHIP BEFORE/ERASE` | `1801664 1801664` | Chip Free revenue à sa valeur de référence |
| `FAST BEFORE/ERASE` | mêmes valeurs avant/après | Fast Free récupérée |
| `OPEN/DB/SHOW` | `1 1 1` | Écran, double buffer, présentation |
| `TRANSPARENT/OPAQUE/EMPTY` | `1 1 1` | Trois rendus réussis |
| `NOS/CLOSE` | `0 -1` | Appel hors écran rejeté et fermeture correcte |
| Résultat global | **`RESULT 1` ; `CLOSE RETURNED`** | **Gate B PASS** |

Le champ `CHIP/FAST AFTER RAM FILE` est **informatif** : une sauvegarde dans `RAM:` peut conserver des allocations liées au fichier ; ce n'est pas le bilan de fuite. Les comparaisons mémoire significatives sont celles avant et après `Erase`.

## Décision et limites

**Gate A : PASS. Gate B WinUAE interprétée : PASS, y compris visuel.** Aucun échec ni Guru visible dans les deux captures. L'essai couvre la création de banque, le remplissage de deux slots à partir de pixels chunky, les masques 8 plans, la transparence couleur 0, cinq entrées invalides, la sauvegarde/relecture ABK et la restitution de mémoire.

**Ce résultat ne valide ni :** Gate C par un **nouveau programme compilé** (réservée, sur demande de l'auteur, à **une seule compilation en fin M18**), Gate D sur matériel physique, performance réelle CPU/Blitter, ou staging dynamique Fast→Chip du cache `FICHIP8`.

**Aucune promotion automatique.** `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste **R63 v0.13.8, 38 736 octets**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. Le binaire R65 et l'ASC actif restent inchangés. La prochaine fonction M18 exige son propre contrat : création/rechargement et staging dynamique du cache Chip, sans assimiler `Bank To Chip` à la conversion du format.
