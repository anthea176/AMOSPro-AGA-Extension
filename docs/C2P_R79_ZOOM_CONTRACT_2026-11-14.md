# C2P-5 / R79 — contrat de Aga C2P Zoom (14/11/2026)

**Statut :** Zoom demandé et engagé par l'auteur avant la clôture C2P. Candidate R79 v0.13.24 implémentée en native, Gate A CPU PASS (62 scénarios), Gate B WinUAE NON TESTÉE. La Gate C Compiler reste **après Zoom**, jamais entre R78 et R79. R78 Gates A/B PASS, R73 `LAST_GOOD` protégée.

## API

```amos
_OK=Aga C2P Zoom(SrcBank,SrcPitch,SrcX,SrcY,SrcW,SrcH,DstX,DstY,DstW,DstH)
```

Fonction entière à **10 paramètres** : `DstH` dans D3, les neuf autres arguments dépilés de A3 dans l'ordre inverse. Retour **1** si au moins un pixel copié, **0** si aucune écriture (appel refusé/rectangle entièrement hors écran).

## Échantillonnage : nearest-neighbour, sans interpolation

`SrcBank` est une banque AMOS **DATA/WORK** d'indices de palette chunky **8 bits**. `SrcPitch` est son pas en **octets par ligne**, indépendamment de `SrcW`. `SrcX,SrcY,SrcW,SrcH` désignent le rectangle source original ; `DstX,DstY,DstW,DstH` désignent le rectangle destination original dans la banque chunky liée à `Aga C2P Open`.

Pour chaque pixel visible `(X,Y)` du rectangle destination après clipping :

```text
localX = X - DstX
localY = Y - DstY
sampleX = SrcX + floor(localX * SrcW / DstW)
sampleY = SrcY + floor(localY * SrcH / DstH)
Dst[Y*320+X] = Src[sampleY*SrcPitch+sampleX]
```

Le clipping se fait **en coordonnées destination** sans re-normaliser l'image au bord visible : un rectangle partiellement hors écran conserve sa géométrie originale. Le pixel d'indice **0 est opaque**. Aucun lissage, alpha, couleur transparente, HAM, changement de palette, Convert ou Swap implicite.

## Bornes et sécurité de la première version

- Écran AGA privé **320×256**, contexte C2P 4..8 plans actif, banque chunky destination **au moins 81920 octets**, CPU 68020+ pour le contrat.
- `SrcBank` numérique **5..65535**, différent de la banque chunky et sans recouvrement physique des allocations. `Bnk.GetAdr` vérifié **pour les deux banques à chaque appel** (aucune adresse conservée après Erase/Load/Reserve). En-têtes DATA/WORK, adresse, taille physique et attributs mémoire vérifiés comme pour R78.
- `SrcPitch >= 1`, `SrcX>=0`, `SrcY>=0`, **1<=SrcW<=320**, **1<=SrcH<=256**, `SrcX+SrcW<=SrcPitch`. Vérifier sans débordement la taille de source nécessaire `(SrcY+SrcH-1)*SrcPitch+SrcX+SrcW <= longueur réelle banque`.
- **1<=DstW<=320**, **1<=DstH<=256**. `-319<=DstX<=319`, `-255<=DstY<=255`. Le rectangle visible est l'intersection du rectangle de destination original et de `[0,320)×[0,256)`. Intersection vide = retour 0 et aucune écriture.
- Multiplications et offsets contrôlés (y compris l'overflow 32 bits). Les divisions d'échantillonnage utilisent les bornes précédentes ; `DIVU.W` 68000 est sûr pour ces bornes. Validation complète avant écriture (pas de dessin partiel lors d'un refus).
- Copie **CPU en chunky Fast/Chip**, jamais DMA Blitter ni accès planar direct. Aucune allocation persistante et aucune modification de l'état de l'écran, du double buffering, des banques source, des palettes ou du SDK C2P.
- Implémentation **append-only** après R78 (nouveau token AP20, nouvelle entrée native), sans changement des sept LEA clavier/souris R76 visant `$2F26`. Un seul ASC courant, journal RAM et `Amos To Back` avant Echap.

## Exemples de comportement

- **Agrandissement 2× :** zoom source 32×32 en destination 64×64, chaque indice source apparaît 2×2 fois.
- **Réduction 2× :** 32×32 vers 16×16, échantillons (0,0), (2,0), etc.
- **Décentrage/clipping :** 32×32 vers 64×64 position `DstX=-8`, puis `DstY=-8` : les premiers pixels affichés échantillonnent respectivement la source `floor(8*32/64)=4`, et non 0.
- **Identité 1× :** la sortie est exactement la même que la copie opaque R78 lorsque source et destination sont de dimensions égales.

## Qualification

1. **Gate A CPU native** : jeux d'images indépendants, vérifications pixel par pixel pour zoom ×1, ×2, réduction, facteurs non entiers, clipping 4 bords, zéro opaque ; contrôles canary, taille/recouvrement de banque, overflow, CPU68000 rejeté, ABI 10 arguments, copie sans SDK ni Convert/Swap, 7 LEA, AP20 V2, provenance R78 figée.
2. **Gate B WinUAE :** un seul ASC en `tests/current/`, 16/32/64/128/256 couleurs, rendu zoom agrandi/réduit et clipping, comparaison par Peek, bilan RAM mode/CPU/compteurs/mémoire, `Amos To Back` devant la touche Echap, nettoyage et `End`.
3. **Gate C :** une seule exécution **compilée** après réussite de Gate B Zoom, sur le dernier ASC C2P complet. **Pas de Compiler à chaque version**. Gate D physique séparée.
4. Pas de promotion, tag, release ou Aminet sans décision distincte de l'auteur. R73 `LAST_GOOD` immuable.

[Contrat R78 Blit](C2P_R78_BLIT_CONTRACT_2026-11-14.md) · [Gate B R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) · [Règles source](../EXTENSION_SOURCE_RULES.md).

## Réalisation candidate et qualification (14/11/2026)

La candidate R79 v0.13.24 est produite en append-only depuis R78 SHA épinglé, **57 344 octets**, SHA256 `ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab`, **69 commandes / 76 entrées AP20**, 1 516 octets natifs additionnels. **Gate A native PASS (62 scénarios), CI complète source PASS 66 étapes**, désassemblage 68000, vrai CPU M68020, pixels nearest-neighbour comparés octet par octet, clipping et garde de toutes les banques et des sept LEA clavier/souris. [Rapport R79](C2P_R79_ZOOM_NATIVE_GATE_A_2026-11-14.md).

**Gate B WinUAE R79 reste NON TESTÉE** ; l'ASC actif `C2P_R79_ZOOM_01.asc` conserve Blit+Close de R78 et ajoute quatre compteurs Zoom (copies/pixels/rejets/réouverture) sur cinq profondeurs avec log RAM. Gate C Compiler seulement après Gate B Zoom, Gate D machine physique séparée. R73 LAST_GOOD protégée.
