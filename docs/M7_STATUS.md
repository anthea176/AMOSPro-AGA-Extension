# M7 — Copper AGA : statut courant

## R18 0.8.2 — `Aga Copper Wait`, `Move`, `End` : **PASS WinUAE (raster RGB4)**

**10/11/2026 — Gate A CPU 68000 : PASS sur 26 scénarios** ([CI préparatoire #42869523014](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42869523014)) ; **CI complète HUNK/AP20/ILBM/M6/M7 : PASS** ([GitHub Actions #42870412601](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42870412601)). **Gate B AMOS interprété/WinUAE : PASS sur le test R18 corrigé, le 10/11/2026.** Raster COLOR00 rouge/vert/bleu/noir visible, comportement des rejets conforme, retour à AMOS ligne 95. **Gate C Compiler et Gate D Amiga AGA réel : NON TESTÉES.**

- **Lib R18 courante validée pour ce scénario :** `dist/AMOSPro_AGA.Lib`, R18 **0.8.2**, **11 480 octets**, SHA256 `600b8c2c38486004adef8c0e7924df877f7dd7829e1c622a89bbdc0db9f9808a`.
- **Archive identique :** `dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib`. **Base R17 validée WinUAE 3/3** conservée intacte dans `dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib`. `LAST_GOOD` reste R10.
- **API nouvelle :** `Aga Copper Wait(v,h)`, `Aga Copper Move(register,rgb4)`, `Aga Copper End`. WAIT ordonnés, COLOR00–31 seulement, max 64 entrées Copper. On/Off empêchent désormais l'édition après activation ; l'entrée R16 Clear passe de CINIT(2) à CINIT(64) ; entrées graphiques M5/M6 inchangées.
- **Test AMOS PASS archivé :** [`tests/passed/M7_R18_COPPER_RASTER_01.asc`](../tests/passed/M7_R18_COPPER_RASTER_01.asc), avec **correction de syntaxe** `X=Aga Copper Off` sur le chemin d'échec (le dépôt contenait un appel de fonction isolé invalide). Les deux captures utilisateur sur MYGIRL.IFF 320×256×8 montrent d'abord les bandes RGB4 visibles, puis les résultats et la fermeture. `tests/current/` ne contient plus de `.asc`.
- **Builder :** `tools/build_m7_copper_raster_r18.py` ; **test CPU :** `tools/test_m7_copper_raster_r18.py`.
- **Résultats observés :** `W1..W4=1`, `M1..M4=1`, `BADREG=0 RGB=0 WAIT=0`, `END=1 END2=0 AFTER=0`, `ON=1 SWAP=1 OFF=1 OFF2=1`, `REOPEN=1 CLEAR2=1 ON2=1 OFF3=1`, `KEY 68`, `CLOSE X2 RETURNED`, fin normale du programme à la **ligne 95**. Pas de Guru ni blocage apparent. **Limites :** pas de preuve d'absence de fuite, pas de stress test, AMOS Compiler et Amiga réel non testés.

**M7 noyau Copper RGB4 : validé pour les scénarios AMOS interprété/WinUAE R16 à R18.** Les effets avancés (palette 24 bits, 256 couleurs), les contraintes temps réel prolongées et les Gates C/D sont hors de cette validation ; voir la [roadmap](ROADMAP.md) pour M8 souris, M9 zones et M10 collisions.

[Spécification et bilan R18](M7_COPPER_R18.md) · [Roadmap](ROADMAP.md).

---

## Historique — R17 0.8.1 : PASS WinUAE (3/3)

**10/11/2026 — Gate A CPU/CI : PASS** ([CI #42866614578](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42866614578), 15 scénarios 68000 et non-régressions R16/M6). **Gate B AMOS interprété/WinUAE : PASS sur 3 exécutions consécutives du test R17, sans incident signalé.** R16 Copper Clear est également validée pour son scénario et archivée.

| Élément | Statut |
|---|---|
| **Lib courante R17 validée sur ce scénario** | `dist/AMOSPro_AGA.Lib`, **R17 0.8.1**, 10 436 octets, SHA256 `cfd73961d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a` |
| **Archive identique** | `dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib` |
| **Base R16 validée** | `dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib`, octets inchangés |
| **LAST_GOOD** | R10 0.6.1, **inchangée** |
| **Nouvelles commandes** | `Aga Copper On`, `Aga Copper Off`, sans paramètres, retour entier 1/0 |
| **Builder / test CPU** | `tools/build_m7_copper_on_off_r17.py` / `tools/test_m7_copper_on_off_r17.py` |
| **Test AMOS PASS, archivé identique** | [`tests/passed/M7_R17_COPPER_ON_OFF_01.asc`](../tests/passed/M7_R17_COPPER_ON_OFF_01.asc) (même blob Git) ; `tests/current/` vide de `.asc` |

**Objectif :** appliquer la liste vide R16 au ViewPort par `Intuition/MakeScreen` puis `RethinkDisplay`, ensuite la détacher et la libérer avec `WaitTOF`, `FreeCopList` et `FreeMem`. Vérifier les erreurs et rollback sans libérer une liste encore rattachée. **Pas d'effet raster** : `Wait/Move/End` restent à développer seulement après ce test. Les routines AP20 R16 et M6 restent protégées, aucun accès direct au matériel.

**Retour utilisateur WinUAE (10/11/2026) : 3 exécutions sans problème.** Capture finale : `M7-R17-COPPER-ON-OFF-01`, `IMAGE 320 X 256 PLANES 8`, `C1 1 ON1 1 SWAP 1`, `OFF1 1 OFF2 1`, `C2 1 ON2 1 OFF3 1`, `REOPEN 1 C3 1`, `ON3 1 OFF4 1`, `KEY 67 CLOSE X2 RETURNED`, puis `End of program at line 83.` **Gate B PASS sur ce scénario (3/3)** ; le fichier `.asc` est archivé sans modification. Cela ne prouve ni l'absence de fuite mémoire, ni la sécurité sous charge, ni le fonctionnement des futurs changements de couleurs pendant le balayage. **Gate C AMOS Compiler et Gate D Amiga réel : NON TESTÉES.** Prochain chantier : R18 `Wait/Move/End` et test raster distinct.

Voir [`M7_COPPER_R17.md`](M7_COPPER_R17.md).

---

## Historique — R16 0.8.0 Copper Clear : PASS AMOS/WinUAE

**10/11/2026 — M7/R16 0.8.0 : PASS sous AMOS Professional interprété/WinUAE pour le scénario Copper Clear ; M7 complet reste en cours.**

- **Binaire candidat :** `dist/AMOSPro_AGA.Lib` = **R16 0.8.0**, **10 036 octets**, SHA256 `ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1`.
- **Archive identique :** `dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib`.
- **Base R15 M6 figée :** `dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib`, les 22 segments précédents **inchangés**. Copy R13, Fill R14 et Clear R15 restent les références validées WinUAE.
- **LAST_GOOD protégé :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1, **inchangé**.
- **Nouvelle fonction :** `_OK=Aga Copper Clear` sans paramètre, **initialise seulement une UCopList vide terminée par CEND**, rattachée au ViewPort du Screen Intuition et destinée au cleanup `CloseScreen`. **Pas de raster visible, pas encore de `Wait/Move/End/On/Off`.**
- **Builder reproductible :** `tools/build_m7_copper_clear_r16.py` ; **tests CPU/ABI :** `tools/test_m7_copper_clear_r16.py`. L'ancien préflight `tools/m7_copper_contract.py` reste un modèle Python indépendant.
- **Test AMOS validé et archivé sans retouche :** [`tests/passed/M7_R16_COPPER_CLEAR_01.asc`](../tests/passed/M7_R16_COPPER_CLEAR_01.asc), blob Git conservé. **Aucun `.asc` dans `tests/current/`.** Capture utilisateur : `M7-R16-COPPER-CLEAR-01`, `IMAGE 320 X 256 PLANES 8`, `C1 1 C2 1 C3 1`, `OPEN 1 REOPEN 1`, `SWAP 1 KEY 67`, `CLOSE X2 RETURNED` puis `End of program at line 74.`
- **Gate A CPU/HUNK/AP20/CI : PASS** ([CI #42864040653](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42864040653) : 13 scénarios 68000, contrôle ABI/allocations, reproductibilité HUNK, non-régression M6). **Gate B AMOS interprété/WinUAE : PASS pour le scénario R16 Clear/Swap/Close/Reopen décrit ci-dessus. Gate C Compiler / Gate D matériel : NON TESTÉES.**

**Périmètre de sécurité :** `ViewPort.UCopIns` et `Screen.UserData` d'un Screen privé, gestion de pointeurs étrangers, aucune écriture Copper matériel, aucune modification des routines R15. **`DBState+20` reste réservé aux notifications Safe/Disp**. Ce candidat ne prouve pas encore la gestion des listes *actives* (On/Off) ; ne pas conclure à la compatibilité de toutes les listes ou du raster.

Pour le détail et le test : [`M7_COPPER_R16.md`](M7_COPPER_R16.md). Architecture globale : [`M7_COPPER_DESIGN.md`](M7_COPPER_DESIGN.md).

**Suite :** le test R16 est archivé à l'identique. Préparer un nouvel incrément indépendant pour `Wait`, `Move`, `End`, `On`, `Off` et le premier raster. Le succès de la fermeture observée ne prouve pas à lui seul l'absence de fuite mémoire ni la sécurité du détachement d'une liste active. Ne pas promouvoir LAST_GOOD sans autorisation.
