# M11 — audit source du back buffer et du RastPort (R25 0.9.1)

**Date : 11/11/2026 — lecture du code et des binaires GitHub, sans modification de l'extension.** Cette note n'est **ni** un test WinUAE M11 **ni** une validation d'une nouvelle commande. Base : `main`, R25 0.9.1, **13 408 octets**, SHA256 `4835473771629bea697d64c9213ff1064013597f7dabc519914f4ea013af6da6`.

## 1. Autorité et preuve de conservation binaire

Le fichier [`src/generated/AMOSPro_AGA_R23_NATIVE.s`](../src/generated/AMOSPro_AGA_R23_NATIVE.s) est une **reconstruction de lecture du binaire R23** : il n'est *pas* un source assembleur dont l'assemblage natif a été démontré bit-à-bit. Les builders et les **octets de bibliothèques AP20** priment.

Une comparaison directe des segments AP20, extraits avec la disposition de [`tools/ap20_utils.py`](../tools/ap20_utils.py), entre l'[archive figée R23](../dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib) (13 088 octets, 34 segments) et la [bibliothèque R25](../dist/AMOSPro_AGA.Lib) (13 408 octets, 36 segments) donne :

| Segment AP20 | Fonction | Taille des deux segments | Identité binaire R23/R25 |
|---|---|---:|---|
| 6 | `Aga Screen Open` | 756 octets | **Identique** |
| 8 | `Aga Screen Close` | 478 octets | **Identique** |
| 9 | `Aga Wait Vbl` | 30 octets | **Identique** |
| 10 | `Aga Double Buffer` | 290 octets | **Identique** |
| 11 | `Aga Swap` | 252 octets | **Identique** |
| 12 | `Aga Back Fill` | 158 octets | **Identique** |
| 13 | `Aga Iff Load` | 2 204 octets | **Identique** |
| 19 | `Aga Blit Copy` | 352 octets | **Identique** |
| 20 | `Aga Blit Fill` | 448 octets | **Identique** |
| 21 | `Aga Blit Clear` | 38 octets | **Identique** |

Les segments nouveaux M9/M10 ne changent pas ces routines ; les délimiteurs AP20 ajoutés ailleurs ne sont pas une nouvelle logique d'écran. Les observations ci-dessous concernent **les octets effectivement présents en R25**, via la correspondance R23/R25 vérifiée, et le générateur [R14 Fill](../tools/build_m6_blit_fill_r14.py).

## 2. Chaîne exacte du pointeur arrière

| Accès 68000 / structure | Signification |
|---|---|
| `456(A5)` = `$1C8(A5)` | pointeur vers l'état privé de l'extension, sous le contexte AMOS |
| `State+0` | pointeur `Screen*` Intuition |
| `State+8` | `GfxBase*` pour `graphics.library` |
| `State+12/+16/+28` | largeur, hauteur et profondeur logique |
| `State+32` | pointeur `DBState*` |
| `DBState+0` / `+4` | `ScreenBuffer* SB0` / `ScreenBuffer* SB1` |
| `DBState+8` | indice frontal : `0` ou `1` |
| `ScreenBuffer+0` | `sb_BitMap`, pointeur vers le **BitMap réel** |
| `ScreenBuffer+4` | `sb_DBufInfo` : **ne pas confondre avec le BitMap** |
| `BitMap+0/+2/+5/+8` | `BytesPerRow`, `Rows`, `Depth` et début de la table `Planes[]` |

**Sélection du back buffer déjà utilisée par `Aga Blit Fill` et `Aga Blit Copy` :**

```text
si DBState.frontIndex = 0 : back = DBState.SB1.sb_BitMap
si DBState.frontIndex = 1 : back = DBState.SB0.sb_BitMap
```

