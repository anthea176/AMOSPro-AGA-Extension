# M17/R57 — test unique

**Programme :** [`M17_R57_RAST_FILL_01.asc`](M17_R57_RAST_FILL_01.asc), exercice Fill, Clear, Copy, Safe et 40 swaps avec `examples/demo.iff`. Résultat attendu : `RESULT 1`, `CLOSE RETURNED`, compteurs d'erreur 0. La fin est `Do / Wait Vbl / Loop` comme dans le programme réellement utilisé par l'auteur.

**Bibliothèque :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R57 0.13.2, 32 980 octets, SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`, monolithe 30 780 octets. **Gates A CPU/CI, B AMOS interprété/WinUAE et C AMOS Compiler/WinUAE PASS** (captures utilisateur : `RESULT 1`, zéro erreur, `CLOSE RETURNED`, aucun Guru). **Gate D physique non testée.** R56 était PASS en benchmark interprété, FAIL compilé (Guru `8000000B`). R57 teste l'hypothèse du placement sans duplication du helper.

**R54 `LAST_GOOD` protégée.** Branche `main` exclusivement.

**Preuve compilée (12/11/2026) :** `M17-R57-RAST-FILL-01`, `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Aucun Guru. Capture fournie par l'auteur ; ce retour ne constitue pas une mesure de performance. Aucun changement de l'ASC pour enregistrer la validation.

**Performance sur le benchmark V2 compilé R57 (12/11/2026) :** BAR G `41/40/41`, CLEAR G `58/58/58`, `AGA ERR 0`, fin correcte. Médianes Fill/Clear R55 compilée **54/115** → R57 **41/58**, soit **−24,1 % / −49,6 % du temps**. [Rapport](../../benchmarks/RESULTATS_32C_R57_COMPILER_2026-11-12.md). Le benchmark historique ne constitue pas un deuxième ASC actif de `tests/current/`.

**Preuve interprétée (12/11/2026) :** `M17-R57-RAST-FILL-01`, `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. L'éditeur indique `Program interrupted at line 169` et pointe `>>>Wait Vbl` : **arrêt manuel normal dans la boucle finale `Do / Wait Vbl / Loop`**, non un crash. Le test ASC et le binaire ont été conservés sans changement.
