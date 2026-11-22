# M19 P2d — état vérifié des sources ASM natives (22/11/2026)

## Référence officielle intangible

La seule bibliothèque installable reste `dist/AMOSPro_AGA.Lib` (identique à
`dist/AMOSPro_AGA_LAST_GOOD.Lib`) : **136 020 octets**,
SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.
**100 commandes et 203 entrées AP20**. CPU natif minimum **MC68020**.

Aucun changement de la bibliothèque, de `LAST_GOOD`, de l'ASC actif ou des
tests précédemment validés. La migration des sources n'ajoute pas d'API.

## Classification de tous les groupes AP20 natifs P2d

| Groupe | Total octets | Instructions ASM source | Autres octets conservés | Modules |
| --- | ---: | ---: | ---: | ---: |
| BOBS (UNIT202) | 60 928 | 56 616 | 4 312 | 80 |
| AGA (UNIT142) | 62 740 | 58 166 | 4 574 | 166 |
| C2P (UNIT153) | 5 558 | 5 490 | 68 | 16 |
| IFF (UNIT156) | 2 508 | 2 330 | 178 | 6 |
| **Total** | **131 734** | **122 602 (93,07 %)** | **9 132** | **268** |

Le pourcentage indique les **instructions encodées en mnémoniques source**,
pas le pourcentage de fonctionnalités testées sur matériel. Aucun des quatre
groupes n'a d'octet résiduel de nature inconnue selon ses inventaires de
provenance. Les 9 132 octets hors instructions actives ne sont **pas** une
réserve de mémoire modifiable.

**BOBS** : 56 582 octets d'instructions, 34 octets de dispatcher AP20,
4 112 octets de structures source intégrées, 200 octets de données
`dc.b` contrôlées. Inventaire :
`tools/m19_p2d_bobs_raw_inventory.py --check` ; les deux NOP et le RTS
sont des instructions explicites.

**AGA/UNIT142** : 58 166 octets de mnémoniques MC68020 et 4 574 octets
de tables, états, signatures et contrats AMOS Main/`GetP`, inventoriés
sans octet inconnu. [Audit détaillé](M19_P2D_UNIT142_RAW_REMAINDER_AUDIT_2026-11-22.md).

**C2P/UNIT153** : 5 490 octets de code répartis dans 16 modules, dont
les deux finitions de boucle aux offsets `$00EDA..$00F04` et
`$014F8..$0151A` ; 68 octets d'ABI/non-code. L'audit contrôle
le recouvrement de tout le groupe et **16 mutations isolées**.
[Commit source](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/aec477e2e19b2875a5697164fbaa7277b5d3d15a) ·
[Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45062152446).

**IFF/UNIT156** : 2 330 octets de code dans 6 modules ;
80 octets de données/ABI (12 de `dos.library`, 64 pour la LUT nibble
RGB indexé et 4 de `GetP`). Les **98 octets à
`$007EE..$00850`** reproduisent exactement le suffixe de
l'ancienne boucle R80 de dépaquetage pixel par pixel. La
construction source R81 OPT020 a remplacé son point d'entrée par le
`BRA.W` à `$007EA` vers la boucle optimisée à `$00932`.
Le suffixe original est **conservé byte-exactement**, y compris
le premier mot `$0007` qui n'est pas une entrée d'instruction valide.
Il n'est ni de la nouvelle donnée graphique, ni une zone de
padding à réutiliser. Le contrat et les octets sont revérifiés par
`tools/m19_p2d_unit156_nibble.py --check` contre
`c2p_r80_iff_chunky_emit.py` et `c2p_opt020_variants.py`.
[Commit de provenance](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/1ae24f6f548e2402fdba01a39732915b9ea3992f) ·
[Gate A source](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45062506007).

## Compilation directe et limites

Le fichier [`src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s`](../src/native/m19_p2d/M19_P2D_LINKED_EDITABLE.s)
est un maître ASM éditable avec les quatre groupes et l'enveloppe
AP20. Il se réassemble **directement avec vasm**, sans régénérer les
sources via Python au moment de l'assemblage :

```sh
cd src/native/m19_p2d
vasmm68k_mot -Fbin -m68020 -no-opt -quiet -o M19_P2D_DIRECT_CHECK.Lib M19_P2D_LINKED_EDITABLE.s
```

Le résultat non modifié doit faire exactement **136 020 octets** et porter
le SHA256 indiqué en tête. Ne pas écrire cette sortie sous `dist/`.

La Gate A CI reconstruit aussi la P2d via le builder historique et
exécute les mutations UNIT142/153/156 ; la correspondance octet-identique
contrôle l'ABI et les positions relatives. Cela **ne constitue pas**
de nouveaux tests Runtime WinUAE (Gate B), vrai AMOS Compiler (Gate C)
ou Amiga physique (Gate D). Les Gates B/C déjà passées pour le scénario
BOB P2d inchangé restent historiques et ne qualifient pas de nouvelles
modifications de code.

## Décision de suite

Le chantier de **classification des sources natives P2d est clos** :
pour continuer, travailler sur une évolution de fonctionnalité ou un
refactoring explicitement défini, sous Gate A avant toute éventuelle
campagne B/C, sans promotion automatique de `LAST_GOOD`.
