# M6 — Blitter AGA : Copy / Fill / Clear validés sous AMOS/WinUAE

**Date du checkpoint : 10/11/2026.** Revalider toujours le HEAD de `main`.

## M6 R15 0.7.2 — `Aga Blit Clear` : PASS AMOS/WinUAE

**Clôture du périmètre M6 sous AMOS Professional interprété/WinUAE le 10/11/2026.** Les commandes `Copy` (R13), `Fill` (R14) et `Clear` (R15) ont chacune un PASS utilisateur confirmé avec `MYGIRL.IFF`. Le périmètre des tests n'inclut **ni AMOS Compiler, ni Amiga réel, ni toutes les conditions matérielles ou de stress**. Revalider toujours le HEAD de `main`.

| Élément | Statut |
|---|---|
| **Candidat courant** | `dist/AMOSPro_AGA.Lib` — **R15 0.7.2**, **9 784 octets**, SHA256 `44530d28cc33ab2aa1bb9bd81aa3f9799e3aca67a714c36891888c3ece4c6e6e` |
| **Archive R15** | `dist/experimental/AMOSPro_AGA_M6_v0.7.2_BLIT_CLEAR_R15.Lib` — contenu identique |
| **Base R14 validée** | `dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib`, SHA256 `a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f` |
| **LAST_GOOD** | R10 0.6.1, **protégée**, sans promotion |
| **Builder** | `tools/build_m6_blit_clear_r15.py`, depuis l'archive R14 figée |
| **CPU/ABI** | `tools/test_m6_blit_clear_r15.py` |
| **Test R15 passé** | `tests/passed/M6_R15_BLIT_CLEAR_01.asc`, bandeau `M6-R15-BLIT-CLEAR-01`, même blob Git que le test exécuté |

**Implémentation :** `_OK=Aga Blit Clear(x,y,w,h)` remet un rectangle du back buffer à l'index couleur **0** en réutilisant exactement la routine R14 `Aga Blit Fill`. Le nouveau code 68000 est un adaptateur de 38 octets : D3=h, A3 contient (w,y,x), reconstitution de la pile temporaire Fill, `D3=0` (pen), BSR vers Fill, restauration SP et **A3 original +12 octets**. R14 entrées 0..19 inchangées, seule l'entrée 20 reçoit le séparateur `GetP`, nouvelle entrée 21. Les tests CPU vérifient la cible BSR et l'ABI.

