# UNIT142 — audit des 12 298 octets en directives brutes (22/11/2026)

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
Les trois enveloppes demeurent comptees dans les 12 298 octets bruts
jusqu'a un reassemblage direct validant des modules .s reellement extraits.

## Sequence de reprise protegee

1. Recouper les limites des 121 plages avec le manifeste, les
   emitters et builders de **la meme P2d**, sans utiliser le binaire
   desassemble comme source de production.
2. Identifier et isoler les **donnees prouvees**, les marqueurs
   `GetP`, les pseudo-appels AMOS Main et le padding ; conserver
   leurs octets dans le wrapper ou dans des modules data explicitement
   contractuels, sans les compter comme instructions converties.
3. Examiner en priorite les trois blocs `AGACBLK` et la zone
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
