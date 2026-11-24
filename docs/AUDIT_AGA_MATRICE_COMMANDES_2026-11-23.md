# Audit AGA — matrice commande / mémoire / page / sécurité (102/102)

**Date : 23 novembre 2026 · Branche `main` · HEAD audité : `45516f8772a24b5d7ad887d2a0f2b7cee5203e98` · État : audit NON CLOS, Sprite GELÉ.**

Référence des **102 commandes publiques** : [README.md figé au HEAD](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/45516f8772a24b5d7ad887d2a0f2b7cee5203e98/README.md). Ordre ci-dessous identique au tableau d'API du README. Les appels à des fonctions AMOS natives non préfixées `Aga` ne sont **pas** des entrées de ces 102 tokens.

**Légende :** `VM` = validation manquante, aucun verdict ; `A001 P0 statique` = lacune Safe IFF observée dans la source, effet WinUAE non reproduit ; `A010 P0 statique` = Back Fill legacy sans garde Safe avant **SetRast(-234)** ; `A003 VM contrat Clear` = absence d'invalidation automatique conforme à la séquence P2d Clear→décor→Swap, régression légale restant à vérifier ; `Axxx P1 risque/interaction` = séquence potentiellement problématique, **non** preuve que la commande isolée est incorrecte ; `GEL` = aucune action Sprite. Les descriptions de garde disent **ce qu'il faut auditer**, pas ce qui a été prouvé pour chaque token.

