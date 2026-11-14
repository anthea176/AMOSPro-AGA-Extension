# R84 — chantier AGAPIC v1/v2 : contrat de travail

**14 novembre 2026 — main uniquement. R83 LAST_GOOD protege.**
Ce document précise les deux APIs du chantier 2 de docs/ROADMAP.md. R84 est une **candidate native dans le seul binaire actif `dist/AMOSPro_AGA.Lib`**, validée en Gate A CPU/CI ; WinUAE Runtime/Compiler B/C restent à tester. `LAST_GOOD` R83 n’a pas changé.

## 2A — _VALEUR=Aga Bank Image Info(Bank,Champ)

Bank = numero d'une banque AMOS DATA vivante (5..65535), resolu par Bnk.GetAdr ; jamais Start(Bank). Champs :
- 1 = largeur, 2 = hauteur, 3 = profondeur 1..8 plans.
- 4 = nombre de couleurs RGB24 **embarquees** : v2 = 2^Depth ; v1 = 0 (aucune palette dans le format).
- 5 = ModeID U32 enregistre : v2 = valeur exacte, v1 = 0 (champ absent). En AMOS, les U32 >= $80000000 apparaissent negatifs, conserver les bits.
- **-1 = erreur** banque absente, champ incorrect, mauvais format ou metadonnees corrompues. Les ModeID v2 0 et $FFFFFFFF sont invalides, donc -1 ne collisionne pas avec un ModeID valide.

Controle natif : enveloppe AMOS, signature AGAPIC, version, flags, codec, dimensions, GroupBytes, taille exacte, layout, palette complete v2, padding nul, table des offsets strictement croissante. Pas de decodage du flux RLE pour Info, ni d'ecriture, de palette appliquee ou de Swap.

## 2B — _OK=Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)

- Nouvelle API 7 arguments, Version **1 ou 2** en dernier. L'ancienne commande Aga Image Capture(...,TransparentIndex) continue a creer uniquement la v1, sans changement ABI/code.
- Version 1 : capture explicite v1 (en-tete 32 octets, meme flux RLE, sans palette ni ModeID).
- Version 2 : capture RLE identique, en-tete 64 octets, palette RGB24 complete GetRGB32 depuis le ColorMap prive, ModeID reel GetVPModeID, Flags 2/3, PixelFormat=1, TableOffset=ALIGN4(64+3*(2^Depth)), offsets ajustes et longueur exacte.
- TransparentIndex=-1 : opaque, y compris la couleur 0 ; sinon index legal : masque independant. Rectangle interieur complet dans le back buffer AGA inactif Safe ; aucune capture du front buffer.
- Banque libre exigée. Deux passes de comptage/ecriture RLE, controle de collision avant Reserve, rejet sans destruction de banque existante, rollback de **la nouvelle banque seulement** sur erreur apres Reserve. Liberer tous les tampons temporaires.
- Retour 1 si succes / 0 si refus. Aucun Swap, attente VBL, application de palette ou creation implicite de banque de destination preexistante.

## Architecture et validation

R83 : 74 commandes, 80 entrees publiques et 3 groupes natifs AP20. R84 : 76 commandes, 82 entrees publiques et les memes trois groupes. Ancien code et anciennes signatures inchanges ; ajout dans l'unite AGA et reindexation controlée des stubs, sans quatrieme unite. Controler **65 534 octets maximum par unite** et le BSR.W du chargeur.

- Gate A **PASS** : builder deterministe, API et GetP, liens 68020, code CPU executé (Info 44 cas, capture 47 cas), palette/ModeID, erreur et mémoire. Ces tests natifs ne prouvent pas le comportement sous AMOS/WinUAE.
- Gate B ensuite : WinUAE Runtime, un seul ASC actif ; meme image capturee v1/v2 en 4/8 plans opaque et masque, Save/Load ABK et dessin, palette/ModeID, rejets et RAM.
- Gate C ensuite : compilation AMOS du meme banc. Gate D Amiga physique non presumee.
- LAST_GOOD R83 inchangee, pas de tag, GitHub Release, Aminet ou branche experimentee sans nouvelle autorisation.

Reference : M16_AGAPIC_V2_CONTRACT_2026-11-14.md et ROADMAP.md.
