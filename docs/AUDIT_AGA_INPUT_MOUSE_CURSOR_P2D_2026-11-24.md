# Audit P2d — passage 12 : Mouse/Key, curseur et donnees State

**24 novembre 2026 — main uniquement — source examinee au commit `f6797d5dfb302785faca0f9f0149cb42807accc5`.** Audit statique. Aucune nouvelle Gate, aucun correctif, aucun binaire ni test modifie. Sprite S1-P1e GELÉ.

## 1. Deux entrees P2d Mouse utilisent le bon offset de donnees

- `Aga Mouse Pressed` : **AP20 53 → UNIT142+$02D90**. [Source native](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_02D90_MC68020.s).
- `Aga Mouse Released` : **AP20 55 → UNIT142+$02DFA**. [Source native](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_02DFA_MC68020.s).

Ces deux fonctions controlent la presence de State et Window et l'option IDCMP correspondante, puis calculent **`lea 12070(a2),a2`** avant de lire et de remettre a zero les champs Pressed/Released. **`12070` (hex `$2F26`)** est le deplacement de la correction **R76**, et non l'ancien **`11932` (hex `$2E9C`)** responsable d'une corruption de code dans R74/R75.

Le [rapport historique R76](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/docs/C2P_R76_RPG_REGRESSION_2026-11-14.md) conserve la cause du freeze/Guru et le controle de **7 sites LEA**. Le script [test_current_input_state_offsets.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/tools/test_current_input_state_offsets.py) a ete concu pour 7 LEA et 8 mutants negatifs. **Deux entrees natives verifiees ne prouvent pas que les sept sites sont conformes apres chaque nouvelle relocation.** La politique SHA du test n'est pas modifiee pendant le gel.

**Verdict :** le deplacement R74/R75 obsolete est **absent de ces deux entrees P2d** ; aucun freeze P2d actuel ne se deduit du vieux rapport. Les autres sites et les Gates B/C d'entree restent VM.

## 2. `Aga Mouse Cursor` possede un etat prive et un chemin de cleanup lie au Close

`Aga Mouse Cursor` → **AP20 99 → UNIT142+$0652C** : [corps natif](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_0652C_MC68020.s). Le code accepte les modes entiers 0/1, verifie Screen et Window, compare le proprietaire et gere un etat prive d'environ **72 octets**. Le mode active/desactive des appels de curseur Intuition ; il ne constitue pas un writer du bitmap arriere.

Le [Close natif R83](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_CROSS_BSR_MC68020.s) contient une **branche `BSR.W L_UNIT142_0660A`**. Ce helper, dans le meme [bloc du curseur](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_0652C_MC68020.s) compare l'owner, libere les ressources associees et, si sa propre allocation est presente, fait **`Exec FreeMem(-210)`** puis remet les pointeurs d'identite a zero.

**Constat positif :** le cleanup du curseur existe dans le chemin de Close reel. **Non prouve :** son comportement sur echec d'alloc/fermeture OS, double Close, End apres Close ou reutilisation de la meme adresse Window. Cela reste couvert par AGA-004 et T14.

## 3. Domaine de securite de la souris : owner et State, pas SafePort bitmap

`Aga Mouse X/Y/Buttons` lisent un Window possede par l'ecran et verifient les limites avant retour. Les entrees [Hotspot Hit](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_0317C_MC68020.s) et [Rect Overlap](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/f6797d5dfb302785faca0f9f0149cb42807accc5/src/native/m19_p2d/M19_UNIT142_BLOCK_031E4_MC68020.s) effectuent des calculs de rectangles et bornes, sans acces direct a des bitplanes graphiques releve dans ces routines.

**Ne pas exiger `GetMsg(SafePort)` de ces fonctions si elles ne lisent/ecrivent pas le bitmap.** Le controle correct est l'integrite de Window, State et des offsets relatifs, et le cycle Close/End.

## 4. Etendue et actions de verification futures

| Chemin | Statique source | Validation manquante |
|---|---|---|
| Pressed / Released | `State+12070` dans les deux routines P2d | 5 autres LEA et recompilation future, Runtime/Compiler |
| Mouse X/Y/Buttons | Garde Window/Screen source | Reouverture et droits IDCMP |
| Cursor mode 0/1 | Owner et petite allocation privee | Cas d'erreur OS, double Close, ABA |
| Curseur + Screen Close | BSR natif vers helper de liberation | End/reouverture et frees balances |
| Hotspot/Overlap | Calculs d'intervalles, pas de dessin bitmap dans les routines vues | Tests de bornes et overflow si changement futur |

**T14** doit inclure Mouse Cursor On/Off, Close, End et reouverture ; les 7 LEA State restent une exigence de tout futur build corrige. **Aucun nouveau test lance, aucune correction, Sprite GELÉ.**

[Audit transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Matrice 102 commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md) · [Cahier 19 scenarios](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).
