# M17/R57 — test unique

**Programme :** [`M17_R57_RAST_FILL_01.asc`](M17_R57_RAST_FILL_01.asc), exercice Fill, Clear, Copy, Safe et 40 swaps avec `examples/demo.iff`. Résultat attendu : `RESULT 1`, `CLOSE RETURNED`, compteurs d'erreur 0. La fin est `Do / Wait Vbl / Loop` comme dans le programme réellement utilisé par l'auteur.

**Bibliothèque :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R57 0.13.2, 32 980 octets, SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`, monolithe 30 780 octets. Gate A CPU/CI PASS. **Gates B/C/D R57 NON TESTÉES.** R56 était PASS en benchmark interprété, FAIL compilé (Guru `8000000B`). R57 teste l'hypothèse du placement sans duplication du helper.

**R54 `LAST_GOOD` protégée.** Branche `main` exclusivement.
