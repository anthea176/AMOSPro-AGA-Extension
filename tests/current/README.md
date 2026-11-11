# M12 — R27 Blitters Safe : essai WinUAE courant

**Unique `.asc` actif :** [`M12_R27_SAFE_BLIT_01.asc`](M12_R27_SAFE_BLIT_01.asc). **Nécessite la candidate R27 0.9.3**, pas l'archive R26. **Gate A 68000/CI PASS 396 cas**, [CI source R27](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42995303489). **Gate B WinUAE NON TESTÉE**.

Importer par **Project → Merge ASCII**, choisir `examples/demo.iff` (320×256, 8 plans PAL) et observer pendant 40 swaps un **grand panneau bleu avec deux rectangles verts, puis deux rouges**, en alternance. Le deuxième rectangle est **copié** depuis le premier par `Aga Blit Copy`. Le programme garde la dernière image pendant 120 VBL, ferme l'écran et revient à AMOS.

Le protocole change **le premier appel graphique après chaque swap** : **Clear 14 fois, Fill 13 fois, Copy 13 fois**. Chaque fonction vérifie elle-même le signal `Safe` ; **aucune sonde `Aga Text`** n'est utilisée. Si ce premier appel renvoie `0`, le test réessaie au maximum **12 fois**, avec `Aga Wait Vbl` entre les tentatives. Même limite de 12 pour les refus temporaires de `Aga Swap`, liés notamment à `Disp`. Ne pas boucler sans borne sur un retour 0.

### Console attendue (les compteurs de refus restent variables)

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

Les compteurs `C0`, `F0`, `P0` et `SWAP0` peuvent être zéro ou positifs ; ils ne prouvent pas individuellement qu'une notification Safe/Disp était la seule cause du refus. En cas de `RESULT 0`, transmettre la capture exacte, les compteurs et le comportement visuel. **40 swaps ne constituent pas un chronométrage de 50 FPS ni un stress exhaustif.** [Contrat R27](../../docs/M12_SAFE_BLITTER_R27.md) · [R26 validée conservée](../passed/M11_R26_SAFE_SWAP_02.asc).