| # | Commande | Famille | Mémoire utilisée | Page(s) | Garde / dépendances à vérifier | Statut |
|---:|---|---|---|---|---|---|
| 1 | `Aga Detect` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | VM |
| 2 | `Aga Screen Open` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | VM |
| 3 | `Aga Screen Close` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | A004 VM ; vrai Close lie |
| 4 | `Aga Double Buffer` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | A002 P1 a qualifier |
| 5 | `Aga Swap` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | A002 P1 structure conditionnelle |
| 6 | `Aga Pic Info` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | VM |
| 7 | `Aga Iff Load` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | A001 P0 statique ; palette RGB32 globale |
| 8 | `Aga Palette Load` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 9 | `Aga Palette Set` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | ColorMap seulement, B8 non invalidé ; T09 VM |
| 10 | `Aga Palette Get` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 11 | `Aga Palette Save` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 12 | `Aga Bank Palette Init` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 13 | `Aga Bank Palette Capture` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 14 | `Aga Bank Palette Apply` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 15 | `Aga Bank Palette Fade` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 16 | `Aga Fade To Black` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 17 | `Aga Fade To White` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 18 | `Aga Palette Cycle` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | ColorMap seulement, B8 non invalidé ; T09 VM |
| 19 | `Aga Key` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 20 | `Aga Wait Key` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 21 | `Aga Wait Vbl` | Ecran / synchronisation | Screen Intuition, DBState, ScreenBuffers | Avant+arriere (controle) | Safe/Disp, GetMsg, READY/DIRTY, Close ; T01,T02,T08,T14 | VM |
| 22 | `Aga Blit Copy` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 23 | `Aga Blit Fill` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 24 | `Aga Blit Clear` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 25 | `Aga Copper Clear` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | VM |
| 26 | `Aga Copper Wait` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | VM |
| 27 | `Aga Copper Move` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | VM |
| 28 | `Aga Copper End` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | VM |
| 29 | `Aga Copper On` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | actif fail-safe R18 ; B/C VM |
| 30 | `Aga Copper Off` | Copper | UserCopperList / OS display | Affichage (pas copie de plan) | On/Off, Close, fenetre et OS Copper ; T14,T16 | rollback owner visible ; B/C VM |
| 31 | `Aga Mouse X` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 32 | `Aga Mouse Y` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 33 | `Aga Mouse Buttons` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 34 | `Aga Mouse Pressed` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 35 | `Aga Mouse Released` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 36 | `Aga Hotspot Hit` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 37 | `Aga Rect Overlap` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 38 | `Aga Text` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 39 | `Aga Font Select` | Polices | Font systeme / bank font AMCAF / Chip | Aucune (selection), puis Text | Propriete, chargement, remplacement, Close ; T09,T14 | commit font sur succes ; Close VM |
| 40 | `Aga Bank Font Select` | Polices | Font systeme / bank font AMCAF / Chip | Aucune (selection), puis Text | Propriete, chargement, remplacement, Close ; T09,T14 | VM |
| 41 | `Aga Plot` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 42 | `Aga Draw` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 43 | `Aga Box` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 44 | `Aga Circle` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | A003 VM contrat Clear |
| 45 | `Aga Mouse Cursor` | Entrees / fenetre | IDCMP, input.device, fenetre et souris | Aucune (sauf curseur OS) | Ressource ouverte, End/Close ; T14 | VM |
| 46 | `Aga Bank Image Draw` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | wrapper Image Draw/GetMsg ; A003 VM |
| 47 | `Aga Image Region` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | GetMsg natif ; A003 VM |
| 48 | `Aga F Icon` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | A003 VM contrat Clear |
| 49 | `Aga F Blit` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | A003 VM Clear ; cache Stage T11 VM |
| 50 | `Aga F Icon Bank Create` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | VM |
| 51 | `Aga F Icon Bank Put` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | restaging FICHIP requis ; T11 VM |
| 52 | `Aga F Chip Bank Create` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | VM |
| 53 | `Aga F Chip Stage` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | ready 0/1 et Chip reel ; T11 VM |
| 54 | `Aga F Icon Capture` | FICON / FICHIP | DATA FICON8/FICHIP8, Chip cache, bitplanes | Arriere pour dessin/capture | Type/len banque, resid. Chip, Safe, WaitBlit ; T06,T10,T11 | capture GetMsg ; restaging FICHIP T11 VM |
| 55 | `Aga C Block Capture` | CBlock | DATA AGACBLK en Chip, Bitmap pages | Arriere lecture/ecriture | Safe, WaitBlit, dimensions, dernier XY ; T06,T10,T13 | GetMsg+WaitBlit local ; B8 VM |
| 56 | `Aga C Block Draw` | CBlock | DATA AGACBLK en Chip, Bitmap pages | Arriere lecture/ecriture | Safe, WaitBlit, dimensions, dernier XY ; T06,T10,T13 | GetMsg+WaitBlit local ; A003 VM |
| 57 | `Aga C Block Restore` | CBlock | DATA AGACBLK en Chip, Bitmap pages | Arriere lecture/ecriture | Safe, WaitBlit, dimensions, dernier XY ; T06,T10,T13 | GetMsg+WaitBlit local ; A003 VM |
| 58 | `Aga Bank Image Info` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | VM |
| 59 | `Aga Bank Image Capture` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | VM |
| 60 | `Aga Bob Batch` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | A003 VM contrat Clear |
| 61 | `Aga Cache Blit` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | Verifier SafePort + WaitBlit + clips + B8 ; T03,T05,T06,T09 | GetMsg et MEMF_CHIP natifs ; A003 VM |
| 62 | `Aga Sprite Bank` | Sprite S1 geles | DATA AGSP, RGB24, lecture de plans, allocations | Arriere lecture (Get) | GEL; Gate A seule, WaitBlit/Safe a revisiter ; T15 (suspendu) | GEL |
| 63 | `Get AGA Sprite` | Sprite S1 geles | DATA AGSP, RGB24, lecture de plans, allocations | Arriere lecture (Get) | GEL; Gate A seule, WaitBlit/Safe a revisiter ; T15 (suspendu) | GEL |
| 64 | `Aga Bob Bank` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 65 | `Aga Bob Bank Free` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | garde CLEAN/owner ; rechargement T10 VM |
| 66 | `Get AGA Bob` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 67 | `Make AGA Bob Mask` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 68 | `No AGA Bob Mask` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 69 | `Aga Bob Blit` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | A003 VM contrat Clear |
| 70 | `Aga Bob` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 71 | `Aga Bob Off` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 72 | `Aga Bob Draw` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | A003 P1 risque |
| 73 | `Aga Bob Clear` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | A002/A003 P1 risque |
| 74 | `Aga Bob Update` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | A002/A003 P1 risque |
| 75 | `Aga Bob Priority` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 76 | `Aga Limit Bob` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 77 | `Aga Del Bob` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 78 | `Aga Ins Bob` | AGBO / edition banques | DATA AGBO, masques, caches Chip, registre Bob | Arriere pour capture/blit | Epoch, validite, Safe, liste 64, READY/DIRTY ; T07,T10,T11 | VM |
| 79 | `Aga Bob Col` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 80 | `Aga Bob Flip` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 81 | `Aga Bob Planes` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 82 | `Aga Bob Auto Update` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | A002 P1 structure conditionnelle |
| 83 | `Aga X Bob` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 84 | `Aga Y Bob` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 85 | `Aga I Bob` | Bobs persistants B8/P2 | Registre 64 Bobs, snapshots CPU des 2 pages | Arriere / physique par Bitmap | Safe, CLEAN/READY/DIRTY, Clear/Update, epoch ; T02,T03,T05,T07,T08 | VM |
| 86 | `Aga Iff To Chunky` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | VM |
| 87 | `Aga C2P Open` | C2P | DATA chunky + Bitmap temporaire Chip, c2p.library | Arriere pour Convert | Safe, WaitBlit, banques/bitmap, Close ; T06,T10,T14 | VM |
| 88 | `Aga C2P Blit` | C2P | DATA chunky + Bitmap temporaire Chip, c2p.library | Chunky CPU uniquement | Safe, WaitBlit, banques/bitmap, Close ; T06,T10,T14 | Chunky CPU, Convert protege DB ; T06 VM |
| 89 | `Aga C2P Zoom` | C2P | DATA chunky + Bitmap temporaire Chip, c2p.library | Chunky CPU uniquement | Safe, WaitBlit, banques/bitmap, Close ; T06,T10,T14 | Chunky CPU, Convert protege DB ; T06 VM |
| 90 | `Aga C2P Convert` | C2P | DATA chunky + Bitmap temporaire Chip, c2p.library | Arriere pour Convert | Safe, WaitBlit, banques/bitmap, Close ; T06,T10,T14 | GetMsg+WaitBlit local ; A003 VM |
| 91 | `Aga C2P Close` | C2P | DATA chunky + Bitmap temporaire Chip, c2p.library | Arriere pour Convert | Safe, WaitBlit, banques/bitmap, Close ; T06,T10,T14 | WaitBlit avant Free ; End VM |
| 92 | `Aga Probe` | Legacy | Etat diagnostic, ecran selon chemin | A determiner | API historique a tracer ; T14 | VM |
| 93 | `Aga Demo` | Legacy | Etat diagnostic, ecran selon chemin | Screen Intuition independant | OpenScreen/CloseScreen, WaitTOF borne ; T14 | demo autonome ; interaction VM |
| 94 | `Aga Screen Pattern` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Screen.RastPort (page physique DB inconnue) | Pas de GetMsg ; SetAPen/RectFill et LoadRGB32 ; T06 | AGA-011 P1 a qualifier |
| 95 | `Aga Back Fill` | Blit / dessin / texte | Bitmap planar Chip, RastPort, cache AGPC | Arriere (ecriture) | SetRast entier ; aucun Safe avant appel ; WaitBlit + B8 ; T03,T05,T06,T09,T19 | A010 P0 statique ; A003 VM contrat Clear |
| 96 | `Aga Palette Bank Init` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 97 | `Aga Palette Bank Capture` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 98 | `Aga Palette Bank Apply` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | ColorMap seulement, B8 non invalidé ; T09 VM |
| 99 | `Aga Fade To Bank` | Palettes | ColorMap, AGAPAL, DATA, etat palette | Couleurs communes aux pages | Ecran/banque vivants, index, Close ; T09,T10,T14 | VM |
| 100 | `Aga Image Draw` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | GetMsg natif ; A003 VM |
| 101 | `Aga Image Capture` | IFF / AGAPIC | DOS/ILBM, RAM, banques AGAPIC, bitplanes | Variable: arriere pour draw/capture | Validation ILBM, Safe, plans, banque, B8 ; T04,T05,T10,T12 | VM |
| 102 | `Aga Font Bank Select` | Polices | Font systeme / bank font AMCAF / Chip | Aucune (selection), puis Text | Propriete, chargement, remplacement, Close ; T09,T14 | release OS/BankFont local ; Close VM |

