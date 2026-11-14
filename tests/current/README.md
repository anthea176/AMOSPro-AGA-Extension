# Test AMOS actif — R84 AGAPIC v1/v2 (main)

**Unique ASC actif :** [AGAPIC_R84_V1_V2_01.asc](AGAPIC_R84_V1_V2_01.asc). **Unique bibliothèque de travail :** [R84 candidate](../../dist/AMOSPro_AGA.Lib), 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, 76 commandes. **R83 LAST_GOOD protégée :** [AMOSPro_AGA_LAST_GOOD.Lib](../../dist/AMOSPro_AGA_LAST_GOOD.Lib), 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`. Le test R83 précédemment validé est archivé dans [tests/passed](../passed/C2P_R83_MODULAR_01.asc).

## WinUAE — Gate B Runtime puis Gate C Compiler

1. Sauvegarder la bibliothèque AMOS actuelle et l’Interpreter Config. Installer **uniquement** `dist/AMOSPro_AGA.Lib` (R84 candidate) dans `APSystem/AMOSPro_AGA.Lib` (même slot AMOS habituel n°14, s'il est libre). La version `LAST_GOOD` n’est **pas** la R84.
2. Dans le banc R84, **Length(N)** sert uniquement à tester l’existence d'une banque ; **Start(N)** sert à obtenir l'adresse des banques effectivement créées pour `Leek`/`Peek`. Ne jamais remplacer les quatre affectations `_P11.._P14=Start(N)` par `Length(N)` : cela produirait des lectures mémoire invalides (ERR 17).
3. Démarrer WinUAE AGA CPU 68020+ (68030 recommandé), AMOS Professional. Utiliser un programme vide puis **Project → Merge ASCII** avec le seul ASC actif. Laisser les banques **11..15 libres** ; le test refuse de les écraser.
4. Le banc ouvre successivement un écran AGA **320×256×16** puis **320×256×256**. Pour chaque profondeur : capture native v1/v2 opaque et masquée, héritage de l'ancienne API v1, Info champs 1..5, contrôle octet par octet des flux RLE, palette RGB24/ModeID, refus invalides, Save/Erase/Load ABK, Draw/Region/Swap, fermeture et RAM.
5. Journaux : `RAM:AGAPIC_R84_RUNTIME.TXT` puis compiler un **nouvel exécutable** AMOS et relever `RAM:AGAPIC_R84_COMPILED.TXT`. Attendus : `RESULT 1`, `VERDICT PASS`, `PASS_4 1`, `PASS_8 1`, `ERR 0`, `CLOSE_COUNT 2`, `CHIP_DELTA 0`, `FAST_DELTA 0`. Transmettre les deux fichiers et signaler toute anomalie visuelle.

**Statut : Gate A native CPU/CI PASS** (44 tests Info et 47 captures sur vrai cœur 68020 émulé). **Gates B WinUAE Runtime / C AMOS Compiler R84 encore à confirmer.** `PRG_STATE 0` strict et Amiga physique Gate D non testés. Ne pas promouvoir R84 ni déplacer l'ASC dans `tests/passed` avant validation de l'auteur.

[Contrat](../../docs/AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Rapport Gate A](../../docs/AGAPIC_R84_GATE_A_2026-11-14.md).
