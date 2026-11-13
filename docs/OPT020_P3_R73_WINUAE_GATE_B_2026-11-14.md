# OPT020/P3 — R73 v0.13.18 : Gate B interprétée WinUAE PASS (14/11/2026)

## Identification et statut

- Dépôt : `anthea176/AMOSPro-AGA-Extension`, branche `main`.
- Candidate active non promue : `dist/AMOSPro_AGA.Lib`, R73 v0.13.18, **51 608 octets**, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.
- **Un seul ASC actif** : `tests/current/OPT020_P3_R73_INTERPRETED_01.asc` (version corrigée à deux phases, commit `402fa71b92ae4b7acbf3f1b246627c334364b64c`).
- Validation **réelle en interprété sous WinUAE** : captures graphique et console fournies par l'auteur. Profil prévu : AGA / 68020 14 MHz / JIT OFF / PAL. Les captures attestent les résultats visibles, sans attester indépendamment la configuration interne de WinUAE.
- Gate A native CPU/ABI : **PASS** (144 scénarios + vérifications AP20, [workflow ciblé](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43524215886)).
- **Gate B intégrée R73 : PASS.** Gate C AMOS Compiler : **NON TESTÉE**. Gate D machine physique : **NON TESTÉE**.

## Mesures relevées sur les captures utilisateur

| Groupe | Affichage | Résultat |
|---|---|---|
| P2 opaque/masqué/décalé | `P2 O/M/SHIFT 1 1 1` | PASS |
| P2 clipping gauche/droite/haut/bas | `P2 CLIP L/R/T/B 1 1 1 1` | PASS |
| P2 hors écran / arguments invalides / après fermeture | `P2 OUT/BAD P/L/M/X/NOS 1 0 0 0 0 0` | PASS |
| Écran 4 plans | `OPEN 1 DB 1 SW0 1 SAFE 1` | PASS |
| P1e quatre régions + décalage | `FRAMES 1 1 1 1 SHIFT 1` | PASS |
| P1e clipping et hors écran | `CLIP 1 1 1 1 OUT 1` | PASS |
| P1e bord/portion/opaque | `EDGE/PART/MASK OPAQUE 1 1 1` | PASS |
| P1e refus banque/coordonnées/dimensions/mode | `BAD BANK/X/Y/W/M 0 0 0 0 0` | PASS |
| Ancien Bank Image Draw, Swap, refus sans écran | `LEGACY 1 SWAP 1 NOS 0 CLOSE -1` | PASS |
| Écran 8 plans | `P3 OPEN/DB/SW0/SAFE 1 1 1 1` | PASS |
| Phase P3 Fill/Swap/Close | `P3 FILL/SWAP/CLOSE 1 1 -1` | PASS |
| Fast Icons dessin opaque/masqué/décalé | `FICON DRAW O/M/SHIFT 1 1 1` | PASS |
| Fast Icons capture et 288 octets | `FICON CAP/EQ288 1 1` | PASS |
| Fast Icons clipping gauche/droite/haut/bas/hors écran | `FICON CLIP L/R/T/B/OUT 1 1 1 1 1` | PASS |
| Fast Icons mauvais paramètres | `FICON BAD B/I/M CAPX/B/I 0 0 0 0 0 0` | PASS |
| Fast Icons après fermeture | `FICON NOS DRAW/CAP 0 0` | PASS |
| Chip Free avant/intermédiaire/après | `1660920 / 1660920 / 1660920` | Stable |
| Bilan / fermeture | `RESULT 1`, `CLOSE RETURNED` | **PASS** |

Le rendu AGA photographié est visuellement cohérent pour les formes, régions et masques de la phase AGAPIC4. La console couvre aussi la seconde phase FICON8. Aucun Guru, blocage ou fuite Chip n'est observable pendant ce scénario. **Aucune équivalence automatique pixel par pixel complète, benchmark de gain, Gate C ou Gate D n'est revendiqué.** L'égalité exacte vérifiée dans l'ASC concerne les **288 octets de l'icône capturée**.

## Incident précédent et correction

Le premier essai intégré R73 avait affiché `RESULT 0` parce que l'ASC ouvrait directement un écran **256 couleurs / 8 plans** pour dessiner une banque AGAPIC à **4 plans**, rejetée conformément aux contrats P1e/P2. **Ce n'était pas une preuve de régression dans le binaire R73**.

La correction du commit `402fa71b92ae4b7acbf3f1b246627c334364b64c` a limité le changement à l'ASC et aux garde-fous documentaires : **écran 16 couleurs pour P1e/P2 → fermeture → écran 256 couleurs pour P3**. Le même binaire R73 (SHA ci-dessus) passe désormais la Gate B. L'ASC unique reste dans `tests/current/`, sans changement d'API ni création de R74.

## Suite autorisée par le plan

**P1e, P2 et P3 ont désormais leurs validations interprétées.** La prochaine phase est **une seule Gate C finale AMOS Compiler pour OPT020**, sans lancer des compilations intermédiaires ni des benchmarks. Ne promouvoir R73 vers `LAST_GOOD` qu'après les validations et l'accord explicite de l'auteur. R68 `LAST_GOOD`, archives et `tests/passed/` restent protégés. Le chantier suivant OPT020 est `c2p.library`, puis AGAPIC v2.
