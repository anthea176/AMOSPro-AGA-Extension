# M5 — Image / IFF / ILBM

## Objectif

Fournir une couche image propre et réutilisable au-dessus de l'infrastructure écran AGA déjà validée.

M5 est désormais découpé en sous-jalons afin de ne plus mélanger parsing IFF, décodage, palette et sélection du mode vidéo.

## Base validée — M5.0

Build :

`M5-R3R1 0.3.1`

Validé sur Clown.iff :

- FORM ILBM ;
- scan BMHD/CMAP/BODY ;
- ByteRun1 ;
- 320×200×8 ;
- palette 256 couleurs ;
- SA_FullPalette ;
- synchronisation palette ;
- Double Buffer / Swap / Close.

## M5.1 — inspection — PASS interprété, compilé à faire

API :

```amos
_V=Aga Pic Info("image.iff",field)
```

Champs :

| field | retour |
|---:|---|
| 0 | largeur |
| 1 | hauteur |
| 2 | bitplanes |
| 3 | nombre de couleurs CMAP |
| 4 | compression |
| 5 | CAMG / ModeID |
| autre | -1 |

Contraintes :

- ne pas ouvrir d'écran ;
- ne pas décoder BODY ;
- scanner FORM/BMHD/CMAP/CAMG ;
- retour -1 sur fichier invalide.

Cette API doit servir de brique commune au loader et aux programmes AMOS.

PicInfo 0.3.2 est PASS en interprété sur tout le lot testé. Le test d'ouverture automatique d'écran à partir de W/H/CAMG est également PASS sur Clown, MYGIRL, DBZ01 et KEKKO. Validation compilée encore à faire.

## M5.2 — indexed 320 px — VALIDÉ R4 0.4.5

Formats :

- largeur 320 ;
- hauteur 200 ou 256 ;
- profondeur 3..8 ;
- masking 0 ;
- ByteRun1 ;
- CMAP 8..256 couleurs.

Le BODY est organisé ligne par ligne puis plan par plan.

```text
rowBytes = ((width + 15) / 16) * 2
```

Le candidat M5.2 R1 0.4.2 :

1. conserve PicInfo et toutes les commandes non-IFF byte-for-byte ;
2. garde le chemin Clown 320×200×8 historique ;
3. ajoute le chemin 320×256 ;
4. accepte 3..8 plans ;
5. utilise le nombre réel de couleurs de l'écran pour la palette ;
6. valide la hauteur et la profondeur du Bitmap destination ;
7. adapte les boucles ligne/plan au BMHD ;
8. conserve ByteRun1 `NEG.L` et le `WaitTOF` R3R1.

Comme l'écran est désormais ouvert à la profondeur exacte via PicInfo, il n'existe pas de bitplanes destination supplémentaires à nettoyer dans le scénario M5.2 normal.

EHB/HAM et `harrison.iff` restent hors périmètre.

## M5.3 — compression 0 et robustesse — candidat R1 0.5.0

R1 implémente :

- BODY brut compression=0 via le chemin literal existant ;
- ByteRun1 conservé et borné ;
- BMHD strict 320×200/256, 3..8 plans, masking=0, compression 0/1 ;
- CMAP 24..768 octets divisible par 3 ;
- scan de chunks refusant les fins résiduelles invalides ;
- BODY consommé exactement ;
- les cas négatifs runtime (BODY tronqué, CMAP invalide, chunk tronqué, longueurs incohérentes) restent à valider après les fixtures RAW positives.

ByteRun1 :

- 0..127 : n+1 littéraux ;
- 129..255 : répétition 257-n ;
- 128 : NOP.

Aucune lecture ne doit dépasser BODY et aucune écriture ne doit dépasser le rowBytes du plan courant.

## M5.4 — CAMG / HiRes / interlace

Ajouter une fonction interne de résolution de mode :

```text
(width,height,depth,CAMG) -> ModeID + flags
```

Support initial :

- 640×256 ;
- 640×512 ;
- PAL HiRes ;
- interlace.

## M5.5 — EHB / HAM

Reconnaissance :

- EHB : CAMG & $80 ;
- HAM : CAMG & $800 ;
- 6 plans + HAM = HAM6 ;
- 8 plans + HAM = HAM8.

Ces modes demandent des chemins palette/rendu spécifiques.

## M5.6 — validation finale

Avant clôture M5 :

- plusieurs fichiers réels par format ;
- 20 chargements successifs ;
- changement d'image sans reboot ;
- fermeture propre ;
- interprété ;
- compilé ;
- WinUAE ;
- vrai AGA si disponible.

## Compatibilité historique

Le format privé SQUASH / compression 128 du viewer 1995 reste une compatibilité optionnelle future.

Il ne doit pas retarder le support ILBM standard.


### Incident R4 0.4.0

R4 a été rejeté en runtime. Cause identifiée : D6 contenait hauteur/profondeur BMHD mais la boucle SetRGB32 utilisait également D6 comme scratch. R4R1 0.4.1 protège D6 autour de la boucle palette et conserve le WaitTOF R3R1.


### Incident R4R1 0.4.1

R4R1 est également rejeté : crash WinUAE sur Clown. Le projet revient sur R3R1 0.3.1 et reprend par M5.1 Aga Pic Info avant toute nouvelle modification multi-format du loader.


### Incident M5.2 R1 0.4.2

R1 est rejeté : le patch réutilisait A5 pour le BMHD alors que A5 est la base AMOS utilisée pour accéder à l'état extension. Résultat : IFF LOAD=0 sur Clown. R2 0.4.3 ne modifie plus A5 et valide directement BMHD hauteur/profondeur contre l'état écran.


### Incident M5.2 R2 0.4.3

R2 est rejeté : blocage avant OPEN sur Clown. Le candidat R3 garde exactement la taille du segment Aga Iff Load et la jump table de PicInfo 0.3.2 afin de ne plus déplacer PicInfo ni les entrées suivantes.


### Incident M5.2 R3 0.4.4

R3 est rejeté pour corruption mémoire Exec (`81000005`). Le calcul du nombre de couleurs devait exécuter `DIVU #3,D7`, mais le builder encodait `86FC 0003` (destination D3). D7 restait donc à la taille CMAP en octets, ce qui faisait dépasser la boucle palette. R4 0.4.5 remplace uniquement cet opcode par `8EFC 0003`.