Cette sélection est présente dans [`tools/build_m6_blit_fill_r14.py`](../tools/build_m6_blit_fill_r14.py) (commentaire « DB front index (+8) » et branchement `front_zero`) et dans la reconstruction [R23, entrées 10/11/12/19/20](../src/generated/AMOSPro_AGA_R23_NATIVE.s). **Ni `AMOS Screen`, ni `ScOnAd`, ni `Ec_RastPort` n'interviennent dans ce chemin.** Le pointeur de back buffer doit être relu après les swaps, jamais mis en cache par-dessus un `Close`/`Open`.

## 3. Un RastPort temporaire existe déjà en R25

Le segment **12 — `Aga Back Fill`** fournit la preuve de faisabilité la plus directe. Dans le [source reconstruit R23](../src/generated/AMOSPro_AGA_R23_NATIVE.s) et donc dans les octets R25 inchangés, la routine :

1. sélectionne le `ScreenBuffer` inactif, puis son `sb_BitMap` ;
2. alloue **128 octets** de contexte temporaire avec Exec `AllocVec` ;
3. appelle **`graphics.library/InitRastPort` (LVO `-198`)** sur ce contexte ;
4. écrit le pointeur `BitMap` dans **`RastPort+4`** ;
5. appelle **`SetRast` (LVO `-234`)**, puis **`WaitBlit` (LVO `-228`)** ;
6. libère le contexte avec `FreeVec`.

