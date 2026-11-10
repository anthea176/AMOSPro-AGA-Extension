# M9 — R24 0.9.0 : première primitive Hotspot Hit

## Objectif

**R24 0.9.0 candidate publiée sur `main` après Gate A CPU/CI PASS** ([402 scénarios 68000, CI complète verte](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42908096685)). Gate B WinUAE NON TESTÉE. R23 0.8.7 reste l'archive WinUAE validée de référence.

Le contrat M9 est issu de [`INTERACTIONS_COLLISIONS.md`](INTERACTIONS_COLLISIONS.md) et de la [roadmap](ROADMAP.md) : les rectangles logiques, les bornes finales exclusives et les zones recouvrantes doivent être déterministes. Un registre interne de zones est **volontairement reporté** : aucune preuve de besoin ne justifie encore de modifier l'état d'entrée R23.

## API R24 proposée

```amos
_HIT=Aga Hotspot Hit(_PX,_PY,_X,_Y,_W,_H)
```

Fonction entière **à six paramètres**, retournant :
- **1** : `px,py` appartient au rectangle `(x,y,w,h)`.
- **0** : en dehors, point négatif, largeur/hauteur non strictement positives.
- Rectangles à bords `x <= px < x+w` et `y <= py < y+h`, **fin exclusive**.
- Les origines `x,y` **négatives sont autorisées** (zone partiellement en dehors de l'écran). `px,py` négatifs, y compris `-1` de `Aga Mouse X/Y`, donnent toujours 0.
- Pas de clamp implicite ; ce noyau travaille en **arithmétique entière signée 32 bits**, sans dépasser les bornes par l'addition `x+w` ou `y+h`. Un `SUB` débordant est rejeté.

Le jeu choisit les IDs et la priorité. Exemple avec trois rectangles, le **dernier déclarant gagnant** en cas de recouvrement :

```amos
_ID=0
If Aga Hotspot Hit(_PX,_PY,20,20,150,120)=1 Then _ID=10
If Aga Hotspot Hit(_PX,_PY,100,70,160,110)=1 Then _ID=20
If Aga Hotspot Hit(_PX,_PY,275,15,25,25)=1 Then _ID=30
```

À l'interpréteur AMOS, si les appels de fonctions doivent être affectés avant les conditions, employer temporairement `_H=Aga Hotspot Hit(...)` puis `If _H=1` dans le programme de test.

## ABI et isolement

- Segment AP20 **34**, après le dispatcher R23 (segment 33). Ajout d'un seul token **`aga hotspot hit`**, signature `00,0,0,0,0,0`. Total **29 commandes nommées**, contre 28 en R23.
- `D3=h`, `(A3)+=w,y,x,py,px` : exactement **20 octets** consommés sur A3.
- Résultat entier `D3=0/1`, `D2=0`, registres non-volatils et pile préservés.
- Le dernier segment R23 contient 144 octets de données privées. Le délimiteur `GetP` est ajouté **après** ces 144 octets : ni adresse ni contenu de l'état R23 ne changent.
- Aucun appel AmigaOS, `WaitPort`, allocation, événement souris consommé, ou effet de bord sur la fenêtre. Appel possible sans écran ouvert.
- Les 34 segments R23 sont identiques, **sauf l'ajout final des quatre octets `GetP` au segment 33**. Pas de déplacement dans les routines R23.

## Limites explicites

Ce premier noyau ne déclare pas de zones actives, ne stocke **aucun ID** et n'attache pas les coordonnées à l'instant précis où `IDCMP_MOUSEBUTTONS` reçoit l'appui. Une souris déplacée entre le clic et `Aga Mouse X/Y` ne peut donc pas être attribuée à sa position historique exacte avec ce seul appel. `drag`, activation/désactivation, priorité native et registre de zones sont des étapes ultérieures si nécessaires.

Un simple ordre d'appels AMOS permet dès maintenant de tester le survol et de donner la priorité au rectangle supérieur, sans état partagé. La fusion des clics successifs du même bouton dans R23 reste inchangée.

## Gates

- **Préflight CPU validé (402 scénarios) :** émetteur [`m9_hotspot_r24_emit.py`](../tools/m9_hotspot_r24_emit.py), builder reproductible [`build_m9_hotspot_hit_r24.py`](../tools/build_m9_hotspot_hit_r24.py), [test 68000 natif](../tools/test_m9_hotspot_hit_r24.py), vérification HUNK/AP20 et invariant des segments R23.
- **Gate A PASS :** 402 scénarios 68000 (géométrie 32 bits, bords, dimensions, recouvrements, A3/D2/SP), [CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42908096685) ; `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib` identiques, **13 228 octets**, SHA256 `cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671`.
- **Gate B NON TESTÉE :** [`tests/current/M9_R24_HOTSPOT_HIT_01.asc`](../tests/current/M9_R24_HOTSPOT_HIT_01.asc), unique programme AMOS courant. Mire originale 320×256×8, trois rectangles colorés dont A/B superposés. Clic **gauche** dans l'intersection autour de **(130,100)** → ID **20** ; clic **droit** hors zone autour de **(300,220)** → hors zone `1`. Teste aussi les bornes exclusives, dimensions nulles, origines négatives, fermeture et réouverture. Temps maximal environ 18 secondes (900 VBL), sortie normale et `RESULT=1` attendus. Pour Ctrl+C et test de focus, R23 avait été validée sur son périmètre ; la présente R24 ne revendique pas leur revalidation.
- **Gates C/D :** AMOS Compiler et vrai Amiga AGA non testés.

## Protections

Ne pas écraser `dist/AMOSPro_AGA_LAST_GOOD.Lib` (R10), l'archive R23 WinUAE PASS, les archives M8/M7/M6, les illustrations IFF, ni les exemples/documentations bilingues du dépôt. Travailler sur `main` seulement ; vérifier le HEAD avant commit. Ne pas mélanger ce noyau M9 avec M10 collisions.
