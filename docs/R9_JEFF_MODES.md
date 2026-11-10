# R9 — images Jeff refusées par l'ouverture d'écran (10/11/2026)

**Suite :** le repli NTSC → PAL de R10 ouvre désormais Jeff-Flag ; le retour utilisateur indique un écran trop bas, que l'on peut repositionner manuellement, sans échec du reste du programme. **R11** cible uniquement la présentation initiale, voir `docs/R11_SCREEN_POSITION.md`. Ne pas ré-ouvrir le chantier loader.

## Checkpoint actif R10 0.6.1 — compatibilité modes Jeff (10/11/2026)

**R9 0.6.0 :** Fallout 640×512×4, **4/4 PASS interprété WinUAE** et **PASS AMOS Compiler rapporté par l'utilisateur** pour le scénario complet. Ces validations restent attachées à R9 et son test archivé `tests/passed/R9_PICINFO_A3_REGRESSION.asc`. Pour Jeff-Flag, R9 a renvoyé `OPEN=0` et terminé proprement sans exécuter le loader. R9 est préservée comme repli `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`.

**R10 candidate active, non validée WinUAE :** `dist/AMOSPro_AGA.Lib` et archive `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`, 8 852 octets, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`. **Seul segment AP20 #6 (`Aga Screen Open`) modifié**, avec BSR local remplaçant l'appel OpenScreenTagList et helper de 80 octets. D'abord l'ouverture originale ; si échec sur ModeID NTSC étendu, `ModeNotAvailable` contrôle l'équivalent PAL, puis réessai **avec mêmes largeur/hauteur/profondeur**, sans couper l'image. Si le mode ou le réessai échoue, `OPEN=0` comme R9. `STATE_MODE` conserve le ModeID **logique demandé**, car `Aga Iff Load` doit comparer au CAMG du fichier. Le ModeID physique réel peut donc être PAL après repli ; ce point est documenté et non exposé par l'API.

**Test actif unique :** `tests/current/R10_JEFF_MODE_FALLBACK.asc`, bandeau `R10-JEFF-MODE-FALLBACK-01`, même chemin que le test R9 validé. Commencer avec Jeff-Flag 736×482 ; si ouverture et rendu valides, vérifier Fallout pour non-régression. **Aucun PASS R10 tant qu'AMOS/WinUAE n'a pas été exécuté.** Tests CPU Unicorn ajoutés dans `tools/test_ntsc_pal_r10.py`, résultats d'exécution non confirmés.

**Statut :** `main` et `LAST_GOOD` inchangés ; branche existante `codex/intuition-input-r1`, PR #4 Draft. Interdiction de merger R10 avant Gate A CPU et Gate B runtime ; Gate C AMOS compilé R10 non testé. Références : `docs/R10_NTSC_PAL_FALLBACK.md`, `docs/R9_JEFF_MODES.md` et `tests/README.md`.

---

## Observations runtime, sans extrapolation

- **R9 0.6.0** : Fallout.iff, séquence complète PicInfo/Open/Double Buffer/IFF Load/Swap/Wait Key/Close, **4/4 PASS**. L'utilisateur rapporte d'autres images testées à plusieurs reprises sans plantage, sans noms ni nombre exacts : ne pas les compter comme PASS individualisés.
- **Capture Jeff-Flag.iff** : `Fichier:DH6:Jeff_Flag.iff`, `SIZE 736 X 482 PLANES 4`, `CMAP 16 COMPRESSION 1`, `MODE 102404 COLORS 16`, `OPEN = 0`, `OPEN FAILED`. AMOS revient normalement à `End of program at line 34`. **`Aga Iff Load` et `Aga Swap` ne sont PAS exécutés** ; ce n'est ni une preuve de défaut de décodage ni un plantage.
- L'utilisateur signale que les images Jeff sont les seules qui refusent de s'ouvrir dans ses essais. Ne pas attribuer un `OPEN=0` individuel aux autres fichiers sans capture.

## Caractéristiques réelles du corpus GitHub

Données de `docs/ILBM_INVENTORY.json`, extraites des BMHD/CAMG des fichiers du dépôt :

| Fichier | BMHD | Plans | Compression | CAMG brut | Famille de mode |
|---|---|---:|---|---|---|
| `Jeff-Flag.iff` | 736×482 | 4 | ByteRun1 | `$00019004` | NTSC HiRes Lace |
| `Jeff-Warhead3.iff` | 736×482 | 4 | ByteRun1 | `$00019004` | NTSC HiRes Lace |
| `Jeff-Space2.iff` | 724×482 | 4 | ByteRun1 | `$00019004` | NTSC HiRes Lace |
| `Jeff-OU-3.iff` | 640×400 | 4 | ByteRun1 | `$00019004` | NTSC HiRes Lace |
| `Jeff-Space.iff` | 320×200 | 5 | ByteRun1 | `$00004000` | CAMG legacy ; normalisation du code nécessaire |
| `Amiga fallout.iff` (comparatif) | 640×512 | 4 | ByteRun1 | `$00029000` | PAL HiRes |

`$00019004 = NTSC_MONITOR_ID ($00011000) | HIRESLACE_KEY ($00008004)`.
`$00029000 = PAL_MONITOR_ID ($00021000) | HIRES_KEY ($00008000)`.
Pour `Jeff-Space.iff`, le code actuel `build_m5_generic.py` applique `CAMG & $00008EFD` aux valeurs legacy sans moniteur étendu ; `$4000` doit donc être filtré vers `0` dans `Aga Pic Info(...,6)`. Ne pas traiter ce fichier comme une preuve d'indisponibilité NTSC.

## Diagnostic technique et limite de ce qu'on sait

Les gardes internes de `Aga Screen Open` (code `patch_open`) ont été étendues à des dimensions positives sur WORD signé jusqu'à 32767 ; 736×482 n'est **pas rejeté par le garde de taille de l'extension**. `SA_Width`, `SA_Height`, `SA_Depth`, `SA_DisplayID` sont transmis à `OpenScreenTagList`, avec `SA_AutoScroll=TRUE`. Ensuite R9 ouvre une Window Intuition qui couvre l'écran. Le résultat public `OPEN=0` peut ainsi venir **d'OpenScreenTagList ou d'OpenWindow**, et n'a pas de code de cause exposé actuellement.

D'après le manuel AmigaOS, la largeur d'overscan visible nominalement maximale en NTSC HiRes est **724 px** : les Jeff de 736 px la dépassent de **12 px**. Cela peut poser problème pour l'affichage visible, **sans prouver que c'est la cause de `OPEN=0`**, car `SA_AutoScroll` autorise un bitmap virtuel plus grand. Jeff-OU-3 (640 px) et Jeff-Space2 (724 px) montrent que la résolution seule n'explique pas nécessairement la famille de refus.

**Hypothèses encore ouvertes**, à ne pas présenter comme des conclusions : disponibilité du mode NTSC dans la configuration WinUAE, limites exactes de l'ouverture d'écran/fenêtre, mémoire Chip, ou ModeID refusé par le système.

Le manuel AmigaOS prévoit `SA_ErrorCode` sur `OpenScreenTagList` (`OSERR_NOMONITOR`, `OSERR_UNKNOWNMODE`, `OSERR_NOCHIPMEM`, etc.) et `ModeNotAvailable()` pour établir la cause. La prochaine correction éventuelle doit distinguer ces résultats avant de choisir un repli via la Display Database / `BestModeIDA`. **Ne pas recadrer ou redimensionner automatiquement les bitplans, ne pas écraser CAMG, et ne pas casser le chemin PAL validé.** Si un écran virtuel 736 px est autorisé, conserver le bitmap complet et gérer la zone visible par le système.

## État du chantier

- **R9 inchangée**, binaire actif `dist/AMOSPro_AGA.Lib` ; R8 et `LAST_GOOD` conservés.
- **Aucun nouveau test `.asc`** ; `tests/current/` reste sans test actif après archivage du PASS R9.
- Correction de compatibilité NTSC/modes non disponibles : **pas encore implémentée / pas de runtime PASS**.
- Validation compilée et Gate A Unicorn/CI R9 toujours en attente.
- Branche unique `codex/intuition-input-r1`, PR #4 Draft, `main` inchangée.

## Références AmigaOS

- <https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0661.html> — `graphics/modeid.h`.
- <https://wiki.amigaos.net/wiki/AmigaOS_Manual%3A_Workbench_Monitors> — largeur NTSC HiRes overscan 724.
- <https://wiki.amigaos.net/wiki/Custom_Screen_Type> — `SA_ErrorCode` et codes d'échec.
- <https://wiki.amigaos.net/wiki/Display_Database> — `ModeNotAvailable()` et disponibilité des modes.
- <https://wiki.amigaos.net/wiki/Public_Screen_Type> — autoscroll et bitmap plus large que la zone visible.
- <https://wiki.amigaos.net/wiki/ILBM_IFF_Interleaved_Bitmap> — filtrage des CAMG legacy et repli sur mode disponible.
