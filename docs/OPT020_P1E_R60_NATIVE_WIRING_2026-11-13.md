# OPT020/P1e — raccordement réel R60 → noyaux 68020

**13 novembre 2026 — Gate A CPU/CI PASS ; R69 Gate B WinUAE interprétée PASS ensuite.** Le début de ce rapport relate la première étape CPU en mémoire ; voir la validation réelle en fin de document.

- Branche unique : `main`, commit source testé : `91de56fcbec4a3ba544fe969ae92a34d0aac92ab`.
- [GitHub Actions OPT020 43497183949](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43497183949) : PASS, y compris tous les contrôles P1/P1b/P1c/P1d et la nouvelle étape P1e.
- 51 cas d'exécution CPU du véritable chemin R60 avec services AMOS/Exec simulés sous Musashi, dont les cas 68000 rejetés avant les instructions 020, 68EC020 et 68020 acceptés.
- La prévalidation 68000 R60 n'est **pas réécrite** : contrôle banque DATA vivante via `Bnk.GetAdr`, enveloppe mémoire, dimensions et format AGAPIC v1, offsets de lignes, tous paquets RLE/masques/padding en PASS 0. Aucun pixel n'est modifié avant succès de cette passe.
- Une fois les limites de la destination vérifiées, acquisition `Safe` non bloquante, PASS 1 et dessin dans les plans du **bitmap Intuition inactif**, sans Blitter ni copie intégrale source en Chip.
- Nouveau peintre [`opt020_p1e_painter_emit.py`](../tools/opt020_p1e_painter_emit.py) : réutilisation du clipping P1c, `emit_masked_multiplane_020` (groupes complets) et `emit_fragment_020` (champs partiels); pointeurs temporaires dans la trame R60.
- `emit_image_region()` historique **inchangé** : 2 012 octets. `emit_image_region(opt020=True)` : 2 174 octets ; SHA256 `504a61d49ac95967cfddab041841c72f09df11d86845c71366c950d1d742a8c9`.
- ABI vérifiée : 7 paramètres consommés `A3+28`, `A7`, `D2=0`, `D3=0/1`, registres, arrière-plan/canaries/front et refus non destructifs ; contrôle `ExecBase.AttnFlags` avant tout opcode 020.
- Vérification V2 sans écriture disque : **51 228 octets** AP20, unité de compilation monolithique **48 528 octets**, structures et jetons conservés ; ce test n'est pas un véritable Compiler.
- Les premiers essais ont révélé deux défauts **du nouvel adaptateur seulement** : retour imbriqué `decode_rows → paint_group` (restauration A2 via `SP+8`, et non `SP+4`) et chute du succès `D3=1` dans le rejet explicite. Corrigés et confirmés par la CI finale.

## Contrat de protection

