# UNIT142 — audit des directives brutes : 12 298 initiaux, 8 894 restants (22/11/2026)

## Etat courant — lot 162 P0e valide

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