## Références source pour vérifier les gardes individuels

- Écran / Swap / Safe : [UNIT142 Swap original](../src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s), [barrière P0j](../tools/m19_p0j_swap_barrier_emit.py), [Auto Update P2d](../tools/m19_p2d_bob_auto_update_emit.py), [B8 Safe](../tools/m19_b8_safe_lifecycle_emit.py).
- Blit / dessin : [R27 Safe](../tools/m12_blit_safe_r27_emit.py), [Plot](../tools/m15_plot_r40_emit.py), [Draw](../tools/m15_draw_r41_emit.py), [Box](../tools/m15_box_r42_emit.py), [Circle](../tools/m15_circle_r43_emit.py), [Text](../tools/m11_text_r26_emit.py).
- IFF / AGAPIC : [UNIT142 IFF Load](../src/native/m19_p2d/M19_UNIT142_IFF_LOAD_BODY_MC68020.s), [AGAPIC Draw](../tools/m16_image_draw_r45_emit.py), [Region](../tools/m18_image_region_v2_emit.py).
- CBlock/FICON/C2P : [CBlock wrapper](../tools/m18_cblock_bank_emit.py), [FICON capture](../tools/m18_ficon_capture_emit.py), [FICHIP draw](../tools/m18_ficon16_chip_blit_emit.py), [C2P Convert](../tools/c2p_r75_convert_emit.py).
- Bobs : [B8 pool](../tools/m19_b8_page_manager_emit.py), [B8 transitions](../tools/m19_b8_clear_update_tx_emit.py), [AGBO capture](../tools/m19_p0a_get_bob_emit.py).
- Sprite S1 : [source candidate](../src/native/m19_s1/M19_S1P1E_GET_PUBLIC_MC68020.s), **gelé**. Ne pas attribuer de Gate B/C à ses nouvelles commandes.