Au premier raccordement CPU P1e (51 cas), les deux bibliothèques étaient encore R68. **Depuis la préparation R69**, seul `dist/AMOSPro_AGA.Lib` a été remplacé par la candidate R69 Gate A de **51 240 octets** (SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`). `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure **R68 v0.13.13 protégée**, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. L'ASC actif unique est `tests/current/OPT020_P1E_R69_INTERPRETED_01.asc`; `tests/passed/` et les archives restent intacts. Aucun autre binaire de travail n'a été produit.

## P1e élargie et candidate R69 0.13.14 — Gate A seulement

- **270 scénarios CPU supplémentaires PASS**, en plus des 51 premiers : matrice 1/2/4/8 plans, largeur destination 16/17/64/65, `BytesPerRow` minimal ou rembourré, clips en bord de bitplane, canaries, masque indépendant, mode opaque, offsets et paquets RLE malformés, DATA flags 0/1/3 acceptés, autres refusés, `Safe` non bloquant et bitmap inactif. [CI étendue](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43499755913).
- Builder [`build_opt020_p1e_r69.py`](../tools/build_opt020_p1e_r69.py) : reconstruit exclusivement en mémoire depuis `LAST_GOOD` R68 SHA-pinnée ; **une seule routine modifiée** (entrée native 59), sans changement des 64 commandes, signatures ou autres 69 unités. [CI construction mémoire](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43499966863) PASS.
- Candidate de travail **R69 v0.13.14** : `dist/AMOSPro_AGA.Lib` ; **51 240 octets**, **SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`**. Native Region 68020 **2 174 octets**, SHA256 `504a61d49ac95967cfddab041841c72f09df11d86845c71366c950d1d742a8c9` ; bloc monolithique Compiler V2 **48 528 octets**.
- **Seul ASC actif :** [`OPT020_P1E_R69_INTERPRETED_01.asc`](../tests/current/OPT020_P1E_R69_INTERPRETED_01.asc), test interprété WinUAE préparé depuis l'ancien R60 ; ancien test R68 figé dans `tests/passed/`.
- `LAST_GOOD` **R68 0.13.13** totalement protégé, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. Aucun autre binaire candidat, aucune archive changée.

**État à la préparation R69 :** Gate A CPU PASS et enveloppe Compiler V2 structurelle en mémoire PASS ; Gate B alors non testée. **Depuis les deux captures utilisateur du 13/11 : Gate B interprétée WinUAE PASS**, voir [rapport dédié R69](OPT020_P1E_R69_WINUAE_GATE_B_2026-11-13.md). Gate C réelle et Gate D physique NON TESTÉES ; benchmark JIT OFF non réalisé.

## CI complète de la candidate R69 — PASS

[Artifact integrity 43501573321](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43501573321) : **SUCCESS 47/47 étapes** sur le commit [`9086e14`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/9086e14332bc46970ff79959d665567eb864d1af), avec la R69 effectivement présente dans `dist/AMOSPro_AGA.Lib` et la R68 `LAST_GOOD` protégée. Audit HUNK/AP20, contrôle déterministe, source native strict, Compiler V2 **simulé**, API EN/FR, exemples et regressions M16–M18 : PASS. [CI OPT020 dédiée 43500643740](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43500643740) : **SUCCESS** (P1–P1e, ABI, R69 exact, ASC actif unique). Les correctifs de préflight réalisés pendant cette CI ont concerné les assertions de version R69 et les chemins des exemples publics renommés ; aucun correctif supplémentaire du moteur P1e ni changement des binaires protégés.

**La réussite CI seule ne constitue pas une Gate B WinUAE ; celle-ci a été validée séparément par les captures en interprété, avec `RESULT 1`, `CLOSE RETURNED` et Chip Free identique. Gate C Compiler réel reste non testée.**

## Limites et prochaine étape

La CI prouve **Gate A CPU** (services simulés `Bnk.GetAdr`, `TypeOfMem`, `GetMsg`, bitmap Intuition). Les captures utilisateur ajoutent une **Gate B interprétée WinUAE PASS pour l'ASC fourni**, pas une comparaison automatique pixel par pixel. CPU, horloge et JIT OFF ne sont pas vérifiables dans ces captures.

**Benchmark interprété R60/R68 vs R69 JIT OFF : PASS (13/11/2026).** [Résultats détaillés](../benchmarks/RESULTATS_OPT020_P1E_R60_VS_R69_2026-11-13.md) : opaque 16×16 **2,17×**, opaque 32×20 **3,32×**, masqué 32×20 **3,25×**, contrôles fonctionnels et Chip RAM corrects. Deux passages AMOS interprétés sur 68020 14 MHz JIT OFF annoncés par l'auteur. Ces résultats ne sont pas ceux d'un exécutable compilé et ne prouvent pas un gain sur Amiga physique. **Prochaine étape :** conserver et figer R69, puis réserver la **seule** compilation AMOS Compiler de P1e à l'artefact final (Gate C). R68 reste `LAST_GOOD` tant que les Gates restantes et l'accord auteur ne sont pas acquis.
