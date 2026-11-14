# R77 C2P Close — Gate B fonctionnelle WinUAE PASS (14/11/2026)

**Preuve :** fichier `C2P_R77_RUNTIME.TXT` fourni par l'auteur, avec la bibliotheque candidate R77 v0.13.22 (54 360 octets, SHA256 `81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11`) et l'ASC `tests/current/C2P_R77_CLOSE_01.asc` **avant correction du focus**.

## Journal transmis

```text
TEST C2P-R77-CLOSE-01
VERSION R77 V0.13.22 CANDIDATE
RUN_MODE RUNTIME
PRG_STATE  1
CPU 68030
CPU_ATTNFLAGS  32823
RESULT  1
VERDICT PASS
DEPTH_TESTED  5
PASS_DEPTH  5
FAIL_DEPTH  0
CLOSE_COUNT  5
C2P_CLOSE_OK  5
EMPTY_CLOSE_OK  5
REOPEN_OK  5
ERR  0
NOS  0
CHIP_BEFORE  1661960
CHIP_AFTER  1661960
CHIP_DELTA  0
FAST_BEFORE  135548368
FAST_AFTER  135630312
FAST_DELTA -81944
CLOSE_RETURNED  5
```

## Verdict

**Gate B WinUAE fonctionnelle PASS** : 5 profondeurs (16, 32, 64, 128, 256 couleurs) validees, 5 fermetures C2P explicites, 5 doubles fermetures refusees proprement, 5 reouvertures et reconversions apres fermeture, 5 fermetures d'ecran ; RESULT 1, ERR 0, NOS 0. CPU **68030 declare par Exec**, mode **RUNTIME / PRG_STATE 1**. Ce n'est pas une Gate C Compiler, ni un test Amiga physique.

**Memoire :** Chip Free 1 661 960 -> 1 661 960 (**delta 0**). Fast Free 135 548 368 -> 135 630 312, soit **+81 944 octets libres en sortie**, non pas une fuite. L'ecart est proche des 81 920 octets de banque chunky, plus 24 octets. L'origine exacte des 24 octets n'est pas demontree.

## Incident de focus : explication de l'auteur

L'auteur a indique avoir interrompu un essai precedent par **Ctrl+C**, pensant a un gel. **Le programme test ne mettait pas AMOS a l'arriere-plan avec `Amos To Back`** ; les `Amos To Front` des iterations precedentes laissaient AMOS devant l'ecran AGA. La boucle `Until _K=69` sur `Aga Key` ne recevait donc pas Echap. L'interruption Ctrl+C pouvait contourner `Erase 12` et laisser la banque DATA 12 de 81 920 octets en memoire. Cette sequence explique plausiblement le gain de Fast libre au prochain essai ; sans prouver l'origine de chaque octet.

**Correction du seul ASC** : instruction `Amos To Back` avant l'attente Echap et la phase d'observation AGA, `Amos To Front` maintenu apres `Aga Screen Close`. Ajout d'un garde-fou statique dans `tools/test_current_amos_blocks.py` et d'une regle permanente dans `EXTENSION_SOURCE_RULES.md`. **Ce changement d'ASC n'est pas encore valide sous WinUAE**, et n'implique aucune modification de `AMOSPro_AGA.Lib`.

**Conclusion :** Gate B fonctionnelle R77 PASS ; seconde execution propre utile pour confirmer le delta Fast nul et l'automatisation du focus, mais **elle ne bloque pas le developpement R78 Blit**, dont le contrat est deja approuve. Gate C Compiler et D physique NON TESTEES ; R73 reste `LAST_GOOD`, jamais promue automatiquement.

[Contrat Close R77](C2P_R77_CLOSE_CONTRACT_2026-11-14.md) · [Contrat Blit R78](C2P_R78_BLIT_CONTRACT_2026-11-14.md).
