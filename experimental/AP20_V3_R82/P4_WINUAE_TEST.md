# P4 — Test de la véritable séparation R82 (WinUAE, sans promotion)

## Fichiers

- [AMOSPro_AGA_V3_R82_SPLIT_TEST.Lib](AMOSPro_AGA_V3_R82_SPLIT_TEST.Lib)
- [P4_R82_SPLIT_SMOKE.asc](P4_R82_SPLIT_SMOKE.asc)

Ceci n'est **pas** la précédente V3 FIX01 ; il n'existe plus de commande
\`Aga V3 Size Probe\`. La R82 officielle sur \`main\` reste \`LAST_GOOD\`.

## Installation

1. Utiliser une **copie isolée** de l'installation WinUAE AGA/68020+.
2. Sauvegarder dans la **copie** \`APSystem/AMOSPro_AGA.Lib\`.
3. Copier \`AMOSPro_AGA_V3_R82_SPLIT_TEST.Lib\` dans cet \`APSystem\` de
   test, sous le nom \`AMOSPro_AGA.Lib\`.
4. Conserver le **slot 14** déjà configuré pour l'extension et relancer AMOS.
   Ne pas modifier la configuration de l'installation originale.

## Trois essais progressifs

1. **Smoke test sans assets** : dans un programme AMOS vide,
   **Project → Merge ASCII** avec \`P4_R82_SPLIT_SMOKE.asc\`. Exécuter en
   Runtime ; cela appelle un handler AGA réel, puis trois handlers réels
   de C2P, avec paramètres refusés proprement.
   Attendu : \`RESULT 1\`, \`ERR 0\`,
   \`R82_DETECT -1\`, \`C2P_OPEN_REJECT 0\`,
   \`C2P_CLOSE_REJECT 0\`, \`IFF_REJECT 0\`.
   Journal \`RAM:AP20_V3_SPLIT_RUNTIME.TXT\`.
2. **Compiler C** : dans le même environnement WinUAE jetable,
   compiler **un nouvel exécutable** à partir du même test.
   Attendu : journal \`RAM:AP20_V3_SPLIT_COMPILED.TXT\`.
3. **Régressions fonctionnelles complètes** avant toute promotion :
   - AGA/AGAPIC : \`tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc\`
     avec les deux banques \`R82_AGAPIC_V2_BANK10.abk\` et
     \`R82_AGAPIC_V1_BANK12.abk\` dans le même répertoire.
   - C2P : \`examples/c2p_iff_showcase/C2P_IFF_SHOWCASE.asc\` avec
     \`iff-TEST/AGA_DEMO_320x256_256c.iff\` et
     \`iff-TEST/AGA_DEMO_320x256_256c.chk\` dans le même répertoire.
     L'installation \`LIBS:c2p.library\` v1.9 reste nécessaire.

**Attention :** \`C2P_IFF_SHOWCASE.asc\` vérifie C2P et ses pixels,
mais **n'exerce pas** le décodage IFF-to-chunky ajouté en R80.
La P4 n'est pas qualifiée pour l'ensemble des fonctions tant que ces
tests et leurs journaux réels n'ont pas été fournis.

Copier les journaux RAM vers un disque avant réinitialisation.
En cas de plantage, replacer la R82 d'origine dans le \`APSystem\`
de test. Aucun tag, fusion vers \`main\` ni nouvelle \`LAST_GOOD\`.


## Author results: initial P4 smoke PASS

The author provided real logs from both execution modes on 2026-11-14:
[Runtime](../../docs/experiments/evidence/AP20_V3_R82_SPLIT_P4_RUNTIME_2026-11-14.TXT) and
[Compiled](../../docs/experiments/evidence/AP20_V3_R82_SPLIT_P4_COMPILED_2026-11-14.TXT).

Both report `RESULT 1`, `ERR 0`, correct invalid-argument refusal,
and zero Chip/Fast net delta.

**Do not confuse this with complete functional Gate B/C qualification.**
Still required on the P4 library: true AGAPIC R82 image/palette test and
true C2P positive conversion/Blit/Zoom/Close test, first Runtime then
fresh Compiler output. Preserve the R82 LAST_GOOD unchanged.
