# R78 C2P Blit — test WinUAE Gate B (NON TESTÉ, 14/11/2026)

**Candidate actuelle :** [R78 v0.13.23](../../dist/AMOSPro_AGA.Lib), 55 772 octets, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`, 68 commandes / 75 AP20. **Gate A native CPU PASS — 46 scénarios de pixels, clipping, banque et ABI**. **Gate B R78 NON TESTÉE** ; Gate C Compiler et Gate D Amiga physique non testées. R77 Close Gates A/B fonctionnelles PASS ; R73 `LAST_GOOD` toujours protégée.

**Un seul ASC actif :** [C2P_R78_BLIT_01.asc](C2P_R78_BLIT_01.asc).

## Marche à suivre

1. Installer la bibliothèque candidate R78 à la place de R77 dans le slot AMOS AGA utilisé jusque-là, conserver `LIBS:c2p.library` v1.9 et redémarrer AMOS sous WinUAE (CPU 68020+, chipset AGA).
2. Vérifier que les banques DATA **12 et 13** sont libres avant l'essai. Importer **C2P_R78_BLIT_01.asc** par **Merge ASCII** dans un nouveau programme. **Exécuter en interprété**, ne pas compiler (Gate C prévue à la fin du chantier C2P).
3. Cinq profondeurs 16/32/64/128/256 couleurs. À chaque profondeur, le test crée 5 sprites depuis la banque 13 sur le chunky de banque 12, dont des clips gauche, droit, haut et bas. Il vérifie directement les pixels indexés avec `Peek` et cinq rejets propres (même banque, mauvaises coordonnées/largeur, banque absente, pitch nul, hors écran).
4. La conversion et le double buffering restent explicites : `Aga C2P Convert` puis `Aga Swap`. Le scénario R77 Close est conservé : Close, second Close, Convert/Blit refusés après Close, réouverture, nouveau Blit/Convert/Swap, second Close.
5. Le test envoie désormais **`Amos To Back` automatiquement** avant d'attendre Échap sur l'écran 256 couleurs ; ne pas utiliser Ctrl+C pour finir. Après `Aga Screen Close`, il effectue `Amos To Front`, écrit le rapport dans `RAM:` et termine par `End`.
6. Récupérer **`RAM:C2P_R78_RUNTIME.TXT`** si `Prg State=1`, sinon le fichier nommé selon le mode indiqué. Vérifier `RESULT 1`, `VERDICT PASS`, `PASS_DEPTH 5`, `BLIT_COPY_OK 5`, `BLIT_PIXEL_OK 5`, `BLIT_REJECT_OK 5`, `BLIT_REOPEN_OK 5`, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `CLOSE_COUNT 5`, `ERR 0`, `NOS 0`, et les codes d'erreur I/O `LOG OPEN ERR 0` / `CLOSE ERR 0` en console.

La banque 13 contient un sprite chunky 32x32 de 1024 octets, banque 12 contient l'écran 320x256 de 81920 octets ; elles sont effacées avant le bilan mémoire en cas de fin normale. Le journal `RAM:` est volatile, **le copier sur disque avant relance ou reset**. Un `FAST_DELTA` non nul après un précédent Ctrl+C peut correspondre à une banque restée allouée, et ne démontre pas une fuite mémoire.

[Contrat Blit](../../docs/C2P_R78_BLIT_CONTRACT_2026-11-14.md) · [Gate A R78](../../docs/C2P_R78_BLIT_NATIVE_GATE_A_2026-11-14.md) · [Gate B R77](../../docs/C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md) · [Protocole RAM](../../docs/AMOS_RAM_TEST_LOGGING.md).