**Attention IFF Save :** aucune commande publique nommée `Aga Iff Save` n'a été trouvée dans les 102 tokens inventoriés. L'enregistrement des banques peut être effectué par les commandes AMOS selon leur contrat ; ne pas inventer un token de sauvegarde IFF.

## Règle de clôture

Remplacer `VM` ou `P1 risque` par `conforme` ou `anomalie confirmée` uniquement après lecture du chemin **réellement lié** (sélection du token AP20 → unité native → sortie) et preuve adaptée, Gate A puis B/C pour les chemins concernés. Tous les états provisoires restent **ouverts**.

Voir [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) et [cahier de tests](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).

## 24 novembre 2026 — liaison AP20 et nouvelle priorité

[Cartographie native exacte des 100 commandes P2d](AUDIT_AGA_AP20_LIAISONS_P2D_2026-11-24.md) : les index AP20, groupes et offsets du dispatcher $22 sont désormais retrouvés. La matrice conserve **102 entrées S1**, mais seuls les **100 tokens P2d** ont été tracés au niveau du master P2d ; les 2 tokens Sprite restent **gelés**. `Aga Back Fill` a été reclassé AGA-010 (P0 statique, limitation déjà documentée dans R27), sans test Runtime ni correction. Ajouter le cas T19 au cahier.

## Requalification AGA-003 (24 novembre 2026)

