# M19 P2.0 — gestionnaire d'objets BASIC, ecran AGA prive

**Unique ASC actif :** [M19_P2_OBJECTS_01.asc](M19_P2_OBJECTS_01.asc). L'ancien P1 **Runtime WinUAE PASS** est archive **sans modification** dans [tests/passed/M19_P1_AGAPIC_BOBS_01.asc](../passed/M19_P1_AGAPIC_BOBS_01.asc), et le [rapport P1](../../docs/M19_P1_WINUAE_RUNTIME_2026-11-15.md) demeure valable.

**Binaire de reference :** R84 v0.13.29 **LAST_GOOD inchange** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucune nouvelle commande native ni dependance `c2p.library`. CPU 68020 minimum.

**État : Gate B P2.0 AMOS Runtime/WinUAE 68030 PASS** après correction des labels (`_SORT_OBJECTS`, etc.). Journal reçu : `RESULT 1`, `ERR 0`, 240 frames, 6 AGAPIC + 4 FICON8, créations 5, suppression 1, rejets invalides, zéro échec Draw/Swap, mémoire Chip/Fast stable et fermeture 1. [Rapport de validation](../../docs/M19_P2_WINUAE_RUNTIME_2026-11-15.md). **Gate C Compiler M19 et Gate D Amiga physique non testées** ; `PRG_STATE 0` non testé.

## Premier essai sous AMOS / WinUAE

1. Verifier que les **banques 11 a 23 sont libres** avant execution. Charger R84 et importer [l'ASC P2.0](M19_P2_OBJECTS_01.asc) avec **Project -> Merge ASCII** dans un projet AMOS vide. Executer d'abord sous AMOS Runtime/WinUAE (AGA, 68020+). La premiere instruction `Set Buffer 20` ajuste l'espace des variables pour ce grand prototype.
2. Ecran AGA prive **320x256, 256 couleurs / 8 plans**, double buffering. Le programme cree six images AGAPIC **24x24** v1/v2 et quatre images FICON8 **16x16**. Aucun asset externe n'est requis.
3. La scene commence avec **quatre objets** : deux AGAPIC controles par **AMAL manuel** (mouvements horizontal et vertical), un FICON8 anime depuis BASIC, et un AGAPIC opaque. Le gestionnaire trie les visibles par **Z, puis ID** pour stabiliser les egalites.
4. Pendant les **240 frames logiques** : quatre placements partiellement hors ecran (gauche, droite, haut, bas), un placement entierement hors ecran (culling), changement d'images a rythme lent, masquage puis reapparition, changement de Z, suppression de l'**ID 4** a la frame 121 et creation de l'**ID 5** a la frame 122. L'ancien ID 4 est refuse ; une frame 3 invalide et une source banque 23 absente sont egalement refusees.
5. Laisser le programme terminer. Echap interrompt volontairement et peut donner `ERR 47` si moins de 180 frames. Observer **l'absence de trainees, de freeze et de scintillement rapide** ; apres fermeture l'affichage doit revenir a AMOS.

## Résultat du journal transmis

Toutes les conditions du tableau ci-dessous sont satisfaites : `RESULT 1`, `VERDICT PASS`, `ERR 0`, `FRAME_OK 240`, `CAP_OK 6`, `ICON_OK 4`, `PROBE_OK 1`, `PIXEL_DIFF 1`, `CREATE_COUNT 5`, `DELETE_COUNT 1`, `CLIP_OK 4`, `CULLED 2`, `DRAW_FAIL 0`, `SWAP_FAIL 0`, `CHIP_DELTA 0`, `FAST_DELTA 0` et `CLOSE_RETURNED 1`. 

## Journal RAM et criteres P2.0

**Fichier attendu :** `RAM:M19_P2_OBJECTS_RUNTIME.TXT` (ou suffixe `_INTERPRETED` / `_COMPILED` suivant `Prg State`). Transmettre le **journal complet** et, si possible, une capture WinUAE.

| Domaine | Condition attendue |
|---|---|
| Statut | `RESULT 1`, `VERDICT PASS`, `ERR 0`, `RUN_MODE RUNTIME` |
| Sources | `CAP_OK 6`, `ICON_OK 4`, `PROBE_OK 1`, `PIXEL_DIFF 1` |
| Creation / vie | `CREATE_COUNT 5`, `NEXT_ID 5`, `DELETE_COUNT 1`, `STALE_ID_REJECT 1` |
| Rejets propres | `BAD_FRAME_REJECT 1`, `BAD_BANK_REJECT 1` |
| Visibilite / ordre | `HIDE_OK 1`, `SHOW_OK 1`, `Z_CHANGE 2`, `STABLE_TIE 1` |
| Clipping / culling | `CLIP_OK 4`, `CULLED >= 2`, `FOUR_VISIBLE_FRAMES >= 120` |
| Animation | `FRAME_OK >= 180`, deplacements X/Y non nuls, changements d'image AMAL/BASIC |
| Stabilite | `DRAW_FAIL 0`, `SWAP_FAIL 0`, `CLOSE_RETURNED 1`, `RAM:` cree |

**Securite :** `Synchro Off` puis `Synchro` dans BASIC, aucun dessin en interruption, fond entier reconstruit sur back buffer `Safe` avant tous les objets, `Aga Swap` explicite. Arret AMAL **avant** liberation de la banque 11. Les banques d'images sont possedees par **le test**, non par les objets : supprimer un objet n'efface pas une banque partagee.

**Mesures memoire :** `CHIP_DELTA` et `FAST_DELTA` sont calcules apres `Dim` et `Set Buffer` mais **avant** les banques. Cela suit les ressources graphiques creees/liberees pendant le test ; ce n'est pas une mesure complete de la consommation du gestionnaire BASIC. Ne pas exiger 0 dans tous les modes sans qualification.

**Limites :** ce test ne qualifie pas la suppression d'un objet lie a AMAL (refusee par le prototype), ni les sprites materiels P3, ni les autres profondeurs. La comparaison de priorite se fait sur un **pixel temoin**, sans preuve pixel par pixel du cadre entier.

[Contrat P2](../../docs/M19_P2_OBJECT_MANAGER_CONTRACT.md) · [Plan M19](../../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Roadmap](../../docs/ROADMAP.md) · [Regles source](../../EXTENSION_SOURCE_RULES.md).
