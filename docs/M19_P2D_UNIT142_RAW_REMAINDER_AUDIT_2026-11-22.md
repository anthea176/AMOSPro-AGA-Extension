# UNIT142 — audit du reliquat brut : 12 298 initiaux, 5 948 restants (22/11/2026)

## Etat courant — lots 174–179 : R83 Close/End, source ASM (Gate A PASS)

La zone historique R83 $0005A..$002A2 (584 octets) est
identique au constructeur SHA-pinne R83. Six modules Motorola
MC68020 couvrent **480 octets** et portent chacun une mutation
de controle :
- $0005A..$00062 : Entry (8)
- $00066..$00088 : Guard (34)
- $000C0..$001B0 : Cleanup (240)
- $001B0..$001B4 : BSR.W vers le label prouve $0660A (4)
- $001B4..$001C2 : Postcall (14)
- $001EA..$0029E : SafeWait (180)

Conservation explicite dans le wrapper : BRA.W $00062..$00066
(4 octets, destination calculee $009DC), bloc brut
$00088..$000C0 (56 octets), Etat AGA
$001C2..$001EA (40 octets), et GetP
$0029E..$002A2 (4 octets).
La verification d'une destination ne suffit pas a convertir
un opcode dont le contrat source n'est pas encore prouve.
Aucune des 56 donnees/octets non classes n'est declaree
padding reutilisable.

**143 modules UNIT142**, **56 792 / 62 740 octets
(90,52 %) de vrai code source** ; **5 948 bruts** :
4 190 non executables prouves et **1 758 non classes**.
[Gate A MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45058090743) : construction directe
P2d 136 020 octets, SHA256 officiel conserve et
143 mutations isolees. Les deux Lib et l'ASC
de regression ne sont pas modifies. Gates B/C/D non requalifiees.

## Etat courant — lots 172-173 : R83 Screen Open, Gate A PASS

**137 modules UNIT142**, **56 312 / 62 740 octets (89,76 %)**
de vrai code MC68020 ; **6 428 octets bruts preserves**.
Les 756 octets de Screen Open R83 sont reproduits par l'emetteur
historique, dont 356 + 360 octets d'ASM editable, 36 octets de noms
de bibliotheques et 4 octets de `GetP`.
[Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45055315521),
avec SHA P2d identique et **137 mutations**.

| Nature non executable, prouvee par source | Octets |
| --- | ---: |
| Etat/tables/noms de bibliotheques | 3 692 |
| Pseudo-appels AMOS Main (45 x 6) | 270 |
| Marqueurs GetP (48 x 4) | 192 |
| Signatures AGACBLK / AGAPIC | 32 |
| **Total non executable source-prouve** | **4 186** |
| **Reliquat non classifie** | **2 242** |

Ce reliquat demeure en directives brutes. Les 2 242 octets
ne sont ni declares padding ni consideres automatiquement du
code : la provenance des emetteurs et le contrat de controle
sont requis avant toute conversion.
L'audit R83 `$0005A..$002A2` est une nouvelle piste, non acquise.

## Etat actuel — lots 170-171 et inventaire source (Gate A PASS)

**135 modules UNIT142**, **55 596 / 62 740 octets (88,61 %)**
de code MC68020 source-verifie et **7 144 octets bruts** conserves.
Les wrappers P1c/P1d apportent 38 + 50 octets de code.
[Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45053448900)
pour vasm direct, SHA P2d et 135 mutations confinees.

| Type d'octets prouve non executable | Octets |
| --- | ---: |
| Etat AGA, P0e/P0f, contexte P1c, table P1d | 3 656 |
| Pseudo-appels AMOS Main Rjsr (45 x 6) | 270 |
| Delimiteurs GetP (47 x 4) | 188 |
| Signatures AGACBLK et AGAPIC | 32 |
| **Total non-code source-prouve** | **4 146** |
| **Residuel non classifie** | **2 998** |

[Audit Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45054203673) :
les emetteurs historiques, la grammaire AMOS Main `rjsr` et
le format `GetP` sont recoupes avec les 135 plages et le SHA P2d.
Les 2 998 octets restants peuvent melanger code et donnees :
aucune conversion sans preuve de source, de point d'entree et de vasm.

## Etat courant — lots 168-169 P0f BSR.W Gate A PASS

**133 modules UNIT142** : **55 508 / 62 740 octets (88,47 %)**
en mnemoniques source, **7 232 octets bruts** conserves.
Les deux `BSR.W` de 4 octets sont prouvés par l'emetteur P0f
et les adresses symboliques de P0e. [CI Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45051866506) :
vasm direct, 133 mutations, AP20 et SHA P2d exacts.

Le code des Open wrappers P1c/P1d et leurs tables se trouvent
a l'extremite du groupe UNIT142. [Sonde source en cours](../tools/m19_p2d_unit142_p1cd_open_probe.py) :
aucune nouvelle classification avant comparaison des emitters et
du resultat vasm.

