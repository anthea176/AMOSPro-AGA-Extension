# M17/R57 — Diagnostic Screen Copy, alignement X et Blitter Wait

**Date : 12/11/2026 · Source : capture utilisateur WinUAE, AMOS interprété.**
Source du test : [`copy_wait_32c_r57.asc`](copy_wait_32c_r57.asc), inchangé. PAL 320×256×32 couleurs, **5 bitplanes**, 1 tick `Timer` = **20 ms**. Pour chaque cas : **1 200 copies par passage, trois passages et trois méthodes**, soit 32 400 appels Copy cumulés.

La capture affiche `AGA ERR 0` et `COPY WAIT FINISHED - CLOSE RETURNED` ; aucune erreur ni Guru visible. L'identité cryptographique de la bibliothèque chargée n'est pas relevée. Ce résultat concerne **l'interpréteur**, et ne doit pas être présenté comme une nouvelle Gate C ou comme un essai sur Amiga physique.

## Résultats bruts — ticks PAL

| Géométrie 64×48 | A : Screen Copy + wait final | W : Screen Copy + wait chaque copie | G : Aga Blit Copy R57 | Médianes A / W / G |
|---|---|---|---|---|
| **ALIGNÉ** — source (16,24) → dest (176,24) | 35 / 35 / 35 | 35 / 35 / 34 | 69 / 69 / 70 | **35 / 35 / 69** |
| **SHIFT X +1** — source (17,24) → dest (177,24) | 84 / 85 / 85 | 85 / 85 / 84 | 84 / 85 / 85 | **85 / 85 / 85** |
| **DEST Y +72** — source (16,24) → dest (176,96) | 35 / 34 / 35 | 34 / 35 / 35 | 69 / 69 / 69 | **35 / 35 / 69** |

**A :** `Screen Copy` natif avec **un** `Blitter Wait` AMCAF après les 1 200 appels. **W :** la même instruction `Screen Copy` avec `Blitter Wait` AMCAF **après chaque appel**. **G :** `Aga Blit Copy` R57, qui emploie `graphics.library/BltBitMap` puis `graphics.library/WaitBlit` à chaque copie. Les trois voies travaillent dans des buffers propres à leur système, avec réinitialisation identique du motif hors chronométrage. Pas de recouvrement entre source et destination.

## Interprétation étayée

1. **Le coût visible de l'attente AMCAF ajoutée ne suffit pas à expliquer l'écart.** Pour chaque géométrie, les médianes **A = W** à la résolution de 20 ms : l'augmentation de 1 à 1 200 `Blitter Wait` explicites ne ralentit pas significativement `Screen Copy` sur ce test. **Cela ne démontre pas que `graphics.library/WaitBlit` a un coût nul** ni qu'AMOS et AMCAF utilisent la même implémentation d'attente.
2. **L'alignement horizontal est déterminant.** Déplacer de **+1 pixel en X la source ET la destination**, sans modifier la largeur ni la hauteur, fait passer AMOS de **35 à 85 ticks** et AGA de **69 à 85 ticks**. L'écart AGA/AMOS disparaît lorsque les positions deviennent non alignées sur 16 pixels. L'effet peut résulter de chemins de copie et de masquage différents ; **le mécanisme interne n'a pas été mesuré**.
3. **Le décalage vertical de la destination ne change rien de mesurable.** Les médianes restent **35/35/69** quand on passe la destination de Y=24 à Y=96.
4. **Sur le cas aligné**, 69/35 = **1,97×** le temps natif AMOS. Soit pour 1 200 appels : **1,15 ms par copie AGA** contre **0,58 ms par copie AMOS** en moyenne sur le lot. Les autres charges du benchmark Copy initial restent quasi à égalité ; l'écart n'est **pas** généralisable à toutes les dimensions.

## Hypothèses restantes et prochaine enquête

- **Hypothèse prioritaire :** `Screen Copy` AMOS emprunte une voie rapide pour les rectangles dont le début et la largeur sont alignés sur 16 pixels ; le chemin `graphics.library/BltBitMap` de notre routine R57 peut payer un coût fixe supplémentaire ou emprunter une voie différente. **Aucune preuve de ce chemin interne AMOS à ce stade** : examiner son implémentation/disassembly avant d'affirmer la cause.
- **Synchro AmigaOS :** le benchmark ne sépare pas le coût propre de `BltBitMap` de celui de `WaitBlit`; les différences A/W ne doivent pas servir à supprimer `WaitBlit`. Conserver les protections `Safe`, l'ABI AMOS Compiler et la synchronisation du back buffer.
- **Prochaine étape conseillée :** étude ciblée des variantes de traitement de `BltBitMap` **via AmigaOS uniquement** (géométrie X alignée/décalée, coût des appels et éventuelle alternative publique démontrablement plus rapide), puis décider d'un test plus fin. Pas de registres Blitter directs, pas de correction R58 avant décision explicite.

**État du dépôt :** R57 Gates A/B/C acquises, Gate D physique non testée. Aucun changement de `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` R54, de `tests/current/M17_R57_RAST_FILL_01.asc`, des benchmarks anciens ou de branche. **`main` exclusivement.**

[Source du benchmark](copy_wait_32c_r57.asc) · [Protocole](README_COPY_WAIT_32C.md) · [Benchmark Copy complet interprété/compilé](RESULTATS_COPY_32C_R57_2026-11-12.md) · [Diagnostic M17](../docs/M17_BLITTER_DIAGNOSTIC.md) · [Autodoc officiel `BltBitMap`](https://developer.amigaos3.net/autodocs/graphics.library/BltBitMap.html).
