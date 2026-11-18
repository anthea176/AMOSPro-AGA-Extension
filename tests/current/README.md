# M19 B7-m1 — benchmark décor texturé / quatre Bobs (Runtime)

**Seul ASC actif :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](M19_P0J_B7_ANIM_RUNTIME_03.asc), **9 624 octets**, SHA256 `8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904`. Même chemin qu'avant pour les workflows ; [l'ancien ASC A/B/C Fill 7 555 octets](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/2d019a555447ab3cd294d1c4b4e69928d7afd9db/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc) est préservé dans l'historique Git. [Rapport du benchmark précédent](../../docs/M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md) : **Gate B PASS**, 720/720 frames et gain de temps de 48,9 % pour l'effacement local.

**Bibliothèque B7-m1 inchangée :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`. Cible native MC68020 minimum ; **WinUAE AGA PAL, 68030/JIT ON**, Runtime uniquement. `LAST_GOOD` R84 inchangée. **Aucun essai Compiler**.

**Résultats WinUAE réels (18/11/2026) : Gate B PASS.** [Rapport détaillé](../../docs/M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md) : A 239/240 ticks (**25,05 FPS**), B 240/239 (**25,05 FPS**), C 123/122 (**48,98 FPS**), `RUN_WAITS` cumulé **719 VBL**, `COPY_FAILS 0`, `ERR 0`. Aucun défaut graphique signalé. **Le banc n'a pas été compilé.**

## Étapes

1. Mettre à jour le clone local (branche `main`), laisser la Lib B7-m1 installée dans `APSystem`. Dans AMOS Professional : ouvrir un programme vide, puis **Project → Merge ASCII** du seul ASC actif (ne pas utiliser `Load` pour un ASC).
2. Vérifier que les banques AMOS **24 et 25** sont libres. N'utiliser `Erase All` que dans une session de test où aucune autre banque ne doit être préservée.
3. Lancer **en Runtime uniquement**. La première étape crée un décor **procédural à tuiles multicolores** de 320×256×256 couleurs. Une bande propre de 64 pixels reste au sommet de **chacune des deux pages** ; elle sert de source aux copies. Ce décor n'est **pas** une image IFF importée.
4. Observer six séries de 120 frames, dans l'ordre **A, B, C, C, B, A**. Les quatre Bobs sont mobiles dans A/C (rouges masqués et jaunes opaques), avec clipping. B laisse le décor sans Bobs.
5. À la fin : `Aga Screen Close`, `Amos To Front`, effacement des deux banques et journal **`RAM:M19_B7M1_DECOR_BENCH.TXT`**. Conserver le journal avant reset et relancer sans `Erase All`.

## Les trois cas mesurés

| Cas | Opérations chronométrées par frame |
|---|---|
| **A — décor complet + Bobs** | 3 copies `Aga Blit Copy` de 320×64, puis 4 Bobs et Swap |
| **B — décor complet seul** | Les mêmes 3 copies et Swap, **sans** Draw |
| **C — zones sales + Bobs** | Deux premières frames : réinitialisation des deux pages. Ensuite : restauration des anciennes zones sur **la page réellement réutilisée**, redessin des 4 Bobs et Swap |

En C, les copies reprennent les pixels de la bande témoin aux **mêmes X et Y modulo 64** ; elles sont **découpées** si elles traversent une frontière de tuile (y=128,192, etc.). Le témoin ne peut pas être recouvert par un Bob (tous sont à y≥72). Les positions précédentes sont mémorisées page par page, et l'indice de page bascule **après Swap réussi**. Toute erreur Copy/Draw interdit le Swap de la frame.

Les mesures `Timer` incluent copies, Bobs, Swap, gestion Safe/Disp et les `Aga Wait Vbl` **uniquement lorsqu'une tentative est refusée**. Le décor témoin, les banques et la pause finale sont **hors chronométrage**. Ce n'est pas un benchmark de cycles CPU ni une mesure isolée du Blitter.

## Journal attendu

Chaque série écrit : `RUN n CASE c`, `RUN_FRAMES`, **`RUN_TICKS`**, **`RUN_WAITS`**, **`RUN_COPIES`**, **`RUN_COPY_PIXELS`**. Calculer les FPS à partir des ticks bruts : **FPS = 120 × 50 / RUN_TICKS**. Les attentes VBL par série permettent de comprendre si l'écart vient surtout du chemin de rendu ou de la synchronisation.

Critères de succès : `RESULT 1`, `ERR 0`, `FRAMES_OK 720`, six fois `RUN_FRAMES 120`, `FILL_FAILS 0`, `COPY_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `BANKS_ERASED 2`, `VERDICT PATH_OK`, écran et clipping corrects, **pas de traînées dans les deux séries C**, ni Guru/freeze, retour AMOS et relance possible.

**Statut : Gate A/PREFLIGHT PASS** (AMOS statique strict, 21 tests du préflight, oracle pixel simulé de 720 frames et 84 découpages). **Gate B Runtime WinUAE PASS pour ce banc décor** : 720/720 frames, ERR 0, zéro erreur Fill/Copy/Draw/Swap, rendu graphique confirmé par l'auteur. **Gate C Compiler et Gate D matériel NON TESTÉES.** [Rapport technique](../../docs/M19_B7M1_DECOR_BENCH_RUNTIME_2026-11-18.md).
