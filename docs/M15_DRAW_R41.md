# M15/R41 v0.11.2 — Aga Draw : Gate A PASS, Gate B WinUAE à tester

**Candidate v0.11.2 publiée :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) = [archive R41](../dist/experimental/AMOSPro_AGA_M15_v0.11.2_DRAW_R41.Lib), **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. **46 commandes AP20**. `LAST_GOOD` = **R40**, [fichier](../dist/AMOSPro_AGA_LAST_GOOD.Lib) et [archive](../dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib) strictement inchangés. **Gate A native 68000 CPU/CI PASS, 325 cas + export strict** ; [CI intégrité](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457) PASS. [`tests/current/M15_R41_DRAW_01.asc`](../tests/current/M15_R41_DRAW_01.asc) est **le seul test actif** pour Gate B utilisateur. La nouvelle candidate n'a pas encore été exécutée sous AMOS/WinUAE ; Gates C Compiler/D Amiga physique non testées.

**R41 Gate A CPU/CI PASS (12/11/2026) :** **325 scénarios CPU 68000**, audit des 46 jetons AP20/52 segments, clipping par Bresenham en dehors des bords, accès direct `Move/Draw` uniquement dans les bornes, structure bitmap, état `Safe/Disp`, intégrité des anciens segments, pile et registres ; export natif 68000 strict PASS et [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43193933457). **Gate B AMOS/WinUAE non testée**, R40 `LAST_GOOD` inchangée. Binaire déterministe R41 généré en mémoire : **24 816 octets**, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`. Publication de candidate en préparation, aucun `.Lib` R41 encore dans `dist/`.

**Décision utilisateur du 12 novembre 2026 :** développer **une seule nouvelle commande**, `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)`, après la validation de R40. **R41 candidate avec Gate A CPU/CI PASS (325 scénarios), Gate B WinUAE NON TESTÉE.** La bibliothèque `R40 v0.11.1` (**45 commandes AP20**) reste `LAST_GOOD` et son archive immuable.

## Contrat public de R41

```amos
_OK=Aga Draw(0,0,319,255,1)
```

- Les quatre coordonnées `X1,Y1,X2,Y2` sont signées en **16 bits** (`-32768..32767`) car `graphics.library/Move` et `Draw` consomment des `SHORT`. AMOS transmet des `LONG` : les valeurs hors de cet intervalle sont **refusées**, sans troncature silencieuse et sans dessin.
- `Pen` est un **index de couleur** de `0` à `2^Depth-1` (1..8 bitplanes). Valeurs négatives et trop grandes : retour `0`, aucun dessin.
- `_OK=1` si le segment a produit au moins un pixel dans le back buffer. `_OK=0` si les paramètres / la structure d'écran sont invalides, si le back buffer n'est pas `Safe`, ou si **aucun pixel visible n'est dessiné**. Une erreur après des écritures partielles n'est **pas atomique** : ne jamais déduire de `0` que toutes les étapes ont été annulées.
- Les extrémités **sont incluses**. Un segment réduit à un seul point valide dessine ce pixel. Les coordonnées négatives ou au-delà de Width/Height sont **autorisées et clippées** si elles restent dans l'intervalle 16 bits. Les segments entièrement hors écran sont rejetés ou parcourus sans écrire de bitplanes.
- La cible est **le back buffer AGA privé uniquement**, jamais l'écran AMOS historique ni le front buffer. `Aga Swap` et `Aga Wait Vbl` restent explicites. Épaisseur fixe 1 px, mode de copie normal (JAM1), pas de XOR, motif de ligne personnalisé, allocation persistante, format de bank ou RGB24.

## Algorithme et garantie de sécurité

R41 reprend les vérifications structurelles de R40 **avant toute écriture** : `State`, écran, `GfxBase`, `DBState`, largeur/hauteur logiques strictes, `BitMap.BytesPerRow`, `Rows`, profondeur identique, pointeurs des bitplanes, index de buffer avant/arrière, et message `Safe` non bloquant via `GetMsg(SafePort)`. La notification `Disp` est conservée ; aucun `WaitPort` ni `ReplyMsg`.

Deux chemins, sans dessin hors limites :

1. **Toutes les coordonnées dans les limites** : `InitRastPort` sur pile, `rp->BitMap=back`, `SetAPen`, `SetDrMd(JAM1)`, puis `Move(x1,y1)` et `Draw(x2,y2)`. Aucun `Draw` n'est appelé avec des extrémités extérieures. Point unique par `WritePixel`.
2. **Au moins une extrémité extérieure** : rejet trivial si les deux points sont du même côté d'une frontière ; sinon tracé de **Bresenham entier**, avec vérification de `0 <= x < Width` et `0 <= y < Height` **avant chaque `WritePixel`**. Les deltas / l'erreur emploient des **entiers 32 bits** afin de traiter `-32768..32767` sans dépassement 16 bits, avec un maximum théorique de **65 536 pas par appel**. Le découpage garantit la conservation de la phase Bresenham d'origine, y compris pour les droites partiellement visibles. Une ligne très longue hors écran peut être plus lente qu'une ligne entièrement visible.

**Pourquoi pas un `Draw` direct ?** Les docs AmigaOS avertissent qu'un `Draw` effectué hors du BitMap avec un `RastPort` sans Layer peut corrompre la mémoire. Le test CPU vérifie qu'aucun appel système de dessin n'est fait avec des coordonnées hors des limites, et que les pixels non concernés restent intacts.

Sources : [AmigaOS graphics primitives](https://wiki.amigaos.net/wiki/Graphics_Primitives) · [graphics.library/Draw](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0436.html) · [graphics.library/Move](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0301.html).

## ABI, garanties de version, Gates

- `R41` : jeton AP20 **51** et signature `00,0,0,0,0`. Appel AMOS : `D3=Pen`, `(A3)+=Y2,X2,Y1,X1`, retour `D3=0/1`, `D2=0`, `A3` avance de **16 octets**, tous les autres registres préservés comme R40.
- Émetteur [`tools/m15_draw_r41_emit.py`](../tools/m15_draw_r41_emit.py), builder [`tools/build_m15_draw_r41.py`](../tools/build_m15_draw_r41.py) et vérification 68000 [`tools/test_m15_draw_r41.py`](../tools/test_m15_draw_r41.py).
- Base de construction **seulement** : archive WinUAE-PASS `dist/experimental/AMOSPro_AGA_M15_v0.11.1_PLOT_R40.Lib`, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`. **Les 50 premières entrées R40 restent identiques** ; seul le dernier délimiteur `GetP` est ajouté à l'entrée Plot, suivi de la nouvelle entrée Draw. R40 `LAST_GOOD` inchangée.
- **Gate A** : CPU 68000 Unicorn/Capstone, cas 8 octants, négatifs, traversée des 4 bords, segments 100 % invisibles, gestion `Safe` et `Disp`, tous les plans, intégrité registre/pile, reconstruction AP20, export source natif strict, régressions antérieures et intégrité. Le succès CPU **ne prouve pas** le succès WinUAE.
- **Gate B** : après Gate A PASS seulement, publier `dist/AMOSPro_AGA.Lib` et son archive **R41 candidate**, un test unique sous `tests/current/`, charger via **Project → Merge ASCII** sous AMOS interprété. Comparer rendu visuel et résultats, y compris deux droites traversantes et des segments complètement hors écran. **Ne promouvoir dans `LAST_GOOD` qu'après confirmation explicite de l'utilisateur**.
- **Gates C/D** : AMOS Compiler et Amiga AGA réel non testés.

R42 `Aga Box` et R43 `Aga Circle` ne sont pas engagées ; R39 bitmap 8×8 reste reportée. Tout développement et toute modification se limitent à `anthea176/AMOSPro-AGA-Extension`, branche `main`, sans création de branche.
