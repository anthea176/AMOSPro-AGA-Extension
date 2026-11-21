# M19 P2a — Bob collision, nouvelle bibliothèque de test (WinUAE)

**21 novembre 2026 — Candidate installable sur main.** L'auteur a demandé explicitement une nouvelle Lib et un exemple, sans promotion du dernier bon.

## À installer

- [Bibliothèque P2a](../dist/AMOSPro_AGA.Lib) — **129 544 octets**, SHA256 `e2d149f67da9eb3a8c7222113338a8e0ad3f08fb512792a54b825987e88d92fe`, **97 commandes, 198 entrées AP20**, MC68020 minimum.
- [Banc AMOS de campagne](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/8b8830fb4d4308deeed8ec58d79d2a5baf2db226/tests/current/M19_P2A_BOB_COL.asc) — fichier ASCII autonome de 3 358 octets, SHA256 `dfb44261c99979b7000e7ae1b2f0ec364b6538687173f25235a20f007bf5e2f4`.
- [Source builder](../tools/build_m19_p2a_public_in_memory.py), [contrôles API](../tools/test_m19_p2a_public_gate_a.py), [Gate A de la Lib livrée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44908165274).

## Démarrage (WinUAE / AMOS Pro)

1. Dans le dépôt Windows, `git pull origin main`. Copier **uniquement** `dist/AMOSPro_AGA.Lib` dans le slot habituel de l'extension AGA sous `APSystem`; **redémarrer AMOS**.
2. Prendre une session **AGA PAL / MC68020+** (référence utilisateur MC68030, JIT ON). Dans un programme vierge, **Project → Merge ASCII** de `tests/current/M19_P2A_BOB_COL.asc` (ne pas ouvrir avec Load).
3. Lancer en **Runtime** (`PRG_STATE 1`) avec les banques **24 et 25** libres.
4. Lire le fichier `RAM:M19_P2A_BOB_COL.TXT`. Attendu : `RESULT 1`, `ERR 0`, `CHECKS 8`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

La nouvelle fonction numérique `Aga Bob Col(A,B,Mode)` renvoie **1** collision, **0** sans collision, **-1** refus; `Mode=0` rectangles, `Mode=1` masques pixel-exacts. L'exemple vérifie en plus la transparence, deux positions, la limite locale P1d, le reset, le mode invalide et Bob OFF.

**Preuve :** Gate A publique PASS (5 tests natifs emulés et préflight ASC) avec Lib candidate reconstruite et comparée octet à octet. **WinUAE Runtime (Gate B) NON TESTÉ**, **AMOS Compiler (Gate C) NON TESTÉ**, matériel (Gate D) NON TESTÉ. En cas d'échec, fournir le contenu de `RAM:M19_P2A_BOB_COL.TXT` et une capture du point de blocage.

**LAST_GOOD reste P1e**, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42` ; aucune promotion P2a.
