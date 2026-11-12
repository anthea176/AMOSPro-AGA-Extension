# M15/R43 — Aga Circle : contrat approuvé, implémentation Gate A en cours

**Statut au 12/11/2026 : contrat explicitement approuvé par l'utilisateur (« oui c tous bon »).** Implémentation 68000, builder reproductible et tests Gate A déposés. Gate A/CI R43 non encore vérifiée ; aucun binaire candidat R43 publié ni test WinUAE actif. La dernière `LAST_GOOD` demeure **R42 v0.11.3**, Gates A et B PASS, 47 commandes AP20, 25 896 octets et SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. Gates C/D non testées. Le présent texte décrit le **contrat approuvé** ; la promotion d'un binaire reste soumise aux Gates réelles.

## Une seule commande proposée

```amos
_OK=Aga Circle(CX,CY,Radius,Pen)
```

- Fonction entière AMOS (_OK 0/1), **une seule commande** exportée, prévue pour la version **R43 v0.11.4**.
- `CX`, `CY` : centre en pixels dans le repère de l'écran AGA privé, valeurs AMOS LONG contrôlées dans la plage **signed16 -32768..32767** avant usage.
- `Radius` : rayon entier en pixels, **0..32767** accepté. `Radius=0` trace un unique pixel au centre, si visible. Rayon négatif ou supérieur à 32767 : retour 0, aucune écriture et aucune troncature.
- `Pen` : index de couleur de la profondeur AGA active, **0..(1<<Depth)-1** (0 est valide), profondeur 1..8. Ni RGB24 ni couleur AMOS `Ink`.
- Cercle **de contour 1 pixel**, sans remplissage, XOR, anticrénelage, motifs ou épaisseur variable. Points cardinaux aux coordonnées `(CX+-Radius,CY)` et `(CX,CY+-Radius)` ; rasterisation entière déterministe et symétrique sur huit octants.
- **Succès 1** si au moins un pixel a été effectivement écrit (y compris écriture de Pen 0 ou valeur déjà présente) ; **retour 0** si l'ensemble du contour est invisible, si un argument/état est invalide, si Safe manque ou si aucune écriture ne réussit. Un échec système après la première écriture n'est **pas atomique**.

## Algorithme de sécurité envisagé

- **Midpoint Circle / Bresenham entier**, même séquence de points pour le cercle visible et le cercle tronqué. Aucun appel à `graphics.library/DrawEllipse` sur le RastPort non-layered, évitant la dépendance à un clipping non garanti et les divergences de rasterisation.
- Calculs du centre +/- rayon, de l'erreur et des coordonnées intermédiaires en **32 bits signés**, afin d'éviter les débordements 16 bits. Maximum proposé : rayon 32767, donc boucle bornée ; aucun arrêt arbitraire n'interrompt un cercle normalement autorisé.
- Pour chaque candidat parmi les huit symétries, vérifier **`0<=X<Width` et `0<=Y<Height` AVANT** tout `WritePixel`. Les doublons aux axes/diagonales sont tolérés : JAM1 en copie rend les écritures idempotentes. Pas de bord inventé au découpage.
- Rejet avant graphiques et avant consommation Safe si la boîte englobante `[CX-R,CX+R] x [CY-R,CY+R]` est entièrement en dehors de l'écran. Une boîte englobante qui contient l'écran **ne signifie PAS que le contour est visible** : ne créer aucune bordure et ne retourner 1 que si un vrai pixel du cercle est écrit.
- Reprendre les gardes R42 : écran privé actif, `Screen*`, `GfxBase*`, `DBState*`, back `ScreenBuffer` valide et non affiché, dimensions logiques et physiques cohérentes, `BitMap.Depth` conforme, 1..8 plans valides, index du front buffer 0/1.
- `Safe` non bloquant : au plus un `Exec/GetMsg` si message Safe en attente ; pas de `WaitPort`, pas de `ReplyMsg` sur Safe/Disp, aucun effacement de Disp. Aucune écriture tant que Safe n'est pas obtenu.
- RastPort temporaire sur la pile, `InitRastPort`, `SetAPen`, `SetDrMd` JAM1, `WritePixel` uniquement dans les bornes. Traduire le succès OS `WritePixel=0` en succès logique. `WaitBlit` avant de restituer le RastPort. **Aucune allocation persistante Chip/Fast**, aucun swap ou VBL implicite et aucun effet sur palette/Workbench/écran AMOS natif.

## ABI et construction prévues

- Entrée AP20 envisagée **53** (après l'entrée R42 52), **48 commandes / 54 segments** après ajout ; token fonction numérique à **quatre paramètres** de signature `00,0,0,0`.
- Registres d'entrée attendus : `D3=Pen`, les trois arguments AMOS restants `(A3)+` consommés dans l'ordre **Radius, CY, CX** (trois LONG sur A3). Retour `D3` 0/1, `D2=0`, pile et autres registres préservés comme en R42.
- Nouveau builder **déterministe depuis l'archive R42 figée** `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` ; vérifier le SHA256 avant build, la continuité du délimiteur `GetP` et l'identité de tous les segments historiques (sauf délimiteur requis). Ne pas reconstruire depuis un ancien binaire ni toucher au `LAST_GOOD` R42 avant Gate B utilisateur.
- **Gate A** : CPU 68000 simulé / Capstone, pixel à pixel, zéro écriture hors plans, symétrie, rayons 0/1/2 et grands, quatre bords/quatre coins, centres externes, écran entièrement enveloppé mais aucun point visible, coordonnées AMOS LONG extrêmes, pen/depth, états BitMap invalides, Safe/Disp, ABI AP20 et non-régressions, export source strict et CI.
- Après seulement une **Gate A complète PASS** : publier `dist/AMOSPro_AGA.Lib` et archive R43 dédiée, plus **un seul test WinUAE actif** sous `tests/current/` ; mettre à jour les deux README et la documentation dans le même commit. Ne pas modifier `LAST_GOOD`.
- **Gate B** : AMOS interprété via Project -> Merge ASCII, rendu et résultat/fermeture confirmés par l'utilisateur ; promotion et archivage du test exact **uniquement après PASS utilisateur**. Gates C (Compiler) et D (AGA réel) restent indépendantes.

## Décision à obtenir

**Contrat confirmé par l'utilisateur ; Gate A en cours.** Ne publier la bibliothèque R43 qu'après tests CPU et CI PASS. R39 reste reportée ; les études M15bis souris et M16 Fast RAM restent séparées. Dépôt unique `anthea176/AMOSPro-AGA-Extension`, branche **`main` seulement**.
