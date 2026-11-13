# M18 / R64 — Gate B WinUAE interprétée : PASS avec contrôle visuel (13/11/2026)

**Résultat : Gates A/B PASS. R64 v0.13.9 reste NON PROMUE ; R63 `LAST_GOOD` inchangée.**
Il ne s'agit pas d'une Gate C Compiler. La validation manuelle Compiler demeure réservée à la fin de M18 ; Gate D Amiga physique non faite.

## Livrables et provenance

- Candidate [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **39 100 octets**, SHA256 `4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c`, 57 commandes, 64 entrées AP20.
- Bibliothèque protégée [`LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) : R63 v0.13.8, **38 736 octets**, SHA256 `fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba`. Aucun remplacement.
- [Gate A native + CI de candidate : PASS, 42 cas](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43441501815) sur le commit `6a939b0` (les deux dispositions ABI, vérification source stricte, régressions).
- [ASC actif exact](../tests/current/M18_R64_FICON8_CREATE_01.asc) : `M18_R64_FICON8_CREATE_01.asc` (unique test actif, à conserver pour relecture).
- Preuves utilisateur : **deux captures WinUAE du 13 novembre 2026**, `image(20261113-142409).png` (écran AGA) et `image(20261113-142421).png` (résultats AMOS). Les captures ont été communiquées dans la conversation, **non déposées en binaires dans GitHub**.

## Retours interprétés observés

| Vérification | Résultat visible | Conclusion |
|---|---|---|
| `CREATE` deux fois, après `Erase` | `1 1` | OK |
| Collision avant et après reload | `DUP 0`, `RELOAD DUP 0` | Refus sans écrasement |
| Création `FICON8` | `SIZE/COUNT 1164 4` | 12+4×288 octets |
| `Save/Erase/Load` | `LOAD 1164 4` | Taille et nombre d'icônes conservés |
| Masque première/dernière icône | `65535 65535` | Masque `$FFFF` correct |
| Plans échantillonnés | `0 0` | Couleur zéro |
| Mauvais numéro et tailles | `BAD BANK/COUNT 0 0 0` | Refus attendus |
| `Chip Free` avant / après premier `Erase` | `1796464 / 1796464` | Mémoire Chip récupérée |
| `Fast Free` avant / après premier `Erase` | `13811632 / 13811632` | Mémoire Fast récupérée |
| Écran, DB, affichage | `OPEN/DB/SHOW 1 1 1` | OK |
| Appels CPU masqué/opaque | `TRANSPARENT/OPAQUE 1 1` | OK |
| Après fermeture | `NOS/CLOSE 0 -1` | Hors écran refusé, écran clos |
| Verdict | **`RESULT 1`** puis **`CLOSE RETURNED`** | **PASS** |

**Attention mémoire :** `CHIP/FAST AFTER RAM FILE` est relevé après une sauvegarde dans `RAM:`. Ce n'est pas une mesure propre de fuite : le fichier créé consomme de la mémoire. La comparaison légitime est **BEFORE/ERASE**.

## Vérification du rendu graphique

L'image WinUAE pendant les 125 VBL de maintien montre un **fond bleu uniforme**, sans carré noir à **X=30, Y=60** (icône vide, mode transparent), et un **carré noir plein à X=90, Y=60** (icône vide, mode opaque). Le comportement attendu pour `FICON8` est ainsi **confirmé visuellement**. Il ne s'agit **pas** d'une comparaison automatisée pixel par pixel ; les captures n'évaluent pas le cache `FICHIP8` ni les performances du Blitter.

## Décision de suivi

**Gate B AMOS interprétée/WinUAE PASS.** Les appels invalides sont refusés, les banques AMOS sont créées, sauvegardées et rechargées, et la mémoire est rendue après effacement. Aucun changement du code source ou du binaire R64 ne résulte de ces captures.

**R64 reste candidate non promue** : ne pas copier dans `LAST_GOOD` sans accord explicite séparé. Gate C Compiler uniquement **en fin M18**, Gate D physique non faite. Prochaine fonction éventuelle : **remplissage/mise à jour d'un slot FICON8**, contrat à discuter et valider avant développement. Voir [conception](M18_FICON8_BANK_CREATE_DESIGN.md), [roadmap](ROADMAP.md), [règles](../EXTENSION_SOURCE_RULES.md).
