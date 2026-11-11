# M13 / R34 0.10.6 — Aga Fade To Black

## Contrat approuvé par l'utilisateur le 11/11/2026

**Fonction unique :** `_OK=Aga Fade To Black(_VBL)`.

- `_VBL` : entier de **1 à 255 inclus**. Une durée 0, négative ou supérieure à 255 retourne **0** sans changement.
- **Bloquant :** un `graphics.library/WaitTOF` et un `graphics.library/LoadRGB32` à chaque étape, sans attente cachée. La durée réelle n'est pas strictement garantie à N/50 seconde si la charge CPU 68000 dépasse une trame.
- **Couleurs concernées :** tous les pens logiques de l'écran AGA Intuition privé actif indexé, de 1 à 8 bitplanes, de 1 à 256 couleurs. La `ColorMap.Count` doit contenir ces pens ; rejet HAM/EHB/dual playfield, aucun recadrage silencieux.
- **Source :** lecture unique `GetRGB32` de la ColorMap courante pour 2..255 VBL. À 1 VBL, chargement direct de noir.
- **Interpolation :** RGB24 linéaire et pas signé 8.8 (même approche que R33), calculé une fois par composante. La dernière image est **exactement noire sur tous les pens logiques**, indépendamment des arrondis intermédiaires. Pas de gamma ni dither.
- **Pixels/banques :** aucune écriture dans les pixels, bitplanes, banques DATA/AGAPAL ou fichiers ABK ; aucun pointeur `Start(bank)` n'est demandé.
- **Mémoire :** une seule allocation temporaire `AllocVec(MEMF_PUBLIC)` de `8+42*N` octets (maximum **10 760**), table `LoadRGB32` + snapshot `GetRGB32` + états DDA. `FreeVec` à la fin ; Fast RAM possible, Chip non requise.
- **Retour entier :** `1` succès, `0` refus avant toute VBL et tout changement. Toutes les ressources validées et allouées avant la première attente. Ne pas détruire l'écran par une autre tâche pendant un fade bloquant.

### Appel AMOS

~~~amos
_OK=Aga Fade To Black(100)
' Retour optionnel vers une palette sauvegardée via R33 :
_OK=Aga Fade To Bank(Start(10),0,100)
~~~

La fonction R34 elle-même est **indépendante des banques** ; le retour AGAPAL n'est qu'un exemple optionnel.

## Statut R34 — Gates A/B PASS, promotion confirmée (11/11/2026)

**Gate A PASS :** 48 scénarios natifs CPU 68000, export 68000 strict, [CI candidate publiée 36/36 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053552010). API R34 : 40 commandes AP20.

**Gate B PASS — capture utilisateur AMOS interprété/WinUAE :** `OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 BLACK 0 0 0 0`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 0 FADE2 1 TWO 0`, `SAME 1 SAME28 0`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale **ligne 113**. L'utilisateur a répondu « nickel » après le test visuel des trois bandes affichées avant le fondu de 150 VBL. **Fonctionnement et effet visuel confirmés** ; cadence/FPS et durée réelle non mesurées, il ne s'agit pas d'un benchmark.

**Promotion sans recompilation ni changement de contenu :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib`, **20 752 octets**, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`, **mêmes octets**. L'archive R33 WinUAE-PASS 0.10.5 reste strictement inchangée (20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`).

**Test WinUAE figé dans `tests/passed/` :** [`M13_R34_FADE_TO_BLACK_01.asc`](../tests/passed/M13_R34_FADE_TO_BLACK_01.asc) (Git blob `5fe2f819048cd3706eedaf363f3415a00270406a`, copie exacte du test exécuté). Aucun ASC actif sous `tests/current/`. Le scénario n'a remplacé aucune banque AMOS ni aucun fichier.

- Source : `tools/m13_aga_fade_black_r34_emit.py`.
- Builder déterministe : `tools/build_m13_aga_fade_black_r34.py`, base figée R33 et contrôle du `LAST_GOOD` R34, sans écriture de fichier.
- Tests CPU : `tools/test_m13_aga_fade_black_r34.py`, vérifications ABI, RGB32 exact, durées, rejets atomiques et mémoire.
- Gates C Compiler et D Amiga AGA physique : **NON TESTÉES**.
- Prochaine fonction (par exemple Fade To White) : contrat à discuter et approuver séparément avant tout codage.


Une seule commande ajoutée : segment AP20 45, signature numérique `00` (une entrée entière, retour entier). Les 39 commandes et l'archive R33 restent inchangées (sauf suffixe de chaînage `GetP` dans le segment R33 du binaire R34 publié). La prochaine fonction, par exemple Fade To White, nécessite un contrat et un accord distincts.
