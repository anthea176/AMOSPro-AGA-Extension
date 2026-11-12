# Benchmark graphique AMOS Pro / AMCAF / extension AGA - 320x256x32

**Etat : programme pret pour essai AMOS interprete / WinUAE ; aucune mesure materielle ou WinUAE n'a encore ete executee.** Pas de modification de la librairie AGA, de ses tests de regression, ni de `LAST_GOOD`.

## Fichier

- `graphics_32c.asc` : programme AMOS Professional **ASCII** unique. Il enchaine des tests sur un ecran natif AMOS (AMOS puis AMCAF), puis des tests sur l'ecran AGA prive de l'extension. Il affiche le resultat des chronometrages apres avoir ferme tous les ecrans.

## Conditions communes

- **320 x 256 pixels, PAL, 32 couleurs indexees = 5 bitplanes.** Toujours la meme couleur **31 (blanc)** sur fond **0 (noir)** ; 5 plans sont reellement ecrits dans le test de cercle AMCAF.
- **AMOS Professional en mode interprete** ; AMCAF **v1.40 ou superieure** chargee (normalement slot 8), extension **AMOSPro_AGA.Lib R43 ou superieure** (R44 v0.11.5 recommandee, slot habituel du projet : 14, s'il est libre).
- Meme configuration WinUAE pendant une execution : CPU, frequence/clock, caches, JIT, Chip/Fast RAM, AGA, PAL. Ne pas comparer un passage interprete avec un autre compile.
- **Trois essais identiques** par operation et par moteur. `Timer` AMOS progresse par pas de 1/50 seconde (**20 ms**). Les nombres affiches sont les **sommes des ticks sur trois essais** : **plus petit = plus rapide**, pour un nombre identique de formes ou de pixels demandes.
- Chaque serie commence avec une operation de chauffe et un nettoyage de l'ecran **hors chronometrage**. Le calcul des coordonnees et l'overhead de boucle restent **dans** le chronometrage : il s'agit d'une mesure **end-to-end depuis AMOS**, pas des seuls cycles du renderer machine.
- Aucun `Wait Vbl`, swap, attente utilisateur, affichage de texte ou ouverture/fermeture d'ecran **dans** les boucles chronometrees. Pour AMCAF, `Blitter Wait` est une barriere de fin prise en compte, afin de ne pas mesurer uniquement l'envoi des operations au Blitter. Le Fill/Clear AGA attend deja le Blitter dans son implementation.
- Les operations concernent un ecran AMOS standard pour AMOS/AMCAF, et **un bitmap prive en back buffer** pour AGA. **Le format est identique, l'architecture memoire et la presentation ne le sont pas.** Ce n'est donc pas une comparaison isolee des seuls algorithmes de tracage.

## Matrice des tests

| Test | AMOS natif | AMCAF | Extension AGA | Charge par essai |
|---|---|---|---|---|
| `PLOT` | `Plot x,y` (`Ink 31` hors mesure) | `Turbo Plot x,y,31` | `_OK=Aga Plot(x,y,31)` | 12 000 points disperses |
| `DRAW` | `Draw x1,y1 To x2,y2` | `Turbo Draw x1,y1 To x2,y2,31` | `_OK=Aga Draw(x1,y1,x2,y2,31)` | 400 longues lignes |
| `BOX` | `Box x1,y1 To x2,y2` | **4 x `Turbo Draw`** pour reproduire le contour | `_OK=Aga Box(x1,y1,x2,y2,31)` | 225 rectangles |
| `CIRCLE` | `Circle cx,cy,r` | **5 x `Bcircle`**, une fois pour chacun des 5 bitplanes | `_OK=Aga Circle(cx,cy,r,31)` | 170 contours de rayons 16..63 |
| `BAR` | `Bar x1,y1 To x2,y2` | **N/A** : pas de primitive AMCAF directement comparable | `_OK=Aga Blit Fill(x,y,width,height,31)` | 100 rectangles 200x136 |
| `CLEAR` | `Cls 0` | **5 x `Blitter Clear 0,plane`** puis `Blitter Wait` | `_OK=Aga Blit Clear(0,0,320,256)` | 80 effacements plein ecran |

**Important :** `Bcircle` agit sur un seul bitplane et n'est **pas** directement equivalent a `Circle`. Les cinq appels AMCAF rendent un contour blanc en index 31 sur un ecran 32 couleurs. Le pixel exact du contour peut legerement differer selon l'algorithme. De meme, quatre `Turbo Draw` reconstituent une `Box` : la mesure correspond au **cout de produire le meme type d'image**, pas a une comparaison une-commande-contre-une-commande. `Fcircle` d'AMCAF est un **cercle plein**, non comparable a un cercle de contour ; il n'est volontairement pas utilise. Aucun `F Plot`, `F Draw` ou `F Circle` de **Turbo Extension 1.9** n'a ete attribue a AMCAF par erreur.

## Execution

1. Sauvegarder la configuration AMOS et les extensions, puis verifier qu'**AMCAF** et **AMOSPro_AGA.Lib** sont installees dans des **slots differents**. Ne pas changer le slot existant de la bibliotheque AGA (programmes AMOS deja tokenises).
2. Copier `graphics_32c.asc` sur un volume visible dans WinUAE ou sur Amiga AGA.
3. Dans AMOS Professional : **nouveau programme vide -> Project -> Merge ASCII**. Ne pas utiliser `Load` pour importer directement le `.asc`.
4. Executer en **interprete**. Le programme montre brievement trois dessins de controle, puis revient a l'ecran AMOS et imprime les temps de chaque test. Le chiffre `M=-1` de `BAR` signifie **non disponible**, pas un temps negatif.
5. Photographier/copier les chiffres de la sortie, ainsi que les parametres WinUAE (CPU, JIT/cycle-exact, Chip/Fast RAM). On pourra ensuite calculer les rapports de vitesse et tracer un graphique. Si les valeurs d'un test sont `0` ou proches de zero, augmenter uniquement son nombre d'iterations en debut de fichier et refaire une passe complete sur le meme profil.

**Controles de bon fonctionnement :** `AGA ERR 0` et `BENCH FINISHED - CLOSE RETURNED`. Les dessins doivent montrer rectangle, cercle, diagonale et point central. La petite barre ne figure que dans les dessins AMOS natif et AGA (AMCAF BAR = N/A).

## Limites et pistes de validation

- Aucune **valeur de performance** n'est fournie avant execution sur WinUAE / Amiga reel. Le **statut d'essai runtime est PENDING**, pas PASS.
- `Timer` ne permet pas une precision fine sur une operation unique : cette recette cumule des centaines ou milliers d'operations pour limiter la quantification a 20 ms. Des ecarts de quelques ticks sont insuffisants pour conclure.
- L'ordre est AMOS -> AMCAF -> AGA. Pour une etude rigoureuse, refaire plusieurs executions, inverser l'ordre via un second programme ou verifier les effets de chauffe/cache, et comparer la **mediane**.
- La sortie affichant seulement des ticks, les traitements non comparables **ne sont pas convertis en ratios trompeurs**.
- Ne pas extrapoler les performances de ces traces sur un ecran classique 5 plans a des images IFF, au rendu de sprites transparents, au code **compile**, ni a l'Amiga reel.
- Ne pas confondre la fonction **`Aga Detect`** exportee par AMCAF avec celle de l'extension : ce benchmark evite volontairement ce nom potentiellement homonyme et teste directement `Aga Screen Open`.

## References

- Manuel AMOS Professional, chapitre Graphic : https://amospromanual.dev/06-04-graphics.html
- Manuel AMCAF v1.40 (Chris Hodges), notamment `Turbo Plot`, `Turbo Draw`, `Bcircle`, `Blitter Clear`, `Blitter Wait` : https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMCAFguide/index.html
- Contrats de l'extension : `docs/M15_PLOT_R40.md`, `docs/M15_DRAW_R41.md`, `docs/M15_BOX_R42.md`, `docs/M15_CIRCLE_R43.md`, `docs/M6_BLITTER_R14.md`, `docs/M6_BLITTER_R15.md` du depot.
