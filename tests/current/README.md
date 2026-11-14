# R80 — IFF vers chunky sous WinUAE

**Candidate de développement R80 v0.13.25** : nouvelle commande `Aga Iff To Chunky(File$,Bank)` ; **Gate A native 68000 PASS**, **Gate B WinUAE non testée**, **Gate C AMOS Compiler non testée**. R73 `LAST_GOOD` inchangée.

**Un seul ASC actif :** [C2P_R80_IFF_CHUNKY_01.asc](C2P_R80_IFF_CHUNKY_01.asc). Le test R79 reste accessible dans l'historique Git ; l'exemple indépendant R79 est conservé dans `examples/c2p_iff_showcase/`.

## Essai

1. Installer `dist/AMOSPro_AGA.Lib` **R80** dans le slot AGA de `APSystem` et garder `LIBS:c2p.library`. WinUAE en AGA, CPU 68020+.
2. Importer l'ASC dans un programme AMOS **vide** avec **Project → Merge ASCII**. Les banques DATA 12 et 13 seront remplacées puis effacées.
3. Sélectionner **n'importe quel IFF/ILBM indexé 320×256, de 4 à 8 plans (16 à 256 couleurs), RAW ou ByteRun1**, sans fichier `.chk`. Les modes HAM/EHB, dual playfield et images masquées ne sont pas pris en charge par R80. L'écran AGA utilise la profondeur du fichier.
4. Observer IFF original → chunky/C2P → montage 3 Blit + 7 Zoom, puis **Échap**. Le programme vérifie 14 correspondances avec la banque source intacte, Close/ReOpen et nettoyage. Pour l'IFF de référence `iff-TEST/AGA_DEMO_320x256_256c.iff`, 14 valeurs numériques historiques restent contrôlées. **Cette image n'est plus obligatoire.**
5. Récupérer le rapport **`RAM:C2P_R80_RUNTIME.TXT`** (`PRG_STATE 1`) ; en interprété strict : `RAM:C2P_R80_INTERPRETED.TXT` ; en compilé : `RAM:C2P_R80_COMPILED.TXT`. Copier avant reset.

**Attendu (ASC corrigé, test WinUAE à confirmer) :** `RESULT 1`, `VERDICT PASS`, `LOAD12_OK 1`, `LOAD13_OK 1`, `CHUNKY_OK 1`, `IFF_OK 1`, `PALETTE_OK 1`, `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1`, `PIXEL_CHECK_COUNT 14`, `REOPEN_OK 1`, `ERR 0`, `CLOSE_RETURNED`. Le journal indique également `IMAGE_DEPTH`, `SCREEN_COLORS`, `GOLDEN_REFERENCE` et `GOLDEN_PIXEL_COUNT` (0 pour les images ordinaires). Conserver la capture et les mesures Chip/Fast du journal. Gate C Compiler toujours distincte.
