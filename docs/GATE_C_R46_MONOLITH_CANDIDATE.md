# AMOS Compiler Gate C — R46 C1 experimental single-segment bridge

**12 novembre 2026 — essai minimal Compiler/WinUAE C1 PASS (confirmation utilisateur). Gate C complète PAS ENCORE VALIDÉE.** La bibliothèque C1 reste expérimentale : aucune promotion ni remplacement des binaires canoniques.

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

## Prochaine validation Compiler — réutiliser les sources déjà passées en interprété

1. Compiler **sans modifier** [`tests/passed/M16_R46_IMAGE_DRAW_01.asc`](../tests/passed/M16_R46_IMAGE_DRAW_01.asc) avec la même candidate C1 installée. Placer [`M16_AGAPIC_SAMPLE_BANK10.abk`](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire courant AMOS. Attention : le test charge la banque 10 et l'écrase si déjà présente. Le nom affiché `R45` dans le dessin est un ancien libellé du test R46, pas une bibliothèque erronée.
2. Exécuter **le nouvel exécutable compilé** sous WinUAE : vérifier que les trois images (opaque/masquées) et le clipping quatre côtés sont visibles, puis que `ERRORS 0 RESULT 1` et `CLOSE RETURNED` s'affichent sans Guru. Ce seul test couvre aussi `Aga Double Buffer`, `Aga Swap`, `Aga Text`, `Aga Box` et le retour à AMOS.
3. Si PASS : compiler ensuite **sans modifier** [`tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc`](../tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc) pour la restauration du curseur et les 500 bascules. Vérifier `RESULT 1`, `CLOSE RETURNED`, absence de perte Chip RAM significative.
4. Si PASS : vérifier la sélection et la libération des fontes via [`tests/passed/M14_R38_FONT_BANK_01.asc`](../tests/passed/M14_R38_FONT_BANK_01.asc), avec son fichier `RAM:AMCAF_FONT9.abk`. Vérifier `RESULT 1` et `CLOSE RETURNED`. Les banques/test sources validés restent inchangés.

Ne pas repasser le test minimal inchangé : il a déjà passé. En cas de Guru, relever le dernier repère et, si possible, le véritable PC de l'exception avant réinitialisation. Pour l'instant, **l'intégration Compiler et les tests de non-régression complets restent à valider**.

## Historique du protocole du premier essai

1. Backup the actually installed APSystem/AMOSPro_AGA.Lib and the interpreter configuration.
2. Copy the experimental C1 library under the exact configured APSystem filename AMOSPro_AGA.Lib. Do NOT replace the canonical GitHub binaries or LAST_GOOD.
3. Fully restart AMOS Professional and AMOS Compiler. Import the existing trace in a new blank project. **Recompile**: a previously compiled executable embeds the OLD library routines and will not test C1.
4. Execute under WinUAE. Pass criterion for this diagnostic is 06 AFTER AGA SCREEN CLOSE and clean program exit without Guru. If Guru returns, capture the true exception PC and preceding trace; a ROM STOP after reset is not the fault PC.
5. If the minimal compiler trace passes, verify mouse cursor cleanup, fonts, double buffer and Aga Image Draw in BOTH interpreted and compiled contexts before a promotion or closure.

**Bilan : tests statiques PASS ; trace minimale compilée sous WinUAE PASS sur retour utilisateur ; non-régression compilée des fonctionnalités non testée.** Ne pas promouvoir C1 en LAST_GOOD à ce stade.
