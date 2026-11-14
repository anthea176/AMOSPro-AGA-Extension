# Reprise actuelle — AMOSPro AGA Extension

## M19 P0 — résultat WinUAE et suppression du clignotement (14/11/2026)

**Validation reçue :** `M19_P0_AMAL_BOBS_RUNTIME.TXT` : `PRG_STATE 1` (Runtime), `CPU 68030`, `RESULT 1`, `ERR 0`, 211 frames, déplacements X/Y = 210/210, aucun refus Draw/Swap, mémoire Chip/Fast à delta 0, `CLOSE_RETURNED 1`. Le rendu des deux Bobs a été confirmé. **Gate B M19 P0 PASS dans ce scénario** ; aucune extrapolation au mode strictement interprété, Compiler ou matériel physique.

**Diagnostic visuel :** le clignotement était lié aux expressions AMAL `Let A=3-A` et `Let A=7-A` (alternance d'image à chaque frame), pas à une erreur observée de dessin/Swap. L'auteur confirme qu'il disparaît en retirant ces expressions. Source `tests/current/M19_P0_AMAL_BOBS_01.asc` mise à jour pour conserver les images fixes 1 et 3. **Nouveau journal de la version corrigée non reçu** ; le PASS chiffré correspond à la version initiale.

**Suite :** P1 = Bobs généraux, transparence, ordre et fond complet sur double buffer, puis animation d'image à cadence réglée. Conserver R84 `LAST_GOOD` et ne pas ajouter d'API sans contrat approuvé. [Rapport](M19_P0_RUNTIME_DIAGNOSTIC_2026-11-14.md) · [Plan](M19_SPRITES_BOBS_AMAL_PLAN.md).

---


## Chantier M19 P0 ENGAGE — 14/11/2026 (apres R84 promue)

**Plan de référence approuvé :** [M19 sprites matériels, Bobs et AMAL](M19_SPRITES_BOBS_AMAL_PLAN.md). Première étape : AMAL manuel (`Synchro Off`, deux programmes `Amal ... To adresse`, `Synchro` dans la boucle BASIC), deux Bobs logiciels via `Aga F Icon` dans le back buffer AGA privé, sans dessin en interruption. **Aucune nouvelle commande native** ; R84 et `LAST_GOOD` restent identiques et protégées.

**Test AMOS courant unique :** `tests/current/M19_P0_AMAL_BOBS_01.asc` (remplace comme banc actif l'ancien R84 déjà figé dans `tests/passed/AGAPIC_R84_V1_V2_01.asc`). Ce P0 est un prototype source et doit être contrôlé sous AMOS/WinUAE ; **Gate B M19 P0 Runtime désormais attestée sur le scénario initial ; Gate C et mode strictement interprété non attestés**. Rapport attendu `RAM:M19_P0_AMAL_BOBS_<RUN_MODE>.TXT`. Suivre [tests/current/README.md](../tests/current/README.md). Un seul ASC courant et aucun binaire M19.

---


## R84 v0.13.29 — PROMUE `LAST_GOOD` le 14/11/2026 (autorisation explicite)

**Circuit unique sur `main` :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib`, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **76 commandes / 85 entrées AP20**, trois modules C2P/IFF/AGA (5 558 / 2 508 / 56 580 octets). **R83 historique** : SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, 64 188 octets, reconstruite par `tools/build_aga_r83_modular.py` et conservée dans Git.

**Validation :** Gate A CPU native/CI PASS (44 cas Info + 47 captures) ; **Gate C AMOS Compiler PASS** sur WinUAE 68030 avec une banque incluse lors de la compilation, 4/8 plans, `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 2`, Chip 0 et Fast **−11 920 octets**. **Gate B Runtime corrigée : NON attestée séparément**, ce que l’auteur accepte en autorisant la promotion, sans nouvel essai. Quatre fichiers ABK restent dans `RAM:` au moment de la mesure Fast ; aucune fuite native n'est établie par ce delta. `PRG_STATE 0` strict et Amiga physique Gate D non testés.

**Test actif unique :** `tests/current/AGAPIC_R84_V1_V2_01.asc`, copie identique figée dans `tests/passed/`. Pas de branche ni binaire parallèle, aucun tag, release GitHub ou publication Aminet. [Rapport de promotion](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Journal compilé](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md).

Les états R84 candidate, R83 et antérieurs ci-dessous sont **historiques**.

---

## HISTORIQUE — R84 v0.13.29 avant promotion (14/11/2026)

- **Unique binaire de travail :** `dist/AMOSPro_AGA.Lib`, R84 **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, 76 commandes / 85 entrées AP20 ; unités C2P 5 558, IFF 2 508, AGA/AGAPIC 56 580 (marge 8 954 octets).
- **`LAST_GOOD` R83 protégée :** `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 64 188 octets, SHA256 `01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb`, ses Gates A/B/C validées. **R84 candidate NON PROMUE.**
- Nouveaux points d’entrée : `Aga Bank Image Info(Bank,Champ)` (5 champs, v1 palette/ModeID absents=0, échec=-1) et `Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` (v1 ou v2). Ancienne `Aga Image Capture` préservée.
- **Gate A native CPU/CI R84 PASS** : 44 cas d'Info v1/v2, 47 captures v1/v2 sur vrai 68020 émulé, structure AP20/ABI, métadonnées/flux RLE, palette/ModeID, banque occupée, mémoire, dispatch.
- **Gates B Runtime WinUAE et C AMOS Compiler EN ATTENTE.** Test unique actif : `tests/current/AGAPIC_R84_V1_V2_01.asc`. Le test R83 est déjà dans `tests/passed`. Exécuter les 2 modes, collecter `RAM:AGAPIC_R84_RUNTIME.TXT` et `RAM:AGAPIC_R84_COMPILED.TXT`. Ne pas déduire une Gate D physique ni `PRG_STATE 0`.
- Pas de nouvelle branche, pas de tag/release/Aminet, pas de binaire parallèle. Ne promouvoir que sur nouvelle autorisation explicite.

[Roadmap](ROADMAP.md) · [Contrat](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Rapport Gate A](AGAPIC_R84_GATE_A_2026-11-14.md).

Les sections R83 et antérieures ci-dessous sont **historiques**.

---

## ÉTAT COURANT — R83 v0.13.28 PROMUE LAST_GOOD (14/11/2026)