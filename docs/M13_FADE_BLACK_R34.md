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

## Statut R34

**R34 Gate A CPU/CI PASS :** 48 scénarios natifs 68000 et export strict de la source 68000 PASS. [CI de Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43053032571). **Gate B WinUAE NON TESTÉE** ; candidate publique à installer uniquement pour ce test.

**Candidate R34 publiée :** `dist/AMOSPro_AGA.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib`, **20 752 octets**, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033` (copies identiques). **R33 0.10.5 reste dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`** et son archive figée, 20 208 octets, SHA256 `e0db41e282bfb8ac92fd5dfa68ab2bee50e1c7ae2a86429d587964337b797b2f`.

- Source : `tools/m13_aga_fade_black_r34_emit.py`.
- Builder : `tools/build_m13_aga_fade_black_r34.py`, déterministe en mémoire, R33 comme base immuable, sans modifier `LAST_GOOD`.
- Tests CPU : `tools/test_m13_aga_fade_black_r34.py`, vraie exécution 68000 sous Unicorn, ABI, ColorMap, durée, interpolation et dernier noir exact, alloc/free, zéro écriture banque/bitplane, paramètres invalides.
- Test WinUAE préparé : [`tests/current/M13_R34_FADE_TO_BLACK_01.asc`](../tests/current/M13_R34_FADE_TO_BLACK_01.asc), avec scène affichée AVANT le fondu 150 VBL ; pen28,29,30,224 noirs, 0/256/-1/65536 refusés, cas 1/2 VBL, noir déjà atteint et écran fermé. **Aucune banque remplacée.**
- **Gate A PASS, publication effectuée :** `dist/AMOSPro_AGA.Lib` et archive R34 sont identiques. `LAST_GOOD` demeure R33 jusqu'à validation utilisateur de Gate B.
- Gates B AMOS interprété/WinUAE, C Compiler et D Amiga AGA réel : **NON TESTÉES** pour R34. Le test actif est prêt dans `tests/current/`, sans remplacement de banque ni fichier.

Une seule commande ajoutée : segment AP20 45, signature numérique `00` (une entrée entière, retour entier). Les 39 commandes et l'archive R33 restent inchangées (sauf suffixe de chaînage `GetP` dans le segment R33 du binaire candidat R34). La prochaine fonction, par exemple Fade To White, nécessite un contrat et un accord distincts.
