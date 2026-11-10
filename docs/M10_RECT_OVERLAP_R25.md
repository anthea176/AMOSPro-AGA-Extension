# M10 — R25 0.9.1 : collision entre deux rectangles (AABB)

## Périmètre du premier incrément

**Développement sur le nouveau dépôt uniquement, sur `main`.** R24 0.9.0 demeure la dernière bibliothèque ayant passé CPU/CI et AMOS interprété/WinUAE. Le premier incrément M10 est une **fonction pure** de collision rectangulaire : aucun moteur physique, aucune allocation, aucune modification des commandes R24 ni du dispatcher souris R23.

### API native proposée

```amos
_C=Aga Rect Overlap(_AX,_AY,_AW,_AH,_BX,_BY,_BW,_BH)
```

Fonction entière à **8 paramètres**. Résultat **1** si les deux rectangles ont une aire de chevauchement positive, **0** sinon. Les bords sont `[x,x+w[` et `[y,y+h[` : **contact bord à bord ou par un seul coin = 0**. Un chevauchement d'un seul pixel = 1. Les largeurs et hauteurs doivent être **strictement positives**. Origines négatives permises ; aucun clamp à la taille de l'écran ; aucun état graphique ou Intuition requis.

La géométrie est calculée en entiers signés 32 bits avec **comparaison des origines et soustraction contrôlée**. Pour éviter les débordements, le code ne calcule pas naïvement `x+w`.

### ABI AP20 et préservation

- Nouveau token entier `aga rect overlap`, index de fonction AP20 **35** et signature de huit arguments `00,0,0,0,0,0,0,0`. Total attendu : **30 commandes nommées**.
- `D3=bh` ; `(A3)+` contient dans l'ordre **`bw,by,bx,ah,aw,ay,ax`**. Consommation exactement **28 octets** de A3.
- Retour `D3=0/1`, `D2=0`, registres non-volatils préservés, SP équilibrée.
- Les 35 anciens segments R24 restent identiques, à l'exception des **4 octets de délimiteur `GetP` ajoutés à la fin du segment 34** avant la nouvelle fonction. Aucun pointeur ni offset interne de R24 modifié.
- Pas d'appel OS ni de blocage, pas de mémoire persistante, pas de collision pixel par pixel.

## Recette graphique WinUAE après préflight CPU/CI

Sélectionner **`iff-TEST/AGA_TESTCARD_320x256_256C.iff`** (320×256×8). Sa CMAP validée garantit les couleurs : index **3 bleu**, **28 vert** et **224 rouge**.

1. Afficher un **rectangle fixe bleu**, et un rectangle de **32×32 qui suit la souris** dans un écran Intuition AGA.
2. Le mobile est **vert** lorsqu'il ne chevauche pas le fixe et **rouge** dès qu'il y a une aire commune (y compris un pixel).
3. Approcher les bords, entrer dans la zone puis en ressortir. Les deux états doivent être observés ; pas de traces des positions précédentes. Le rafraîchissement se fait sur le back buffer avec `Aga Blit Clear`, `Aga Blit Fill` et `Aga Swap`.
4. Après avoir vu au moins une séparation et un chevauchement, cliquer **gauche** pour terminer, ou attendre le timeout de **900 VBL**. Le récapitulatif doit afficher `SEEN FREE 1`, `SEEN HIT 1`, `RESULT 1`, puis `CLOSE X2 RETURNED`.

Le même programme testera automatiquement des cas de collisions statiques **avant ouverture de l'écran** : deux rectangles identiques, inclusion, contact de bord, contact de coin, chevauchement d'un pixel, tailles nulles et origines négatives. Il contrôlera également l'ouverture, le double buffer, le chargement IFF, le Blitter, les `Swap` et la fermeture/réouverture.

### Limites du test

La souris est échantillonnée à chaque image. Ce test **ne valide pas la vitesse continue**, les collisions `pixel-perfect`, les collisions d'objets tournés, la prévention de traversée de mur ni l'instant exact d'un clic très bref. L'index CMAP de la mire est référencé pour éviter d'annoncer des couleurs non maîtrisées.

**Gate A CPU/CI :** 68000 émulation, ABI 8 paramètres, géométrie signée 32 bits, invariance des anciennes commandes et reproductibilité HUNK/AP20. **Gate B WinUAE :** seulement après retour utilisateur. Gates C (AMOS Compiler) et D (matériel Amiga) non testées.

## Livrables et précautions

- [Émetteur R25](../tools/m10_rect_overlap_r25_emit.py)
- [Builder pur R25](../tools/build_m10_rect_overlap_r25.py)
- [Tests CPU R25](../tools/test_m10_rect_overlap_r25.py)
- [Dernier jalon M9 validé](M9_HOTSPOT_R24.md)

Ne jamais réintroduire l'ancien historique Git. Ne pas modifier `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R10), les archives R24/R23 ni les sources et illustrations du nouveau dépôt. Les 2 README (EN/FR) seront mis à jour **dans le même commit que la promotion du nouveau token**.
