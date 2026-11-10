# M3b-1 v0.0.4 — Prototype fonctionnel à tester sous WinUAE

**État historique : premier essai WinUAE interprété ÉCHOUÉ** — `AGA DETECT=-1`, `M3B OPEN=0`. La cause a été identifiée comme une inversion des paramètres reçus par AMOS 365. **Ne plus installer ce binaire ; utiliser [la révision R1](M3B_V004_R1_FIX.md).**

Le **binaire défectueux historique** se trouve sous [dist/experimental/AMOSPro_AGA_M3b_v0.0.4.Lib](../dist/experimental/AMOSPro_AGA_M3b_v0.0.4.Lib). Il ne remplace **pas** les bibliothèques M2 et M3a validées. Pour l'installer, quitter AMOS et copier ce fichier sous le nom `AMOSPro_AGA.Lib` dans `APSystem/` de l'**installation de test uniquement**. Le slot 14 reste inchangé.

## Nouvelles commandes

- `Aga Screen Open(width,height,colors,modeID)` : fonction numérique. `0` = refus/échec ; valeur non nulle = écran ouvert. Un écran déjà ouvert n'est pas ouvert une seconde fois.
- `Aga Screen Pattern` : instruction dessinant un dégradé vert vers rouge sur le *screen* Intuition ouvert. Utilise la largeur, la hauteur et le nombre de couleurs réellement demandés.
- `Aga Screen Close` : instruction de fermeture répétable sans double-libération.

La fonction `Aga Detect`, la commande `Aga Probe` et l'ancienne démo `Aga Demo` restent présentes. Les routines M3a 1 à 5 sont conservées octet pour octet ; seule l'initialisation Cold a été réécrite pour ajouter une zone d'état de 32 octets, un hook RESET et un hook END (sources AMOS 365 `+Music.s`, `+CompExt.s`).

L'ouverture utilise `OpenScreenTagList` d'Intuition, `SA_Width`, `SA_Height`, `SA_Depth`, `SA_DisplayID`. Le `ModeID` est transmis à AmigaOS : un mode non disponible peut être refusé. Aucun registre Copper ECS n'est directement modifié.

## Périmètre v0.0.4

- Largeurs de 160 à 1280 pixels, multiples de 16.
- Hauteurs de 160 à 512 pixels.
- Couleurs indexées : 2,4,8,16,32,64,128,256 (1 à 8 plans, palette RGB24).
- ModeID brut choisi par le programme appelant (PAL/NTSC/HiRes/interlacé selon disponibilité réelle).
- Refus volontaire des modes HAM, EHB et Dual Playfield : ils exigent d'autres règles de pixel/palette.

Ces limites sont des contrôles logiciels. La compatibilité matérielle d'une combinaison reste à vérifier avec les retours d'AmigaOS et sous WinUAE.

## Procédure d'essai, dans cet ordre

1. Sauvegarder le binaire de travail validé **M3a v0.0.3** (disponible dans [archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib](../archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib)).
2. Installer le binaire M3b expérimental sur une **copie** d'AMOS 365.
3. Charger [M3B_320.asc](../tests/M3B_320.asc) et **exécuter en interprété uniquement d'abord**.
4. Attendu : `M3B OPEN` non nul, dégradé AGA 320×256 en 256 couleurs durant ~3 secondes, retour à AMOS, message `M3B CLOSED`.
5. Si réussite, compiler le **même** programme et lancer l'exécutable.
6. Ensuite seulement, tester [M3B_MODES.asc](../tests/M3B_MODES.asc) (640×256, 32 couleurs), puis [M3B_ERRORS.asc](../tests/M3B_ERRORS.asc) et [M3B_CYCLES.asc](../tests/M3B_CYCLES.asc).

Comme pour M3a, les scripts utilisent `Amos To Back` et `Amos To Front` autour des appels graphiques, car l'éditeur peut masquer les écrans Intuition.

## État des vérifications

- **10/10 tests statiques passent** : structure HUNK, table de tokens, limites des sauts et registres, hooks de nettoyage, préservation des anciennes routines, adresses API OS, signatures des paramètres, réouverture/fermeture au niveau du code, reproductibilité.
- **Pas de compilation native Genam** : code machine 68k généré par script Python, avec corrections PC-relatives.
- **WinUAE interprété : à valider**.
- **WinUAE compilé : à valider après interprété**.
- **Fermeture lors de RESET/END, absence de fuite Chip, manque de mémoire et ECS : à valider**.

Binaire : **1 564 octets** ; SHA256 `b602f90b8cd66c701f53d83014c0723cf74cbed73bdc5ecbd300dc9d40ed2af4`.

**En cas de dysfonctionnement :** quitter AMOS, restaurer le binaire M3a sous le nom `APSystem/AMOSPro_AGA.Lib` de l'installation de test. Ne pas utiliser M3b dans des programmes existants avant recette complète.


## Incident constaté le 31 octobre 2026

Capture WinUAE utilisateur : `AGA DETECT = -1`, `M3B OPEN = 0`, `OPEN FAILED (NO SCREEN DISPLAYED)`. AMOS 365 passe **le dernier argument dans D3**, puis les trois autres à `(A3)+` en ordre inverse. Le code interprétait le ModeID PAL `$00021000` comme une largeur et échouait au test des limites. Correction et nouveau ZIP : [M3B_V004_R1_FIX.md](M3B_V004_R1_FIX.md).
