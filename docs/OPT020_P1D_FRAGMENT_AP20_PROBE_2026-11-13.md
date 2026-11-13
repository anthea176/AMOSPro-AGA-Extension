# OPT020/P1d — fragments natifs BFINS et sonde ABI AP20 (13/11/2026)

**Statut validé : P1d CPU/sonde ABI PASS — 13 novembre 2026.** [CI native SUCCESS, 13/13 étapes](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43494522268), sur [commit 81c628e](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/81c628e0431fc7c0630ea4c0918254da85cd020e). Branche unique `main` ; R68 `LAST_GOOD` et ASC actif inchangés. Cette étape est un prototype technique, **pas une bibliothèque R69**.

## Objectif

P1c exécutait déjà le décodage de ligne RLE, le clipping horizontal/vertical et l'écriture des groupes 16 pixels sous Musashi **68EC020/68020**, mais les fragments partiels étaient peints dans Python hôte. P1d supprime ce **dernier traitement pixel Python** :

- [Nouveau noyau natif de fragments](../tools/opt020_p1d_fragment_emit.py) : champs dynamiques `BFEXTU/BFINS` pour 1 à 16 pixels, 1–8 plans, lecture d'un masque indépendant et fusion `old XOR ((old XOR source) AND mask)`. Préserve tous les bits adjacents.
- [Runner Musashi partagé](../tools/opt020_p1d_native_runner.py), qui réutilise sans les altérer le décodeur, le clipping et le peintre complet de P1c. **Une seule machine CPU par test**, pour éviter le conflit de traps entre émulateurs.
- [Rendu AGAPIC de contrôle](../tools/opt020_p1d_region.py) : RLE et clipping natifs, groupes complets via le noyau P1b, fragments via le nouveau BFINS. La **validation globale de l'image** et l'orchestration demeurent en Python ; aucune écriture directe de pixel n'est effectuée par Python.
- [Tests rendus et fragments](../tools/test_opt020_p1d_fragments.py) : profondeur 1/2/4/8, masque nul/plein/partiel, X non aligné, 1–16 pixels, source partielle, crops/clipping. Résultats comparés à un oracle indépendant sur **tous les octets des plans**, avec gardes et vérification non destructive des erreurs.

## Entrée de type AP20, strictement expérimentale

[Émetteur de sonde](../tools/opt020_p1d_ap20_probe_emit.py) · [Test ABI et Compiler V2 simulée](../tools/test_opt020_p1d_abi.py).

La sonde reprend les encodages de **sauvegarde/restauration** du validateur [R60](../tools/m18_image_region_emit.py) : `MOVEM 48e7efee / 4cdf77f7`, avance les sept paramètres `(A3)+` exactement comme `Aga Image Region(Bank,SrcX,SrcY,Width,Height,X,Y,Mode)`, et retourne `D3=0/1, D2=0`. Elle vérifie **avant le premier opcode 68020** `SysBase = *(LONG*)4` puis `ExecBase.AttnFlags` au décalage **0x128 (296)**, bit **AFF_68020 = 1**. Référence : [AmigaOS NDK / execbase.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0609.html). Les routines de garde sont **exclusivement du 68000 légal**. La première sonde avait tenté un `TST.L An` (adressage direct interdit au 68000) avant le contrôle CPU ; le correctif utilise `MOVE.L An,Dn` + `TST.L Dn`. Le banc vérifie désormais aussi par désassemblage 68000 toutes les instructions précédant le bloc 020. Les tests d'exécution sur **M68000, 68EC020 et M68020** ont ensuite réussi : le 68000 est refusé sans opcode 020, tandis que 68EC020/68020 sont autorisés lorsque `AFF_68020` est présent. Un second correctif a aligné la consommation des **sept paramètres A3 avant tout refus**, conformément à la routine R60.

**Limite capitale :** A0 pointe dans ce test vers un **descripteur artificiel déjà prévalidé**, PAS vers une banque AMOS. La sonde n'appelle pas encore `Bnk.GetAdr`, ne valide pas réellement la banque DATA et n'acquiert pas le `Safe` du back buffer. Elle **ne doit jamais remplacer l'entrée R60 dans une Lib livrée**.

Le test Compiler V2 ne modifie aucune bibliothèque sur disque : il déplie **en mémoire** la R68 promue, substitue **temporairement dans ce tableau en mémoire** l'entrée expérimentale à la fonction R60, reconstitue l'enveloppe Compiler V2 et vérifie les offsets, stubs `Rbsr`, `GetP` et la taille d'unité. La substitution est **inutilisable en AMOS** par conception ; c'est une preuve de structure AP20, **pas Gate C**.

## Résultats mesurés en CI — PASS

| Vérification sur Musashi | Total | Verdict |
|---|---:|---|
| Fragments exécutés directement 68EC020/68020 | **4 096** | PASS |
| Rendus AGAPIC complets comparés à l'oracle | **432** | PASS |
| Groupes complets écrits en BFINS natif | **5 352** | PASS |
| Fragments écrits en BFINS dynamique natif | **3 672** | PASS |
| Pixels de fragments recopiés | **25 816** | PASS |
| Lignes RLE parcourues en code natif | **2 976** | PASS |
| Refus de sources invalides sans écrire | **14** | PASS |
| Appels de la sonde ABI CPU/paramètres | **140** | **80 succès / 60 refus** |
| Registres sauvegardés, pile, A3+28, D2=0, D3=0/1 | — | PASS |
| Enveloppe Compiler V2 reconstruite uniquement en mémoire | **70 segments**, enveloppe **49 308 octets** | PASS structurel |

- **Noyau fragment CPU020** : 36 octets, SHA256 `7ac2e2d9c068bcac868558dd56467539cab6287cdf4235f2d8ad26d340cdbce3`.
- **Sonde ABI** : 256 octets, SHA256 `ab0ea734ca6c069a8dc4b97ebec7eb6a4a3d7e57f30668e11670a4fe69c1bf30`.
- L'unité Compiler V2 factice occupe **46 610 octets** à l'intérieur du binaire **provisoire uniquement en mémoire** ; ce fichier n'est **pas** écrit ni livré, et sa fonction Image Region aurait été remplacée par une sonde incompatible avec les vraies banques AMOS.
- Tous les fonds, les bitplanes, les canaries, les 7 paramètres et le résultat D3/D2 sont conformes aux tests. **Aucune accélération WinUAE n'est mesurée**.

[Log complet de la CI P1d](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43494522268).

## Prévalidation globale : éviter une réécriture dangereuse

La validation globale AGAPIC existe déjà **en assembleur natif 68000 compatible 020** dans [l'émetteur R60](../tools/m18_image_region_emit.py) : banque DATA/`Bnk.GetAdr`, en-tête et longueur, offsets, paquets RLE complets, padding du dernier groupe, **PASS 0 avant tout dessin**, puis acquisition non bloquante `Safe` et PASS 1. Il n'est **pas nécessaire** de la réécrire aveuglément en instructions 020 ; il faudra **la réutiliser et rebrancher le nouveau peintre** avant toute candidate publique.

La CI P1d valide des modules CPU et un cadre de test mais ne valide pas encore le *raccordement réel de R60 à ces modules*. Seule une future intégration native complète avec contrôle AP20/HUNK, WinUAE interprété (Gate B), puis nouvel exécutable AMOS Compiler (Gate C) pourra qualifier cette version.

**Protections :** `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent R68 byte-identiques, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Aucun autre ASC actif, aucune branche ni PR, aucune publication, aucun nouveau binaire.
