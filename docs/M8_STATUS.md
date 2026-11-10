# M8 — Souris AGA : statut

## R23 0.8.7 — dispatcher IDCMP, Gate A + B PASS

**Validation du 10/11/2026 :** Gate A **CPU/CI PASS** (15 scénarios 68000, CI complète (archive CI privée, run #42899343161)) ; Gate B **AMOS interprété/WinUAE PASS sur les scénarios testés**. La capture utilisateur du programme R23 donne `PRESSED=RELEASED=3`, `AGAIN=0/0`, `KEYS=64/64/-1`, `WAIT=16` (touche A sur AZERTY), `RESULT=1`, `OPEN=DB=LOAD=SWAP=REOPEN=1`, fermetures correctes et `CLOSE X2 RETURNED`.

**Ctrl+C testé séparément :** l'utilisateur confirme « Programme interrompu » à la ligne `_WAITK=Aga Wait Key`, avec **écran Intuition correctement fermé**. Le test Ctrl+C interrompant volontairement le programme, aucun `RESULT=1` n'est attendu pour cette exécution.

- **Binaire validé dans ce périmètre :** `dist/AMOSPro_AGA.Lib` = archive `dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib`, **13 088 octets**, SHA256 `899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23`.
- **Test exact archivé sans modification :** [`tests/passed/M8_R23_IDCMP_QUICK_01.asc`](../tests/passed/M8_R23_IDCMP_QUICK_01.asc), SHA Git `3e73efc9634db4567d20464081ae6f6b8187ad1a`. **Aucun `.asc` actif dans `tests/current/`.**
- **API inchangée (28 commandes) :** événements `IDCMP_MOUSEBUTTONS` pour Pressed/Released, FIFO `RAWKEY` 16 entrées pour `Aga Key/Wait Key` ; conservation des appuis/relâchements entre deux lectures.
- **Limites restantes :** clic droit sans menu pendant l'appui non montré sur les captures finales, gestion du focus réel, saturations/stress prolongés, AMOS Compiler et Amiga physique non testés. Masques = événements fusionnés, pas un compteur de doubles clics. [Rapport R23](M8_IDCMP_R23.md).
- **Protections :** archives R22/R21/R20/R19/R18 et `LAST_GOOD` R10 **inchangées**. M8 peut encore recevoir des tests approfondis ; ne pas déduire une compatibilité exhaustive de cette validation.

---

## R22 0.8.6 — Pressed/Released : Gate A + B PASS

**R22 validée le 10/11/2026 dans le périmètre de son scénario AMOS interprété/WinUAE.** Gate A CPU/CI PASS 25 cas (CI complète (archive CI privée, run #42893816454)) ; Gate B PASS sur capture utilisateur. Les fonctions `Aga Mouse Pressed/Released` utilisent des masques de fronts indépendants ; elles n'absorbent pas les messages clavier.

- **Binaire courant :** `dist/AMOSPro_AGA.Lib`, archive R22 `dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib`, 12 852 octets, SHA256 `96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997`. R21/R20/R19/R18 et `LAST_GOOD` R10 inchangés.
- **Test R22 exact archivé sans modification :** [`tests/passed/M8_R22_MOUSE_EDGES_01.asc`](../tests/passed/M8_R22_MOUSE_EDGES_01.asc). Aucun `.asc` actif dans `tests/current/`.
- **Preuve WinUAE :** `10/11/2026 — capture WinUAE utilisateur : MYGIRL.IFF 320×256×8 ; OPEN=DB=LOAD=SWAP=REOPEN=1 ; BEFORE=-1/-1 ; BASE=0/0 ; PRESSED=3, RELEASED=3, PL=PR=RL=RR=1 ; DONE=1, ERR=0, FRAME=1001 (fin de boucle For) ; KEY=64, MOUSE=(221,185) ; CLOSED=-1/-1, CLOSE2=-1, REOPEN BASE=0/0 ; CLOSE X2 RETURNED ; fin AMOS normale ligne 117. Pas de preuve visuelle de la barre Intuition pendant le clic droit. Clics très courts, perte/reprise de focus réelle, Compiler, Amiga physique et stress non testés.`
- **Réserves :** M8 reste ouvert pour la capture des clics très brefs avec dispatcher Intuition, le focus réel et les autres fonctionnalités (drag/molette). [Contrat R22](M8_MOUSE_EDGES_R22.md).

---

## R21 0.8.5 — RMBTRAP / boutons : Gate A + B PASS

**10/11/2026 : R21 validée par l'utilisateur après test AMOS interprété/WinUAE.** Le clic droit ne déclenche plus la barre de menus Intuition, contrairement à R20 ; les boutons gauche/droit sont utilisables dans le scénario. Gate A **PASS : 11 cas CPU 68000, CI #42887916480 (archive CI privée)** ; Gate B **PASS utilisateur pour ce test**. Aucune nouvelle capture chiffrée R21 fournie : ne pas attribuer à R21 les chiffres de la capture R20.

- **Lib courante :** `dist/AMOSPro_AGA.Lib` **R21 0.8.5**, archive identique `dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib`, **12 016 octets**, SHA256 `a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644`.
- **Code :** `Aga Screen Open` transmet `NewWindow.Flags $00031900` au lieu de `$00021900`, activant `WFLG_RMBTRAP`. Un seul octet de code changé dans l'entrée AP20 #6. Les 30 autres entrées, fonctions `Aga Mouse X/Y/Buttons` et tokens de R20 restent identiques.
- **Test R21 validé :** [`tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc`](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc), conservé **octet pour octet** depuis `tests/current/`. Ce dossier ne contient plus de `.asc` courant.
- **R20 :** `PRESSED=RELEASED=SEEN=3`, `DONE=1`, `IOERR=0`, `KEY=64` et retour AMOS ligne 100 observés ; **menu Intuition persistant**. Test R20 inchangé dans `tests/historical/` ; Gate B R20 partielle.
- **Protections :** archives R20/R19/R18 immuables ; `LAST_GOOD` R10 inchangée.
- **Gates non exécutées :** AMOS Compiler, Amiga AGA réel, stress/fuites et appuis courts entre deux lectures.
- **M8 reste en cours :** `Aga Mouse Pressed/Released` natives, transitions événementielles, focus, drag et éventuelle molette sont à étudier. Le test R21 calcule des fronts *côté AMOS*, pas dans la bibliothèque.

[Compte rendu technique R21](M8_RMBTRAP_R21.md) · [Plan interactions](INTERACTIONS_COLLISIONS.md).

## R20 0.8.4 — historique avec défaut de barre Intuition — boutons souris : candidat de test

**R20 est archivée après un essai WinUAE avec boutons fonctionnels mais défaut d'interface**. Gate A **PASS : 21 tests CPU 68000 et CI complète verte** (run #42883983376 (archive CI privée)), Gate B R20 **partielle (barre Intuition persistante)**.

- Fonction entière ajoutée : `_B=Aga Mouse Buttons`, masque `1=gauche, 2=droit, 4=central`, `0=aucun`, `-1=écran fermé/invalide ou entrée indisponible`.
- Source : `input.device/PeekQualifier()` V36, avec `OpenDevice/CloseDevice` équilibrés et IOStdReq sur la pile ; aucune consommation d'IDCMP clavier ni état permanent.
- R20 : `dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib`, **12 016 octets**, SHA256 `9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe`. R20 archivée, R21 candidate sur `main`, **R19 archive conservée octet pour octet**.
- Builder et tests : `tools/build_m8_mouse_buttons_r20.py`, `tools/test_m8_mouse_buttons_r20.py`, [test AMOS courant](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc).
- Limite : instantanés globaux ; transitions `pressed/released` calculées par le script AMOS entre lectures successives, sans garantie pour les clics plus courts que la période de polling.
- [Protocole R20](M8_MOUSE_BUTTONS_R20.md) ; R19 demeure la dernière version PASS WinUAE.

---

## R19 0.8.3 — positions X/Y validées sous WinUAE

**10/11/2026 : Gate A CPU 68000 PASS (76 cas), CI générale PASS, Gate B AMOS interprété/WinUAE PASS** pour le scénario de position R19. CI #42878271256 (archive CI privée). Gate C AMOS Compiler, Gate D Amiga réel et stress/fuites **NON TESTÉS**.

- Fonctions entières : `_X=Aga Mouse X` et `_Y=Aga Mouse Y`. Coordonnées en pixels logiques, `-1` hors écran/fermé. Non bloquantes et sans consommation des événements clavier.
- Bibliothèque courante : `dist/AMOSPro_AGA.Lib`, **R19 0.8.3, 11 744 octets**, SHA256 `32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295`. Archive identique `dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib`.
- Base R18 Copper PASS WinUAE archivée : `dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib`, inchangée. `LAST_GOOD` R10 **inchangée**.
- [Test AMOS R19 archivé](../tests/passed/M8_R19_MOUSE_POSITION_01.asc), bandeau `M8-R19-MOUSE-POS-01` ; test GitHub conservé **octet pour octet** depuis `tests/current/`, désormais sans `.asc` actif.
- Builder : `tools/build_m8_mouse_position_r19.py` ; test CPU : `tools/test_m8_mouse_position_r19.py`.

### Preuves WinUAE

Deux captures WinUAE le 10/11/2026 : premier essai `P1=(112,65)`, `P2=(24,238)` ; second essai confirmatoire `P1=(0,0)`, `P2=(319,255)` sur `MYGIRL.IFF` 320×256×8. `OPEN=DB=LOAD=SWAP=REOPEN=1`, `BEFORE/CLOSED/CLOSED2=-1 -1`, `KEY=64` deux fois, `POS3=(319,255)`, `CLOSE X2 RETURNED`, retour AMOS normal ligne 87. La seconde capture lève la réserve de position du premier essai.

**Périmètre validé :** positions extrêmes, sentinel `-1` avant ouverture/après fermeture, réouverture, coexistence clavier, fin normale de l'interpréteur, sur le test R19. **M8 reste ouvert :** boutons gauche/droit, fronts appui/relâchement, clics/drag et éventuelle molette non implémentés. M9 hotspots et M10 collisions restent à faire.

Voir [contrat R19](M8_MOUSE_R19.md), [interactions](INTERACTIONS_COLLISIONS.md), [roadmap](ROADMAP.md) et [tests](../tests/README.md). Ne pas promouvoir `LAST_GOOD` sans demande explicite.

---

**Historique :** M7 Copper R16/R17/R18 PASS WinUAE sur leurs scénarios, voir [M7_STATUS](M7_STATUS.md).
