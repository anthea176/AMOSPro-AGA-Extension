# OPT020/P3 — R73 v0.13.18 : Gate C AMOS Compiler PASS (14/11/2026)

## Preuve et limites

**Essai final compilé sous WinUAE communiqué par l'auteur le 14/11/2026.**
La capture porte le titre de programme `OPT020-P3-R73-COMPILE-01`. L'auteur a
explicitement signalé qu'il s'agissait de l'exécution compilée : les retours
relevés ci-dessous montrent un fonctionnement conforme de P1e, P2 et P3.
**Gate C fonctionnelle : PASS selon le test compilé fourni.**

La deuxième ligne affiche encore `OPT020 P1e+P2+P3 - GATE B ONLY` :
**ancien texte de l'ASC interprété resté dans le programme**, sans relation
avec le résultat des fonctions. Ne pas changer l'ASC ni réclamer un nouveau
passage Compiler uniquement pour un libellé cosmétique.

La capture ne livre pas l'exécutable compilé, les journaux de génération
Compiler ou une preuve indépendante du profil CPU WinUAE ; il ne faut donc
pas revendiquer un audit binaire de l'exécutable ni une validation sur
Amiga physique. La validation ci-dessous porte sur le comportement observé.

## Identification de la bibliothèque testée

- Dépôt `anthea176/AMOSPro-AGA-Extension`, branche `main` uniquement.
- Seule bibliothèque active de travail : `dist/AMOSPro_AGA.Lib`,
  **R73 v0.13.18**, **51 608 octets**,
  SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.
  Cette référence est celle de la candidate installée ; le SHA n'est pas
  recalculable à partir de la seule capture.
- **Un seul ASC actif dans Git** :
  `tests/current/OPT020_P3_R73_INTERPRETED_01.asc` (Gate B PASS).
  Le programme compilé présenté est identifié localement
  `OPT020-P3-R73-COMPILE-01`. Ne pas créer de second ASC actif ni
  renommer `tests/current` après validation.
- R68 `dist/AMOSPro_AGA_LAST_GOOD.Lib` **protégée** (51 064 octets,
  SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`).

## Résultats visibles sur la capture du programme compilé

| Test | Résultats visibles | Verdict |
|---|---|---|
| P2 opaque / masqué / décalé | `1 1 1` | PASS |
| P2 clipping L/R/T/B | `1 1 1 1` | PASS |
| P2 OUT/BAD P/L/M/X/NOS | `1 0 0 0 0 0` | PASS |
| Écran AGAPIC4 Open/DB/Swap/Safe | `1 1 1 1` | PASS |
| P1e frames et shift | `1 1 1 1` et `1` | PASS |
| P1e clipping L/R/T/B/OUT | `1 1 1 1 1` | PASS |
| P1e edge/part/mask opaque | `1 1 1` | PASS |
| Refus P1e Bad Bank/X/Y/W/M | `0 0 0 0 0` | PASS |
| Legacy Bank Draw/Swap/NOS/Close | `1 1 0 -1` | PASS |
| Écran FICON8 Open/DB/Swap/Safe | `1 1 1 1` | PASS |
| P3 Fill/Swap/Close | `1 1 -1` | PASS |
| Fast Icons Draw opaque/masqué/décalé | `1 1 1` | PASS |
| Fast Icons Capture / EQ 288 octets | `1 1` | PASS |
| Fast Icons clipping L/R/T/B/OUT | `1 1 1 1 1` | PASS |
| Fast Icons refus B/I/M et Capture X/B/I | `0 0 0 0 0 0` | PASS |
| Fast Icons NO SCREEN Draw/Capture | `0 0` | PASS |
| Chip Free START / MID / END | `1726752 / 1726752 / 1726752` | Stable |
| Bilan / fermeture | `RESULT 1`, `CLOSE RETURNED` | **PASS** |

Aucune fuite Chip ni Guru visible sur ce scénario. Les valeurs de Chip Free
peuvent différer du mode interprété, mais l'égalité avant/milieu/après
est vérifiée **au sein de ce test compilé**. L'égalité exacte de pixels
démontrée par le programme concerne le slot capturé de **288 octets** ;
pas de comparaison globale pixel à pixel ni de benchmark demandé.

## État final OPT020 et suite

| Gate | État |
|---|---|
| A — CPU natif / ABI / intégrité AP20 | **PASS** |
| B — WinUAE, AMOS interprété, P1e+P2+P3 | **PASS** ([rapport](OPT020_P3_R73_WINUAE_GATE_B_2026-11-14.md)) |
| C — WinUAE, AMOS Compiler, P1e+P2+P3 | **PASS (capture auteur)** |
| D — matériel Amiga physique | **NON TESTÉE** |

**Chantier OPT020 P1e/P2/P3 validé sur les Gates A/B/C.**
R73 reste une **candidate non promue**. Ne pas écrire dans
`LAST_GOOD`, `tests/passed/`, les archives ou un autre dépôt sans accord
explicite de l'auteur. Pas de R74 ni nouvelle compilation pour la seule
mise à jour documentaire. Après décision sur la promotion/fermeture du
chantier : `c2p.library`, puis AGAPIC v2.
