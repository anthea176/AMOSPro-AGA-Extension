# AMOS Compiler Gate C — R46 C1 experimental single-segment bridge

**12 novembre 2026 — Gate C du test intégré R46 C1 sous AMOS Compiler/WinUAE : PASS sur capture utilisateur (`RESULT 1`, `CLOSE RETURNED`, 500 bascules/0 erreur, Chip drop 0).** C1 reste expérimentale, la couverture totale des 50 commandes n'est pas revendiquée, et aucune bibliothèque officielle n'est promue.

The user-supplied AMOSPro_AGA.Lib is exactly R46 v0.12.1 (29,288 bytes; SHA256 5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580). The GitHub main branch has since promoted the same R46 to LAST_GOOD after interpreted AMOS/WinUAE Gate B PASS. This experimental compiler bridge does not replace that validated R46, historical R44 or frozen R45.

## Why

The compiled trace established Aga Probe PASS, Aga Screen Open returns 1, then Guru 80000004 during Aga Screen Close, after step 05 and before step 06. Cross-AP20-segment BSR.w displacements are fragile because AMOS Compiler copies library routines independently. The first R44 candidate only repaired four of fourteen identified cross-segment branches. The close path also involves font-state cleanup (8 -> 48 -> 49).

## How C1 works

C1 retains every original R46 68000 instruction, GetP marker, state byte and intra/inter-routine displacement in its original position, but moves the entire 27,856-byte code block into ONE AP20 segment with a 32-byte dispatcher (27,888 bytes total, below 32 KiB). Stub entries for each original public API use Rbsr to call the dispatcher, with an embedded 16-bit offset into that original block. Register D0/A0 and return stack are intended to be preserved by the dispatcher, but this MUST be checked in actual 68000 execution.

The tradeoff is that AMOS Compiler will copy approximately 28 KiB even if only one AGA command is used; this is a compatibility experiment, not the final lean architecture.

## Candidate identity

- Artifact: dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib
- Size: 29,964 bytes
- SHA256: d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b
- Reproducible generator: tools/build_aga_compiler_bridge_r46.py
- Static check: tools/test_aga_compiler_bridge_r46.py
- Trace: tests/diagnostics/R44_COMPILER_STAGE_TRACE.asc (historical file name; tests the INSTALLED library)
- Baseline SHA is locked to the R46 0.12.1 archive. Original code block and the 50 public AMOS API definitions stay byte-for-byte identical.

## Résultat du premier essai compilé C1

**PASS déclaré par l'utilisateur le 12/11/2026.** La trace re-compilée sous WinUAE avec la candidate C1 affiche successivement :

```text
05 BEFORE AGA SCREEN CLOSE
06 AFTER AGA SCREEN CLOSE
COMPILER TRACE COMPLETED
```

Le Guru `80000004` n'a donc pas été reproduit sur ce chemin `Probe → Screen Open → Screen Close → retour AMOS`. C'est une **Gate C smoke PASS**, et **non** une Gate C complète PASS. Le binaire réellement chargé n'a pas été re-hashé depuis WinUAE ; le résultat est rattaché à la C1 fournie pour cet essai. Le benchmark compilé supplémentaire (détaillé ci-dessous) a également fonctionné sans plantage, mais certaines commandes demeurent non testées.

## Deuxième résultat utilisateur : benchmark `graphics_32c_v2.asc` en compilé

**PASS d'exécution / absence de Guru déclaré par l'utilisateur le 12/11/2026**, avec la candidate expérimentale C1 utilisée dans ce diagnostic. La source jointe par l'utilisateur a été lue telle quelle : **369 lignes, 9 495 octets CRLF**, SHA256 `0fcb08cdab1c983b8afdd8eae9e9118341e74143b668e7689ebd59419deb8276`. Aucun chiffre de timings ni capture du résultat final n'a été fourni. Le commentaire initial du source mentionne R44 et une validation interprétée en attente : il est historique et **n'identifie pas** la bibliothèque réellement installée lors du test.

