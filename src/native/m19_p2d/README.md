# M19 P2d — migration progressive vers des modules ASM MC68020

**80 modules metier maintenables** issus des emetteurs Python historiques P0i/B7/B8/P2a/P2b/P2c/P2d (Gate A) :

**BOBS actuel :** 56 582 octets d'instructions MC68020 (dont
2 NOP de padding et 1 RTS explicite), 4 112 octets de structures deja
integrees aux modules, 200 octets de donnees `dc.b` dans le source BOBS
principal et 34 octets de dispatcher AP20. Total **60 928 octets**,
inchange octet pour octet.

| Source native | Plage BOBS (debut inclus, fin exclue) | Octets |
| --- | --- | ---: |
| [P0 Core Dispatch — entrées BOBS et cycles AMOS](M19_P0_CORE_DISPATCH_MC68020.s) | `$00022..$020A2` | 8 320 |
| [P0 Get Pipeline — capture banque et validation image](M19_P0_GET_PIPELINE_MC68020.s) | `$020CE..$03772` | 5 796 |
| [P0j Image Gate return — epilogue ABI](M19_P0J_IMAGE_RETURN_MC68020.s) | `$06254..$06264` | 16 |
| [P0j Prechecked Paint — validation et chemin All](M19_P0J_PRECHECKED_PAINT_MC68020.s) | `$06264..$0627E` | 26 |
| [P0 Screen Pre-Close — fermeture et callbacks](M19_P0_SCREEN_PRECLOSE_MC68020.s) | `$046D4..$048FA` | 550 |
| [P0c Program End callback — registre et retour ABI](M19_P0C_PROGRAM_END_CALLBACK_MC68020.s) | `$048FA..$049A8` | 174 |
| [P0 banque/image — resolution et relais](M19_P0_BANK_IMAGE_RESOLVE_MC68020.s) | `$049A8..$05A5C` | 4 276 |
| [P0 Relais Off/Read/Reset et retour](M19_P0_RELAY_COMMANDS_MC68020.s) | `$05A6A..$05B6E` | 260 |
| [P0 Relay Put — entree et selecteur](M19_P0_RELAY_PUT_MC68020.s) | `$05A5C..$05A6A` | 14 |
| [P0 Bob public et precontrole de frame](M19_P0_PUBLIC_FRAME_MC68020.s) | `$05B6E..$05CF8` | 394 |
| [B7 Guarded Draw — callback et control End](M19_B7_GUARDED_DRAW_MC68020.s) | `$06D4E..$06EAC` | 350 |
| [B7 End — pont AMOS et fermeture sure](M19_B7_END_MC68020.s) | `$06EAC..$06FA6` | 250 |
| [B7/B8 Draw/Close — relais et garde End](M19_B7_B8_DRAW_BRIDGE_MC68020.s) | `$06FA6..$071E8` | 578 |
| [B8 Close Branch — relais fermeture](M19_B8_CLOSE_BRANCH_MC68020.s) | `$071E8..$071EC` | 4 |
| [B8 S1 Bank Free — registre, Chip et 64 objets](M19_B8S1_BANK_FREE_MC68020.s) | `$076A8..$07962` | 698 |
| [B8 NoDraw/Prestage — enregistrement End et staging banque](M19_B8_NODRAW_PRESTAGE_MC68020.s) | `$07364..$07698` | 820 |
| [B8 S1 Bank Return — epilogue ABI](M19_B8S1_BANK_RETURN_MC68020.s) | `$07698..$076A8` | 16 |
| [B8 End/Register — cycle de vie et callbacks](M19_B8_END_REGISTER_MC68020.s) | `$071EE..$07364` | 362 code + 12 data |
| [P1b HotSpot Join — jonction et pointeurs image](M19_P1B_HOTSPOT_JOIN_MC68020.s) | `$07962..$079F2` | 144 |
| [P1b Paint Continue — jonction et drapeau clip](M19_P1B_PAINT_CONTINUE_MC68020.s) | `$079F2..$07A14` | 34 |
| [P1b HotSpot — origine et clipping signes](M19_P1B_HOTSPOT_ORIGIN_MC68020.s) | `$07A14..$07AC2` | 174 |
| [P1c Frame Dispatch — mode de priorite](M19_P1C_FRAME_DISPATCH_MC68020.s) | `$07AC2..$07AE8` | 38 |
| [P1c Priority — reglage 0 a 3 et retour AMOS](M19_P1C_PRIORITY_MC68020.s) | `$07B84..$07BBA` | 54 |
| [P1c Context — garde State, owner et lecture mode](M19_P1C_CONTEXT_MC68020.s) | `$07AE8..$07B84` | 156 |
| [P1c Frame Preflight — garde Etat et collecteur](M19_P1C_FRAME_PREFLIGHT_MC68020.s) | `$07BBA..$07C18` | 94 |
| [P1c Order Collect — tri stable des Bobs](M19_P1C_ORDER_COLLECT_MC68020.s) | `$07C18..$07C98` | 128 |
| [P1c Ordered Frame Draw — parcours, dessin et restauration](M19_P1C_FRAME_DRAW_MC68020.s) | `$07C98..$07D7E` | 230 |
| [P1d Bob Limit — rectangles, validation et reset](M19_P1D_LIMIT_MC68020.s) | `$07D7E..$07DFE` | 128 |
| [P1d Scoped Paint — relais et nettoyage Bob ID](M19_P1D_SCOPED_PAINT_MC68020.s) | `$07DFE..$07E1C` | 30 |
| [P1d Clip Bridge — bornage et Safe Blitter](M19_P1D_CLIP_BRIDGE_MC68020.s) | `$07E20..$07E6A` | 74 |
| [P1d Intersect — intersection des deux rectangles](M19_P1D_INTERSECT_MC68020.s) | `$07E6A..$07F00` | 150 |
| [P1e Del Bob — validation arguments suppression](M19_P1E_DEL_BOB_MC68020.s) | `$07F00..$07F2E` | 46 |
| [P1e Ins Bob — preparation arguments insertion](M19_P1E_INS_BOB_MC68020.s) | `$07F2E..$07F54` | 38 |
| [P1e Edit Bootstrap — controle banque et allocation](M19_P1E_EDIT_BOOTSTRAP_MC68020.s) | `$07F54..$08306` | 946 |
| [P1e Edit Objects — validation objets et adresses stamp](M19_P1E_EDIT_OBJECTS_MC68020.s) | `$08306..$0840A` | 260 |
| [P1e Edit Preflight — validation banque et recherche image](M19_P1E_EDIT_PREFLIGHT_MC68020.s) | `$0840A..$08498` | 142 |
| [P1e Preflight Next — iteration et release Chip](M19_P1E_EDIT_PREFLIGHT_NEXT_MC68020.s) | `$08498..$084C6` | 46 |
| [P1e Edit Publish — remplacement banque et registre](M19_P1E_EDIT_PUBLISH_MC68020.s) | `$084C6..$08516` | 80 |
| [P1e Edit Stamps — selection et actualisation des objets](M19_P1E_EDIT_STAMPS_MC68020.s) | `$08516..$085A6` | 144 |
| [P1e Edit Commit — iteration, Bnk.Change et Lst.Del](M19_P1E_EDIT_COMMIT_MC68020.s) | `$085A6..$085E8` | 66 |
| [P1e Cleanup — purge cache et Lst.Del AMOS](M19_P1E_EDIT_CLEANUP_MC68020.s) | `$085E8..$08632` | 74 |
| [P1e Validate Bank — wrapper validation](M19_P1E_VALIDATE_BANK_MC68020.s) | `$08632..$0865E` | 44 |
| [P1e Validate Stage — relais Chip](M19_P1E_VALIDATE_STAGE_MC68020.s) | `$0865E..$0866C` | 14 |
| [P1e Repack Entry — copie, generation et validation tailles](M19_P1E_REPACK_ENTRY_MC68020.s) | `$0866C..$08722` | 182 |
| [P1e Repack Insert — dimensions, stride et plan](M19_P1E_REPACK_INSERT_MC68020.s) | `$08722..$087C2` | 160 |
| [P1e Repack Scan — lecture repertoire AGBO](M19_P1E_REPACK_SCAN_MC68020.s) | `$087C2..$08820` | 94 |
| [P1e Repack Prepare — capacite et nouvelle banque](M19_P1E_REPACK_PREPARE_MC68020.s) | `$08820..$088EE` | 206 |
| [P1e Repack Copy — repertoire et pixel planes](M19_P1E_REPACK_COPY_MC68020.s) | `$088EE..$089B6` | 200 |
| [P1e Repack Final — image vide et fermeture](M19_P1E_REPACK_FINALIZE_MC68020.s) | `$089B6..$08A6E` | 184 |
| [P0i Routed Paint — banque privée et Blitter Safe](M19_P0I_ROUTED_PAINT_MC68020.s) | `$05CF8..$05F30` | 568 |
| [P0j Frame Image Gate — validation images avant rendu](M19_P0J_IMAGE_GATE_MC68020.s) | `$05F30..$06254` | 804 |
| [P0j Explicit Bank — resolution banque/Chip et Safe](M19_P0J_EXPLICIT_BANK_MC68020.s) | `$0627E..$0685C` | 1 502 |
| [P0j Safe Tail — validation finale des buffers](M19_P0J_SAFE_TAIL_MC68020.s) | `$0685C..$068FA` | 158 |
| [P1b Frame Branch — relais de mode](M19_P1B_FRAME_BRANCH_MC68020.s) | `$068FA..$068FE` | 4 |
| [P1b Frame/Guard — dessin, barrières, fermeture](M19_P1B_FRAME_GUARD_MC68020.s) | `$06902..$06D36` | 1 076 |
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
| [P2d support tail — code source restaure](M19_P2D_SUPPORT_TAIL_MC68020.s) | `$0B72A..$0C4FE` | 3 540 |
| [P2d service body — routines natives](M19_P2D_SERVICE_BODY_MC68020.s) | `$0C51E..$0DA10` | 5 362 |
| [P2d system service — code source restaure](M19_P2D_SYSTEM_SERVICE_MC68020.s) | `$0DA30..$0DCB4` | 644 |
| [P2d Service Update Bridge — controles et appel service](M19_P2D_SERVICE_UPDATE_BRIDGE_MC68020.s) | `$0DCB4..$0DD96` | 226 |
| [P2d service guards — controles internes](M19_P2D_SERVICE_GUARDS_MC68020.s) | `$0DD96..$0E538` | 1 954 |
| [P2d Service Root Reset — remise a zero du contexte](M19_P2D_SERVICE_ROOT_RESET_MC68020.s) | `$0E538..$0E59E` | 102 |
| [P2d public update — routines de service](M19_P2D_PUBLIC_UPDATE_MC68020.s) | `$0E5C8..$0EDD0` | 2 056 |
| [P2d Service Return — epilogue ABI](M19_P2D_SERVICE_RETURN_MC68020.s) | `$0E59E..$0E5B0` | 18 |
| [P2d Public Query Head — resultat AMOS](M19_P2D_PUBLIC_QUERY_HEAD_MC68020.s) | `$0EDD0..$0EDF4` | 36 |
| [P2d Public Query Tail — epilogue d'ABI](M19_P2D_PUBLIC_QUERY_TAIL_MC68020.s) | `$0EDF4..$0EE00` | 12 |
| [P0 Checked Registry — controle de banque et registre](M19_P0_CHECKED_REGISTRY_MC68020.s) | `$03792..$046CC` | 3 898 |
| **Total de code ASM propre** | | **56 582** |

En plus du code, [P2b slots](M19_P2B_SLOTS_DATA_MC68020.s) definit **4 100 octets de donnees** (pointeur proprietaire 4 octets et 64 emplacements de 64 octets) ; le module B8 End/Register ajoute **12 octets de donnees** (`B8RG` et racine des callbacks). Soit **4 112 octets de donnees**, non comptes comme code ASM converti.

## Provenance, contrats, limites

Les modules sont reconstitues **depuis les emetteurs sources** : `tools/m19_p2b_bob_flip_emit.py`, `m19_p2b_planar_orientation020_emit.py`, `m19_p2c_bob_planes_emit.py` et `m19_p2d_bob_auto_update_emit.py`. Le builder verifie les plages et leur contenu a partir des emetteurs d'origine ; la validation exige une reconstruction byte-exacte de P2d. L'assembler est cible `MC68020` minimum.

**La zone P2b Flip `$09E36..$0A4C0` est convertie de bout en bout** (1 674 octets de code). P2a est converti, ainsi que les blocs P0i Routed Paint, P1b origine HotSpot, P1c priorite/dispatch/contexte/preflight/tri/dessin et P1d Limit / Scoped Paint / Clip Bridge / Intersect et P1e Del/Ins, bootstrap, controles objets/stamps, recherche image, iteration, publication, fermeture et actualisation, nettoyage, validation, staging et repacking integral (entree, insertion, scan, preparation, copie, finalisation), B7 End, B8 End/Register et B8 S1 Bank Free. Il reste d'autres routines BOBS P0/P1/B7/B8 a migrer. Le gros fichier [BOBS editable](M19_P2D_BOBS_EDITABLE.s), les unites AGA/C2P/IFF et le wrapper AP20 reposent encore partiellement sur les exports d'audit. Une unique exception `DC.W $4C04,$3000` dans le planar conserve le codage historique non canonique de `MULU.L D4,D3`. **Cette migration ne represente pas la conversion integrale de la bibliotheque.**


## Extraction par lots source-verifiee (depuis M19 P2d)

Le script [tools/m19_p2d_asm_batch.py](../../../tools/m19_p2d_asm_batch.py)
extrait plusieurs plages d'un seul coup. **Le listing d'audit ne fait pas
autorite** : le script exige les memes offsets et chaque octet de l'emetteur
Python historique ET du groupe BOBS AP20 P2d, refuse toute directive de donnees
non classee, et verifie la signature de chaque pseudo-appel AMOS Main.

Commande de controle rapide, sans modification des fichiers :
```bat
py -3 tools\m19_p2d_asm_batch.py --plan
py -3 tools\m19_p2d_asm_batch.py --check
BUILD_P2D_ASM.bat --self-test-batch
```

Pour afficher des sources candidates sans ecraser les modules :
```bat
py -3 tools\m19_p2d_asm_batch.py --emit src\generated\p2d_batch_preview
```

**CI :** chaque push reassemble P2d integralement, verifie son SHA, compare
l'assemblage direct et realise **un seul reassemblage avec une edition distincte
dans chaque module du lot actif**. L'exhaustif historique et le test groupe restent
lancables avec `--self-test-edit`, declenches automatiquement chaque dimanche
ou manuellement via GitHub Actions (`full_edit_tests`). Le binaire de
`vasmm68k_mot` est mis en cache par SHA source verrouille. Tout changement
de lib `dist/`, de `LAST_GOOD` ou des tests verrouilles est refuse par la CI
pour une livraison de source seule.

Le premier lot P1e a converti les plages `$07F54..$08306` (946 octets,
4 appels AMOS Main symboliques) et `$085A6..$085E8` (66 octets,
2 appels AMOS Main symboliques). Le controle de modification porte sur
`$07F59` et `$085E3`. Ces 1 012 octets sont du **source maintenable**
incluant 36 octets de pseudo-appels AMOS; ils ne correspondent pas a
1 012 octets d'instructions Motorola pures.

Le deuxieme lot source-verifie traite **4 plages, 3 704 octets** dans les
routines P0j/B7/B8 : `$05F30..$06254` (804 octets, un appel AMOS Main),
`$0627E..$0685C` (1 502 octets, deux appels AMOS Main),
`$06FA6..$071E8` (578 octets) et `$07364..$07698` (820 octets).
Le controle collectif modifie un octet de chaque nouveau module dans une
seule reconstruction AP20.
Le troisieme lot ajoute **1 584 octets** (3 modules) : P0j Safe Tail
`$0685C..$068FA` (158), P1b Frame/Guard `$06902..$06D36` (1 076)
et B7 Guarded Draw `$06D4E..$06EAC` (350). Le controle source verifie les
offsets et octets contre l'emetteur Python d'origine et le groupe BOBS P2d ;
la CI recalcule l'AP20 complet et teste une edition par module du lot.

Le quatrieme lot convertit **4 826 octets / 2 modules** : P0 Screen Pre-Close
`$046D4..$048FA` (550 octets) et P0 Bank/Image Resolve + relais
`$049A8..$05A5C` (4 276 octets). Les plages sont prouvees par l'emetteur
P2d et l'AP20 officiel ; aucune directive de donnees n'est convertie.
Le second module s'arrete sur le label source `relay_put_entry`, sans
absorber les octets du relais Put voisin. Le cinquieme lot ajoute
**654 octets / 2 modules** : P0 Relay Commands `$05A6A..$05B6E`
(260 octets) et P0 Public/Frame `$05B6E..$05CF8` (394 octets).
Le relais Put `$05A5C..$05A6A` demeure en octets historiques car
l'audit n'y fournit pas d'instructions sources verifiees. Le second
module s'arrete a la frontiere du module P0i deja migré, sans absorber
de code P0i. Le controle source prouve l'assembleur par l'emetteur P2d.
Le self-test groupe couvre desormais **22 modules**. Le source direct
`M19_P2D_BOBS_EDITABLE.s` inclut les quatre modules P0 des
quatrieme et cinquieme lots ; la CI controle leur assemblage MC68020
direct octet-identique avec P2d, sans regeneration Python.


Le sixieme lot restaure **4 184 octets de code / 2 modules** :
`P2D_SUPPORT_TAIL` (`$0B72A..$0C4FE`, 3 540 octets) et
`P2D_SYSTEM_SERVICE` (`$0DA30..$0DCB4`, 644 octets).
Ce sont des plages d'instructions pures sans donnees ni
pseudo-instructions AMOS Main. Leurs deux bornes sont des labels
d'offset et non des symboles natifs exportes par l'emetteur :
le controle de provenance compare d'abord le suffixe BOBS **entier**
de l'emetteur Python avec la Lib officielle puis impose les octets
et les offsets exacts de chaque plage; aucun desassemblage n'est
accepte comme seule autorite. L'assemblage direct et le test de
modification groupe couvrent desormais **22 modules**.

Le septieme lot convertit **5 362 octets de code / 1 module** :
`P2D_SERVICE_BODY` (`$0C51E..$0DA10`, 1 501 instructions
MC68020, aucun octet de donnees ni pseudo-appel AMOS).
La tranche `$0DA10..$0DA30` contient **32 octets de donnees**
`p2d_service_root`, conserves exactement dans le fichier BOBS
historique, hors du module executable. Preuve de source :
comparaison sur l'ensemble du suffixe BOBS avec l'emetteur P2d,
controle de chacun des 5 362 octets et des offsets, assemblage direct
vasm MC68020 byte-exact et test groupe portant desormais sur
**22 modules**. Aucun changement de `dist/`, `LAST_GOOD` ou
`tests/current/`.

Le huitieme lot ajoute **4 010 octets / 2 modules** :
`P2D_SERVICE_GUARDS` (`$0DD96..$0E538`, 1 954 octets) et
`P2D_PUBLIC_UPDATE` (`$0E5C8..$0EDD0`, 2 056 octets).
Ces plages sont du code sans donnees ni pseudo-appels AMOS Main.
Les donnees brutes `$0DCB4..$0DD96` (226 octets),
`$0E538..$0E59E` (102 octets) et `$0E5B0..$0E5C8`
(24 octets) restent intactes, comme les relais de code non
migres `$0E59E..$0E5B0` et `$0EDD0..$0EE00`.
La frontiere `$0E538` s'appuie sur la premiere ligne de
donnees verifiee, sans introduire de label dans l'export audit.
Le test groupe de la CI controle maintenant **22 modules**.
La validation reste Gate A source sans remplacement des Lib ni
qualification nouvelle WinUAE B/C.

Le neuvieme lot restaure **4 042 octets / 2 modules** :
`P0_CHECKED_REGISTRY` (`$03792..$046CC`, 3 898 octets,
deux pseudo-appels symboliques `AMOS_MAIN_GETADR` de 6 octets) et
`P1B_HOTSPOT_JOIN` (`$07962..$079F2`, 144 octets).
Les appels AMOS Main sont confirmes par les octets emetteurs
`FE11F700031D` et conserves a ABI identique. Le bloc de donnees
`registry_state` a `$046CC` et le relais brut
`p2b_paint_continue` a `$079F2` restent inchanges.
Le self-test groupe controle desormais **22 modules**.
Cette migration source ne change ni les bibliotheques officielles
ni les conditions des Gates B/C/D.

Le dixieme lot migre **14 116 octets / 2 modules** :
`P0_CORE_DISPATCH` (`$00022..$020A2`, 8 320 octets avec
12 pseudo-appels AMOS Main) et `P0_GET_PIPELINE`
(`$020CE..$03772`, 5 796 octets avec 4 pseudo-appels).
Le dispatcher AP20 original `$00000..$00022` (34 octets)
reste hors de l'emetteur natif et dans `M19_P2D_BOBS_EDITABLE.s`.
Les etiquettes historiques `UNIT_BOBS` et `get_entry` restent
dans le source principal; les modules commencent immediatement
apres ces etiquettes. Le bloc de banque `$020A2..$020CE`
(44 octets) et la table `$03772..$03792` (32 octets)
ne sont pas modifies. Le format `start_marker` du batch
permet les deux entrees qui n'utilisent pas `L_BOBS_xxxxx`.
Tous les appels `FE11F700xxxx` sont conserves symboliquement.
Pour les deux modules P0 du dixieme lot, la provenance est **composee** :
le prefixe P2c est reconstruit par `build_p2c()` avec `P2C_SHA`
epingle ; le suffixe P2d est reconstruit par
`emit_bob_auto_update()`, et leur frontiere interne est verifiee.
Un module peut traverser cette frontiere, mais chaque octet est
prouve independamment avant comparaison au P2d officiel.
Ce n'est pas une restitution fondee sur un desassemblage seul. La Gate A inclut
l'assemblage MC68020 direct et l'edition groupee de
**22 modules**. Aucun changement des bibliotheques installees,
des ASC ou de la LAST_GOOD.

Le onzieme lot source-verifie isole **86 octets de code / 4 modules** :
P0j Image Return (`$06254..$06264`, 16 octets), B8 S1 Bank Return
(`$07698..$076A8`, 16 octets), P2d Service Return
(`$0E59E..$0E5B0`, 18 octets) et le debut de la requete publique
P2d (`$0EDD0..$0EDF4`, 36 octets). Les labels ABI externes, les
deplacements et les destinations de branche sont conserves ; les
instructions sont comparees aux octets produits par l'emetteur natif
P2d avant reconstruction vasm MC68020. Le test d'edition groupee porte
desormais sur **26 modules**, chacun avec une mutation d'un octet
independante. Les zones `dc.b` non classees et la fin de l'epilogue
`$0EDF4..$0EE00` demeurent inchangees. Aucune nouvelle Lib, aucun ASC
et aucune promotion ; Gates WinUAE B/C/D non transferees.

Le douzieme lot migre **20 octets / 3 modules** : deux branchements
verifies P1b Frame (`$068FA..$068FE`) et B8 Close (`$071E8..$071EC`),
puis le retour public P2d (`$0EDF4..$0EE00`). Cette derniere plage est
a la fin de l'unite BOBS : le moteur de batch traite explicitement une borne
EOF sans creer de label artificiel ni changer un octet du binaire.
Les deux branches exposent leur octet bas sous forme d'une constante
edit-test, sans deplacement de cible dans la baseline ; la CI verifie
une mutation d'un octet par module du lot. Le test groupe couvre
desormais **29 modules source-verifies**. Les segments non classes,
notamment les zones `dc.b`, ne sont pas reinterpretés comme code.
Aucune modification des Lib officielles, des ASC ni des Gates B/C/D.

Le treizieme lot convertit **74 octets d'instructions / 3 modules**
provenant des zones auparavant `dc.b` : P0 Relay Put
(`$05A5C..$05A6A`, 14 octets), P0j Prechecked Paint
(`$06264..$0627E`, 26 octets) et P1b Paint Continue
(`$079F2..$07A14`, 34 octets). Le fichier d'audit demeure intact.
L'extracteur accepte ces trois ilots uniquement si les octets bruts
et leurs offsets concordent avec les deux emetteurs sources P2c/P2d
SHA-epingles ; les nouvelles sources ASM redigees explicitement
sont ensuite assemblees directement en mode MC68020 avec comparaison
byte-exact de l'AP20 officiel, plus une mutation distincte par module.
Le controle d'edition groupee couvre maintenant **32 modules**.
Les **708 octets** residuels `dc.b` dans BOBS doivent rester analyses
avant migration ; aucune bibliotheque ni ASC modifie.

Le quatorzieme lot migre **174 octets / 1 module P0c** :
callback `Program End` `$048FA..$049A8`, selon
`tools/m19_p0c_program_end_bridge_emit.py::emit_program_end_bridge`.
Le label interne `end_bridge_return` et la signature de l'ancien
End restent maintenus ; tous les branchements restent en taille .w.
L'audit original reste intact ; le nouvel ASM doit s'assembler en
MC68020 exactement comme la P2d source-reconstruite et passer l'edition
groupee de **33 modules**. Il reste **534 octets bruts** dans BOBS,
dont des donnees et de plus grosses routines a classifier. Aucun
binaire installable ni ASC modifie.

Le quinzieme lot migre **328 octets / 2 modules** : service update bridge
(`$0DCB4..$0DD96`, 226 octets) et service root reset
(`$0E538..$0E59E`, 102 octets). Branches inter-modules conservees,
validations pointeurs Exec et nettoyage transactionnel. Le second
module commence au premier octet brut de l'audit `$0E538` :
`raw_inclusive_start` ne recouvre pas le module Guards precedent.
Controle de provenance par emetteur P2d, vasm MC68020 byte-exact et
edition groupee **35 modules**. Il reste **206 octets en dc.b**
(donnees, padding et un relais RTS). Aucune bibliotheque officielle,
aucune LAST_GOOD ni campagne ASC modifiees.


Le seizieme lot convertit **6 octets de code/padding BOBS** restant :
les deux instructions `NOP` a `$068FE..$06902` et le `RTS`
a `$071EC..$071EE`, auparavant inscrits en `dc.b`. Aucun
module supplementaire : le total reste 80. Le controle
`tools/m19_p2d_bobs_raw_inventory.py` verrouille les **200 octets
encore en `dc.b`** comme donnees, leurs huit plages et les trois
opcodes de jonction ; il dispose d'un autotest et s'execute en CI.
La reconstruction P2d et l'assemblage vasm MC68020 doivent encore
etre identiques aux 136 020 octets et au SHA256 de la Lib officielle.
Aucune nouvelle Lib, aucune LAST_GOOD ni ASC modifies.

 Les sous-plages avec octets non classes ou donnees
(`$06264..$0627E`, `$068FA..$06902`, `$06D36..$06D4E`,
`$071E8..$071EE`, `$07698..$076A8`) sont sciemment laissees
hors des nouvelles inclusions. Les mnemoniques d'audit ne constituent
pas, seuls, une preuve de code maintenable.

La migration P1e est couverte par des modules; il reste des routines
BOBS P0/B7/B8, et les unites AGA/C2P/IFF et wrapper AP20 reposent encore
partiellement sur les exports d'audit. **Gate A source ne constitue pas
Gate B/C WinUAE.**

## UNIT156 — premier lot natif hors BOBS (17e lot)

Le bloc `UNIT156+$00932..$0095E` (44 octets, boucle de decomposition
des demi-octets via la table `$0095E`) a ete isole dans
[M19_UNIT156_NIBBLE_MC68020.s](M19_UNIT156_NIBBLE_MC68020.s).
La copie de travail [UNIT156_EDITABLE](M19_P2D_UNIT156_EDITABLE.s)
conserve tout le reste du groupe a l'identique, y compris les zones
d'audit et les donnees. Le groupe provient de l'emetteur P2d source,
taille 2 508 octets et SHA256 `4e14633eea1ed1fd906ee9f4691e3a0bfc3c6086aaea858f8d2fc1a88ea8f31b`.
Le nouveau [controle](../../tools/m19_p2d_unit156_nibble.py) confronte
les 44 octets a ceux du groupe source-verifie, impose l'identite des
modules, reconstruit la Lib P2d sous vasm -m68020, puis execute
une mutation d'un octet dans UNIT156 (et aucun autre groupe).
Total : **80 modules BOBS + 1 module UNIT156**, sans remplacement de
`dist/`, de `LAST_GOOD` ni de l'ASC de campagne. Ce Gate A
ne valide pas de nouveaux tests WinUAE Runtime/Compiler.

### UNIT156 — 18e lot : garde DOS systeme (42 octets)

Deuxieme zone source-verifiee de UNIT156 :
[M19_UNIT156_DOS_GUARD_MC68020.s](M19_UNIT156_DOS_GUARD_MC68020.s),
`$0099E..$009C8` (**42 octets**) ; acces Exec, detection
DOS/buffer et relais vers les chemins internes existants.
La table d'expansion `$0095E..$0099E`, la chaine `dos.library`
et le marqueur `GetP` suivant `$009C8` restent intacts.
Le test de groupe edite maintenant une constante par module et doit
observer **seulement deux octets changes** dans UNIT156, aucun ailleurs.
UNIT156 total source-verifie : **86 octets / 2 modules**.
Ensemble : **82 modules**, dont 80 BOBS. Gate A uniquement.

### UNIT156 — 19e lot : fin de conversion et nettoyage (214 octets)

La plage `UNIT156+$00850..$00926` devient le troisieme module
[M19_UNIT156_CONVERT_TAIL_MC68020.s](M19_UNIT156_CONVERT_TAIL_MC68020.s)
(214 octets). L'instruction `move.l #0,d0` de `$00918` encore
en `dc.b` est classee avec preuve emitter et code assemble MC68020 ;
les donnees `dos.library` a `$00926` restent en place.
Trois substitutions d'un octet, aux positions `$0091D`, `$00937`
et `$009AF`, sont controlees ensemble sans mutation hors UNIT156.
UNIT156 migre : **300 octets / 3 modules** ; ensemble **83 modules ASM**.
Aucune bibliotheque de `dist/` ni source ASC modifiees.

### UNIT156 — 20e lot : corps principal (1 494 octets)

Le corps `UNIT156+$00218..$007EE` est extrait du source d'audit
apres controle de la provenance sur **1 494 octets / 380 instructions**,
sans donnees intercalees. Nouveau module source :
[M19_UNIT156_MAIN_BODY_MC68020.s](M19_UNIT156_MAIN_BODY_MC68020.s).
Le seuil de lecture `cmpi.l #24,d5` devient un parametre ASM
a taille inchangee, avec mutation d'un seul octet a `$0021F`.
Gate A : egalite avec l'emetteur P2d, assemblage MC68020 direct,
puis **quatre octets modifies exactement** dans UNIT156 et aucun
autre groupe. Les 98 octets bruts suivants `$007EE..$00850`
restent hors module, sans classification hasardeuse.
UNIT156 migre : **1 794 octets / 4 modules** ; ensemble **84 modules ASM**.
Aucune bibliotheque officielle ou ASC modifie.

### UNIT156 — 21e lot : pipeline Get public (502 octets)

Nouveau module source : [M19_UNIT156_PUBLIC_GET_MC68020.s](M19_UNIT156_PUBLIC_GET_MC68020.s),
`UNIT156+$00022..$00218` (502 octets). Le dispatcher AP20 V2 de
34 octets a `$00000..$00022` reste inchange. L'appel AMOS Main
`FE11F700031D` a `$00212` est conserve en `dc.w` symbolique
(`UNIT156_AMOS_MAIN_GETADR=797`), pas modifie comme simple data.
Seuil d'image `cmpi.l #5,d0` parametre, test d'edition controle
les **5 octets mutables distincts** de UNIT156, aucun ailleurs.
UNIT156 source-verifie : **2 296 octets / 5 modules**.
Projet : **85 modules ASM** au total. Il reste le dispatcher,
les donnees et l'ilot `$007EE..$00850` encore brut.
Aucune modification des deux Lib officielles, ni des ASC.

### UNIT153 — 22e lot : premier preflight public (446 octets)

La plage `UNIT153+$00372..$00530` (121 instructions et deux labels)
devient le module source [M19_UNIT153_PUBLIC_PREFLIGHT_MC68020.s](M19_UNIT153_PUBLIC_PREFLIGHT_MC68020.s).
L'appel AMOS Main a `$00530` (`FE11F700031D`) et le dispatcher de
34 octets sont preserves dans le wrapper/audit non modifie.
Le [controle UNIT153](../../tools/m19_p2d_unit153_source.py) exige la
reconstruction P2d officielle, l'unite de **5 558 octets** SHA256
`6eda5283af42617aa13ad81e24d9130abedc4528ed05b469de2d765d20b4d700`,
l'identite directe vasm MC68020 et une mutation d'un octet en `$00381`.
Projet : **86 modules ASM** (80 BOBS, 5 UNIT156, 1 UNIT153).
Aucune bibliotheque officielle et aucun ASC modifies.

### UNIT153 — 23e lot : garde entree/systeme (230 octets)

Source native [M19_UNIT153_ENTRY_GUARD_MC68020.s](M19_UNIT153_ENTRY_GUARD_MC68020.s),
`UNIT153+$00022..$00108` (62 instructions). La pseudo-instruction AMOS
Main `$00108..$0010E` demeure dans le wrapper. Le zero initial de D3
devient `UNIT153_ENTRY_ZERO`, sans changement de longueur ni d'octets
par defaut.

### UNIT153 — 24e lot : validation du pointeur et nettoyage (596 octets)

Source native [M19_UNIT153_POINTER_VALIDATE_MC68020.s](M19_UNIT153_POINTER_VALIDATE_MC68020.s),
`UNIT153+$0010E..$00362` (150 instructions, quatre labels).
Le seuil de 24 octets devient `UNIT153_MIN_POINTER_BYTES`. La chaine
`c2p.library`, le marqueur GetP et le dispatcher restent intacts.
Le test d'edition modifie une constante dans chacun des trois modules
UNIT153 : exactement les octets `$00033`, `$00115`, `$00381`,
sans alteration des autres groupes AP20.

**UNIT153 : 1 272 octets / 3 modules. Total : 88 modules ASM**,
dont 80 BOBS et cinq UNIT156. Reconstruction et controle vasm MC68020
par CI Gate A ; aucune Gate B/C/D nouvelle par cette migration.
Les deux bibliotheques de `dist/` et les ASC restent proteges.

### UNIT153 — 25e lot : second chemin Get (1 040 octets)

Module [M19_UNIT153_SECOND_GET_MC68020.s](M19_UNIT153_SECOND_GET_MC68020.s),
`UNIT153+$00536..$00946` : 265 instructions et cinq labels,
sans donnees intercalees. Le seuil 24 devient la constante
`UNIT153_SECOND_MIN_POINTER_BYTES`; le marqueur GetP reste identique.

### UNIT153 — 26e lot : service court (180 octets)

Module [M19_UNIT153_SHORT_SERVICE_MC68020.s](M19_UNIT153_SHORT_SERVICE_MC68020.s),
`UNIT153+$0094A..$009FE` : 50 instructions et deux labels.
L'initialisation D3 devient `UNIT153_SHORT_INITIAL_D3`. Les marqueurs
GetP et toutes les autres plages sont conserves. La Gate A doit
detecter **cinq mutations d'un octet** aux positions `$00033`,
`$00115`, `$00381`, `$0053D`, `$00959`, sans changer
tokens, titre, structure AP20 ni autres groupes natifs.

**UNIT153 : 2 492 octets / 5 modules ; total : 90 modules ASM.**
Aucun changement de la Lib P2d, de `LAST_GOOD`, de l'ASC actif,
ni transfert de preuve WinUAE B/C par la seule migration source.

### UNIT153 — 27e lot : preflight de masse (466 octets)

Module [M19_UNIT153_BULK_PREFLIGHT_MC68020.s](M19_UNIT153_BULK_PREFLIGHT_MC68020.s),
`UNIT153+$00A02..$00BD4` : 122 instructions MC68020.
La constante initiale D3 devient parametree ; l'appel AMOS Main a
`$00BD4` est conserve hors source Motorola.

### UNIT153 — 28e lot : controle secondaire du pointeur (190 octets)

Module [M19_UNIT153_POINTER_RECHECK_MC68020.s](M19_UNIT153_POINTER_RECHECK_MC68020.s),
`UNIT153+$00BDA..$00C98` : 51 instructions et un label.
Le seuil de 24 octets devient parametrique. Sept mutations isolees
sont desormais verifiees dans UNIT153 par la Gate A, aucune ailleurs.

**UNIT153 : 3 148 octets / 7 modules ; 92 modules ASM au total.**
Aucune nouvelle Lib, aucun ASC, aucune promotion de LAST_GOOD.

### UNIT153 — 29e lot : marche memoire (572 octets)

[M19_UNIT153_MEMORY_WALK_MC68020.s](M19_UNIT153_MEMORY_WALK_MC68020.s) :
`UNIT153+$00C9E..$00EDA`, 159 instructions et 6 labels.
Le seuil de 24 octets devient symbolique. Le segment brut
`$00EDA..$00F04` est preserve sans interpretation.

### UNIT153 — 30e lot : nettoyage et resultat (152 octets)

[M19_UNIT153_WALK_CLEANUP_MC68020.s](M19_UNIT153_WALK_CLEANUP_MC68020.s) :
`UNIT153+$00F04..$00F9C`, 46 instructions, 11 labels.
Zero D3 parametre, GetP au bord final non converti. **Neuf mutations
d'un octet** controlees ensemble dans UNIT153, aucune ailleurs.

**UNIT153 : 3 872 octets / 9 modules. Total : 94 modules ASM.**
La bibliotheque officielle, LAST_GOOD et les tests AMOS sont inchanges.

### UNIT153 — 31e lot : troisieme preflight public (518 octets)

[M19_UNIT153_THIRD_PUBLIC_MC68020.s](M19_UNIT153_THIRD_PUBLIC_MC68020.s),
`UNIT153+$00FA0..$011A6`, 136 instructions ; zero initial symbolique.

### UNIT153 — 32e lot : troisieme controle pointeur (190 octets)

[M19_UNIT153_THIRD_POINTER_MC68020.s](M19_UNIT153_THIRD_POINTER_MC68020.s),
`UNIT153+$011AC..$0126A`, 51 instructions et un label ;
seuil minimum de 24 octets symbolique.

### UNIT153 — 33e lot : troisieme validateur (648 octets)

[M19_UNIT153_THIRD_VALIDATION_MC68020.s](M19_UNIT153_THIRD_VALIDATION_MC68020.s),
`UNIT153+$01270..$014F8`, 178 instructions, neuf labels ;
la plage brute `$014F8..$0151A` reste hors code source.

### UNIT153 — 34e lot : nettoyage final (152 octets)

[M19_UNIT153_THIRD_FINAL_MC68020.s](M19_UNIT153_THIRD_FINAL_MC68020.s),
`UNIT153+$0151A..$015B2`, 43 instructions et dix labels ;
dernier GetP intact. Quatre nouvelles constantes modifiables
sont controlees avec les neuf precedentes (13 mutations isolees).

**UNIT153 : 5 380 octets / 13 modules ; total : 98 modules ASM.**
Les **178 octets non migrés** de UNIT153 sont le dispatcher AP20,
les pseudo-appels AMOS Main, les donnees, marqueurs GetP et deux
iles brutes `$00EDA..$00F04` / `$014F8..$0151A`.
Ils restent volontairement dans le wrapper, sans interpretation.
La CI Gate A doit reconstruire P2d octet-identique ;
aucune modification de dist/ ni ASC et aucune nouvelle Gate B/C/D.

### UNIT153 — 35e lot : dispatcher AP20 V2 (34 octets)

[M19_UNIT153_DISPATCH_V2_MC68020.s](M19_UNIT153_DISPATCH_V2_MC68020.s) :
les 11 instructions `$00000..$00022` du dispatcher sont maintenant
un module source, sans changement binaire. Le test modifie uniquement
l'octet de l'instruction `subq.l #4,a7` (`$00000`) dans sa
reconstruction privee, avec 13 autres edits propres a UNIT153.

### UNIT156 — 36e lot : dispatcher AP20 V2 (34 octets)

[M19_UNIT156_DISPATCH_V2_MC68020.s](M19_UNIT156_DISPATCH_V2_MC68020.s) :
meme contrat de 11 instructions sur `$00000..$00022`.
La source native est rattachee a l'emetteur P2d, pas a un desassemblage
libre ; controle de six mutations d'un octet dans UNIT156, dont
`$00000` pour le dispatcher.

**Total : 100 modules ASM (80 BOBS, 14 UNIT153, 6 UNIT156).**
**UNIT153 : 5 414 / 5 558 octets**, les 144 restants sont des marqueurs,
donnees et deux ilots bruts. **UNIT156 : 2 330 / 2 508 octets**.
Les octets de l'ABI AP20 V2 doivent rester strictement identiques
dans la Lib P2d et LAST_GOOD. Les Gates B/C historiques ne se
transmettent pas a des edits futurs.

### UNIT142 — 37e a 40e lots : premiers modules natifs (458 octets)

Quatre plages autonomes de UNIT142 sont maintenant maintenues comme source
MC68020 et epinglees au builder officiel P2d :

- [dispatcher AP20 V2](M19_UNIT142_DISPATCH_V2_MC68020.s) : `$00000..$00022`, 34 octets ;
- [initialisation AGA](M19_UNIT142_INIT_ENTRY_MC68020.s) : `$00022..$0005A`, 56 octets ;
- [garde graphics.library](M19_UNIT142_GRAPHICS_GUARD_MC68020.s) : `$002C2..$0030C`, 74 octets ;
- [preflight ecran/graphics](M19_UNIT142_GRAPHICS_SCREEN_MC68020.s) : `$00322..$00448`, 294 octets.

Le [validateur UNIT142](../../tools/m19_p2d_unit142_source.py) epingle
l'ensemble des **62 740 octets UNIT142**, SHA256
`8627166cde406a11d4fd1c81bb03f301bb6efd91532b8796436ae8ec2543dee7`,
contre le groupe AP20 du builder source P2d. Il verifie les offsets et les
instructions, conserve les donnees et les marqueurs non classifies et
compare le wrapper natif compact a sa reconstruction deterministe.
Gate A : vasm MC68020 direct sans regen et **4 mutations d'un octet**
aux positions `$00000`, `$00045`, `$002CD`, `$00327`,
sans modifier les autres groupes, tokens, titre ou longueur.

**Total projet : 104 modules ASM** (80 BOBS, 14 UNIT153, 6 UNIT156,
4 UNIT142). Il reste 62 282 octets de UNIT142 hors modules, contenant
des instructions historiques et des zones de donnees / brut non classees.
Le passage des segments bruts en opcodes n'est pas presume. Aucune nouvelle
Lib, aucune LAST_GOOD, aucun ASC, aucune nouvelle Gate B/C/D.

### UNIT142 — 41e a 44e lots : validation IFF et couleurs (4 660 octets)

Quatre modules MC68020 issus de plages code-only, source-verifiees et
assemblees sans toucher aux marqueurs `GetP`, aux pseudo-appels AMOS Main
ou aux blocs bruts adjacents :

- [corps IFF load](M19_UNIT142_IFF_LOAD_BODY_MC68020.s) : `$00D3C..$0153A`, 2 046 octets ;
- [palette et ecran IFF](M19_UNIT142_IFF_PALETTE_BODY_MC68020.s) : `$015D8..$01BC4`, 1 516 octets ;
- [garde appel AMOS Main](M19_UNIT142_IFF_AP20_PRECALL_MC68020.s) : `$01BDE..$01E0C`, 558 octets ;
- [controles des couleurs](M19_UNIT142_COLOR_RANGE_MC68020.s) : `$0299A..$02BB6`, 540 octets.

Le validateur UNIT142 exige huit mutations d'un octet dans le seul groupe
UNIT142, comparant tous les groupes, le titre et les tokens AP20.
Reconstruction integrale P2d SHA256 et vasm direct `-m68020` inchanges.
**TOTAL : 108 modules ASM**, dont **5 118 octets UNIT142 en 8 modules**.
Les **57 622 octets** restants demeurent dans le wrapper natif source
verifie, sans requalification des zones brutes. Aucune Lib, LAST_GOOD
ou ASC de campagne modifies ; Gate B/C/D non transferees.

### UNIT142 — 45e a 48e lots : quatre entrees 020 (3 660 octets)

Quatre nouvelles plages d'instructions pures sont promues en modules
editables MC68020 a partir de l'emetteur P2d et de la preuve SHA globale :

- [entree $02E64](M19_UNIT142_ENTRY_02E64_MC68020.s) : `$02E64..$030E8`, 644 octets ;
- [entree $03270](M19_UNIT142_ENTRY_03270_MC68020.s) : `$03270..$034F0`, 640 octets ;
- [entree $034F4](M19_UNIT142_ENTRY_034F4_MC68020.s) : `$034F4..$03986`, 1 170 octets ;
- [entree $03C46](M19_UNIT142_ENTRY_03C46_MC68020.s) : `$03C46..$040FC`, 1 206 octets.

Les bornes avant les donnees/markers et tous les labels sont conserves.
Le test d'edition exige maintenant 12 mutations d'un seul octet dans
le seul groupe UNIT142. **112 modules ASM total, dont 8 778 octets
UNIT142 en 12 modules.** Aucun changement de Lib active, LAST_GOOD,
ASC ou qualification nouvelle Runtime/Compiler.

### UNIT142 — 49e a 52e lots : quatre entrees supplementaires (5 198 octets)

Source MC68020 verifiee contre le groupe UNIT142 integral du P2d
SHA-epingle, sans decoder les zones de donnees :
[entree $0530E](M19_UNIT142_ENTRY_0530E_MC68020.s) 1 004 octets,
[entree $0609E](M19_UNIT142_ENTRY_0609E_MC68020.s) 1 162 octets,
[entree $06678](M19_UNIT142_ENTRY_06678_MC68020.s) 2 446 octets,
[entree $0700A](M19_UNIT142_ENTRY_0700A_MC68020.s) 586 octets.

Les 16 constantes d'edition sont testees en une re-compilation
vasm MC68020 avec 16 octets distincts dans UNIT142 et aucun
autre changement AP20.
**TOTAL : 116 modules ASM, dont 13 976 octets UNIT142 en 16 modules.**
Les pseudo-appels AMOS Main, les marqueurs GetP et les champs de donnees
demeurent dans le wrapper au meme offset. Lib/LAST_GOOD/ASC inchanges.

### UNIT142 — 53e a 58e lots : six entrees exactes (3 810 octets)

Les plages **`$04256..$044E6`, `$044EA..$0479A`,
`$0479E..$04B3C`, `$04B40..$04D48`, `$04D4C..$04F54`
et `$04F58..$0514C`** deviennent six modules natifs
`M19_UNIT142_ENTRY_xxxxx_MC68020.s`, avec source prouve par les
octets du builder P2d. Chacune possede son test d'edition a un octet,
soit **22 mutations distinctes** limitees au groupe UNIT142.
Aucune donnee GetP ou autre segment brut n'est requalifie en code.

**TOTAL : 122 modules ASM**, dont **17 786 octets UNIT142 / 22 modules**.
Les bibliotheques P2d et LAST_GOOD, tous les ASC et Gates B/C/D
demeurent sans changement.

### UNIT142 — lots 59 a 64 : six blocs de code source (8 414 octets)

Ces blocs `$078A4..$07B2A`, `$07BC8..$08564`,
`$08618..$08CD6`, `$08D78..$09424`,
`$09C80..$09F66` et `$0A006..$0A472` deviennent
des modules `M19_UNIT142_BLOCK_xxxxx_MC68020.s`.
Les marqueurs AMOS Main / GetP et les donnees restent dans le wrapper.
Les `28` constantes editables ont chacune une mutation unique,
verifiee seulement sur le groupe UNIT142 par une compilation privee
vasm MC68020.

**TOTAL : 128 modules ASM**, dont **26 200 / 62 740 octets
UNIT142 en 28 modules**. Aucun changement de Lib installable,
LAST_GOOD, ASC ni nouvelle validation WinUAE.

### UNIT142 — lots 65 a 73 : neuf plages natives (9 614 octets)

Les neuf blocs `$0A476..$0A6DC`, `$0A71A..$0AB90`,
`$0B0A6..$0B58A`, `$0BA5E..$0BF52`, `$0C41C..$0C8BA`,
`$0C946..$0CED4`, `$0CF3E..$0D332`, `$0D336..$0D68E`
et `$0D99A..$0DCFC` sont du code MC68020 nettoye de ses
annotations d'audit, avec cible native prouvee par la Lib P2d.
Les marqueurs GetP/AMOS Main et donnees non code sont inchanges.
37 mutations distinctes de taille constante, dans UNIT142 seulement,
sont maintenant exigees par le test d'edition source.

**TOTAL : 137 modules ASM**, dont **35 814 / 62 740 octets de
UNIT142 en 37 modules**. Pas de modification des Lib, LAST_GOOD,
des ASC ni des preuves WinUAE/Compiler deja gelees.

### UNIT142 — lots 74 a 80 : sept plages natives (4 478 octets)

Sept plages additionnelles de mnemoniques MC68020 sont extraites de l'audit
et verrouillees contre la reconstruction officielle P2d :

- [bloc $0219C](M19_UNIT142_BLOCK_0219C_MC68020.s) : `$0219C..$0235C`, **448 octets** ;
- [bloc $0282C](M19_UNIT142_BLOCK_0282C_MC68020.s) : `$0282C..$02996`, **362 octets** ;
- [bloc $05150](M19_UNIT142_BLOCK_05150_MC68020.s) : `$05150..$052CA`, **378 octets** ;
- [bloc $05706](M19_UNIT142_BLOCK_05706_MC68020.s) : `$05706..$058C2`, **444 octets** ;
- [bloc $058C6](M19_UNIT142_BLOCK_058C6_MC68020.s) : `$058C6..$05C76`, **944 octets** ;
- [bloc $05C7A](M19_UNIT142_BLOCK_05C7A_MC68020.s) : `$05C7A..$0609A`, **1056 octets** ;
- [bloc $07482](M19_UNIT142_BLOCK_07482_MC68020.s) : `$07482..$077D0`, **846 octets** ;

**Total de migration source : 144 modules ASM**, dont **44 UNIT142** ;
**40 292 / 62 740 octets UNIT142 (64,22 %)** maintenables.
Le validateur exige 44 mutations distinctes d'un octet et une reconstruction
P2d identique, y compris le titre, les tokens et toutes les unites AP20.
Les **22 448 octets UNIT142 restants** conservent exactement leurs octets
d'audit, dont les donnees, GetP et pseudo-appels AMOS Main non classes.
Source-only : Lib, LAST_GOOD, ASC actif et preuves WinUAE inchanges.
Gate A a confirmer par CI ; aucune nouvelle Gate B/C/D revendiquee.


### UNIT142 — lots 81 a 100 : vingt blocs natifs (6 236 octets)

Vingt plages MC68020 source-verifiees contre le builder P2d ont ete
converties avec un test d'editabilite isole par module. Les donnees brutes,
marqueurs GetP et pseudo-appels AMOS Main restent dans le wrapper.

- [bloc $0D7C8](M19_UNIT142_BLOCK_0D7C8_MC68020.s) : `$0D7C8..$0D980`, 440 octets
- [bloc $01F32](M19_UNIT142_BLOCK_01F32_MC68020.s) : `$01F32..$020E0`, 430 octets
- [bloc $095EC](M19_UNIT142_BLOCK_095EC_MC68020.s) : `$095EC..$0978A`, 414 octets
- [bloc $09790](M19_UNIT142_BLOCK_09790_MC68020.s) : `$09790..$0992C`, 412 octets
- [bloc $0AF3A](M19_UNIT142_BLOCK_0AF3A_MC68020.s) : `$0AF3A..$0B0A0`, 358 octets
- [bloc $09B16](M19_UNIT142_BLOCK_09B16_MC68020.s) : `$09B16..$09C7A`, 356 octets
- [bloc $0B8FE](M19_UNIT142_BLOCK_0B8FE_MC68020.s) : `$0B8FE..$0BA58`, 346 octets
- [bloc $0652C](M19_UNIT142_BLOCK_0652C_MC68020.s) : `$0652C..$0666C`, 320 octets
- [bloc $0411A](M19_UNIT142_BLOCK_0411A_MC68020.s) : `$0411A..$04252`, 312 octets
- [bloc $03A24](M19_UNIT142_BLOCK_03A24_MC68020.s) : `$03A24..$03B4E`, 298 octets
- [bloc $00A80](M19_UNIT142_BLOCK_00A80_MC68020.s) : `$00A80..$00B9E`, 286 octets
- [bloc $01E12](M19_UNIT142_BLOCK_01E12_MC68020.s) : `$01E12..$01F30`, 286 octets
- [bloc $0D694](M19_UNIT142_BLOCK_0D694_MC68020.s) : `$0D694..$0D7A4`, 272 octets
- [bloc $02584](M19_UNIT142_BLOCK_02584_MC68020.s) : `$02584..$0268C`, 264 octets
- [bloc $07360](M19_UNIT142_BLOCK_07360_MC68020.s) : `$07360..$07468`, 264 octets
- [bloc $00BA2](M19_UNIT142_BLOCK_00BA2_MC68020.s) : `$00BA2..$00C9A`, 248 octets
- [bloc $03B52](M19_UNIT142_BLOCK_03B52_MC68020.s) : `$03B52..$03C42`, 240 octets
- [bloc $0273C](M19_UNIT142_BLOCK_0273C_MC68020.s) : `$0273C..$02828`, 236 octets
- [bloc $02C9A](M19_UNIT142_BLOCK_02C9A_MC68020.s) : `$02C9A..$02D7E`, 228 octets
- [bloc $0725A](M19_UNIT142_BLOCK_0725A_MC68020.s) : `$0725A..$0733C`, 226 octets

**164 modules ASM MC68020** au total, dont **64 UNIT142**,
**46 528 / 62 740 octets (74,16 %)** ; **16 212 octets UNIT142**
restent a examiner. Gate A a verifier en CI ; pas de nouvelle Gate
B/C/D, ni modification des deux Lib ou de l'ASC de regression.


### UNIT142 — lots 101 a 125 : vingt-cinq plages source-verifiees (3 104 octets)

25 blocs MC68020 supplementaires sont maintenant explicites en ASM et
verrouilles par les octets de l'emetteur P2d, les offsets et une mutation
isolee de chaque module. Le wrapper conserve tous les octets non couverts.

- [bloc $020E6](M19_UNIT142_BLOCK_020E6_MC68020.s) : `$020E6..$02198`, 178 octets
- [bloc $08568](M19_UNIT142_BLOCK_08568_MC68020.s) : `$08568..$08612`, 170 octets
- [bloc $02690](M19_UNIT142_BLOCK_02690_MC68020.s) : `$02690..$02738`, 168 octets
- [bloc $099C6](M19_UNIT142_BLOCK_099C6_MC68020.s) : `$099C6..$09A66`, 160 octets
- [bloc $00C9E](M19_UNIT142_BLOCK_00C9E_MC68020.s) : `$00C9E..$00D38`, 154 octets
- [bloc $08CDA](M19_UNIT142_BLOCK_08CDA_MC68020.s) : `$08CDA..$08D72`, 152 octets
- [bloc $09F6A](M19_UNIT142_BLOCK_09F6A_MC68020.s) : `$09F6A..$0A000`, 150 octets
- [bloc $00764](M19_UNIT142_BLOCK_00764_MC68020.s) : `$00764..$007F6`, 146 octets
- [bloc $031E4](M19_UNIT142_BLOCK_031E4_MC68020.s) : `$031E4..$0326C`, 136 octets
- [bloc $09564](M19_UNIT142_BLOCK_09564_MC68020.s) : `$09564..$095E6`, 130 octets
- [bloc $01540](M19_UNIT142_BLOCK_01540_MC68020.s) : `$01540..$015BA`, 122 octets
- [bloc $0398C](M19_UNIT142_BLOCK_0398C_MC68020.s) : `$0398C..$03A06`, 122 octets
- [bloc $09A9E](M19_UNIT142_BLOCK_09A9E_MC68020.s) : `$09A9E..$09B10`, 114 octets
- [bloc $094BE](M19_UNIT142_BLOCK_094BE_MC68020.s) : `$094BE..$0952C`, 110 octets
- [bloc $02BBA](M19_UNIT142_BLOCK_02BBA_MC68020.s) : `$02BBA..$02C26`, 108 octets
- [bloc $02C2A](M19_UNIT142_BLOCK_02C2A_MC68020.s) : `$02C2A..$02C96`, 108 octets
- [bloc $07B56](M19_UNIT142_BLOCK_07B56_MC68020.s) : `$07B56..$07BC2`, 108 octets
- [bloc $0C8D8](M19_UNIT142_BLOCK_0C8D8_MC68020.s) : `$0C8D8..$0C940`, 104 octets
- [bloc $02D90](M19_UNIT142_BLOCK_02D90_MC68020.s) : `$02D90..$02DF6`, 102 octets
- [bloc $02DFA](M19_UNIT142_BLOCK_02DFA_MC68020.s) : `$02DFA..$02E60`, 102 octets
- [bloc $0317C](M19_UNIT142_BLOCK_0317C_MC68020.s) : `$0317C..$031E0`, 100 octets
- [bloc $09428](M19_UNIT142_BLOCK_09428_MC68020.s) : `$09428..$09486`, 94 octets
- [bloc $09930](M19_UNIT142_BLOCK_09930_MC68020.s) : `$09930..$0998E`, 94 octets
- [bloc $0781C](M19_UNIT142_BLOCK_0781C_MC68020.s) : `$0781C..$07874`, 88 octets
- [bloc $0C3C2](M19_UNIT142_BLOCK_0C3C2_MC68020.s) : `$0C3C2..$0C416`, 84 octets

**189 modules ASM**, dont **89 UNIT142** : **49 632 / 62 740 octets
(79,11 %)**. Il reste **13 108 octets UNIT142** (donnees/markers
non classes et autres petits blocs). La reconstruction P2d et les
mutations demeurent Gate A et doivent etre confirmees par CI.
Aucune nouvelle Gate B/C/D ni livraison de Lib/ASC.


### UNIT142 — lots 126 a 147 : vingt-deux petits blocs (702 octets)

Les 22 derniers segments de mnemoniques avec immediat editable sont
extraits avec controle exact des offsets et une mutation d'un octet
par module. Les 11 petits segments sans immediat et les blocs bruts
restent conserves dans le wrapper.

- [bloc $0CEF2](M19_UNIT142_BLOCK_0CEF2_MC68020.s) : `$0CEF2..$0CF38`, 70 octets
- [bloc $0C2C6](M19_UNIT142_BLOCK_0C2C6_MC68020.s) : `$0C2C6..$0C308`, 66 octets
- [bloc $0C344](M19_UNIT142_BLOCK_0C344_MC68020.s) : `$0C344..$0C386`, 66 octets
- [bloc $077DC](M19_UNIT142_BLOCK_077DC_MC68020.s) : `$077DC..$07816`, 58 octets
- [bloc $0C30E](M19_UNIT142_BLOCK_0C30E_MC68020.s) : `$0C30E..$0C340`, 50 octets
- [bloc $0C38C](M19_UNIT142_BLOCK_0C38C_MC68020.s) : `$0C38C..$0C3BE`, 50 octets
- [bloc $07878](M19_UNIT142_BLOCK_07878_MC68020.s) : `$07878..$0789E`, 38 octets
- [bloc $0949E](M19_UNIT142_BLOCK_0949E_MC68020.s) : `$0949E..$094B8`, 26 octets
- [bloc $099A6](M19_UNIT142_BLOCK_099A6_MC68020.s) : `$099A6..$099C0`, 26 octets
- [bloc $0A6FA](M19_UNIT142_BLOCK_0A6FA_MC68020.s) : `$0A6FA..$0A714`, 26 octets
- [bloc $07342](M19_UNIT142_BLOCK_07342_MC68020.s) : `$07342..$0735A`, 24 octets
- [bloc $0AB96](M19_UNIT142_BLOCK_0AB96_MC68020.s) : `$0AB96..$0ABAE`, 24 octets
- [bloc $0D7AA](M19_UNIT142_BLOCK_0D7AA_MC68020.s) : `$0D7AA..$0D7C2`, 24 octets
- [bloc $0C8BE](M19_UNIT142_BLOCK_0C8BE_MC68020.s) : `$0C8BE..$0C8D4`, 22 octets
- [bloc $0CED8](M19_UNIT142_BLOCK_0CED8_MC68020.s) : `$0CED8..$0CEEE`, 22 octets
- [bloc $09546](M19_UNIT142_BLOCK_09546_MC68020.s) : `$09546..$09558`, 18 octets
- [bloc $09A80](M19_UNIT142_BLOCK_09A80_MC68020.s) : `$09A80..$09A92`, 18 octets
- [bloc $0ABB4](M19_UNIT142_BLOCK_0ABB4_MC68020.s) : `$0ABB4..$0ABC6`, 18 octets
- [bloc $0746E](M19_UNIT142_BLOCK_0746E_MC68020.s) : `$0746E..$0747C`, 14 octets
- [bloc $09532](M19_UNIT142_BLOCK_09532_MC68020.s) : `$09532..$09540`, 14 octets
- [bloc $09A6C](M19_UNIT142_BLOCK_09A6C_MC68020.s) : `$09A6C..$09A7A`, 14 octets
- [bloc $0D986](M19_UNIT142_BLOCK_0D986_MC68020.s) : `$0D986..$0D994`, 14 octets

**211 modules ASM MC68020 au total**, dont **111 UNIT142**.
**50 334 / 62 740 octets UNIT142 (80,23 %)** ; il reste **12 406 octets**
(12 298 octets de directives brutes et 108 octets de mnemoniques
sans constante editable de ce type). Source-only, P2d/LAST_GOOD/ASC
proteges. Gate A en attente des CI de la revision.


### UNIT142 — lots 148 a 151 : quatre petits relais (68 octets)

Quatre courts blocs de mnemoniques sont restaures sans inventer
les zones brutes : appel graphics.library LVO et champs de structures.
Leurs deplacements sont parametres pour une mutation source isolee
d'un octet dans le banc Gate A.

- [bloc $00A62](M19_UNIT142_BLOCK_00A62_MC68020.s) : `$00A62..$00A7C`, 26 octets
- [bloc $0A6E2](M19_UNIT142_BLOCK_0A6E2_MC68020.s) : `$0A6E2..$0A6F4`, 18 octets
- [bloc $0948C](M19_UNIT142_BLOCK_0948C_MC68020.s) : `$0948C..$09498`, 12 octets
- [bloc $09994](M19_UNIT142_BLOCK_09994_MC68020.s) : `$09994..$099A0`, 12 octets

**215 modules ASM**, dont **115 UNIT142** : **50 402 / 62 740 octets
(80,33 %)** en ASM editables. **12 338 octets UNIT142** restent bruts
ou non classes (12 298 octets de directives et 40 octets de code sans
mutation simple). Pas de nouveau binaire, ASC ni qualification WinUAE.
Validation Gate A a confirmer.


### UNIT142 — lots 152 a 158 : sept epilogues et relais (40 octets)

**Gate A MC68020 PASS :** [CI source et edits 122 modules](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45045272699).

Les sept derniers segments en mnemoniques de l'audit sont maintenant
independants : quatre epilogues `tst.l`, deux `rts` et un branchement
`bra.w`. Les mutations d'edition utilisent `ifne/else/endif` vasm
pour les instructions sans immediat : baseline = opcodes d'origine,
edit = une seule difference d'octet, sans installer le code edite.

- [bloc $015C0](M19_UNIT142_BLOCK_015C0_MC68020.s) : `$015C0..$015C8`, 8 octets
- [bloc $01BCA](M19_UNIT142_BLOCK_01BCA_MC68020.s) : `$01BCA..$01BD2`, 8 octets
- [bloc $03A0C](M19_UNIT142_BLOCK_03A0C_MC68020.s) : `$03A0C..$03A14`, 8 octets
- [bloc $04102](M19_UNIT142_BLOCK_04102_MC68020.s) : `$04102..$0410A`, 8 octets
- [bloc $002A2](M19_UNIT142_BLOCK_002A2_MC68020.s) : `$002A2..$002A4`, 2 octets
- [bloc $002B2](M19_UNIT142_BLOCK_002B2_MC68020.s) : `$002B2..$002B4`, 2 octets
- [bloc $02360](M19_UNIT142_BLOCK_02360_MC68020.s) : `$02360..$02364`, 4 octets

**222 modules ASM MC68020**, dont **122 UNIT142**. Les **14 628
 octets de mnemoniques audites** restants au checkpoint des lots 73
sont convertis, soit **50 442 / 62 740 octets UNIT142 (80,40 %)**
en source editable. Les **12 298 octets de directives brutes**
restent strictement conserves : donnees, marqueurs GetP, pseudo-appels
AMOS Main et zones sans classification certaine. La CI Gate A confirme la reconstruction P2d octet-identique,
l'assemblage direct vasm MC68020 et les 122 modifications isolees.
Aucune nouvelle Gate WinUAE B, Compiler C ni materiel D.

### UNIT142 — lots 159 a 161 : 3 noyaux CBlock en ASM (2 616 octets)

Les trois copies du noyau historique `M18 CBlock` sont desormais
du vrai source Motorola MC68020. Source de provenance :
`tools/m18_cblock_copy_emit.py::emit_cblock_copy_core()`,
SHA256 noyau `8a3df13b72b0a62f237b7df068cc9d3f47c70af759d0bc64949ed765cfd65a97`.

| Position du code UNIT142 | Module | Octets |
| --- | --- | ---: |
| `$0ABCE..$0AF36` | [CBlock noyau A](M19_UNIT142_CBLOCK_CORE_0ABCE_MC68020.s) | 872 |
| `$0B592..$0B8FA` | [CBlock noyau B](M19_UNIT142_CBLOCK_CORE_0B592_MC68020.s) | 872 |
| `$0BF5A..$0C2C2` | [CBlock noyau C](M19_UNIT142_CBLOCK_CORE_0BF5A_MC68020.s) | 872 |

Chaque copie conserve un namespace de labels distinct. Les 8 octets
`AGACBLK ` et les 4 octets `GetP` par enveloppe restent du `dc.b`
(explicitement hors code). Une mutation `moveq` unique par copie
s'ajoute aux 122 edits UNIT142 existants.

**Total : 225 modules ASM MC68020**, dont **125 UNIT142** ;
**53 058 / 62 740 octets UNIT142 (84,57 %)** editables.
**9 682 octets UNIT142** restent sous directives brutes.
Gate A [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45047314451) ; aucune nouvelle Gate B/C/D,
aucune modification de P2d, LAST_GOOD ou de l'ASC actif.

### UNIT142 — lot 162 : code P0e de table d'objets (788 octets)

L'emetteur historique `m19_p0e_object_table_emit.py::emit_object_table()`
est **exactement present dans UNIT142** a `$0DD04..$0E620`,
selon la [Gate A de provenance](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45048150577).
Ses **788 octets executables `$0DD04..$0E018`** sont convertis en
[module MC68020](M19_UNIT142_P0E_OBJECT_CORE_MC68020.s).
Les quatre routines Put/Off/Read/Reset ont un assemblage direct vasm
MC68020 byte-identique et un resultat mutable isole.

Les 8 octets d'etat proprietaire et les 64 emplacements de 24 octets
(**1 544 octets au total**) sont des donnees initialisees a zero,
conservees comme `dcb.b 8,0` et `dcb.b 1536,0` dans le wrapper.
La signature `AGAPIC  ` (8 octets) reste une directive `dc.b`.

**Total : 226 modules ASM MC68020**, dont **126 UNIT142** ;
**53 846 / 62 740 octets UNIT142 (85,82 %)** en source.
**8 894 octets UNIT142** restent bruts ou non classes.
La [Gate A du lot 162](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45048818538)
a valide la 126e mutation source isolee, la reconstruction P2d et
l'assemblage direct MC68020. Pas de nouveau binaire ni d'ASC,
pas de nouvelles Gates B/C/D.

### UNIT142 — lot 163 : pont AGA P0e natif (470 octets)

L'emetteur `m19_p0e_split_bridge_emit.py::AGA_CORE` est
**identique octet pour octet** au groupe UNIT142 `$0E620..$0E7F6`.
Le [module ASM du pont AGA](M19_UNIT142_P0E_AGA_BRIDGE_MC68020.s)
reprend les quatre entrees Put/Off/Read/Reset en 470 octets de
mnemoniques, sans directive brute. [Preuve vasm 470/470](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45048898071).
Une mutation source isolee supplementaire est integree au Gate A.
**Gate A lot 163 en attente**. Projection : **227 modules ASM**,
dont **127 UNIT142**, **54 316 / 62 740 (86,57 %)** ; **8 424 octets
bruts**. Aucune promotion ni ASC modifie, Gates B/C/D non revendiquees.

### UNIT142 — lots 164 a 167 : P0f stamp et binder (1 184 octets)

Quatre modules Motorola extraient les **1 184 octets de code MC68020**
du noyau source `m19_p0f_object_identity_emit.py`, en conservant
**14 octets de pseudo-operations / branches non decodees** sous `dc.b`
dans le wrapper. Chaque plage possede une constante mutable et un
controle de modification isolee. La table des 64 empreintes (1 024
 octets) reste en `dcb.b 1024,0`, sans etre comptee comme instruction.

- [Module P0f 1](M19_UNIT142_P0F_STAMP_HEAD_MC68020.s) : 226 octets
- [Module P0f 2](M19_UNIT142_P0F_STAMP_BODY_MC68020.s) : 582 octets
- [Module P0f 3](M19_UNIT142_P0F_BIND_CHECK_MC68020.s) : 198 octets
- [Module P0f 4](M19_UNIT142_P0F_BIND_RETURN_MC68020.s) : 178 octets

[Preuve d'emetteur et vasm exact 1 198 octets](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45048989705).
La Gate A d'integration doit encore confirmer la P2d complete et les
quatre edits. **231 modules ASM**, dont **131 UNIT142** :
**55 500 / 62 740 octets (88,46 %)** en code source,
**7 240 octets en donnees ou octets non classifies**.
Aucun changement de Lib, ASC ni qualification Gates B/C/D.

### UNIT142 — lots 168 a 169 : P0f BSR.W restaurés (8 octets)

Les deux branches auparavant conservees en donnees opaques sont des
**BSR.W Motorola** dont les adresses cibles correspondent exactement
aux entrees Put (`$0DD04`) et Read (`$0DEAC`) du module P0e
restaure. La source P0f historique impose les deplacements respectifs
`F1DE` et `F2BC`. Les modules [BSR Put](M19_UNIT142_P0F_BSR_PUT_MC68020.s) et
[BSR Read](M19_UNIT142_P0F_BSR_READ_MC68020.s) recuperent ces 8 octets de code avec deux mutations
isolees (+2 sur la destination), sans toucher a la Lib.

Seul le pseudo-appel AMOS Main `FE11 F700 031D` (6 octets) reste brut.
**Gate A [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45051866506) : 233 modules ASM**, dont **133 UNIT142**,
**55 508 / 62 740 octets (88,47 %)** et **7 232 octets bruts**.
Les 133 edits isoles et la reconstruction P2d SHA256 ont ete valides.

### UNIT142 — lots 170 a 171 : Screen Open P1c/P1d (88 octets)

Deux routines Motorola MC68020 d'ouverture proviennent des emetteurs
M19 P1c et P1d, avec octets de reference verrouilles :

- [P1c Priority Open](M19_UNIT142_P1C_PRIORITY_OPEN_MC68020.s) :
  `$0F0A4..$0F0CA`, 38 octets executables ; contexte de 8 octets
  conserve en `dcb.b` immediatement apres la routine.
- [P1d Limit Open](M19_UNIT142_P1D_LIMIT_OPEN_MC68020.s) :
  `$0F4E2..$0F514`, 50 octets executables ; table de 65 x 16 octets
  conservee en `dcb.b` et initialisee comme dans le constructeur P1d.

Les appels PC-relatifs utilisent l'extension longue MC68020 de 8 octets,
non une instruction 68000 ni des octets de donnees arbitraires.
Deux edits `cmpi.l` confines (1 -> 2) sont valides par Gate A.

**Gate A [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45053448900) : 235 modules ASM**, dont 135 UNIT142,
**55 596 / 62 740 octets (88,61 %)**, **7 144 octets bruts**.
Assemblage vasm P2d byte-exact, **135 mutations isolees**.
[Inventaire PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45054203673) :
4 146 octets de donnees/marqueurs source-prouves, 2 998 non classes.
Pas de qualification WinUAE B, Compiler C ou materiel D supplementaire.

### UNIT142 — lots 172 a 173 : Screen Open historique R83 (716 octets)

Le constructeur historique R83, independamment SHA-pinne, reproduit
octet pour octet la routine AGA `$00470..$00764` (756 octets).
L'appel P1c vers `$00470` est prouve et la previsualisation de cette
routine a passe vasm en source directe.

Deux modules Motorola MC68020 recuperent **716 octets executables** :
- [Screen Open principal](M19_UNIT142_LEGACY_OPEN_HEAD_MC68020.s),
  `$00470..$005D4` : 356 octets, NOP compris ;
- [Screen Open auxiliaires](M19_UNIT142_LEGACY_OPEN_HELPERS_MC68020.s),
  `$005F8..$00760` : 360 octets.

Les 36 octets des noms `intuition.library` / `graphics.library`
et le delimitateur AMOS `GetP` (4 octets) ne sont pas des instructions
et restent dans le wrapper. Deux edits `moveq` independants sont prevus.

**Projection a valider en Gate A : 237 modules ASM**, dont 137 UNIT142 ;
**56 312 / 62 740 octets (89,76 %)** de code UNIT142, **6 428 octets
bruts**. La classification source devrait isoler **4 186 octets
non executables et 2 242 octets encore indetermines**.
Aucune nouvelle Gate B/C/D ; les Lib P2d, LAST_GOOD et l'ASC restent intacts.

## Compilation directe (Windows)

```bat
BUILD_P2D_ASM_DIRECT.bat
```

Point d'entree vasm : `M19_P2D_LINKED_EDITABLE.s`. Sortie de developpement : `src/generated/p2d_editable/M19_P2D_DIRECT_ASM_UNTESTED.Lib`. Cette commande ne regenere aucun source Python et ne verifie pas le contrat AP20 avant d'ecrire le resultat. La CI confirme l'identite avec la bibliotheque P2d intacte.

## Compilation gardee et tests de modification

```bat
BUILD_P2D_ASM.bat
BUILD_P2D_ASM.bat --self-test-batch
BUILD_P2D_ASM.bat --self-test-edit
```

Le script `tools/build_m19_p2d_editable_asm.py` refuse toute derive de taille, de tokens AP20, de titre, des autres unites ou d'une zone non migree. Sans edition, la reconstruction doit produire exactement **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Le self-test altere temporairement **une instruction dans chacun des 45 modules historiques, puis deux edits dans un assemblage groupe** (P0i, B7, B8 et P2a/P2b/P2c/P2d), recompilant en memoire et exigeant un changement sur un seul octet dans le groupe BOBS.

Pour un edit a longueur constante, `BUILD_P2D_ASM.bat --allow-edited` cree uniquement `src/generated/p2d_editable/M19_P2D_EDITED_UNTESTED.Lib`. **Ne pas installer une version modifiee sans validation specifique.** Les bibliotheques de `dist/`, `LAST_GOOD`, les tests et exemples ne sont pas modifies par cette migration. Les Gates WinUAE Runtime B, vrai AMOS Compiler C et physique D **ne qualifient pas les futures editions natives** par la seule CI.

## Acceleration du controle d'edition groupe en CI

La Gate A d'un push conserve les deux preuves precedentes :
reconstruction de P2d par les emetteurs source (taille/SHA/AP20 exacts), puis
assemblage direct MC68020 du code natif. Le controle groupe **reutilise
uniquement les fichiers ASM deja prepares par cette reconstruction** ;
il ne relance pas les emetteurs Python historiques une deuxieme fois.

La commande de la CI est :

```sh
python -B tools/build_m19_p2d_editable_asm.py --vasm "$RUNNER_TEMP/vasm/vasmm68k_mot" --self-test-batch --batch-staged "$RUNNER_TEMP/p2d_asm_baseline"
```

Ce mode refuse les sources ASM perimees, exige le binaire P2d officiel
et la LAST_GOOD octet-identiques, controle la sortie P2d preparee, puis
**reassemble reellement avec vasm** une baseline exacte et une variante
editant **chaque module du lot**. Il verifie les octets modifies dans
l'unique unite BOBS, tous les autres octets, la longueur, les tokens,
le titre, la topologie AP20 et la validite structurelle. Les deux
assemblages temporaires sont detruits apres le test. Aucun binaire de
`dist/` ni test de campagne n'est modifie.

Sans `--batch-staged`, le test autonome `--self-test-batch` garde son
chemin complet historique. Le dimanche ou lors d'un lancement manuel
`full_edit_tests=true`, le test exhaustif garde toutes ses modifications
individuelles et inclut deja le test groupe ; la CI n'execute donc pas
le controle rapide en doublon. Cette optimisation ne change aucune preuve
WinUAE B, Compiler C ou materiel D.

## Pseudo-instructions AMOS Main

Les 28 appels directs AMOS Main du groupe BOBS sont maintenant symboliques : `Bnk.GetAdr`, `Bnk.Change`, `Lst.Cree`, `Lst.Del`. `DC.W $FE11,$F700,INDEX` conserve la pseudo-instruction AMOS (non Motorola), avec index source verifie dans `amos_main_abi.rjsr`. La CI impose le nombre et les octets originaux de chaque appel.

Le bloc B8 source definit 4 octets ASCII `B8RG` et 8 octets `b8_b7_hook_root` comme donnees, non comme opcodes MC68020. L'ancien epilogue `End` est redirige vers le nettoyage P2b, exactement comme dans la bibliotheque P2d.
