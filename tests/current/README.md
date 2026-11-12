# M17/R57 — test unique

**Programme :** [`M17_R57_RAST_FILL_01.asc`](M17_R57_RAST_FILL_01.asc), exercice Fill, Clear, Copy, Safe et 40 swaps avec `examples/demo.iff`. Résultat attendu : `RESULT 1`, `CLOSE RETURNED`, compteurs d'erreur 0. La fin est `Do / Wait Vbl / Loop` comme dans le programme réellement utilisé par l'auteur.

**Bibliothèque :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R57 0.13.2, 32 980 octets, SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`, monolithe 30 780 octets. **Gates A CPU/CI et C AMOS Compiler/WinUAE PASS** (capture utilisateur : `RESULT 1`, zéro erreur, `CLOSE RETURNED`, aucun Guru). **Gate B R57 interprétée non confirmée ; Gate D physique non testée.** R56 était PASS en benchmark interprété, FAIL compilé (Guru `8000000B`). R57 teste l'hypothèse du placement sans duplication du helper.

**R54 `LAST_GOOD` protégée.** Branche `main` exclusivement.

**Preuve compilée (12/11/2026) :** `M17-R57-RAST-FILL-01`, `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Aucun Guru. Capture fournie par l'auteur ; ce retour ne constitue pas une mesure de performance. Aucun changement de l'ASC pour enregistrer la validation.
