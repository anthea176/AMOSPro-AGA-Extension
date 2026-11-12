# Benchmark Copy M17/R57 — AMOS Screen Copy contre Aga Blit Copy

**Date : 12 novembre 2026.** Deux captures fournies par l'auteur sous WinUAE : une en **AMOS interprété**, une en **AMOS Compiler**. Source inchangée : [`copy_32c_r57.asc`](copy_32c_r57.asc) ; [protocole](README_COPY_32C.md). Mode PAL **320×256×32 couleurs**, 5 bitplanes, 3 passages par cas, `Timer` : **1 tick = 20 ms**.

Les captures indiquent toutes deux **`AGA ERR 0`** et **`COPY BENCH FINISHED - CLOSE RETURNED`**. Pas de Guru visible. L'identité SHA256 de la bibliothèque réellement chargée, la configuration détaillée WinUAE et l'intégrité pixel par pixel de chaque copie ne sont pas établies par ces captures.

## Mesures interprétées — ticks bruts

| Cas | Nombre de copies / passage | AMOS Screen Copy A | AGA Blit Copy G | Médiane A / G |
|---|---:|---|---|---|
| ALIGNÉ 64×48 | 1 200 | 35 / 35 / 34 | 69 / 69 / 69 | **35 / 69** |
| NON ALIGNÉ 95×72 | 900 | 130 / 130 / 130 | 129 / 130 / 134 | **130 / 130** |
| GRAND 200×112 | 500 | 210 / 207 / 206 | 210 / 206 / 206 | **207 / 206** |
| RECOUVREMENT 128×96 | 700 | 173 / 175 / 174 | 172 / 178 / 175 | **174 / 175** |

`AGA ERR 0` et fermeture normale visibles. Pour les deux méthodes, **9 900 copies** sur les 3 passages, soit **19 800 appels au total**.

## Mesures compilées — ticks bruts

| Cas | Nombre de copies / passage | AMOS Screen Copy A | AGA Blit Copy G | Médiane A / G | Écart du temps G vs A |
|---|---:|---|---|---|---:|
| ALIGNÉ 64×48 | 1 200 | 35 / 35 / 35 | 69 / 69 / 69 | **35 / 69** | **+97,1 %** |
| NON ALIGNÉ 95×72 | 900 | 130 / 131 / 131 | 130 / 129 / 129 | **131 / 129** | **−1,5 %** |
| GRAND 200×112 | 500 | 206 / 206 / 207 | 206 / 206 / 206 | **206 / 206** | **0 %** |
| RECOUVREMENT 128×96 | 700 | 173 / 173 / 173 | 172 / 172 / 172 | **173 / 172** | **−0,6 %** |

Le pourcentage est calculé par `(G-A)/A ×100`, sur les médianes : **positif = AGA plus lente**, négatif = AGA plus rapide. Toutes les durées affichées sont des lots de copies, non des temps d'une opération isolée.

### Lecture des résultats

- **Petit rectangle aligné (64×48) :** AGA prend **69 ticks contre 35** en interprété **et** en compilé, soit environ **1,97 fois le temps AMOS**. En compilé : 1 380 ms / 1 200 ≈ **1,15 ms par copie AGA** contre 700 ms / 1 200 ≈ **0,58 ms AMOS**.
- **Trois autres cas :** performances pratiquement identiques entre A et G sur le même scénario en compilé ; les écarts de 0 à 2 ticks sont faibles et ne prouvent pas une supériorité générale d'un moteur.
- **Interprété vs compilé :** les chiffres sont très proches, notamment sur le petit rectangle aligné (**35/69** dans les deux modes). Le surcoût de ce cas ne semble donc **pas causé principalement par l'interpréteur AMOS**.
- **Hypothèse de coût fixe/synchronisation :** `Screen Copy` natif est suivi d'un seul `Blitter Wait` **en fin de série**, tandis que `Aga Blit Copy` attend `WaitBlit` **à chaque copie**. Sur de petites zones, un coût fixe/une voie AMOS spécialisée peut peser davantage. Ce n'est **pas une preuve** de la cause exacte ; ne jamais enlever l'attente sans justifier la sécurité DMA.
- **Modèles d'écran différents :** AMOS écrit dans son écran 0 ; AGA copie dans son back buffer privé. Le benchmark compare les **commandes observables**, pas deux chemins matériels parfaitement identiques. Le cas overlap n'est pas une validation exhaustive de la copie correcte des pixels.
- **Contrôle d'erreur limité :** `AGA ERR 0` vérifie le dernier résultat de chacune des 12 séries AGA, pas les 9 900 retours intermédiaires.

## État du projet et suite

**Benchmark Copy interprété : PASS (exécution)**. **Benchmark Copy compilé : PASS (exécution)**. Cette validation ne remplace pas les Gates A/B/C fonctionnelles **déjà PASS pour R57** ; elle apporte des mesures comparatives de vitesse. **Gate D sur Amiga physique non testée.**

**Prochaine piste, diagnostic seulement :** analyser le chemin `Aga Blit Copy` de R57 (nombre de `BltBitMap`/`WaitBlit`, contrôles `Safe`, alignement, éventuelles différences de chemins de `Screen Copy`) et mesurer séparément le coût fixe de la petite copie alignée. Aucun correctif de code décidé par ces chiffres seuls.

**Circuit respecté :** `main` uniquement, **`dist/AMOSPro_AGA.Lib` R57 inchangée**, **unique test actif `tests/current/M17_R57_RAST_FILL_01.asc` inchangé**, R54 `LAST_GOOD` protégé. Aucun autre binaire ni ASC actif.

[Source Copy](copy_32c_r57.asc) · [Protocole Copy](README_COPY_32C.md) · [Benchmark Fill/Clear R57](RESULTATS_32C_R57_COMPILER_2026-11-12.md) · [Diagnostic technique M17](../docs/M17_BLITTER_DIAGNOSTIC.md).
