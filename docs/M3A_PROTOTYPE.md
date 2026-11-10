# M3a — Premier écran AGA 256 couleurs (v0.0.3)

**Statut : prototype binaire validé sous WinUAE en interprété avec bascule AMOS/Intuition. Retour `AGA DEMO RETOUR = 1` confirmé par le développeur. Essai compilé également validé le 31/10/2026.**

## Téléchargement

Bibliothèque expérimentale : [dist/experimental/AMOSPro_AGA_M3a.Lib](../dist/experimental/AMOSPro_AGA_M3a.Lib).

La version **v0.0.2 R1 validée** reste accessible dans [dist/AMOSPro_AGA.Lib](../dist/AMOSPro_AGA.Lib) et dans l'archive M2. Elle n'est pas remplacée par ce prototype.

## Mode d'emploi (installation de test uniquement)

1. Quitter AMOS, sauvegarder `APSystem/AMOSPro_AGA.Lib`.
2. Copier le fichier M3a sous le nom **`AMOSPro_AGA.Lib`** dans `APSystem/` de la **copie de test** d'AMOS 365.
3. Relancer AMOS avec l'extension dans le slot **14**, inchangé.
4. Importer [AGA_DEMO.asc](../tests/AGA_DEMO.asc) et lancer en **interprété**.
5. Attendre : un écran AGA PAL **320×256, 8 bitplanes** doit montrer un dégradé vert → rouge sur **256 lignes** pendant environ **3 secondes**, puis se fermer et revenir à AMOS.
6. Si interpréteur OK, compiler et lancer le **même test** en exécutable.
7. En cas de plantage / écran noir permanent, restaurer le binaire M2 sous le nom `AMOSPro_AGA.Lib` ; transmettre capture et symptômes.

La fonction expérimentale `Aga Demo` retourne une valeur **non nulle** si l'écran a été ouvert et refermé (booléen vrai), et **0** sinon. Elle réalise l'ouverture, le dessin et la fermeture **en un seul appel synchrone**. Elle ne propose pas encore une paire permanente `Aga Screen Open` / `Aga Screen Close`.

## Architecture détaillée

- Validation du CPU : `ExecBase.AttnFlags` bit AFF_68020 dans l'octet bas du mot (offset $129).
- Validation AGA : `graphics.library` 39+ et `GfxBase.ChipRevBits0`, bits Alice/Lisa = $0C.
- Ouverture : `intuition.library/OpenScreenTagList` (-612), tags `SA_Width`=320, `SA_Height`=256, `SA_Depth`=8, `SA_DisplayID`=PAL/LORES $00021000.
- Palette : `graphics.library/SetRGB32` (-852) pour les **256 entrées**, rouge croissant, vert décroissant, bleu fixe.
- Dessin : `SetAPen` (-342) et `RectFill` (-306) sur `Screen.RastPort`, une ligne horizontale par index de couleur.
- Temporisation : `WaitTOF` (-270), environ 151 tops VBL PAL.
- Libération : `CloseScreen` (-66), puis fermeture de graphics.library et intuition.library. Toutes les voies d'échec évitent la fermeture d'une ressource non acquise.
- Aucun accès direct aux registres du Copper / DMA / bitplanes d'AMOS.
- Mémoire bitmap minimale : 81920 octets (80 Kio) Chip RAM, hors autres allocations système.

## Compatibilité et risques

- Les routines M2 (Aga Probe et Aga Detect) sont conservées octet pour octet dans la bibliothèque M3a.
- Prototype AP20 construit par le script hôte [build_m3_compact.py](../tools/build_m3_compact.py) à partir du binaire M2 archivé ; **ce n'est pas encore un assemblage Genam natif**.
- Taille HUNK : **688 octets**, SHA256 `ea2c3d970569e870952f843b96264a27bce79a2dc337115d738e4e6d3e6ee2aa`.
- Vérifications statiques : 5/5 réussies, notamment HUNK, table des tokens et offsets, préservation M2 et appels AmigaOS.
- **Aucune validation réelle sous WinUAE n'a été effectuée par l'assistant.** La commutation entre les écrans Intuition et les écrans AMOS est précisément ce qu'il faut vérifier.
- La valeur booléenne peut s'afficher `-1` (TRUE AMOS). La bibliothèque devrait retourner 0 si AGA absent / ouverture impossible, mais ce cas négatif n'est pas encore validé.
- Conserver les expériences de l'extension séparées des autres projets et de l'installation AMOS 365 validée.

## Sources des interfaces

- AMOS 365 : +Music.s / +Equ.s / +Request.s.
- NDK 3.1 : intuition/screens.i (SA_*), graphics/view.i (ViewPort), graphics/rastport.i (RastPort).
- Intuition : https://wiki.amigaos.net/wiki/Custom_Screen_Type
- DisplayID : https://d0.se/include/graphics/modeid.i
- Palette : https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0328.html


## Retour d'essai : ecran non visible (31/10/2026)

Le programme M3a initial n'affichait pas l'ecran AGA. Le test correctif `AGA_DEMO_VISIBLE.asc` avec `Amos To Back` / `Amos To Front` affiche effectivement le degrade sous WinUAE, selon confirmation utilisateur. Le retour indique **`AGA DEMO RETOUR = 1`**, ce qui confirme le chemin de succes de la fonction. **Validation interpretee acquise pour ce scenario precis ; pas encore de validation compilee.**

Cause pratique confirmee : AMOS Professional conserve sa propre vue devant le nouvel ecran Intuition sans bascule explicite. La commande documentee `Amos To Back` cache la vue AMOS et revele Workbench. **Test sans modification du binaire** : [tests/AGA_DEMO_VISIBLE.asc](../tests/AGA_DEMO_VISIBLE.asc) utilise `Amos To Back` avant `Aga Demo`, puis `Amos To Front` au retour.

Interpretation :
- Degrade visible : le changement de vue est necessaire dans le test initial.
- Degrade absent et `AGA DEMO RETOUR = 0` : ouverture impossible ou fonction sortie en erreur ; diagnostiquer sans supposer qu'il s'agit du Copper.
- Degrade absent et retour non nul : investiguer `ScreenToFront`, gestion de l'affichage Intuition, affichage par AMOS, ou anomalie interne du prototype.

Source AMOS TO BACK / FRONT : https://amospromanual.dev/11-04-multitasking.html


## Compte rendu du test de visibilité

Le 31 octobre 2026, le développeur confirme que `tests/AGA_DEMO_VISIBLE.asc` fonctionne sous WinUAE et précise **« 1 le retour »** : `AGA DEMO RETOUR = 1`. Le test original sans `Amos To Back` n'affichait pas le nouvel écran. Conserver **le même binaire M3a** ; seule la gestion de visibilité au niveau du programme de test a changé. Le même test compilé avec AMOS 365 fonctionne aussi (confirmation du développeur le 31/10/2026).


## Validation M3a compilée — 31 octobre 2026

Le développeur confirme « ca marche aussi » après avoir compilé puis exécuté le même programme `AGA_DEMO_VISIBLE.asc` sous AMOS 365. M3a est validé pour **la démo en interprété et en compilé**. La valeur numérique brute affichée par l'exécutable compilé n'a pas été communiquée. Les cas ECS, erreurs mémoire et ouvertures répétées restent non testés.

Binaire figé sans modification : [archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib](../archive/AMOSPro_AGA_M3a_v0.0.3_WinUAE_OK.Lib).