## Historique — lot 162 P0e valide

**126 modules UNIT142 : 53 846 / 62 740 octets en ASM (85,82 %)** ;
**8 894 octets bruts**. Les **788 octets de code P0e** ont ete
extraits avec [Gate A MC68020 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45048818538).
Les 1 544 octets de table P0e restent en `dcb.b` ; ils ne sont pas
comptes comme instructions. Le bilan des lots 159 a 161 ci-dessous
reste un **checkpoint historique**, non l'etat courant.

## Etat historique valide — lots 159 a 161

Le [commit CBlock](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/b2a3186a85e62fbe4431607343800616e95708f3)
a migre **2 616 octets** supplementaires (3 noyaux x 872 octets)
vers des modules MC68020, avec [Gate A source PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45047314451).
La couverture atteint **53 058 / 62 740 octets (84,57 %)**, soit
**125 modules UNIT142**. Le reliquat est **9 682 octets bruts**.
Les 36 octets de signatures \`AGACBLK \` / marqueurs \`GetP\`
sont des donnees, conserves. Aucun changement de Lib ni d'ASC.

Le manifeste d'export audit donne toujours la classification historique
**50 442 / 12 298** ; ces chiffres sont le point de depart, et non
la couverture courante des modules natifs. La preuve des 2 616 octets
CBlock provient de l'emetteur M18 et de vasm byte-exact.

## Provenance et limite

Le manifeste source officiel `src/asm_migration/m19_p2d/M19_P2D_SOURCE_MANIFEST.json`
de M19 P2d documente UNIT142 a **62 740 octets**, SHA256
`8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7`,
avec **50 442 octets de mnemoniques audites** et **12 298 octets dc**.
La reconstruction complete P2d reste **136 020 octets** SHA256
`ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.
Ce rapport classe **le type de preuve**, pas arbitrairement toutes les
directives comme du code ou des donnees.

Les 122 modules UNIT142 reconstruisent les 50 442 octets en source
MC68020 editable ; la presente phase n'a pas touche les 12 298
octets restants. Les controles du validateur imposent toujours
l'identite de **tous** les 62 740 octets du groupe et de la Lib complete.

## Inventaire des principaux blocs bruts

L'audit source versionne comporte **121 plages contigues dc**, total
**12 298 octets**. Les huit plus longues representent 11 364 octets :

| Offset UNIT142 (borne fin exclue) | Octets | Constat verifiable |
| --- | ---: | --- |
| `$0DCFC..$0F514` | 6 168 | zone AGAPIC, melange non classe de code, donnees et longues suites zero ; englobe entree publique non decodee `$0F4E2` |
| `$0ABC6..$0AF3A` | 884 | bloc commence par signature ASCII `AGACBLK ` |
| `$0B58A..$0B8FE` | 884 | contenu byte-identique au precedent |
| `$0BF52..$0C2C6` | 884 | contenu byte-identique aux deux precedents |
| `$00448..$00764` | 796 | bloc composite non classe ; marqueurs GetP presents |
| `$007F6..$00A62` | 620 | bloc composite non classe ; marqueurs GetP presents |
| `$0005A..$002A2` | 584 | bloc composite non classe |
| `$02364..$02584` | 544 | bloc composite non classe |

Le manifeste officiel signale une entree publique **non decodee**
a l'offset UNIT142 **62690 = `$0F4E2`**. Cela interdit toute
qualification globale de la grande zone finale comme simple padding.
Les trois blocs de 884 octets sont maintenant **recoupes avec le source**
`tools/m18_cblock_copy_emit.py::emit_cblock_copy_core()` : chacun est
exactement `b"AGACBLK " + core + b"GetP"`, avec un noyau natif de
**872 octets**. SHA256 du noyau source emis :
`8a3df13b72b0a62f237b7df068cc9d3f47c70af759d0bc64949ed765cfd65a97`.
La [Gate A source](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45046188073)
a confirme les trois enveloppes octet-identiques au noyau emis
par le constructeur historique. Cela etablit la **provenance source**,
pas encore un module Motorola editable ni un contrat d'allocation DMA.
Depuis le commit des lots 159–161, leurs 2 616 octets de code sont
**migrés et Gate A PASS**. La signature et GetP (36 octets) restent en
`dc.b`. Les **9 682 octets bruts** restants sont a classer sans invention.

## Inventaire automatique complementaire — Gate A PASS

Le script source-only
[`tools/m19_p2d_unit142_raw_probe.py`](../tools/m19_p2d_unit142_raw_probe.py)
est controle par [la CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45047829366)
avec resultat **PASS** : il recoupe le groupe P2d original avec les
**53 058 octets des 125 modules UNIT142**, sans remplacer la Lib.
Reliquat confirme : **9 682 octets**, dont le bloc
`$0DCFC..$0F514` de **6 168 octets**.

