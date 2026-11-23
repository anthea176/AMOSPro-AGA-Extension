# S1-P1e — Get AGA Sprite : première commande publique de capture AGSP

**Date :** 23 novembre 2026. **Statut : source MC68020 et candidate AP20 uniquement en mémoire, aucun fichier Lib distribué.**

## Syntaxe candidate

Après `Aga Screen Open` et chargement d'une planche IFF indexée 256 couleurs / palette RGB24 dans le buffer AGA approprié, sélectionner la banque avec `Aga Sprite Bank N` puis appeler :

`Get AGA Sprite I,X1,Y1,X2,Y2,TransparentPen`

Les bornes X2/Y2 sont **inclusives**. Cette première tranche S1-P1e ne capture que **16 pixels de largeur** (`X2-X1+1=16`) et **1..256 lignes** ; les autres largeurs sont refusées. L'image est remappée sans quantification en **2 bitplanes, 0 transparent et 1..3 couleurs opaques RGB24**. La banque DATA `AGSP` peut contenir plusieurs IDs et être sauvegardée avec AMOS `Save` ; une capture ultérieure remplace l'ID sans écraser les autres images. **Aucune commande Sprite DMA n'est encore activée.**

## Source, sélection et allocation

[Source publique MC68020](../src/native/m19_s1/M19_S1P1E_GET_PUBLIC_MC68020.s) incluse dans [l'unité de sélection `Aga Sprite Bank`](../src/native/m19_s1/M19_S1P1D_BANK_PUBLIC_MC68020.s), avec les mêmes constantes et état de sélection `agsp_s1_selection_state` (propriétaire AMOS Main `A5` + numéro). Le runtime d'exécution de cette capture est **AGSP_P1C_PIPELINE_ENTRY**, construit depuis les quatre composants natifs de capture, repack, validation et publication.

**Signature AP20 candidate :** `get aga sprite`, `00,0,0,0,0,0` ; D3 reçoit TransparentPen, les cinq LONGS à A3 sont lus dans l'ordre Y2, X2, Y1, X1, I. Les cinq paramètres sur A3 sont consommés sur tous les chemins, y compris le refus ; D3 retourne 1/0 et D2=0.

La commande refuse si l'écran AGA n'est pas en état Safe, si une banque DATA étrangère occupe le numéro sélectionné, si l'ancien AGSP est corrompu ou si le rectangle/les couleurs dépassent S1. **Avant d'écrire dans la liste des banques AMOS**, l'ancien payload AGSP est contrôlé intégralement. La routine alloue avec Exec.AllocVec **5104 octets temporaires** (requête, RGB32, RGB24, capture, bitplanes, palette, repack et commit), puis un payload AGSP de staging de capacité `ancien+96+4*H`, plafonné à 16 Mio. Ces deux allocations sont libérées par FreeVec sur tous les chemins de retour, même lorsque la publication a réussi. L'écriture atomique du nouveau nœud DATA appartient au publisher P1c ; **aucun canal hardware ni Chip RAM DMA n'est alloué ici**.

La publication P1c a été alignée sur la sélection P1d : une banque DATA réellement rechargée sous AMOS peut avoir ses drapeaux normalisés à **zéro**, tout en gardant `AGASPRT `/payload AGSP valides. Les deux chemins acceptent ce cas et refusent les autres types de banques.

## Candidate AP20 et tests

Le [builder strictement en mémoire](../tools/build_m19_s1p1e_get_sprite_ap20.py) repart du P2d **SHA256 `ce5fb614...`**, 100 commandes, 203 entrées, puis ajoute deux GETP et deux stubs RBSR pour **`Aga Sprite Bank`** et **`Get AGA Sprite`**. Candidate : 102 commandes, 208 entrées AP20, code MC68020 VASM assemblé dans un unique groupe. Tous les anciens tokens et toutes les anciennes entrées P2d restent octet pour octet identiques.

[Banc CPU réel MC68020 avec services AMOS simulés](../tools/test_m19_s1p1e_get_sprite_cpu.py) : sélection initiale, capture, remplacement multi-images, palette RGB24 et bitplanes comparés à l'oracle, tests de refus, double buffer, allocations et libération sur erreur, banque AGSP déjà chargée avec flags normalisés. [Tests AP20/HUNK](../tools/test_m19_s1p1e_get_sprite_ap20.py). [CI dédiée](../.github/workflows/m19-s1-p1c-amos-bank-commit.yml).

**Une candidate de test non validée est produite uniquement sous `RUNNER_TEMP` en CI, avec `actions/upload-artifact` (7 jours), jamais dans le dépôt ni dans `dist/`.** [Récupérer la candidate, l'IFF et le banc Runtime](../tests/proto/agsp_capture/README.md). Elle n'est ni une release ni une validation WinUAE.  La Gate A CPU après validation CI sera limitée aux services AMOS/graphics/Exec simulés. **Gate B Runtime de cette nouvelle commande : pas encore testée.** Le PASS Runtime B de la sonde `Load/Save` AGSP reste acquis sur son propre fichier, pas transposable à `Get AGA Sprite`. **Gate C de la sonde DATA volontairement sautée selon la demande de l'auteur** ; Gate D Amiga physique non testée. Ne pas copier les prototypes dans `examples/`.

## Suite

Avant essai Runtime du nouveau token, bâtir une **candidate Lib explicitement distincte de P2d**, avec audit HUNK/GETP et installation sur environnement de test sous responsabilité de l'auteur. Vérifier visuellement que l'IFF est sur le bon buffer inactif Safe, et tester les refus de couleurs / mémoire, puis le Save/Load de la banque créée par capture. Aucune promotion LAST_GOOD ni animation Sprite DMA sans qualification du Copper.