La partie AGA du benchmark utilise trois séries chronométrées, en 320×256×32, de **120 000 `Aga Plot`, 400 `Aga Draw`, 225 `Aga Box`, 8 000 `Aga Circle`, 100 `Aga Blit Fill` et 80 `Aga Blit Clear` par série**. Le code sollicite aussi `Aga Screen Open`, `Aga Double Buffer`, `Aga Palette Set`, `Aga Text`, `Aga Swap`, `Aga Wait Vbl`, `Aga Screen Close` et le retour à l'écran AMOS. Des opérations AMOS natives et AMCAF sont également exécutées dans le même programme.

**Portée du résultat :** stabilité compilée et chemin de fermeture dans un scénario graphique intensif, plus fort que le smoke test précédent ; **pas de mesure numérique validée**, ni preuve que le compteur final `AGA ERR` est nul. Le code incrémente ce compteur uniquement selon les retours de la *dernière* opération de chaque série et certains swaps. Ce test **n'utilise pas `Aga Image Draw`, `Aga Mouse Cursor`, `Aga Font Select` ni `Aga Font Bank Select`**. Conserver la Gate C complète ouverte pour ces régressions ciblées. Éviter tout nouvel essai redondant de la trace minimale ou du benchmark compilé qui viennent de passer.

**Décision :** R46 C1 reste une candidate Gate C expérimentale distincte ; aucune promotion. Les binaires canoniques R46 LAST_GOOD, les archives R44/R45 et la branche `main` restent préservés.

## Troisième résultat utilisateur : `Aga Image Draw` compilé

**Fonctionnement confirmé par l'utilisateur le 12/11/2026** après exécution sous AMOS Compiler/WinUAE du test proposé `tests/passed/M16_R46_IMAGE_DRAW_01.asc` avec la candidate **R46 C1**. La recette utilise la banque `M16_AGAPIC_SAMPLE_BANK10.abk` (DATA AGAPIC), ouvre un écran AGA, exerce `Aga Image Draw` en modes opaque/masqué, avec décalage et clipping, puis appelle `Aga Screen Close`. Le retour « ça fonctionne ! » valide le **test fonctionnel compilé déclaré par l'utilisateur**.

**Limite de preuve :** aucune capture ni transcription chiffrée des lignes finales n'a été fournie dans ce retour ; ne pas inventer `ERRORS 0 RESULT 1`, les valeurs de `CLIP`, ni une égalité mesurée entre Chip RAM avant/après. Ne pas refaire cet essai sans modification de code pertinente.

## Test intégré réalisé : un seul ASC, régressions graphiques et ressources

Une [archive ZIP unique](../examples/COMPILER_R46_ALL_IN_ONE.zip) et un [dossier autonome `examples/compiler_r46_all_in_one/`](../examples/compiler_r46_all_in_one/) ont été préparés : **un seul programme ASCII** `COMPILER_R46_ALL_IN_ONE.asc`, la banque image AGAPIC (10), la fonte AMCAF Hwarf (25), son attribution et la [procédure FR/EN](../examples/compiler_r46_all_in_one/README.md). Il regroupe les tests AGA 2D, `Aga Image Draw`, clipping, modes invalides, double buffer/Swap/Safe, fontes AMCAF et Topaz, **500 bascules du curseur** et restitution du pointeur lors de `Aga Screen Close`, avec bilan `RESULT` après fermeture. Tous les essais se font avec la **candidate expérimentale C1** déjà installée ; aucune bibliothèque officielle modifiée. **Cet exemple a désormais été exécuté en compilé sous WinUAE : PASS confirmé et capture des résultats ci-dessous.** Attention aux banques AMOS 10 et 25 remplacées. Suivre le dossier pour le répertoire courant AmigaDOS.

## Validation utilisateur du test compilé R46 C1 tout-en-un — 12/11/2026

