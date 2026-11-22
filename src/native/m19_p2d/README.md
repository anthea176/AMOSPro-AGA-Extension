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
