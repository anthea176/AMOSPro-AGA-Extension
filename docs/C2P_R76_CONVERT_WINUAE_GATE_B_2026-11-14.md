# R76 C2P Open + Convert — Gate B WinUAE PASS (14/11/2026)

## Environnement et evidence

- **Candidate :** `dist/AMOSPro_AGA.Lib` R76 v0.13.21, 54 144 octets, SHA256 `9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897`.
- **Programme actif :** `tests/current/C2P_R76_CONVERT_01.asc` ; ecran AGA 320x256, 4 a 8 plans, 16/32/64/128/256 couleurs. Deux conversions + deux swaps par profondeur, stripe blanche sur la deuxieme image.
- **Preuves utilisateur :** captures WinUAE de la mire 256 couleurs et des retours pour les profondeurs 16/32/64/128, puis fichier texte utilisateur `C2P_R76_RUNTIME.TXT` fourni dans la conversation.
- **Incident de focus resolu :** pendant la pause graphique `Until _K=69` (ligne 138 du script), AMOS etait au premier plan et la touche Echap n'arrivait pas a la fenetre AGA. Ctrl+C interrompait le programme proprement (pas de Guru). L'auteur a bascule le focus avec **Amiga+A**, puis termine le programme et recupere le journal RAM. Ce n'etait pas une panne native de `Aga C2P Convert`.
- **Mode rapporte par AMOS :** `RUN_MODE RUNTIME`, `PRG_STATE 1`. Le manuel AMOS Pro confirme que `Prg State=1` est un environnement runtime (`0` interpreteur, `-1` compile). Ce log **ne constitue pas une preuve de Gate C Compiler** et ne doit pas etre rebaptise « interprete » sans evidence supplementaire.

## Resultats exacts du journal RAM

```text
TEST C2P-R76-CONVERT-01
VERSION R76 V0.13.21 CANDIDATE
RUN_MODE RUNTIME
PRG_STATE  1
CPU 68030
CPU_ATTNFLAGS  32823
RESULT  1
VERDICT PASS
DEPTH_TESTED 5
PASS_DEPTH  5
FAIL_DEPTH  0
CLOSE_COUNT  5
ERR  0
NOS  0
CHIP_BEFORE  1799064
CHIP_AFTER  1799064
CHIP_DELTA  0
FAST_BEFORE  138134008
FAST_AFTER  138215952
FAST_DELTA -81944
CLOSE_RETURNED  5
```

- **Gate B C2P Convert PASS** sur le perimetre observe : 5 profondeurs sur 5, deux conversions/swaps par profondeur (capture console sur 16..128, rendu final 256 + rapport final), cinq fermetures, aucun echec enregistre et retour normal.
- **Chip Free : stable**, 1 799 064 octets avant et apres.
- **Fast Free : +81 944 octets disponibles apres le test**. La valeur `FAST_DELTA=-81944` est calculee comme `before-after` ; ce n'est pas une fuite. L'ecart est de 81 920 (taille banque chunky) + 24 octets : lien plausible avec la gestion de banque, non prouve sans mesure complementaire. Le log est cree **apres** les mesures memoire.
- **CPU :** 68030 selon `ExecBase.AttnFlags` (32823), et non une preuve de materiel Amiga physique. Le log RAM est effectivement produit : l'instrumentation a donc un premier retour runtime positif.
- Ne pas inferer de mesure de vitesse, de validation Amiga reel ou de Compiler.

## Etat du projet apres cette Gate B

- **R76 Gate A CPU 68000/68020 : PASS** (24 scenarios correction input-state + controles C2P).
- **R76 Gate B RPG : PASS** sur retour utilisateur (tests M0).
- **R76 Gate B C2P Open + Convert : PASS** sur captures et journal utilisateur du 14/11/2026.
- **Gate C AMOS Compiler et Gate D Amiga physique : NON TESTEES** ; ne pas anticiper la compilation avant le jalon final du chantier C2P.
- **R76 reste une candidate**. `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R73 (51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`). Aucune promotion sans autorisation expresse.
- Aucun fichier `.Lib` ni ASC historique modifie lors de cette documentation.

[Rapport regression RPG](C2P_R76_RPG_REGRESSION_2026-11-14.md) · [Protocole RAM](AMOS_RAM_TEST_LOGGING.md) · [ASC actif](../tests/current/C2P_R76_CONVERT_01.asc).