**PASS confirmé sous WinUAE/AMOS Compiler** avec la bibliothèque expérimentale R46 C1. Source [`COMPILER_R46_ALL_IN_ONE.asc`](../examples/compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc), archivée à l'identique dans [`tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc`](../tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc) (Git blob `eded9040e382e9177b3c929bfa19e3c61ee9dd69`, 5 404 octets). **Capture utilisateur fournie et confirmation « c'est parfait ! ».**

~~~text
R46 C1 / COMPILER ALL IN ONE
OPEN 1 DB 1 SWAP 1 BACKSAFE 1
IMAGE O/M/S 1 1 1
CLIP L/R/T/B 1 1 1 1
BAD M/P/L 0 0 0 OUT 1
2D 1 1 1 1
FONT BANK 1 BAD 0
FONT OS 1 RESET 1 TEXT 1 1 1
CUR 500 ERR 0 SHOW 1 1
CUR HIDE 1 1 BAD 0
CHIP BEFORE/END 1847416 1847416 DROP 0
CLOSED -1 NO IMG/CUR/FONT/BANK 0 0 0 0
PALETTE ERR 0 RESULT 1
CLOSE RETURNED
~~~

**Portée :** ouverture/fermeture, images AGAPIC opaques/masquées/décalées et clipping, rejets invalides, dessin 2D, double buffering/Swap/Safe, fontes AMCAF/Topaz, 500 bascules du curseur, état après fermeture. La mémoire libre Chip est identique **sur cet essai** ; cela ne prouve pas l'absence de toute fuite dans l'ensemble de l'API. **Gate C de la recette intégrée C1 : PASS.**

**Limites :** cette preuve concerne **R46 C1 expérimentale**, pas la bibliothèque canonique à 56 segments. Elle ne valide pas une à une les 50 commandes, ni l'Amiga physique (Gate D). **Ne pas promouvoir automatiquement** C1 en LAST_GOOD. Vérifier le coût d'incorporation d'environ 28 Kio et l'ABI du trampoline avant une décision de production. Ne pas refaire les tests déjà passés sans modification pertinente.

## Suite technique après validation fonctionnelle

La recette Gate C intégrée R46 C1 est PASS. **Ne pas redemander les essais Open/Close, benchmark, Image Draw, curseur ou fontes** inchangés. Restent les contrôles d'ABI/relocation du trampoline, l'incorporation du segment monolithique (~28 Kio) et la décision explicite d'intégration du correctif en production. Gate D matérielle et couverture API exhaustive encore ouvertes.

## Historique du protocole du premier essai

1. Backup the actually installed APSystem/AMOSPro_AGA.Lib and the interpreter configuration.
2. Copy the experimental C1 library under the exact configured APSystem filename AMOSPro_AGA.Lib. Do NOT replace the canonical GitHub binaries or LAST_GOOD.
3. Fully restart AMOS Professional and AMOS Compiler. Import the existing trace in a new blank project. **Recompile**: a previously compiled executable embeds the OLD library routines and will not test C1.
4. Execute under WinUAE. Pass criterion for this diagnostic is 06 AFTER AGA SCREEN CLOSE and clean program exit without Guru. If Guru returns, capture the true exception PC and preceding trace; a ROM STOP after reset is not the fault PC.
5. If the minimal compiler trace passes, verify mouse cursor cleanup, fonts, double buffer and Aga Image Draw in BOTH interpreted and compiled contexts before a promotion or closure.

**Bilan actualisé au 12/11/2026 : Gate C du scénario intégré R46 C1 PASS sous WinUAE, capture utilisateur : `RESULT 1`, `CLOSE RETURNED`, 500 curseur/0 erreur, fontes/image PASS, Chip drop 0.** Audit ABI/coût et couverture API exhaustive restent ouverts. **Ne pas promouvoir C1 en `LAST_GOOD` à ce stade.**