Il est donc **inutile de modifier les écrans AMOS ou le Copper** pour utiliser les primitives `graphics.library` sur le buffer de l'extension. Les docs AmigaOS confirment qu'`InitRastPort` installe les attributs standard et une fonte système, **mais ne renseigne pas le pointeur `BitMap`** : il doit être associé explicitement. Références : [InitRastPort (Autodoc 3.x)](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node02F7.html) · [Graphics Primitives](https://wiki.amigaos.net/wiki/Graphics_Primitives).

Pour du texte, le chemin à étudier est **`InitRastPort → rp.BitMap=backBitMap → SetAPen / SetDrMd(JAM1) → Move → Text → WaitBlit`**. Sur 68000, `graphics.library/Text` est la fonction **LVO `-60`**, avec `A1=RastPort*`, `A0=texte`, `D0.w=longueur`. La coordonnée `y` de `Move` correspond à la **ligne de base** du texte, et non à son coin supérieur. Références : [Graphics Library and Text](https://wiki.amigaos.net/wiki/Graphics_Library_and_Text) · [Autodocs graphics.library](https://developer.amigaos3.net/autodocs/graphics.library/).

L'entrée R25 **13 — `Aga Iff Load`** fournit un autre contrat utile pour la future API : sa chaîne AMOS arrive comme un **pointeur en `D3`**, avec un **WORD de longueur** en tête, suivi immédiatement des caractères. Ceci est explicite dans [`build_m5_generic.py`](../tools/build_m5_generic.py), `read_file`. Ne pas traiter cette chaîne comme un pointeur C NUL-terminé ; vérifier séparément la signature et l'ordre des autres arguments AMOS avant d'écrire un token nouveau.

## 4. Risque confirmé : Safe/Disp après `Aga Swap`

Dans le segment **11 — `Aga Swap`**, un `ChangeScreenBuffer` réussi change `DBState+8` et pose **`DBState+20 = 3`**, indiquant deux notifications en attente :

| Donnée | Usage |
|---|---|
| `DBState+12` | port de réponse **Safe** |
| `DBState+16` | port de réponse **Disp** |
| `DBState+20` bit 0 (`1`) | ancien buffer **pas encore certifié réutilisable en écriture** |
| `DBState+20` bit 1 (`2`) | affichage de la nouvelle image / swap suivant en attente |

`Aga Swap` dépile ces réponses de manière **non bloquante** avec `Exec/GetMsg`, sans `ReplyMsg` supplémentaire, et refuse un nouveau swap tant que des réponses nécessaires manquent. **`Aga Wait Vbl` ne fait que `graphics.library/WaitTOF` (LVO `-270`) : ce n'est pas une notification Safe.** Les fonctions R25 `Aga Blit Fill/Copy/Clear` sélectionnent le BitMap arrière, mais **ne vérifient pas elles-mêmes le bit Safe en attente**. Le test R25 WinUAE passé ne constitue pas une preuve générale d'absence de course Safe dans toutes les cadences de rendu.

C'est le principal verrou pour un nouveau `Aga Text` : **ne pas écrire après un swap dans un BitMap encore marqué non-Safe**. Un appel non bloquant pourrait dépiler la réponse Safe si elle est arrivée, effacer le bit 0 sans `ReplyMsg`, ou retourner « pas prêt » sans dessiner. Il faudrait vérifier cette interaction avec le suivi existant de `Aga Swap`, sans introduire de second consommateur incohérent. Éviter `WaitPort`/attente infinie (contrat [M4b](M4B_RUNTIME_SAFETY.md)). Voir aussi [synchronisation R8](DB_SYNC_R8_TECHNICAL.md) et [Autodoc AllocDBufInfo](https://developer.amigaos3.net/autodocs/graphics.library/AllocDBufInfo.html).

## 5. Contrat envisagé — **aucune API R26 approuvée**

Une première primitive texte pourra être spécifiée **après résolution du Safe**. Interface candidate, **non implémentée** :

```amos
_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)
```

- Texte d'une seule ligne, fonte système d'abord (pas de banque AMCAF requise), `JAM1` et couleur **indexée** 0..`(2^Depth-1)`.
- `_OK=1` uniquement si la préparation et le dessin ont été effectués sans refus ; `0` pour écran/DB absents, chaîne invalide, couleur hors plage, géométrie invalide ou buffer non-Safe. La distinction « pas prêt » / « appel invalide » restera à concevoir.
- **Pas de clipping implicite dans un RastPort nu** : calculer les limites du texte (fonte, `TextLength`/`TextExtent`, baseline et descenders) et rejeter un rendu débordant, plutôt que risquer une écriture hors `BitMap`.
- Limiter explicitement la longueur lue du descripteur AMOS avant le passage `D0.w` à `Text`, vérifier les pointeurs, préserver l'ABI AP20 (A3/SP, D2/D3 et registres non volatils), et appeler `WaitBlit` avant `Aga Swap`.
- Conserver les segments R25 **octet pour octet** ; aucune dépendance à `AMOS Screen` ou au `Window.RPort`. Ne jamais libérer un `ScreenBuffer` ou un `BitMap` appartenant à Intuition.

## 6. Validation nécessaire avant de proposer une bibliothèque

1. **Gate A** : coder une seule nouvelle entrée AP20 depuis l'archive R25 figée, puis vérifier structure HUNK, token/signature, ordre des arguments mixtes et registre `A3`, géométrie, police/chaîne, absence d'allocation perdue, comportements quand Safe/Disp sont différés, cas `Close/Open` et invariance binaire R25.
2. **Gate B** : un unique test AMOS interprété/WinUAE avec `Aga Screen Open`, `Aga Double Buffer`, palette connue (IFF tant qu'aucun setter n'existe), texte **dessiné par l'extension dans le back buffer**, `Aga Swap`, `Aga Wait Vbl` et fermeture propre. Ne pas tester `Text` natif AMOS pour cette compatibilité.
3. **Gates C/D** : AMOS Compiler et Amiga AGA physique séparément. Ne pas extrapoler à une cadence PAL de 50 FPS.

**Conclusion :** le support bas niveau des `RastPort` sur le back buffer est **déjà présent dans R25**. Le nouveau travail n'est pas d'inventer un écran graphique ni un Copper différent, mais de **sécuriser la synchronisation Safe puis d'ajouter une primitive texte dirigée vers le BitMap arrière**. Aucun source runtime, aucune bibliothèque, aucun test courant modifiés par cet audit.
