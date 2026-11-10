# M7 / R17 0.8.1 — Copper On / Off : cycle d'activation Intuition

**Statut : Gate A CPU/CI PASS** ([GitHub Actions #42866614578](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42866614578), 15 scénarios 68000, SHA et reproductibilité HUNK/AP20) ; **Gate B AMOS/WinUAE PASS sur 3 exécutions du test R17 le 10/11/2026.** Ce jalon ajoute uniquement `Aga Copper On` et `Aga Copper Off` pour appliquer et détacher par Intuition la liste vide initialisée par **`Aga Copper Clear` R16**. Aucun effet raster n'est attendu tant que `Wait/Move/End` ne sont pas implémentés.

## Artifacts

| Élément | Fichier |
|---|---|
| Lib candidate R17 0.8.1 | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **10 436 octets** |
| Copie versionnée | [`dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib`](../dist/experimental/AMOSPro_AGA_M7_v0.8.1_COPPER_ON_OFF_R17.Lib) |
| SHA256 | `cfd73961d6cf75a6c57ed529b2bacc11908cd96a0aad615e325597d5bfb0a02a` |
| Base R16 VALIDÉE WinUAE | `dist/experimental/AMOSPro_AGA_M7_v0.8.0_COPPER_CLEAR_R16.Lib` (SHA256 `ba55e92f1d50339b50a06c5b1903767bde549e6738dae320a0ef9ead6251bab1`) |
| Repli LAST_GOOD | R10 0.6.1, protégé, **inchangé** |
| Builder | `tools/build_m7_copper_on_off_r17.py` |
| Tests CPU | `tools/test_m7_copper_on_off_r17.py` |
| **Test AMOS PASS archivé identique** | [`tests/passed/M7_R17_COPPER_ON_OFF_01.asc`](../tests/passed/M7_R17_COPPER_ON_OFF_01.asc) ; aucun `.asc` actif |

## Contrat AMOS

```amos
_OK=Aga Copper Clear
_OK=Aga Copper On
_OK=Aga Copper Off
```

- `Aga Copper On` **(entrée AP20 23, aucun argument)** : exige une liste Copper appartenant à l'extension (`Screen.UserData == Screen.ViewPort.UCopIns != 0`). Appelle `intuition.library/MakeScreen(-378)` puis `RethinkDisplay(-390)`. Retour **1** si les deux appels réussissent, **0** sinon. N'alloue et ne libère aucune mémoire.
- `Aga Copper Off` **(entrée AP20 24, aucun argument)** : valide le propriétaire de la liste, place `UCopIns=0`, puis appelle **MakeScreen et RethinkDisplay** avant de libérer la liste intermédiaire avec `graphics.library/FreeCopList(-546)` et le bloc `UCopList` avec `exec.library/FreeMem(-210)`. `WaitTOF(-270)` avant libération pour synchronisation. Met `Screen.UserData=0` après détachement réussi. Retour **1** si libérée, ou si aucun Copper n'était attaché ; **0** pour écran invalide, pointeur étranger ou erreur de reconstruction. Aucun appel à `FreeVPortCopLists`.
- En cas d'échec `MakeScreen` lors de Off : `UCopIns` est rétabli, **aucune libération**. Si `RethinkDisplay` échoue : restauration du pointeur puis tentative de reconstruction de l'affichage d'origine, et **aucune libération**. Une erreur persistante du système doit être traitée comme un échec réel, sans supposer le retour à un état graphique sain.
- Les deux commandes renvoient un entier en D3 et `D2=0`, **A3 inchangé**, SP équilibrée ; autres registres préservés selon l'ABI validée. Aucun accès direct aux registres Copper/DMA.

La R17 est construite **uniquement depuis l'archive R16 figée** : segments 0..21 inchangés ; entrée 22 `Clear` complétée par le séparateur `GetP` AP20 et nouvelle entrée 23 `On` complétée par `GetP`, puis entrée 24 `Off`.

## Test unique AMOS/WinUAE

Sélectionner `MYGIRL.IFF` **320×256×8**, après avoir installé la nouvelle Lib R17. Le script `M7_R17_COPPER_ON_OFF_01.asc` crée l'écran, le double buffer, charge IFF, exécute `Clear/On/Swap`, attend une touche, réalise `Off` deux fois (idempotence), réinitialise et active/désactive à nouveau, puis teste un second cycle d'écran.

- **Effet visible attendu : aucun raster** ; l'image IFF doit rester intacte, sans écran noir ni palette incorrecte.
- **Résultats observés**, capture utilisateur du 10/11/2026 : `C1 1 ON1 1 SWAP 1`, `OFF1 1 OFF2 1`, `C2 1 ON2 1 OFF3 1`, `REOPEN 1 C3 1`, `ON3 1 OFF4 1`, `KEY 67 CLOSE X2 RETURNED`. Le programme se termine normalement à la **ligne 83**. L'utilisateur confirme **3 exécutions sans incident**.
- Aucune fermeture forcée, Guru, gel ou retour à AMOS dégradé. **Ne pas traiter un PASS des appels de retour comme une preuve d'absence de fuite mémoire** ; le comportement d'un vrai affichage raster actif n'est pas encore testé.

## Portes de validation

- **Gate A : PASS** ([CI #42866614578](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42866614578)). AP20/HUNK, SHA, reproduction du binaire, 15 scénarios CPU 68000 (Unicorn/Capstone), registres, A3, SP, propriété, erreurs et rollback, anciens tests ILBM/Blitter/Copper Clear.
- **Gate B : PASS pour les 3 exécutions sous AMOS Professional interprété/WinUAE** du scénario `Clear/On/Swap/Off/Off/Clear/On/Off/Close/Reopen/Clear/On/Off/Close`, et retour AMOS normal ligne 83. Ne pas extrapoler aux listes raster non encore programmées, à l'absence de fuite mémoire ou aux tests prolongés.
- Gate C AMOS Compiler et Gate D Amiga réel : **NON TESTÉES**.

## Suite

**R17 validée et test exact archivé** dans [`tests/passed/M7_R17_COPPER_ON_OFF_01.asc`](../tests/passed/M7_R17_COPPER_ON_OFF_01.asc), sans retouche du contenu. Prochain incrément : **M7/R18 `Aga Copper Wait` / `Move` / `End`**, avec liste blanche des registres couleur, bornes et ordre des WAIT, mémoire sûre et test WinUAE distinct d'un premier raster visible. **M7 complet n'est pas encore terminé.** Ne jamais promouvoir automatiquement `LAST_GOOD`.

## Documentation technique

- [Intuition MakeScreen / RethinkDisplay](https://wiki.amigaos.net/wiki/Classic_Intuition_Screens)
- [Exemple user-Copper : CINIT/CWAIT/CMOVE/CEND et remise à zéro](https://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node059E.html)
- [graphics.library / FreeVPortCopLists (libère aussi les listes système intermédiaires)](https://build.alb42.de/fpcbin/docu/amigaos4/agraphics/freevportcoplists.html)
