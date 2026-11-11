# Test AMOS actif — R31 0.10.3 AGAPAL Capture

**Un seul ASC à tester :** [`M13_R31_AGAPAL_CAPTURE_01.asc`](M13_R31_AGAPAL_CAPTURE_01.asc) sous AMOS interprété/WinUAE. **Gate A 107 scénarios CPU PASS**, [CI source 33/33 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43027092394) et export 68000 strict PASS. **Gate B WinUAE EN ATTENTE**, Gates C Compiler/D matériel physique NON TESTÉES.

Installer [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **R31 0.10.3** (18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`) directement dans `APSystem` sous son nom exact ; conserver le slot AMOS, quitter et relancer AMOS. R30 0.10.2 reste protégée dans `dist/AMOSPro_AGA_LAST_GOOD.Lib` : **ce n'est pas la candidate R31**.

Depuis un projet AMOS vide : **Project → Merge ASCII** avec l'ASC actif, puis exécuter. **Attention : écrase les banques 10 et 11 et le fichier `RAM:R31_AGAPAL_CAPTURE.ABK`.** Trois captures sont prévues (vert index0, rouge index1, bleu réécrivant index0), puis refus d'index invalides, contrôle absence d'écran et sauvegarde/rechargement ABK AMOS.

Attendu : `CAP0 1 CAP1 1 OVER 1`, `GREEN 255 RED 255 BLUE 255`, `COUNT0 256 COUNT1 256`, `BEFORE 255 AFTER 255`, `BADNEG 0 BAD8 0 BADSIZE 0`, `NOSCREEN 0 SENTINEL 99`, `ABK AGAPAL SIZE 6224`, `RELOAD 255 255 10 56`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Pas de promotion `LAST_GOOD` avant confirmation de ce PASS en WinUAE par l'utilisateur.
