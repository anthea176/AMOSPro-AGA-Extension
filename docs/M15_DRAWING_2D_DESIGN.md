# M15 — Primitives de dessin 2D sur écran AGA (étude et propositions)

**État au 12/11/2026 : chantier M15 sélectionné par l'utilisateur.** La piste M14/R39 `Change Print Font` 8×8 est **écartée / reportée**, **aucune commande R39 n'est implémentée**. Le présent document **ne constitue pas une autorisation de coder d'un seul coup quatre fonctions** : les noms, signatures et comportements ci-dessous sont des **propositions**, à confirmer **une commande à la fois** avant chaque candidat. Pas de `M15` dans le binaire à cette date.

**Socle immuable :** `R38 v0.11.0`, **44 commandes AP20**, `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive R38 (23 380 octets ; SHA256 `09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366`). Gates A CPU/CI et B AMOS interprété/WinUAE **PASS**, y compris stress de 500 changements de fontes sans perte Chip RAM observée. Gate C (Compiler) et D (Amiga AGA réel) non testées. La dernière CI du dépôt `main` était PASS avant l'ouverture de cette étude. Tous les développements restent strictement dans `anthea176/AMOSPro-AGA-Extension`, branche **`main`**, sans création de branche.

## 1. Ce qui est vérifié, pas supposé

### Code du dépôt actuel

- `tools/m11_text_r26_emit.py` : `Aga Text` utilise **un RastPort temporaire sur la pile**, créé par `graphics.library/InitRastPort(-198)`, dont `rp->BitMap` pointe explicitement vers **le back buffer AGA Intuition privé** (`DBState.ScreenBuffer.sb_BitMap`). Les écrans AMOS classiques restent indépendants.
- `tools/m12_blit_safe_r27_emit.py` : le bit 0 de `DBState+20` indique qu'une réponse **Safe** est en attente. Un seul `Exec/GetMsg(-372)` non bloquant sur le `SafePort`; sinon **retour 0 sans dessin**. Ne jamais confondre `Safe` avec `Disp`, ne jamais répondre à ce message avec `ReplyMsg`, ne pas introduire de `WaitPort` bloquant.
- `Aga Text`, `Aga Blit Fill` et `Aga Blit Copy` valident **l'écran, le GfxBase, le DBState, les dimensions logiques, les dimensions physiques du BitMap, la profondeur et les pointeurs des plans**. Ces contrôles préalables doivent être repris pour chaque primitive.
- Le rendu M15 doit concerner **le buffer arrière non affiché**, puis `Aga Swap` est appelé séparément par AMOS. Aucun swap ni VBL implicite.
- Les index de couleur sont ceux des **bitplanes**, de `0` à `2^Depth-1` (1 à 8 plans). Un index n'est **pas** une couleur RGB24 ; la palette actuelle détermine son apparence.

### Commandes originales / API système documentées

- **AMOS Professional :** `Plot` (pixel), `Draw` (segment), `Box x1,y1 To x2,y2` (rectangle de contour) et `Circle x,y,radius` (contour de cercle). Les paramètres de `Box` sont les deux coins ; ceux de `Circle` sont centre et rayon. Les styles `Ink`, `Set Line` et le curseur graphique AMOS **ne doivent pas être importés tacitement** dans l'API indépendante.
- **AMCAF V1.40 :** `Turbo Draw x1,y1 To x2,y2,colour[,bitplane]` indique **explicitement** que ses lignes hors écran sont automatiquement clippées ; cela ne prouve pas que `graphics.library/Draw` fasse pareil. AMCAF documente également `Bcircle` pour dessiner un contour d'un pixel destiné au Blitter. Ne pas assimiler sans preuve `F Draw` / `F Plot` d'une autre extension à `Turbo Draw`.
- **graphics.library :** `InitRastPort(-198)` prépare le RastPort mais **ne définit pas le BitMap** ; `SetAPen(-342)` choisit l'index de couleur ; `SetDrMd(-354)` permet le mode de rendu ; `WritePixel(-324)` écrit un pixel et renvoie **0 si succès, -1 si hors portée** ; `Move(-240)` positionne le curseur, `Draw(-246)` trace depuis ce curseur ; `DrawEllipse(-180)` dessine une ellipse.
- **Avertissement de sécurité confirmé :** `graphics.library/Draw` et `DrawEllipse` sur un **RastPort non lié à un Layer** ne possèdent pas le clipping garanti pour les cas hors limites ; une géométrie sortant du BitMap peut corrompre la mémoire. Le code M15 doit **clipper ou refuser avant tout appel dangereux**. `DrawEllipse` indique explicitement ce défaut dans l'autodoc.

Références techniques : [AMOS Pro Graphics](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/6/629.html), [AMCAF Turbo Draw](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMCAFguide/manual/graphicblitter.html), [AmigaOS Graphics Primitives](https://wiki.amigaos.net/wiki/Graphics_Primitives), [Autodocs graphics.library](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node05A6.html), [LVO graphiques](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0550.html).

## 2. Découpage proposé — une seule commande à la fois

| Sous-jalon proposé | Interface AMOS proposée | Périmètre minimal | Difficulté |
|---|---|---|---|
| **R40 — Plot** | `_OK=Aga Plot(X,Y,Pen)` | 1 pixel **strictement dans les bornes** | Faible |
| **R41 — Draw** | `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)` | Segment d'un pixel d'épaisseur, **clippé** aux bords du back buffer | Moyenne à forte |
| **R42 — Box** | `_OK=Aga Box(X1,Y1,X2,Y2,Pen)` | Contour, coins/segments définis **par leurs coordonnées**, non largeur/hauteur, clipping | Moyenne |
| **R43 — Circle** | `_OK=Aga Circle(CX,CY,Radius,Pen)` | Contour d'un pixel d'épaisseur, clipping sûr, pas de remplissage | Forte |

La numérotation R40–R43 est **provisoire**, car R39 est reportée et non publiée ; elle ne crée aucun jeton dans le binaire. Aucun `Aga Bar`, `Aga Ellipse`, `Aga Polyline`, `Aga F Plot`, `Aga Print Font` ni changement d'`Aga Text` n'est autorisé par cette étude.

### Proposition contractuelle prioritaire — R40 `Aga Plot`

```amos
_OK=Aga Plot(319,255,1)
```

- `X,Y,Pen` sont trois arguments entiers sur l'interface AP20 ; résultat entier AMOS **1 si l'écriture du pixel réussit**, sinon **0**. Le succès n'implique pas que le pixel ait changé de valeur (il peut déjà posséder cette couleur).
- `0 <= X < Width`, `0 <= Y < Height`, `0 <= Pen < (1 << Depth)`. Valeurs négatives et hors plage rejetées **sans modifier le BitMap**. Les bornes sont **inclusives sur les pixels valides**, avec `(Width-1,Height-1)` accepté et `(Width,Height)` refusé.
- Écran AGA privé ouvert, GfxBase valide, double-buffering actif, profondeur 1..8, `BitMap.BytesPerRow*8 >= Width`, `Rows >= Height`, profondeur identique et **chaque pointeur Planes[] utilisable** : toutes les conditions doivent être vérifiées avant de dessiner.
- Si Safe est en attente, un seul `GetMsg(SafePort)` sans attente bloquante ; **pas Safe -> retour 0**. Le bit `Disp` n'est jamais effacé. Ne pas écrire sur le front buffer.
- RastPort temporaire sur pile, `InitRastPort`, `rp->BitMap=back`, `SetAPen(Pen)`, `SetDrMd` en mode de copie normal, `WritePixel(X,Y)`; traduire **`WritePixel=0` vers `_OK=1`**. Ne pas confondre le retour brut d'AmigaOS avec le résultat AMOS !
- Aucun `Wait Vbl`, `Aga Swap`, changement de palette, accès écran AMOS, allocation heap ou commande AMCAF. Pas de nouveau format de banque. Convention de synchrone / attente blitter à vérifier dans le code et les tests CPU avant le candidat.
- ABI à établir comme les fonctions existantes : consommation exacte des arguments AP20, sauvegarde des registres attendus, pile équilibrée, `D3` pour le résultat et `D2=0`, séparation `GetP` valide, **source 68000 strict**. L'index d'entrée sera déterminé par l'audit du R38 figé, pas deviné.
- Toutes les erreurs de validation doivent laisser les buffers intacts. Un échec système après le début du rendu **ne doit pas être présenté comme atomique**.

### Études complémentaires avant R41/R42/R43

- **R41 — clipping de ligne :** ne jamais envoyer de coordonnées hors plage à un `Move/Draw` non-layered. Comparer le clipping logiciel des extrémités (arrondi et inclusion du dernier pixel) avec un tracé pixel par pixel. Vérifier horizontal, vertical, diagonales sur 8 octants, traversée de chaque bord et segments complètement invisibles ; aucune hypothèse implicite sur le pixel de départ.
- **R42 — Box :** préciser avant codage le contrat des coins inversés, rectangles de largeur/hauteur 1, corners identiques, le clipping partiel, les coins dessinés une ou plusieurs fois, et l'**inclusivité** des deux coordonnées finales. Ne pas recycler les conventions `Aga Blit Fill(x,y,width,height,pen)`.
- **R43 — Circle :** `graphics.library/DrawEllipse` convient seulement si **le cercle entier est vérifié dans les bornes**. Pour un cercle partiellement extérieur, choisir un algorithme logiciel avec clipping **avant** tout appel ; ne pas appeler `DrawEllipse` hors limites. Définir rayon 0, rayon négatif, dépassements et entiers signés sans overflow. Pas de disque rempli.
- Les styles AMOS `Ink` / `Set Line` / `Gr Writing`, tracés XOR, épaisseur variable et masques sélectifs de bitplanes **ne font pas partie de ces contrats initiaux** ; les ajouts éventuels exigent d'autres décisions explicites.

## 3. Recette et critères de promotion

**Gate A (ordinateur / CPU simulé) — avant candidate publique :**

1. Bâtir le nouveau segment AP20 depuis **l'archive R38 immuable**, sans modifier les segments historiques (hors délimiteur `GetP` nécessaire). La R38 `LAST_GOOD` reste inchangée.
2. Tester l'ABI 68000 avec de vrais appels OS simulés : `InitRastPort`, `SetAPen`, `SetDrMd`, `WritePixel`, `GetMsg`; valider **l'ordre** des appels, le retour `WritePixel=0` -> 1, `-1` -> 0, les registres et la pile.
3. Géométrie `(0,0)`, `(319,255)`, bord droit/inférieur hors champ, valeurs négatives, profondeur 1/2/4/8, index `Pen` maximal et invalide, pointeurs `BitMap`/plans et dimensions physiques cassés, mauvais état DB/screen.
4. Safe absent / présent, notification en attente non reçue, présence du bit `Disp` ; vérifier **zéro dessin** avant Safe et zéro attente bloquante.
5. Audit AP20, désassemblage strict 68000, reproductibilité binaire ; régressions R38 (BankFont, stress archivé), R37, R27, R26 et autres vérifications CI. **Gate A ne démontre jamais la réussite sous WinUAE**.

**Gate B (AMOS interprété / WinUAE) — après Gate A PASS :** un seul fichier de test actif dans `tests/current/`, importé par `Project -> Merge ASCII`. Dessiner des pixels de plusieurs index aux quatre coins, un pixel central, et tester les valeurs invalides sans corruption ; double-buffer et `Aga Swap` ; vérifier le rendu visuel et les résultats AMOS, puis fermeture et retour normal. Répéter les swaps pour éprouver `Safe`. Archiver **le test exact** dans `tests/passed/` et promouvoir `dist/AMOSPro_AGA_LAST_GOOD.Lib` **uniquement après confirmation explicite de réussite par l'utilisateur**.

**Gates C et D :** compilation AMOS, puis Amiga AGA physique, chacune indépendante. Ne jamais inventer des résultats.

## 4. État de décision

- **Décidé :** M15 est la prochaine priorité, M14/R39 est reportée ; l'ordre de discussion est Plot, Draw, Box, Circle ; dépôt unique, branche `main`.
- **Non encore décidé :** signature définitive R40, sémantique précise du résultat et des refus, choix exact des algorithmes R41–R43. Les propositions ci-dessus **ne sont pas encore des commandes disponibles**.
- **Interdit pour l'instant :** changer le binaire R38, `LAST_GOOD`, archiver à tort un test M15 non exécuté, annoncer Gate A/B PASS, travailler sur d'autres branches ou dépôts.
