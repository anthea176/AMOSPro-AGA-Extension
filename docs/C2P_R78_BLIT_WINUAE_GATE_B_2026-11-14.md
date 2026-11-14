# R78 v0.13.23 — C2P Blit : Gate B WinUAE PASS (14/11/2026)

## Identité et preuve

- **Candidate testée :** `dist/AMOSPro_AGA.Lib` **R78 v0.13.23**, 55 772 octets, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`, 68 commandes / 75 entrées AP20.
- **Programme :** `tests/current/C2P_R78_BLIT_01.asc`, importé et exécuté sous AMOS/WinUAE.
- **Preuve :** journal utilisateur `C2P_R78_RUNTIME.TXT` fourni le 14/11/2026, mode `RUNTIME` (`PRG_STATE 1`), CPU **68030 signalé par Exec** (`CPU_ATTNFLAGS 32823`). Ceci ne prouve **ni** une exécution AMOS Compiler **ni** une validation sur Amiga physique.
- **Observation visuelle :** l'auteur a vu des blocs se détacher des motifs ; aucune capture n'a été conservée. Cette observation est cohérente avec les copies de rectangles et le clipping prévus dans le test, sans constituer une vérification graphique indépendante pixel par pixel.

## Journal fourni (contenu)

```text
TEST C2P-R78-BLIT-01
VERSION R78 V0.13.23 CANDIDATE
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
BLIT_COPY_OK  5
BLIT_PIXEL_OK  5
BLIT_REJECT_OK  5
BLIT_REOPEN_OK  5
ERR  0
NOS  0
CHIP_BEFORE  1522984
CHIP_AFTER  1522984
CHIP_DELTA  0
FAST_BEFORE  133036864
FAST_AFTER  133036864
FAST_DELTA  0
CLOSE_RETURNED  5
```

## Verdict et limites

**Gate B fonctionnelle R78 PASS sur le scénario couvert :** cinq profondeurs 16/32/64/128/256 couleurs, cinq copies avec clipping, cinq vérifications de pixels indexés et de l'index 0 opaque, cinq ensembles de refus sans écriture, cinq copies après réouverture, cinq fermetures et doubles fermetures correctement traitées. `RESULT 1`, `PASS_DEPTH 5`, `ERR 0`, `NOS 0`, `CLOSE_RETURNED 5`.

**Mémoire stable sur cette exécution :** Chip Free **1 522 984 → 1 522 984** ; Fast Free **133 036 864 → 133 036 864** ; deux deltas **0 octet**. Ceci confirme la fermeture/nettoyage des banques dans le périmètre exécuté, pas l'absence universelle de fuite sur tous les chemins d'erreur possibles.

**Gate A native PASS** dans la [CI du SHA R78](C2P_R78_BLIT_NATIVE_GATE_A_2026-11-14.md) (46 scénarios CPU/pixels). **Gate C AMOS Compiler / WinUAE NON TESTÉE**, **Gate D Amiga physique NON TESTÉE**. R73 v0.13.18 reste `LAST_GOOD` protégée, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`. Aucune promotion ni publication.

## Suite autorisée

Le périmètre C2P actuellement approuvé comprend `Aga C2P Open`, `Convert`, `Close` et `Blit`. L'étape **C2P-5** consiste en **une seule Gate C globale sous AMOS Compiler**, en **réutilisant le même ASC R78**, sans modifier une source qui a passé la Gate B ni créer d'autre commande. [Plan Gate C](C2P_R78_COMPILER_GATE_C_PLAN_2026-11-14.md). Le Zoom reste une **idée distincte** : pas de nouvelle API sans contrat approuvé.

[Contrat R78](C2P_R78_BLIT_CONTRACT_2026-11-14.md) · [État de reprise](NEXT_SESSION.md) · [Roadmap](ROADMAP.md).