| Plage de zeros dans UNIT142 | Octets | Classement |
| --- | ---: | --- |
| `$0E018..$0E620` | 1 544 | zeros constates, usage a rapprocher de P0e |
| `$0ECA4..$0F0A4` | 1 024 | zeros constates, usage a rapprocher de P0f |
| `$0F0CA..$0F4E2` | 1 048 | zeros constates, role non qualifie |

Le meme outil retrouve octet-identiques les sources historiques
`capture_r84_v2` (**2 510 octets a `$0D336`**),
`bank_info_r84` (**1 088 octets a `$0CEF2`**), et
`scanline_r47` (**758 octets a `$074DA` et `$0DA06`**).
Les fonctions anciennes restent source-dependantes : ces correspondances
ne constituent **aucune nouvelle qualification Runtime/Compiler**.

La plage `$0DD04` commence par le prologue du noyau
`m19_p0e_object_table_emit.py`, mais son extraction ASM et son
reassemblage exact relevent d'une **validation distincte**.
Le marqueur `AGAPIC  ` a `$0DCFC` est conserve comme donnee, et
l'entree `$0F4E2` reste non decodee. Les suites de zeros ne sont
pas declarees comme padding reutilisable.

## Cartographie de la zone AGAPIC / P0e / P0f

Les limites suivantes sont recoupees avec les emetteurs Python de la
**P2d officielle**. La table explicite les roles prouvables ; des octets
nuls ne prouvent pas qu'une zone soit du padding reutilisable.

| Offset UNIT142 (fin exclue) | Octets | Provenance et classification |
| --- | ---: | --- |
| `$0DCFC..$0DD04` | 8 | nom de banque `AGAPIC  `, donnee |
| `$0DD04..$0E018` | 788 | P0e Object Table, code MC68020 migre au lot 162 |
| `$0E018..$0E620` | 1 544 | P0e : racine 8 octets + 64 slots de 24 octets, initialises a zero |
| `$0E620..$0E7F6` | 470 | pont AGA P0e, emitter `AGA_CORE` source-exact, migration en attente |
| `$0E7F6..$0ECA4` | 1 198 | P0f Stamp/Binder, executable et marqueurs AMOS a distinguer |
| `$0ECA4..$0F0A4` | 1 024 | P0f : table de 64 empreintes de 16 octets, initialisee a zero |
| `$0F0A4..$0F0CA` | 38 | residu non classe, a auditer avant tout source edit |
| `$0F0CA..$0F4E2` | 1 048 | zone de zeros, usage non qualifie |
| `$0F4E2..$0F514` | 50 | entree publique dont le decodage n'est pas encore prouve |

Cette decomposition couvre exactement **6 168 octets** de la zone
`$0DCFC..$0F514`. Le code P0e de 788 octets est deja extrait dans
[`src/native/m19_p2d/M19_UNIT142_P0E_OBJECT_CORE_MC68020.s`](../src/native/m19_p2d/M19_UNIT142_P0E_OBJECT_CORE_MC68020.s).
Le P0e AGA Bridge et P0f possedent leurs emitters sources
[`m19_p0e_split_bridge_emit.py`](../tools/m19_p0e_split_bridge_emit.py),
[`m19_p0f_object_identity_emit.py`](../tools/m19_p0f_object_identity_emit.py).
Un match source exact n'autorise pas a remplacer des `dc.b` sans un
reassemblage de module et un test de mutation confines. Les marqueurs
AMOS `FE11` ne sont jamais a compter comme du code MC68020.

## Sequence de reprise protegee

1. Recouper les limites des 121 plages avec le manifeste, les
   emitters et builders de **la meme P2d**, sans utiliser le binaire
   desassemble comme source de production.
2. Identifier et isoler les **donnees prouvees**, les marqueurs
   `GetP`, les pseudo-appels AMOS Main et le padding ; conserver
   leurs octets dans le wrapper ou dans des modules data explicitement
   contractuels, sans les compter comme instructions converties.
3. Les trois CBlock etant migres, examiner en priorite la zone
   `$0DCFC..$0F514`, puis qualifier l'entree `$0F4E2` par son
   contrat AP20/source. Aucune classification par simple analogie.
4. Pour toute plage executable prouvee, imposer offsets, etiquettes,
   assemblage direct `vasmm68k_mot -Fbin -m68020 -no-opt`, mutation
   unique, parite des autres groupes AP20 et SHA officiel P2d.
5. **Aucune modification de `dist/AMOSPro_AGA.Lib`, de
   `LAST_GOOD`, du seul ASC actif ou des archives** sans
   autorisation expresse distincte. Gate A != WinUAE B / Compiler C /
   materiel D.

**Statut : audit documentaire uniquement.** Aucune declaration
de nouvelle fonction, token AP20, DMA ou test WinUAE.
