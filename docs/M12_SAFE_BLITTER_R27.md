# M12 — R27 0.9.3 : sécurisation Safe des Blitters AGA

**11/11/2026 — R27 0.9.3 candidate WinUAE, Gate A CPU/CI 68000 PASS (403 scénarios), Gate B AMOS/WinUAE NON TESTÉE.** [CI R27 complète 28 étapes PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997093650). [Binaire candidat courant](../dist/AMOSPro_AGA.Lib) = [archive R27](../dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib), **14 252 octets**, SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe`. Les archives R26/R25/R24 et `LAST_GOOD` R10 sont conservées à l'identique. **R26 0.9.2 reste la dernière version WinUAE-PASS**, sur ses deux scénarios. Aucune autre branche.

## Correction obligatoire des liens R23

**Incident de prévalidation :** une première candidate R27 (commit `e1aa39f`) modifiait uniquement 19/20/21. Le strict exporter 68000 a révélé des appels BSR.W non relocalisés vers le dispatcher clavier/souris R23, ainsi qu'une ancre d'état obsolète. Ce binaire défectueux a été **retiré avant tout essai WinUAE**, et remplacé par le binaire corrigé SHA256 `64647f508e5681a09a8c8b51ec9ba8405caf3a52972b5f50034da40a684f0fbe` ci-dessus (nouveau Gate A CPU/CI **403 cas PASS** et exporter strict PASS).

**Neuf segments ont finalement changé :** `6` écran/ancre d'état ; `17/18` clavier/Wait Key vers `key_next` ; `19/20/21` Blitters Safe ; `31/32` Mouse Pressed/Released et branchement `pump` ; `33` dispatcher/FIFO et stockage des événements. Les **31 commandes AP20**, **37 segments** et toutes les autres entrées, dont `Aga Text`, demeurent strictement identiques à R26. La relocalisation est calculée depuis les étiquettes R23 d'origine et validée par tests 68000 clavier/souris et export source strict. **R26 reste figée dans son archive WinUAE-PASS**.

## Problème vérifié dans R26

Après un `Aga Swap` réussi, le buffer anciennement affiché peut rester indisponible en écriture tant que la réponse **Safe** n'est pas reçue. L'ancienne fonction `Aga Text` de R26 gère elle-même cette notification, mais **`Aga Blit Copy`**, **`Aga Blit Fill`** et le wrapper **`Aga Blit Clear`** ne la gèrent pas directement. Le test [R26 à 40 swaps](../tests/passed/M11_R26_SAFE_SWAP_02.asc) employait donc un appel `Aga Text` servant de **sonde** avant chaque Blitter.

Ce protocole a passé les 40 images avec `DONE 40 PROBEOK 40`, `PROBE0 39 SWAP0 0`, erreurs nulles et `RESULT 1`. Ces 39 refus ne démontrent cependant pas que chaque retour `0` provenait exclusivement de Safe ; ce point reste une limite observée.

## Objectif R27 — aucune nouvelle commande AMOS

**Les signatures et les résultats restent identiques :**

```amos
_OK=Aga Blit Copy(sx,sy,dx,dy,w,h)
_OK=Aga Blit Fill(x,y,w,h,pen)
_OK=Aga Blit Clear(x,y,w,h)
```

La routine centrale `_emit_safe_guard`, insérée dans les émetteurs des fonctions **Copy (segment AP20 19)** et **Fill (segment 20)**, s'exécute **après validation de tous les paramètres/bitplanes, mais avant toute commande `BltBitMap`**. La fonction **Clear (segment 21)** appelle déjà Fill en interne : elle hérite de la protection, mais son déplacement relatif `BSR.W` vers Fill doit être **recalculé** lorsque le code Fill grandit.

1. Si `DBState+20` bit0 = 0 : pas de message Safe en attente, continuer immédiatement.
2. Si le bit0 = 1 : contrôler le port `DBState+12`, puis appeler **une seule fois** `Exec/GetMsg(SafePort)`, sans blocage.
3. Si aucun message n'est disponible : **ne dessiner aucun pixel**, restaurer registres/pile et retourner `0`. Aucun `WaitPort`, `Wait` ni `ReplyMsg`.
4. Si le message arrive : vider **seulement** le bit0, conserver le bit1 `Disp`, restaurer `GfxBase` et tous les registres vivants, puis effectuer l'opération graphique existante et `WaitBlit` normalement.
5. `D6` doit absolument être conservé : **Fill l'utilise comme limite `1<<depth`** après la validation de la couleur. Les arguments AMOS et le pointeur `A3` sont conservés exactement dans le contrat existant.

**Sémantique `0` :** refus de dessin (zone/couleur/état invalide **ou** buffer non `Safe`), sans distinction nouvelle. L'appelant peut réessayer **avec une limite** et `Aga Wait Vbl` ; une boucle illimitée sur un `0` est interdite. `Aga Wait Vbl` n'est pas lui-même un accusé Safe. Le `SafePort` et le suivi `Disp` restent ceux de `Aga Swap`, sans second consommateur indépendant.

## Compatibilité binaire et périmètre exact

La candidate est reconstruite **en mémoire** depuis [l'archive R26](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. Le format reste **AP20, 37 segments, 31 commandes nommées**, et **la table des tokens est strictement identique à R26**. Les trois modifications fonctionnelles sont limitées aux Blitters, mais les six segments R23 liés aux nouvelles adresses sont également recalculés :

- 19 `Aga Blit Copy` : garde Safe avant son unique DMA, `GetP` terminal conservé ;
- 20 `Aga Blit Fill` : même garde avant sa boucle de plans, `GetP` terminal conservé ;
- 21 `Aga Blit Clear` : wrapper historique inchangé dans ses opérations, **seul le déplacement BSR vers le nouvel Fill** peut varier.

**Hors des neuf segments 6/17/18/19/20/21/31/32/33, toutes les entrées sont conservées à l'octet près.** Les segments R23 relocalisés ne changent aucune fonction : seuls les déplacements BSR et l'ancre d'état sont corrigés. `Aga Swap`, `Aga Wait Vbl`, `Aga Back Fill` et `Aga Text` restent inchangés. **`Aga Back Fill` (ancienne commande autonome, segment 12) n'est pas incluse dans la protection R27** et reste à distinguer des trois `Aga Blit ...` couvertes. Ce périmètre évite une modification implicite d'une fonction WinUAE-validée sans contrat complémentaire.

## Validation exigée

**Gate A 68000/CI avant tout binaire publié :**

- [Émetteur des fonctions Copy/Fill](../tools/m12_blit_safe_r27_emit.py), [builder HUNK en mémoire](../tools/build_m12_blit_safe_r27.py) et [tests CPU Unicorn](../tools/test_m12_blit_safe_r27.py).
- Vérifier l'identité de la table de tokens, la différence limitée aux neuf segments audités (dont six relocalisations R23), le `BSR.W` exact de Clear, les instructions 68000 (Capstone), ABI `D2/D3/A3/SP` et les registres non volatils.
- Pour Copy/Fill/Clear et les deux valeurs de `frontIndex` : bit Safe nul, bit Safe en attente avec message absent/présent, bit Disp seul ou combiné, port Safe nul, géométrie invalide, préservation du buffer en cas de refus, `GetMsg` au plus une fois par appel.
- Vérifier que des appels répétés après consommation du message ne le consomment pas une deuxième fois ; simuler des alternances de 40 images. **PASS : 403 cas CPU natifs et vérifications de structure AP20**, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42997093650). La candidate ne fut publiée qu'après cette validation.

**Gate B AMOS interprété/WinUAE : NON TESTÉE.** [Unique test courant M12_R27_SAFE_BLIT_01.asc](../tests/current/M12_R27_SAFE_BLIT_01.asc) (à importer via **Project → Merge ASCII**) ; sélectionner `examples/demo.iff` 320×256×8 PAL. **40 alternances** : panneau bleu, deux rectangles verts puis deux rouges, le second copié par `Aga Blit Copy`. Le **premier dessin** de chaque image alterne **Clear (14 fois), Fill (13), Copy (13)** pour vérifier que chacune des trois commandes sonde directement Safe, **sans appel préalable à `Aga Text`**. Chacune des tentatives est bornée à 12 VBL en cas de retour 0 ; idem pour `Aga Swap`.

**Résultats attendus, pas encore observés :**
```text
M12-R27-SAFE-BLIT-01
IMAGE 320 X 256 PLANES 8
OPEN 1 DB 1 LOAD 1
DONE 40 C 14 F 13 P 13
C0 <n> F0 <n> P0 <n> SWAP0 <n>
SAFEERR 0 SWAPERR 0 DRAWERR 0
CLOSED -1 RESULT 1
CLOSE RETURNED
```
Les compteurs `C0/F0/P0/SWAP0` sont variables, y compris zéro ; leurs valeurs ne prouvent pas seules la cause exclusive d'un refus. **L'alternance des deux rectangles doit être constatée visuellement en plus de la console.** Ce n'est pas une mesure 50 FPS ni un stress exhaustif.


**Gates C/D :** AMOS Compiler et Amiga AGA physique restent NON TESTÉS. Aucune mesure 50 FPS ni validation exhaustive de course mémoire ne découle automatiquement de 40 alternances.

**Règles de projet :** uniquement `main`. La R27 candidate remplace le chemin courant `dist/AMOSPro_AGA.Lib` **après** Gate A PASS, sans toucher à aucune archive R26/R25/R24, ni à `LAST_GOOD` R10, ni aux tests déjà archivés. Ne pas classer le test R27 PASS avant WinUAE utilisateur.
