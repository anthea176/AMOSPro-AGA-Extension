# Promotion LAST_GOOD — R73 v0.13.18 (14/11/2026)

## Autorisation et périmètre

L'auteur a explicitement répondu **« promotion ok »** après la qualification
finale OPT020/P1e+P2+P3. Promotion **sur `main` uniquement** ; aucune
branche, PR, tag, release GitHub, livraison Aminet, benchmark ou
recompilation AMOS supplémentaire n'est demandée.

**Gates validées :**

- **A native CPU / ABI / AP20 : PASS** — 144 scénarios 68EC020/68020
  Fast Icons P3, rejet CPU000, clippings/masques, canaries, garde-fous
  des trois branchements R70 ; [CI P3 ciblée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43524215886).
- **B AMOS interprété / WinUAE : PASS** — [rapport du test intégré](OPT020_P3_R73_WINUAE_GATE_B_2026-11-14.md),
  `RESULT 1`, `CLOSE RETURNED`, Chip Free `1660920/1660920/1660920`.
- **C AMOS Compiler / WinUAE : PASS sur capture auteur** — [rapport](OPT020_P3_R73_COMPILER_GATE_C_2026-11-14.md),
  `OPT020-P3-R73-COMPILE-01`, `RESULT 1`, `CLOSE RETURNED`,
  Chip Free `1726752/1726752/1726752`. Aucun exécutable fourni pour
  un audit binaire indépendant ; le libellé imprimé `GATE B ONLY`
  n'était qu'un texte historique du source.
- **D Amiga AGA physique : NON TESTÉE.** Aucune prétention de couverture
  exhaustive de toute l'API ni de benchmark.

## Identité exacte de la promotion

| Élément | Valeur |
|---|---|
| Version | **R73 v0.13.18 — OPT020 P1e/P2/P3** |
| `dist/AMOSPro_AGA.Lib` | **51 608 octets** |
| `dist/AMOSPro_AGA_LAST_GOOD.Lib` | **Copie exacte du même binaire** |
| SHA256 identique | `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407` |
| Git blob identique | `2d764b08cdde34b3b1dcbe2c698a8cc2499dd3d0` |
| API | **64 commandes publiques / 71 entrées AP20** |
| ASC actif unique, inchangé | `tests/current/OPT020_P3_R73_INTERPRETED_01.asc` |

Aucun nouveau binaire n'est construit pour la promotion : on déplace
seulement le pointeur protégé `LAST_GOOD` vers **les octets déjà validés**
de la bibliothèque active.

L'ancienne **R68 v0.13.13** (51 064 octets,
SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`)
reste récupérable au [commit antérieur à promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/593963ea88a623c7c349b0250c89380758970928/dist/AMOSPro_AGA_LAST_GOOD.Lib),
Git blob `1582afef850e67efd3bdfb335ff5417a69770904`.
Aucune archive figée ni `tests/passed/` n'a été modifié.

## Garde-fous de reproductibilité

Les constructeurs historiques **R69→R73** reconstruisent désormais
leur base R68 **via `tools/build_m18_r68_cblock.py` et son SHA épinglé**,
et non en lisant `LAST_GOOD` (qui est volontairement mobile). Ils
préservent la provenance octet pour octet de R68 et R69/R70/R71/R72,
tout en reconstruisant R73 à l'identique. L'ancien défaut de branchement
relatif R70 reste interdit et soumis aux trois mutations négatives.

Les scripts `active_library.py`, `verify_artifacts.py`,
`build_aga_current.py` et les vérifications Compiler V2 et OPT020
reconnaissent `LAST_GOOD` R73 et exigent l'égalité stricte
`current == LAST_GOOD == build_r73()[0]`. Les SHA historiques restent
figés. **Une seule bibliothèque de travail**, un **seul ASC actif**.

## Contrôle CI de release

Le commit de promotion `release: R73` déclenche **une seule fois**
la CI d'intégrité rapide puis la régression historique complète sur le
SHA final publié. Les workflows P1 et P3 redondants ne sont pas rejoués.
**Résultat du contrôle de release : à relever après exécution** ; un
contrôle CI statique/CPU ne remplace pas les captures Gates B/C.

**Suite de roadmap :** OPT020 terminé et R73 promue ; prochain chantier
`c2p.library`, puis AGAPIC v2. Pas de modification de code c2p/AGAPIC
dans cette promotion.
