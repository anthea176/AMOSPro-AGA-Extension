# R12 0.6.3 — correction du deuxième OpenScreenTagList

**Clôture IFF/ILBM 10/11/2026 :** PASS utilisateur HAM6, HAM8, SuperHiRes 1280×256, SuperHiRes Lace 1280×512 ; EHB et Jeff-Flag validés antérieurement. DblPAL/DblNTSC non testés, non bloquants. Compilation R12 et matériel physique non confirmés. R12 et LAST_GOOD R10 inchangés.

**Statut : Jeff-Flag affichée correctement sous WinUAE selon le retour utilisateur du 10/11/2026.** **CI CPU 68000/ILBM/HUNK PASS** ([résultat GitHub Actions](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42836826630)). Non-régression Fallout, compilation R12 et Amiga physique encore à confirmer. Le dernier test R10 avec `Amos To Back` déplacé avant `Aga Screen Open` n'a **strictement rien changé** au défaut de positionnement de Jeff. Il est archivé.

Le contrat officiel Intuition est `OpenScreenTagList(NewScreen=A0, TagList=A1)`. Le premier appel R10 remet A0 à zéro par `SUBA.L A0,A0` (opcode `91C8`), **pas le second** lors du repli NTSC vers PAL. Or A0 est volatil. Un pointeur parasite peut fournir à Intuition une structure `NewScreen` involontaire, avec des paramètres de position non présents dans les tags. Ceci est une **violation ABI démontrée**, et **le retour utilisateur R12 confirme la disparition du mauvais positionnement Jeff sous WinUAE**.

**Correctif R12 :** ajout uniquement de `91C8` avant le deuxième `JSR -612(A6)` ; trois branchements internes relocalisés de +2 octets, sans changement d'instruction autre. Un seul segment AP20 changé : **#6 Aga Screen Open**. Tous les autres sont identiques à R10 (IFF loader, PicInfo A3, DB, Swap, clavier, Close). Aucun `MoveScreen`, `ScreenToFront`, redimensionnement ou nouveau ModeID.

- Active : `dist/AMOSPro_AGA.Lib`, R12, **8856 octets**.
- Archive : `dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib`.
- SHA256 : `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec`.
- Repli **inchangé** : `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`.
- R11 rejetée et M4b historique restent archivées.

Builder reproductible : `tools/build_newscreen_a0_r12.py`. Le test `tools/test_newscreen_a0_r12.py` utilise le vrai code 68000 dans Unicorn et fait **échouer** toute tentative de `OpenScreenTagList` avec A0 non nul. Exécution CI/CPU **PASS** (GitHub Actions, run 42836826630).

**Test archivé :** `tests/passed/R12_JEFF_A0_RETRY.asc`, bandeau `R12-JEFF-NEWSCREEN-A0-01`, PASS Jeff confirmé ; ne pas attribuer ce `.asc` aux essais HAM/SuperHiRes sans preuve.

Références officielles : [OpenScreenTagList](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node03D4.html). PR #4 fusionnée sur `main` le 10/11/2026.
