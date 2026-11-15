# Test actif — M19 P2.5 R87 : smoke AMOS simplifié

**Un seul ASC actif** : [M19_P25_R87_BOBS_SMOKE_01.asc](M19_P25_R87_BOBS_SMOKE_01.asc).

- Bibliothèque requise : `dist/AMOSPro_AGA.Lib` **R87 v0.13.32**, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. **Ne pas installer la R84 LAST_GOOD** pour ce test.
- Source directement dérivée de [M19 P2.3 R86 PASS](../passed/M19_P23_BOBS_BATCH_01.asc), sans appel à `Aga Bob Probe`. Crée elle-même ses images et banques DATA, sans ressources externes.
- Contrôle trois refus attendus, trois dessins BOBS, une capture, un Swap explicite, la fermeture et le retour à AMOS. **Ce test ne décode pas les pixels et ne mesure pas les performances.**
- Le programme P2.4 de 611 lignes a été conservé **inchangé, non validé**, dans [tests/design](../design/M19_P24_BOBS_PIXELS_BENCH_01_UNVALIDATED.asc). **Ne pas le traiter comme un résultat PASS.**
- Préflight du skill : `python -B tools/amos_preflight.py --strict-target --fail-on-warnings tests/current/M19_P25_R87_BOBS_SMOKE_01.asc`, ainsi que `python -B tools/test_amos_preflight.py`.
- Exécuter sous WinUAE 68020/14 MHz/PAL/JIT OFF : dans AMOS, **Project -> Merge ASCII**, Runtime puis Compiler V2 du **même** ASC. Récupérer `RAM:M19_P25_RUNTIME.TXT` et `RAM:M19_P25_COMPILED.TXT`.

Attendu pour chacun : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CAPTURE 2`, `DRAW 3`, `REJECT 3`, `SWAPS 1`, `CLOSE_RETURNED 1`.

**Statut avant nouveaux logs : PREFLIGHT PASS (statique) ; Gates B/C R87 NON TESTÉES.** R84 `LAST_GOOD` reste protégée.

[Revue technique et protocole](../../docs/M19_P25_R87_AMOS_SMOKE_REVIEW_2026-11-15.md).