**Validation : Gate A statique/CPU/CI PASS** (CI #42857827475 (archive CI privée) : 27 scénarios valides, 25 rejetés/erreurs, non-régression Fill/Copy, build reproductible). **Gate B AMOS/WinUAE : PASS pour ce scénario** ; **Gate C AMOS Compiler : NON TESTÉE ; Gate D vrai Amiga : NON TESTÉE**.

**PASS utilisateur du 10/11/2026 (deux captures)** : `M6-R15-BLIT-CLEAR-01` avec `MYGIRL.IFF` (320×256, 8 plans) : deux rectangles colorés, chacun avec intérieur effacé à l'index palette 0, copie du premier en bas, **aucune corruption visible**. Capture de sortie : `F1 1 C1 1 F2 1 C2 1`, `NEG 0 EDGE 0 ZERO 0`, `COPY 1 SWAP 1`, `KEY 97 CLOSE RETURNED`, puis boîte AMOS **`End of program at line 79.`**. Ce retour confirme le clavier, la fermeture et le retour à AMOS pour le scénario réalisé.

**Clôture M6 sur les essais WinUAE :** `Copy` R13, `Fill` R14 et `Clear` R15 **PASS** ; les trois scripts exacts sont dans `tests/passed/`, **aucun `.asc` dans `tests/current/`**. R15 0.7.2 reste la Lib candidate courante dans `dist/AMOSPro_AGA.Lib` et sa copie versionnée est archivée. Aucune modification ni promotion de `LAST_GOOD` R10, des règles ou du prompt universel. Les Gate C et D restent ouvertes si une validation ultérieure est demandée.

Voir [`M6_BLITTER_R15.md`](M6_BLITTER_R15.md).

---

## Historique — R14 Fill validé, base protégée de R15

### R14 0.7.1 — `Aga Blit Fill` : PASS WinUAE

**État au 10/11/2026 :** R14 générée depuis l'archive R13 et **validée sous AMOS Professional interprété / WinUAE pour le scénario Fill + régression Copy**. R13 Copy reste archivée, binaire intact et déjà PASS sur MYGIRL. Compilation et matériel AGA réel non testés.

| Élément | État |
|---|---|
| **Lib candidate** | `dist/AMOSPro_AGA.Lib`, **R14 0.7.1**, 9 712 octets, SHA256 `a8c43c478efdb2ddcb3547a807a2dba60bd125fc0d7ab5bb791ef565aeb90e4f` |
| **Archive exacte** | `dist/experimental/AMOSPro_AGA_M6_v0.7.1_BLIT_FILL_R14.Lib` |
| **Base R13 protégée** | `dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib`, copie WinUAE validée, SHA256 `c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf` |
| **LAST_GOOD** | R10 0.6.1, **inchangé**, aucune promotion |
| **Builder** | `tools/build_m6_blit_fill_r14.py` |
| **CPU/ABI** | `tools/test_m6_blit_fill_r14.py`, avec contrôle de R13 Copy |
| **Test validé et archivé** | `tests/passed/M6_R14_BLIT_FILL_01.asc`, bandeau `M6-R14-BLIT-FILL-01`, contenu inchangé |

La fonction `Aga Blit Fill(x,y,w,h,pen)` écrit un index de couleur dans le back buffer, à travers un `BltBitMap` par plan (`mask=1<<plane`, minterm `$F0` ou `$00`), suivi de `WaitBlit`. Elle valide toutes les dimensions et tous les pointeurs de plans avant la première modification. **R13 segments 0..18 identiques ; entrée 19 Copy avec seul ajout `GetP` ; entrée 20 nouvelle.**

**Gate A : PASS** (CI #42854705517 (archive CI privée) : 56 scénarios CPU R14, non-régression R13 Copy, HUNK/AP20/archives). **Gate B AMOS/WinUAE : PASS pour ce scénario**. Deux captures utilisateur confirment, avec `MYGIRL.IFF` (320×256×8) : trois rectangles remplis (index 15, 63 et 0), copie du premier rectangle en bas, puis `F1 1 F2 1 F0 1`, `COL 0 RECT 0`, `COPY 1 SWAP 1`, `KEY 64 CLOSE RETURNED` et boîte AMOS `End of program at line 77.` **Gate C Compiler : NON TESTÉ. Gate D matériel : NON TESTÉ.**

**Test `M6_R14_BLIT_FILL_01.asc` déplacé tel quel vers `tests/passed/`. Aucun `.asc` actif dans `tests/current/`.** Suite M6 : développer **`Aga Blit Clear`** comme sous-jalon séparé, avec builder, tests CPU et nouveau test AMOS unique. **Aucune promotion de `LAST_GOOD`.** Voir [`M6_BLITTER_R14.md`](M6_BLITTER_R14.md).

---

## Historique — R13 Copy validée (état du précédent candidat)

### R13 0.7.0 — Blit Copy validé sous AMOS/WinUAE

`Aga Blit Copy(sourceX,sourceY,destX,destY,width,height)` : copie dans le back buffer, `graphics.library/BltBitMap` + `WaitBlit`, contrôles de géométrie avant lancement. Seul `Copy` est implémenté ; `Fill` / `Clear` ne le sont pas.

| Élément | Fichier / statut |
|---|---|
| Candidat courant | `dist/AMOSPro_AGA.Lib` — **R13 0.7.0**, 9236 octets |
| Archive du candidat | `dist/experimental/AMOSPro_AGA_M6_v0.7.0_BLIT_COPY_R13.Lib` — contenu identique |
| SHA256 R13 | `c71cab88d2294ed70c019f546d6c60ac72c278c1b625ded07d0aa6603e50a0cf` |
| Base immuable | `dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib` — R12 0.6.3, 8856 octets |
| LAST_GOOD protégé | `dist/AMOSPro_AGA_LAST_GOOD.Lib` — R10 0.6.1, 8852 octets |
| Génération | `tools/build_m6_blit_copy_r13.py`, base R12 archivée (pas la Lib active) |
| Tests CPU | `tools/test_m6_blit_copy_r13.py` |
| Test AMOS validé | `tests/passed/M6_R13_BLIT_COPY_01.asc` — bandeau `M6-R13-BLIT-COPY-01`, fichier inchangé |

## Portes de validation

- **Gate A — CPU/CI : PASS** pour le binaire R13 actif, reproductibilité et 47 images ILBM (CI #42851646766 (archive CI privée)).
- **Gate B — AMOS/WinUAE : PASS** du scénario Blit Copy R13 sur MYGIRL, copie avec chevauchement, retour d'erreur, Swap, clavier et fermeture confirmés.
- **Gate C — AMOS Compiler : NON TESTÉ**.
- **Gate D — vrai AGA : NON TESTÉ**.

R13 est **validée sous AMOS interprété/WinUAE pour ce scénario précis**, sans certification AMOS Compiler ou Amiga réel. Ne pas modifier `LAST_GOOD` sans autorisation. Conserver R12 archivée et les segments déjà validés.

## Validation utilisateur du 10/11/2026

**PASS AMOS/WinUAE, R13 0.7.0, 10/11/2026 :** sur `MYGIRL.IFF` (320×256, 8 plans), le programme `M6-R13-BLIT-COPY-01` montre deux copies correctes, dont une avec chevauchement. Capture finale : `COPY1 1 COPY2 1 BAD 0` ; `SWAP 1 KEY 68 CLOSE RETURNED`. La sortie clavier et le retour après `Aga Screen Close` sont confirmés ; aucun plantage signalé. Les aplats presque noirs proviennent de la zone source de `MYGIRL.IFF` (42,0 % de pixels couleur 0 dans le rectangle 0,0,96,80). **Portée : PASS du scénario AMOS interprété sous WinUAE, et non validation AMOS Compiler, matérielle, ou de tous les cas Blitter.**

**Classement :** `M6_R13_BLIT_COPY_01.asc` déplacé **octet pour octet** de `tests/current/` vers `tests/passed/`. Aucun test `.asc` actif après cette clôture de `Copy`.

## Suite M6

**Prochain incrément : `Aga Blit Fill`, puis `Aga Blit Clear`.** Les deux restent à implémenter et n'ont aucun PASS. Préparer un seul test correspondant au prochain candidat lorsqu'il sera développé. Ne pas demander de relancer `Copy` sans régression constatée.

Voir aussi `docs/M6_BLITTER_R13.md`, `docs/NEXT_SESSION.md`, `EXTENSION_SOURCE_RULES.md` et `docs/M5_STATUS.md`.