Le [modèle P2d](M19_P2D_BOB_AUTO_UPDATE_MODEL.md) exige **`Aga Bob Clear` avant toute modification de décor** avec Auto Update : `Clear → dessin → Swap`. Le [code B8](../tools/m19_b8_clear_update_tx_emit.py) utilise le masque `cleared` pour ne pas restaurer l'ancien fond et capturer le nouveau. **AGA-003 = validation manquante du chemin contractuel**, pas P1 confirmé à partir d'une séquence sans Clear. Se reporter à [T03](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md) et [Passage 4 de l'audit](AUDIT_TRANSVERSAL_AGA_2026-11-23.md). Les P0 Safe des commandes Back Fill et IFF restent indépendants.

## 24 novembre 2026 — AGA-002 confirmée par chaîne native

Les appels publiés `Aga Swap` (AP20 181 → BOBS+$0B606) et `Aga Bob Auto Update` (AP20 195 → BOBS+$0B58C) sont liés à [`M19_P2D_CONTROLS_MC68020.s`](../src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s). Le premier Bind B8 utilise le [sélecteur natif `L_BOBS_0BE32`](../src/native/m19_p2d/M19_P2D_SUPPORT_TAIL_MC68020.s) qui refuse Safe pending **sans GetMsg**, avant le Swap original. Statut **P1 anomalie structurelle conditionnelle de progression**, pas freeze WinUAE confirmé ; [cas T02 A–E](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).

## Passage 6 — 24 novembre 2026 : preuves locales, pas de validation globale

Le [dossier de contrôle CBlock/C2P/Copper/Close/Fonts](AUDIT_AGA_LIFECYCLE_COPPER_CBLOCK_C2P_2026-11-24.md) donne la liaison AP20 et les lignes source MC68020 : **GetMsg avant copie dans CBlock et C2P**, `WaitBlit` avant libération C2P, rollback Copper prévu, et **Screen Close atteint le Close historique même sans root B8**. Les statuts mis à jour désignent exclusivement une **présence de garde locale** ou un **comportement contractuel intentionnel**, **jamais une conformité Runtime/Compiler**. AGA-004 reste ouverte pour les chemins d'échec, callback End et réouverture ; T09/T13/T14/T16 affinés, tous non exécutés.

## Passage 7 — 24 novembre 2026 : P0 après Swap et séparation palettes / plans

[Rapport P2d IFF/Back Fill/AGBO/Palette](AUDIT_AGA_SWAP_IFF_BACKFILL_B8_PALETTES_2026-11-24.md) : `Aga Swap` réussi arme `DB+20=3` ; `Aga Iff Load` écrit le BODY sans acquisition Safe et `Aga Back Fill` appelle **SetRast(-234)** sans garde. L'ancienne attribution de ce vecteur à `RectFill` était une erreur de lecture LVO. **Palette Set/Bank Apply/Cycle** agissent sur `ColorMap`, pas sur les plans de pixels B8 : leur absence de notification de contenu B8 n'est **pas** une anomalie. `Aga Bob Bank Free` garde CLEAN et purge un cache, pas la banque AMOS DATA ; `Load/Erase Bank` externes gardent le statut VM (T10). 102/102 commandes inventoriées, aucune Gate nouvelle.

## Passage 8 — 24 novembre 2026 : dépendances et caches

[Audit des dépendances graphiques/caches](AUDIT_AGA_DEPENDANCES_CACHE_C2P_2026-11-24.md). **AGA-011** : `Aga Screen Pattern` peint `Screen.RastPort` sans acquittement Safe ni sélection back explicite, **page physique après Swap inconnue** (T06). `Aga Demo` ouvre son propre Screen Intuition temporaire. AGAPIC Draw/Region, FICON Capture et Cache Blit ont des protections locales visibles ; FICHIP doit être **explicitement re-stagé** après modification FICON. `C2P Blit/Zoom` touchent le chunky, alors que `C2P Convert` accède au bitmap arrière.

**GetMsg natif / MEMF_CHIP / ready=1 décrivent seulement des chemins source inspectés**, jamais un PASS Runtime/Compiler du socle complet. Les 102 noms restent inventoriés, T01–T19 non exécutés lors de cette passe, Sprite gelé.
