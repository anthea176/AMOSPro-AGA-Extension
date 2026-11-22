# M19 P2d — migration progressive vers des modules ASM MC68020

**Dix-sept modules metier maintenables** depuis les emetteurs Python P2b/P2c/P2d (Gate A) :

| Source native | Plage BOBS (debut inclus, fin exclue) | Octets |
| --- | --- | ---: |
| [B8 S1 Bank Free — registre, Chip et 64 objets](M19_B8S1_BANK_FREE_MC68020.s) | `$076A8..$07962` | 698 |
| [B8 End/Register — cycle de vie et callbacks](M19_B8_END_REGISTER_MC68020.s) | `$071EE..$07364` | 362 code + 12 data |
| [P0i Routed Paint — banque privée et Blitter Safe](M19_P0I_ROUTED_PAINT_MC68020.s) | `$05CF8..$05F30` | 568 |
| [P2a Pair Check — lecture sécurisée Bob/P0f](M19_P2A_PAIR_CHECK_MC68020.s) | `$08A6E..$08BB6` | 328 |
| [P2a Geometry — deux descripteurs et limites](M19_P2A_GEOMETRY_MC68020.s) | `$0918A..$09858` | 1 742 |
| [P2a HotSpot — lecture et revalidation AGBO](M19_P2A_HOTSPOT_MC68020.s) | `$08E20..$0918A` | 874 |
| [P2a Chip Resolve — identities et cache Chip](M19_P2A_CHIP_RESOLVE_MC68020.s) | `$08BB6..$08E20` | 618 |
| [P2a Collision Kernel — rectangle et masque](M19_P2A_COLLISION_KERNEL_MC68020.s) | `$09858..$09B54` | 764 |
| [P2a Collision Query — private CPU bridge](M19_P2A_COLLISION_QUERY_MC68020.s) | `$09B54..$09D38` | 484 |
| [P2a public Bob Col — ABI/AP20 et callbacks](M19_P2A_PUBLIC_COL_MC68020.s) | `$09D38..$09E36` | 254 |
| [P2b Flip — setter/slots/cache](M19_P2B_FLIP_PUBLIC_MC68020.s) | `$09E36..$09F26` | 240 |
| [P2b Variant/Anchor — cache des orientations et HotSpot](M19_P2B_VARIANT_ANCHOR_MC68020.s) | `$09F26..$0A0AA` | 388 |
| [P2b Paint/Geometry — dessin et collisions](M19_P2B_PAINT_GEOMETRY_MC68020.s) | `$0A0AA..$0A1D2` | 296 |
| [P2b Cleanup — close/end/bank free/purge](M19_P2B_CLEANUP_MC68020.s) | `$0A1D2..$0A28E` | 188 |
| [P2b Planar — retournement H/V et allocation Chip](M19_P2B_PLANAR_MC68020.s) | `$0A28E..$0A4C0` | 562 |
| [P2c Planes](M19_P2C_PLANES_MC68020.s) | `$0B4C4..$0B58C` | 200 |
| [P2d Auto Update / Swap / Close](M19_P2D_CONTROLS_MC68020.s) | `$0B58C..$0B72A` | 414 |
| **Total de code ASM propre** | | **8 980** |

De plus, [P2b slots](M19_P2B_SLOTS_DATA_MC68020.s) definit **4 112 octets de donnees** (pointeur proprietaire 4 octets, 64 emplacements de 64 octets) avec des directives symboliques ; ces donnees ne sont pas du code converti.

## Provenance, contrats, limites

Les modules sont reconstitues **depuis les emetteurs sources** : `tools/m19_p2b_bob_flip_emit.py`, `m19_p2b_planar_orientation020_emit.py`, `m19_p2c_bob_planes_emit.py` et `m19_p2d_bob_auto_update_emit.py`. Le builder verifie les plages et leur contenu a partir des emetteurs d'origine ; la validation exige une reconstruction byte-exacte de P2d. L'assembler est cible `MC68020` minimum.

**La zone P2b Flip `$09E36..$0A4C0` est maintenant convertie de bout en bout** (1 674 octets de code). Le reste des modules BOBS (dont P2a, P1, P0 et B8) demeure a convertir. Le gros fichier [BOBS editable](M19_P2D_BOBS_EDITABLE.s), les unites AGA/C2P/IFF et le wrapper AP20 reposent encore partiellement sur les exports d'audit. Une unique exception `DC.W $4C04,$3000` dans le planar conserve le codage historique non canonique de `MULU.L D4,D3`. **Cette migration ne represente pas la conversion integrale de la bibliotheque.**

## Compilation directe (Windows)

```bat
BUILD_P2D_ASM_DIRECT.bat
```

Point d'entree vasm : `M19_P2D_LINKED_EDITABLE.s`. Sortie de developpement : `src/generated/p2d_editable/M19_P2D_DIRECT_ASM_UNTESTED.Lib`. Cette commande ne regenere aucun source Python et ne verifie pas le contrat AP20 avant d'ecrire le resultat. La CI confirme l'identite avec la bibliotheque P2d intacte.

## Compilation gardee et tests de modification

```bat
BUILD_P2D_ASM.bat
BUILD_P2D_ASM.bat --self-test-edit
```

Le script `tools/build_m19_p2d_editable_asm.py` refuse toute derive de taille, de tokens AP20, de titre, des autres unites ou d'une zone non migree. Sans edition, la reconstruction doit produire exactement **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Le self-test altere temporairement **une instruction dans chacun des dix-sept modules** (P2b Flip, P2b Planar, P2c, P2d), recompilant en memoire et exigeant un changement sur un seul octet dans le groupe BOBS.

Pour un edit a longueur constante, `BUILD_P2D_ASM.bat --allow-edited` cree uniquement `src/generated/p2d_editable/M19_P2D_EDITED_UNTESTED.Lib`. **Ne pas installer une version modifiee sans validation specifique.** Les bibliotheques de `dist/`, `LAST_GOOD`, les tests et exemples ne sont pas modifies par cette migration. Les Gates WinUAE Runtime B, vrai AMOS Compiler C et physique D **ne qualifient pas les futures editions natives** par la seule CI.

## Pseudo-instructions AMOS Main

Les 28 appels directs AMOS Main du groupe BOBS sont maintenant symboliques : `Bnk.GetAdr`, `Bnk.Change`, `Lst.Cree`, `Lst.Del`. `DC.W $FE11,$F700,INDEX` conserve la pseudo-instruction AMOS (non Motorola), avec index source verifie dans `amos_main_abi.rjsr`. La CI impose le nombre et les octets originaux de chaque appel.

Le bloc B8 source definit 4 octets ASCII `B8RG` et 8 octets `b8_b7_hook_root` comme donnees, non comme opcodes MC68020. L'ancien epilogue `End` est redirige vers le nettoyage P2b, exactement comme dans la bibliotheque P2d.
