# Second run — benchmark graphique 320x256x32 (V2)

**Statut : source preparee, pre-verification de syntaxe PASS, execution AMOS interprete / WinUAE EN ATTENTE.** Le premier programme reste intact dans `graphics_32c.asc`.

## Fichier a utiliser

[`graphics_32c_v2.asc`](graphics_32c_v2.asc)

Ouvrir un programme AMOS Professional **vide** et importer ce seul fichier via **Project -> Merge ASCII**. Ne pas utiliser l'instruction de chargement de programme AMOS pour un source `.asc`.

Prerequis inchanges : **AMOS Professional + AMCAF v1.40+ + notre extension AGA R44 v0.11.5**, deja en place lors du premier essai. **Ne pas modifier les extensions ni leurs slots.** Ce second programme ne requiert aucun IFF, ABK, fichier externe ou changement de `.Lib`.

## Objectif

La premiere execution en 320x256x32 PAL (5 bitplanes) a donne des mesures `CIRCLE` de 0/1/0 ticks cumules et des temps `PLOT` de seulement 3-6 ticks. La resolution de `Timer` (20 ms en PAL) est insuffisante pour une comparaison fiable de ces deux cas.

La **V2** :
- augmente `PLOT` de 12 000 a **120 000** pixels par passage ;
- augmente `CIRCLE` de 170 a **8 000** cercles par passage ;
- conserve les charges `DRAW`, `BOX`, `BAR` et `CLEAR` de V1 pour verifier la reproductibilite ;
- conserve les memes tracés, coordonnees, 32 couleurs / 5 bitplanes, index blanc 31 ;
- affiche **les trois temps individuels** plutot qu'un seul total sur trois passages ;
- place `Blitter Wait` **hors mesure**, apres la grande `Bar` preparatoire des essais `CLEAR` AMOS/AMCAF, pour ne pas prendre en compte des travaux restants du setup.

### Tableau des charges

| Operation | AMOS | AMCAF | AGA | Appels/passages |
|---|---|---|---|---:|
| Plot | `Plot` | `Turbo Plot` | `Aga Plot` | 120 000 |
| Draw | `Draw` | `Turbo Draw` | `Aga Draw` | 400 |
| Box | `Box` | 4 x `Turbo Draw` | `Aga Box` | 225 |
| Circle | `Circle` | 5 x `Bcircle` | `Aga Circle` | 8 000 |
| Bar | `Bar` | N/A | `Aga Blit Fill` | 100 |
| Clear | `Cls 0` | 5 x `Blitter Clear` + `Blitter Wait` | `Aga Blit Clear` | 80 |

Le programme execute **3 passages pour chaque moteur** et affiche une ligne par moteur et operation, avec les ticks des passages 1, 2, 3. Par exemple, `PLOT 120K A 52 54 51` signifie trois observations de 52, 54 et 51 ticks pour AMOS. **Un tick = 20 ms**. Comparer les **medians** pour eviter d'etre trompe par une mesure atypique.

## Ce qui est comparable — et ce qui ne l'est pas

Le mode 320x256x32 et les pixels a tracer sont identiques. Mais AMOS/AMCAF dessinent sur un ecran AMOS, tandis que l'extension AGA dessine sur un **back buffer prive**. C'est une comparaison du temps de commande observe en AMOS, **pas un comparatif des primitives machine a conditions parfaitement identiques**.

Un rectangle AMCAF exige ici **quatre `Turbo Draw`**. `Bcircle` ne dessine qu'un bitplane : il en faut **cinq** pour le contour d'index 31. Les contours de cercles peuvent varier selon le moteur. Pas d'equivalent direct AMCAF retenu pour `BAR` ; le resultat est `N/A`.

`Timer` inclut la boucle AMOS, la preparation des coordonnees et l'appel. Le programme laisse les ouvertures d'ecran, clears preparatoires, `Aga Swap`, `Wait Vbl` et impression des resultats hors des chronos. La synchronization de `Blitter Wait` de fin de serie AMCAF est incluse.

## Resultats attendus

La sortie doit finir par :

```
AGA ERR 0
CIRCLE M = 5 BCIRCLE / RING
V2 FINISHED - CLOSE RETURNED
```

Si `AGA ERR` differe de zero, les mesures AGA ne peuvent pas etre considerees comme fiables.

**Envoyer une capture de la sortie finale** avec les trois nombres de chaque ligne, ainsi que le profil CPU WinUAE (68020/030/040/060, cycle exact/JIT si connu). Les gains seront estimes a partir des medians, sans modifier l'extension avant un diagnostic.

**Validation :** preverification statique de structure et syntaxe texte effectuee. **Execution sous WinUAE, Compiler AMOS et Amiga AGA reel non testees pour V2.**

Documentation precedente : [V1 et protocole original](README.md) ; [manuel AMCAF v1.40](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMCAFguide/manual/graphicblitter.html).
