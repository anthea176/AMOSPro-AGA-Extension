# M17/R59 v0.13.4 — Compiler V2 compact, `LAST_GOOD` PROMUE

**12 novembre 2026 — `main` uniquement.** [Binaire de travail unique](../dist/AMOSPro_AGA.Lib) de **32 984 octets**, SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`. **53 commandes, 60 entrées AP20, 59 routines natives R57**, bloc Compiler V2 **30 782 octets** = 34 octets de dispatcher + 30 748 octets de code original. L'ensemble des tokens et des stubs AP20 de R57 est préservé exactement. **`LAST_GOOD` R59** validée : les deux bibliothèques `dist/` sont désormais identiques (SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`). R57 v0.13.2 (SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`) demeure historiquement reproductible.

## Objectif et différence avec R58

R58 v0.13.3 (42 264 octets, SHA256 `c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b`) avait prouvé l'appel natif à l'offset **40 000** en AMOS interprété et avec un **nouvel exécutable AMOS Compiler**, via deux captures utilisateur indépendantes : **Gates A/B/C PASS** sur ce témoin. Son code contenait **9 252 octets de remplissage zéro** et une routine NOP/RTS artificielle. R59 **supprime les deux**, rétablit le token `Aga Probe` d'origine et conserve **seulement** le dispatcher V2 de 34 octets (contre 32 pour R57). Le maximum théorique de 65 534 octets du Compiler n'a pas été qualifié sous WinUAE.

Le builder [`build_m17_r59_compact_v2.py`](../tools/build_m17_r59_compact_v2.py) reconstruit le code à partir du builder historique R57 SHA-pinné, sans modifier les archives. **Test R59 exact archivé** : [`M17_R59_COMPACT_V2_01.asc`](../tests/passed/M17_R59_COMPACT_V2_01.asc) ; aucun ASC ne reste actif dans `tests/current/`. Le [témoin exact R58](../tests/passed/M17_R58_COMPILER_BRIDGE_01.asc) reste archivé sans retouche.

## Gates et recette

| Gate | Statut |
|---|---|
| A — SHA/AP20/CPU 68000/CI | **PASS**, [Artifact integrity 43310033167](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43310033167), constructeur reproductible et tests BSR.W / JSR absolu, pile et registres |
| B — AMOS interprété / WinUAE | **PASS** — capture utilisateur du 12/11/2026, `RESULT 1`, `CLOSE RETURNED`, puis `Program interrupted` après interruption manuelle dans la boucle finale ; pas de Guru visible |
| C — Nouvel exécutable AMOS Compiler / WinUAE | **PASS** — capture utilisateur distincte du 12/11/2026, bandeau « compilé », `RESULT 1`, `CLOSE RETURNED` ; pas de Guru visible |
| D — Amiga AGA réel | **NON TESTÉE** |

**Résultats reçus le 12/11/2026 :** les deux captures montrent `M17-R59-COMPACT-V2-01`, `AGA PROBE RETURNED`, `AGA PROBE AFTER CLOSE RETURNED`, `COMPACT V2 / NO 40K PADDING`, `OPEN 1 DB 1 PAL 1`, `SW0 1 SAFE 1 FILL 1`, `COPY 1 SWAP 1 CLOSED -1`, `RESULT 1` et `CLOSE RETURNED`. La première identifie AMOS interprété par le prompt `AMOS Pro>` après l'arrêt manuel ; la seconde identifie le mode compilé par le bandeau « compilé ». **A/B/C PASS sur ce scénario ; D non testée.** La Gate A et le strict export de la bibliothèque active ont repassé la [CI rapide sur HEAD](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43310529201). La démonstration de l'appel au-delà de 32 Ko appartient à R58, et n'est pas refaite dans la R59 compacte.

**Recette R59 utilisée :** installer `dist/AMOSPro_AGA.Lib` R59 dans `APSystem`, redémarrer AMOS et Compiler, importer l'ASC par `Project → Merge ASCII`. Lancer en interprété (Gate B), puis **compiler ce même ASC dans un nouveau fichier exécutable** (Gate C). Résultat attendu : `AGA PROBE RETURNED`, `AGA PROBE AFTER CLOSE RETURNED`, `OPEN 1 DB 1 PAL 1`, `SW0 1 SAFE 1 FILL 1`, `COPY 1 SWAP 1 CLOSED -1`, `RESULT 1`, `CLOSE RETURNED` sans Guru. Le `Program interrupted` de la boucle finale `Do / Wait Vbl / Loop` est normal après interruption manuelle.

**Promotion autorisée et effectuée le 12/11/2026.** Régression complète manuelle [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43312486348) sur le HEAD exact `5f29d78e65b666f7260f5a32e28bd4e8bcf59a4a` (binaire R59 inchangé), après Gates A/B/C ; accord explicite donné par l'auteur. **Gate D physique NON TESTÉE.** La bibliothèque a été copiée à l'octet près dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, sans changer `dist/AMOSPro_AGA.Lib`. Aucun chantier M18 ni autre changement fonctionnel engagé.
