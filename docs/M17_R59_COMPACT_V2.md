# M17/R59 v0.13.4 — Compiler V2 compact (candidate)

**12 novembre 2026 — `main` uniquement.** [Binaire de travail unique](../dist/AMOSPro_AGA.Lib) de **32 984 octets**, SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`. **53 commandes, 60 entrées AP20, 59 routines natives R57**, bloc Compiler V2 **30 782 octets** = 34 octets de dispatcher + 30 748 octets de code original. L'ensemble des tokens et des stubs AP20 de R57 est préservé exactement. La `LAST_GOOD` R57 v0.13.2 (SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`) reste protégée.

## Objectif et différence avec R58

R58 v0.13.3 (42 264 octets, SHA256 `c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b`) avait prouvé l'appel natif à l'offset **40 000** en AMOS interprété et avec un **nouvel exécutable AMOS Compiler**, via deux captures utilisateur indépendantes : **Gates A/B/C PASS** sur ce témoin. Son code contenait **9 252 octets de remplissage zéro** et une routine NOP/RTS artificielle. R59 **supprime les deux**, rétablit le token `Aga Probe` d'origine et conserve **seulement** le dispatcher V2 de 34 octets (contre 32 pour R57). Le maximum théorique de 65 534 octets du Compiler n'a pas été qualifié sous WinUAE.

Le builder [`build_m17_r59_compact_v2.py`](../tools/build_m17_r59_compact_v2.py) reconstruit le code à partir du builder R57 SHA-pinné, sans modifier les archives ni `LAST_GOOD`. Un unique test est actif : [`M17_R59_COMPACT_V2_01.asc`](../tests/current/M17_R59_COMPACT_V2_01.asc). Le [témoin exact R58](../tests/passed/M17_R58_COMPILER_BRIDGE_01.asc) est archivé sans retouche.

## Gates et recette

| Gate | Statut |
|---|---|
| A — SHA/AP20/CPU 68000/CI | **PASS**, [Artifact integrity 43310033167](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43310033167), constructeur reproductible et tests BSR.W / JSR absolu, pile et registres |
| B — AMOS interprété / WinUAE | **À TESTER** sur la bibliothèque R59 et l'ASC R59 |
| C — Nouvel exécutable AMOS Compiler / WinUAE | **À TESTER** sur R59 ; le PASS R58 ne peut pas être transféré automatiquement |
| D — Amiga AGA réel | **NON TESTÉE** |

**Pour WinUAE :** installer `dist/AMOSPro_AGA.Lib` R59 dans `APSystem`, redémarrer AMOS et Compiler, importer l'ASC par `Project → Merge ASCII`. Lancer en interprété (Gate B), puis **compiler ce même ASC dans un nouveau fichier exécutable** (Gate C). Résultat attendu : `AGA PROBE RETURNED`, `AGA PROBE AFTER CLOSE RETURNED`, `OPEN 1 DB 1 PAL 1`, `SW0 1 SAFE 1 FILL 1`, `COPY 1 SWAP 1 CLOSED -1`, `RESULT 1`, `CLOSE RETURNED` sans Guru. Le `Program interrupted` de la boucle finale `Do / Wait Vbl / Loop` est normal après interruption manuelle.

**Ne pas promouvoir R59 en `LAST_GOOD` sans confirmation indépendante B/C R59, régression complète sur le HEAD de livraison, et accord explicite de l'auteur.** La CI ne remplace pas un test Compiler WinUAE. Aucun autre chantier fonctionnel engagé.
