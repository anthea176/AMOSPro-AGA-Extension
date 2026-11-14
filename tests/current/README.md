# R81 OPT020 — IFF, Blit et Zoom sous WinUAE

**Candidate de développement R81 v0.13.26** : optimisation CPU 68020 de `Aga C2P Blit`, `Aga C2P Zoom` et `Aga Iff To Chunky`. **Gate A native 68020 PASS (22 Blit / 14 Zoom / 15 lignes IFF), Gate B WinUAE Runtime R81 NON TESTÉE**. Aucun essai AMOS Compiler demandé. R73 `LAST_GOOD` inchangée. La Gate B Runtime R80 (sur l'image 8 plans) était PASS.

**Un seul ASC actif :** [C2P_R80_IFF_CHUNKY_01.asc](C2P_R80_IFF_CHUNKY_01.asc) — même scénario natif IFF/Blit/Zoom 320×256 que R80, **désormais identifié R81 dans le journal**. Ce nom de fichier est conservé pour éviter un second ASC et les régressions de références ; l'exemple indépendant R79 est sous `examples/c2p_iff_showcase/`.

## Essai

1. Installer `dist/AMOSPro_AGA.Lib` **R81 OPT020 (59 972 octets, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`)** dans le slot AGA de `APSystem` et conserver `LIBS:c2p.library`. WinUAE AGA, CPU 68020 minimum.
2. Importer l'ASC dans un programme AMOS **vide** avec **Project → Merge ASCII**. Les banques DATA 12 et 13 seront remplacées puis effacées.
3. Sélectionner **n'importe quel IFF/ILBM indexé 320×256, de 4 à 8 plans (16 à 256 couleurs), RAW ou ByteRun1**, sans fichier `.chk`. Les modes HAM/EHB, dual playfield et images masquées ne sont pas pris en charge par R80. L'écran AGA utilise la profondeur du fichier.
4. Observer IFF original → chunky/C2P → montage 3 Blit + 7 Zoom, puis **Échap**. Le programme vérifie 14 correspondances avec la banque source intacte, Close/ReOpen et nettoyage. Pour l'IFF de référence `iff-TEST/AGA_DEMO_320x256_256c.iff`, 14 valeurs numériques historiques restent contrôlées. **Cette image n'est plus obligatoire.**
5. Récupérer le rapport **`RAM:C2P_R81_RUNTIME.TXT`** (`PRG_STATE 1`) ; en interprété strict : `RAM:C2P_R81_INTERPRETED.TXT` ; en compilé : `RAM:C2P_R81_COMPILED.TXT` (**ce dernier n'est pas demandé**). Copier le rapport avant reset.

**Attendu (Gate B R81 pas encore réalisée) :** `RESULT 1`, `VERDICT PASS`, `LOAD12_OK 1`, `LOAD13_OK 1`, `CHUNKY_OK 1`, `IFF_OK 1`, `PALETTE_OK 1`, `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1`, `PIXEL_CHECK_COUNT 14`, `REOPEN_OK 1`, `ERR 0`, `CLOSE RETURNED`. Le journal indique `IMAGE_DEPTH`, `SCREEN_COLORS`, `GOLDEN_REFERENCE` et `GOLDEN_PIXEL_COUNT` (0 pour une image ordinaire). Aucune Gate C AMOS Compiler n'est prévue sur demande de l'auteur.
