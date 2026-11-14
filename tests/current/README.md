# R78 C2P Blit — Gate B WinUAE PASS ; même ASC pour Gate C Compiler (14/11/2026)

**Candidate actuelle :** [R78 v0.13.23](../../dist/AMOSPro_AGA.Lib), 55 772 octets, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`, 68 commandes / 75 AP20. **Gate A native CPU PASS — 46 scénarios de pixels, clipping, banque et ABI**. **Gate B R78 PASS** : journal utilisateur `C2P_R78_RUNTIME.TXT`, `RESULT 1`, 5/5 profondeurs et quatre compteurs Blit à 5, **Chip/Fast delta 0**. **Gate C Compiler et Gate D physique non testées.** R77 Close Gates A/B fonctionnelles PASS ; R73 `LAST_GOOD` toujours protégée.

**Un seul ASC actif :** [C2P_R78_BLIT_01.asc](C2P_R78_BLIT_01.asc).

## Déjà validé en Gate B ; procédure du même test pour Gate C

1. Installer la bibliothèque candidate R78 à la place de R77 dans le slot AMOS AGA utilisé jusque-là, conserver `LIBS:c2p.library` v1.9 et redémarrer AMOS sous WinUAE (CPU 68020+, chipset AGA).
2. Vérifier que les banques DATA **12 et 13** sont libres avant l'essai. Importer **C2P_R78_BLIT_01.asc** par **Merge ASCII** dans un nouveau programme. Pour la **Gate C finale**, **compiler une seule fois ce même programme** sous AMOS Compiler et lancer l'**exécutable compilé** ; ne pas confondre avec une simple exécution interprétée. Voir [plan Gate C](../../docs/C2P_R78_COMPILER_GATE_C_PLAN_2026-11-14.md).
3. Cinq profondeurs 16/32/64/128/256 couleurs. À chaque profondeur, le test crée 5 sprites depuis la banque 13 sur le chunky de banque 12, dont des clips gauche, droit, haut et bas. Il vérifie directement les pixels indexés avec `Peek` et cinq rejets propres (même banque, mauvaises coordonnées/largeur, banque absente, pitch nul, hors écran).
4. La conversion et le double buffering restent explicites : `Aga C2P Convert` puis `Aga Swap`. Le scénario R77 Close est conservé : Close, second Close, Convert/Blit refusés après Close, réouverture, nouveau Blit/Convert/Swap, second Close.
5. Le test envoie désormais **`Amos To Back` automatiquement** avant d'attendre Échap sur l'écran 256 couleurs ; ne pas utiliser Ctrl+C pour finir. Après `Aga Screen Close`, il effectue `Amos To Front`, écrit le rapport dans `RAM:` et termine par `End`.
6. Récupérer **`RAM:C2P_R78_RUNTIME.TXT`** si `Prg State=1`, sinon le fichier nommé selon le mode indiqué. Pour la Gate C, vérifier `RESULT 1`, `VERDICT PASS`, `PASS_DEPTH 5`, `BLIT_COPY_OK 5`, `BLIT_PIXEL_OK 5`, `BLIT_REJECT_OK 5`, `BLIT_REOPEN_OK 5`, `C2P_CLOSE_OK 5`, `EMPTY_CLOSE_OK 5`, `REOPEN_OK 5`, `CLOSE_COUNT 5`, `ERR 0`, `NOS 0`, et les codes d'erreur I/O `LOG OPEN ERR 0` / `CLOSE ERR 0` en console.

La banque 13 contient un sprite chunky 32x32 de 1024 octets, banque 12 contient l'écran 320x256 de 81920 octets ; elles sont effacées avant le bilan mémoire en cas de fin normale. Le journal `RAM:` est volatile, **le copier sur disque avant relance ou reset**. Un `FAST_DELTA` non nul après un précédent Ctrl+C peut correspondre à une banque restée allouée, et ne démontre pas une fuite mémoire.

[Contrat Blit](../../docs/C2P_R78_BLIT_CONTRACT_2026-11-14.md) · [Gate A R78](../../docs/C2P_R78_BLIT_NATIVE_GATE_A_2026-11-14.md) · [Gate B R77](../../docs/C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md) · [Protocole RAM](../../docs/AMOS_RAM_TEST_LOGGING.md).

**Journal Gate B reçu :** [rapport R78](../../docs/C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md), `CHIP_BEFORE 1522984`, `CHIP_AFTER 1522984`, `FAST_BEFORE 133036864`, `FAST_AFTER 133036864` : tous les deltas à 0. **Ne pas modifier le test pour Compiler** : l'ASC ici est celui déjà qualifié en interprété. Conserver une preuve que l'exécutable compilé a réellement été lancé ; `RUN_MODE RUNTIME` seul n'est pas suffisant. Aucune promotion de R73 `LAST_GOOD` n'est autorisée par ce changement de test.
