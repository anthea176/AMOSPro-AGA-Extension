# M5 — clôturé (historique conservé)

**M6 est désormais le chantier actif :** statut courant dans [`docs/M6_STATUS.md`](M6_STATUS.md). Les mentions ci-dessous d'une « Lib active R12 » ou « aucun test courant » décrivent le checkpoint M5 et **ne s'appliquent plus à M6**. La R12 archivée reste la base de M6 R13 ; `LAST_GOOD` R10 demeure inchangé.

## CLÔTURE IFF / ILBM R12 — 10/11/2026

**Chantier terminé sur décision utilisateur.** Tests R12 0.6.3 réussis : HAM6, HAM8, SuperHiRes 1280×256, SuperHiRes Lace 1280×512. Jeff-Flag (736×482, NTSC HiRes Lace et position correcte) et EHB avaient déjà été essayés avec succès. **DblPAL et DblNTSC non testés** faute de moniteur, sans caractère bloquant. Ne pas les déclarer compatibles sur cette seule base.

**Portée de la validation :** retour visuel utilisateur sur les nouveaux modes, sans identification précise du `.asc` ni preuve de compilation R12. AMOS Compiler R12, vrai Amiga AGA, stress exhaustif, Fallout sous R12 restent non confirmés ; ils ne rouvrent pas le chantier IFF clos. CI HUNK/AP20/ILBM/CPU [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42838022562).

**État Git :** PR #4 fusionnée sur `main`. `dist/AMOSPro_AGA.Lib` R12 0.6.3, 8856 octets, SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec`. `dist/AMOSPro_AGA_LAST_GOOD.Lib` = R10 0.6.1, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`, **inchangé**.

**Tests :** test Jeff R12 archivé octet pour octet dans `tests/passed/R12_JEFF_A0_RETRY.asc` ; aucun `.asc` dans `tests/current/`. Ne pas attribuer ce script aux essais HAM/SuperHiRes non identifiés. Prochain chantier possible : **M6 Blitter Copy / Fill / Clear**, sans développement commencé. Les anciennes sections ci-dessous sont historiques si contradictoires.

---


## HISTORIQUE — R12 NewScreen et repli PAL (10/11/2026)

**Échec du test précédent :** déplacer `Amos To Back` avant `Aga Screen Open` sous R10 ne change **strictement rien** au placement trop bas de Jeff. Hypothèse éliminée, test archivé `tests/historical/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`.

**Erreur concrète trouvée dans R10 :** lors du second `OpenScreenTagList` (repli NTSC → PAL), le helper restaure A1 (TagList) mais pas A0 (NewScreen). Le premier appel initialise pourtant A0 à NULL ; le second peut hériter d'une valeur volatile après les appels système. R12 ajoute uniquement `SUBA.L A0,A0` (`91C8`) juste avant cet appel, avec les trois branchements internes correctement relocalisés. Les **18 autres segments AP20 sont identiques à R10** ; le loader ILBM, les dimensions, palettes, DB, Swap, clavier, fermeture et gestion du mode restent inchangés. **Le retour WinUAE sur R12 confirme que Jeff est désormais affichée à la bonne position**, ce qui renforce le diagnostic ABI A0 ; les autres formats et la compilation R12 ne sont pas encore validés.

**Binaire actif :** `dist/AMOSPro_AGA.Lib` = R12 0.6.3, **8856 octets**, SHA256 `b4b06bedb955a23dc048ead7f2ecac8bab955591c6bcc094d4d6e6c4bad4eaec` ; archive `dist/experimental/AMOSPro_AGA_M5_v0.6.3_NEWSCREEN_A0_R12.Lib`. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` RESTE R10 0.6.1** (SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`), tel que demandé explicitement. M4b historique et R11 rejetée restent archivés.

**Test unique :** `tests/current/R12_JEFF_A0_RETRY.asc`, bandeau `R12-JEFF-NEWSCREEN-A0-01` : d'abord Jeff-Flag 736×482, vérifier position directe en haut + retour AMOS ; si PASS, Fallout PAL avec le même test. Ce programme conserve l'ordre `Amos To Back` du test R10 qui chargeait les images.

**Tests :** contrôle HUNK/AP20, reproductibilité, ILBM et CPU Unicorn 68000 **PASS en CI** ([run 42836826630](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42836826630)). Jeff-Flag **PASS utilisateur** sous WinUAE, sans nombre d'itérations précisé. **R12 compilée, Fallout sous R12 et matériel physique non confirmés.** `tools/verify_artifacts.py` a été adapté ; les anciens builders R9/R10/R11 n'écrasent plus la Lib active.

Voir `docs/R12_NEWSCREEN_A0.md` et `tests/README.md`. Même branche `codex/intuition-input-r1`, PR #4 Draft, **`main` inchangée**. Ne pas promouvoir R12 dans LAST_GOOD avant validation.

---

## Vérification en cours — ordre AMOS To Back / écran R10 (10/11/2026)

**La R10 active et LAST_GOOD restent intactes.** Un seul test diagnostique (`tests/current/R10_JEFF_AMOS_BACK_BEFORE_OPEN.asc`, bandeau `R10-JEFF-AMOS-BACK-ORDER-01`) déplace `Amos To Back` de l'après-Swap vers **avant `Aga Screen Open`**, avec restauration `Amos To Front` sur échec d'ouverture. Aucun autre changement de logique AGA.

Ce test vise le défaut de position de Jeff observé sur R10 ; le fonctionnement correct **n'est pas encore validé** avec cet ordre. Source AMOS `+W.s` : `TAMOSWb` rend la main au Copper/Workbench. Les Autodocs indiquent déjà `SA_Top=0` par défaut si `SA_Height` est explicite : ajout de tag `SA_Top=0` non justifié. **Ne pas recréer R11** ni modifier le loader. Voir `docs/R10_AMOS_BACK_ORDER.md`.

---

## ÉTAT ACTUEL : R10 restaurée, LAST_GOOD R10, R11 rejetée (10/11/2026)

**R11 0.6.2 REJETÉE sous WinUAE :** l'utilisateur obtient un écran gris au lieu de l'image Jeff. Le débogueur affiche PC `$00F81472`, instruction ROM `STOP #$2000` en mode superviseur. Ce relevé n'établit pas la cause exacte : il ne démontre ni gel CPU ni défaut du loader. La régression graphique par rapport à R10 est en revanche confirmée. La R11 reste conservée dans `dist/experimental/AMOSPro_AGA_M5_v0.6.2_JEFF_POSITION_R11.Lib` et le test de cet échec dans `tests/historical/R11_JEFF_SCREEN_POSITION.asc`.

**Retour à la version fonctionnelle R10 0.6.1** : `dist/AMOSPro_AGA.Lib` = l'archive `dist/experimental/AMOSPro_AGA_M5_v0.6.1_NTSC_PAL_R10.Lib`. Taille **8 852 octets**, SHA256 `e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3`. R10 ouvre et charge Jeff-Flag avec repli NTSC→PAL ; les fonctions DB, Swap, clavier et fermeture fonctionnent selon l'utilisateur. **Limite connue : écran Jeff placé trop bas, repositionnable à la souris.** R9 reste validée 4/4 sur Fallout interprété et en AMOS Compiler selon le retour utilisateur.

**Exception demandée explicitement par l'utilisateur :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` est également remplacé par la **copie binaire identique de R10**. Le LAST_GOOD historique M4b est déjà archivé sans perte à `archive/AMOSPro_AGA_M4b_v0.0.9_R6C_R1_WinUAE_OK.Lib` (même blob Git que l'ancien LAST_GOOD). **R10 est la dernière version M5 fonctionnelle connue, mais le défaut de positionnement et des gates non validés subsistent** : ne pas l'appeler un jalon parfaitement finalisé.

**Reprise :** analyser le cycle de vie de Screen/Window à partir de **R10**, sans modifier les fonctions IFF déjà validées et sans reproduire le helper R11 qui provoque l'écran gris. Aucun nouveau binaire ni test actif créé pour ce retour. `tools/verify_artifacts.py` et le builder historique R11 doivent respecter cette nouvelle référence.

Branche existante `codex/intuition-input-r1` ; PR #4 Draft, **main inchangée**, aucun merge.

---



## Checkpoint R9 0.6.0 — 4/4 PASS WinUAE interprété (10/11/2026)

**Candidat actif :** `dist/AMOSPro_AGA.Lib` = **R9 0.6.0**, 8 772 octets, SHA-256 `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`. Identique à `dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib`; R8 conservée dans `dist/experimental/`, `LAST_GOOD` inchangé.

**Runtime utilisateur :** le 10/11/2026, **4 exécutions successives sans problème** du programme identifié par le bandeau `R9-A3-REGRESSION-01`, avec `Fallout.iff` 640 × 512, 4 plans, compression ByteRun1. Capture : `OPEN=1`, `DB=1`, `LOAD=1`, `SWAP=1`, `KEY=68`, `CLOSE RETURNED`, puis boîte de dialogue AMOS `End of program at line 68`. **Gate B (ce scénario interprété) : PASS 4/4.** Ceci appuie la correction A3, sans démontrer la stabilité de tous les formats ou la qualité pixel à pixel.

**Archivage :** test exact `tests/passed/R9_PICINFO_A3_REGRESSION.asc` (SHA GitHub conservé), aucun `.asc` restant dans `tests/current/`. Le fichier n'a pas été retouché depuis le PASS.

**Restent ouverts :** Gate A — tests CPU Unicorn/CI R9 non confirmés ; Gate C — version compilée ; Gate D — vrai Amiga AGA ; Ctrl+C en cours de Swap et stress multi-IFF hors validation. **Ne pas merger la PR #4 (Draft)** et ne pas promouvoir `LAST_GOOD` avant les gates requis. Même branche `codex/intuition-input-r1`, sans nouvelle branche.

Les autres sections de ce document sont historiques lorsque leurs anciens statuts « candidat courant » ou « non testé » contredisent ce checkpoint. Voir `docs/PICINFO_A3_R9.md` et `tests/README.md`.


## NOUVELLE PRIORITÉ — root cause AMOS LGoto et R9 candidat (10/11/2026)

**Relevé WinUAE décisif :** PC `$4019CAB8` = `ADDA.W (A3),A3`, et `BRA.B $4019CAA8` revient dans `LGoto` (source officielle `AOZ-Studio/AMOS-Professional-Official/+ILib.s` : `LGoto`, lignes 2795–2808). `A3=$403DFA96`, `(A3)=$0000`, `D0/BasA3=$403E39F0`. **La boucle de parcours des structures de contrôle AMOS n'avance pas**. Ce n'est pas une attente clavier ni une routine Double Buffer bloquée.

**Défaut ABI confirmé dans le binaire R8 :** `Aga Pic Info(fichier$,champ)` dépile le premier paramètre avec `MOVE.L (A3)+,D3`, puis le `MOVEM` d'épilogue restaure A3 à sa valeur initiale. Source officielle `+ILib.s` : `Ent_2` empile le premier paramètre sur A3. Ce défaut peut laisser des mots parasites dans la pile de contrôle de l'interpréteur, consommés ensuite par `LGoto`. **Causalité sur WinUAE à vérifier après correction**, mais violation ABI démontrée.

**R9 0.6.0 (expérimental, NON VALIDÉ runtime)** : correction uniquement du segment AP20 n°14 (PicInfo) :
`48E7 EFFE → 48E7 EFEE` et `4CDF 7FF7 → 4CDF 77F7`, permettant la progression d'A3 de 4 octets, sans modifier le reste des commandes. Binaire de 8 772 octets, SHA256 `58312880cf4096170b1361232d298e8b54f762219d22a0e5c83d41d3f1177e7c`.

- <https://github.com/anthea176/AMOSPro-AGA-Extension/blob/codex/intuition-input-r1/dist/experimental/AMOSPro_AGA_M5_v0.6.0_PICINFO_A3_R9.Lib>
- Builder reproductible : `tools/build_picinfo_a3_r9.py`.
- CPU tests Unicorn ajoutés : `tools/test_picinfo_a3_r9.py` ; **résultat CI pas encore établi**.
- Documentation de preuve : `docs/PICINFO_A3_R9.md`.

**Sécurité :** `dist/AMOSPro_AGA.Lib` reste **R8** ; `LAST_GOOD` et `main` inchangés. Branche existante `codex/intuition-input-r1`, PR #4 Draft. Aucun nouveau fichier `.asc` : après préflight CPU, valider R9 avec le **test original déjà existant** dans `tests/passed/M5_R8_ILBM_SINGLE_SWAP.asc` (avec `Aga Wait Key`), sans réécrire le test.

**Compatibilité images Jeff (10/11/2026) :** R9 fonctionne sur plusieurs autres images selon l'utilisateur ; `Jeff-Flag.iff` (736×482×4, CAMG NTSC HiRes Lace `$00019004`) donne `Aga Screen Open=0`, puis retour normal à AMOS ligne 34, **sans crash**. L'IFF n'est pas encore chargé à cette étape. La plupart des Jeff du corpus utilisent le même mode NTSC, tandis que Fallout utilise le mode PAL HiRes `$00029000`. 736 px dépasse les 724 px de l'overscan NTSC HiRes mais `SA_AutoScroll` peut autoriser une image virtuelle plus grande. La cause exacte d'Open=0 (mode indisponible, fenêtre, mémoire ou géométrie) **n'est pas établie** ; voir `docs/R9_JEFF_MODES.md`. **Ne pas modifier R9/loader ni recadrer l'image sans preuve.**


---

## DERNIER CONSTAT R8 : diagnostic clavier non concluant (10/11/2026)

**Capture :** bandeau `R8-FALLOUT-KEY-POLL-01`, puis `IMAGE 640 X 512 PLANS 4` ; aucune autre information visible, curseur texte clignotant, souris mobile, Ctrl+C et Amiga+A inopérants.

**Lecture exacte du source** : le programme n'affiche **aucun checkpoint après `Pic Info` jusqu'à la fin**. Les opérations `Aga Screen Open`, `Aga Double Buffer`, `Aga Iff Load` et `Aga Swap` sont intercalées avant `Amos To Back`, et la boucle `Aga Key` + 500 `Aga Wait Vbl` n'arrive **qu'ensuite**. La limite de 500 VBL ne protège donc **ni les quatre appels précédents, ni une commande d'extension bloquée**. La capture ne prouve **ni un blocage du clavier, ni une absence de RAWKEY, ni un défaut de focus**. Aucun correctif matériel ou logiciel ne doit en être déduit.

**Prochain diagnostic non destructif** dans la session WinUAE encore bloquée : appuyer sur **Shift+F12** pour ouvrir le débogueur WinUAE ; saisir `r` (registres, PC) puis `d` (désassemblage au PC), et conserver la capture. Ne pas redémarrer ni modifier la mémoire avant le relevé. Ne pas relancer un autre test AMOS en aveugle. Le PC permettra de cibler une routine avec davantage de certitude (éventuellement besoin d'un deuxième relevé si tâche système active).

**Statut GitHub :** `R8_FALLOUT_KEY_POLL_SAFE.asc` reclassé `tests/historical/`, **NON VALIDÉ**. Aucun test `.asc` dans `tests/current/`. La Lib R8 0.5.9 et `LAST_GOOD` sont inchangés, PR #4 Draft sur la **même** branche ; pas de merge `main`.

---

## Reprise prioritaire — clavier Intuition après Fallout (10/11/2026)

**Capture utilisateur confirmée :** l'ancienne version de `M5_R8_ILBM_SINGLE_SWAP.asc`, bandeau `M5 R8 - SINGLE ILBM / SWAP / CLOSE`, a affiché `OPEN=1 DB=1 LOAD=1 SWAP=1 KEY=68 CLOSE RETURNED`. Cette version utilise bien `_K=Aga Wait Key`. Elle est rétablie **octet pour octet** dans `tests/passed/` ; **PASS sur cet essai uniquement**, l'intermittence n'est pas résolue.

**Analyse du code R8 :** `Aga Wait Key` attend en boucle `GetMsg` puis `WaitTOF`, sans limite tant qu'aucun RAWKEY n'arrive. `OpenWindow` active la fenêtre via `WFLG_ACTIVATE`, mais Intuition peut différer l'activation ; après les bascules `Amos To Front/Back`, une perte de focus est une **hypothèse sérieuse**, pas un défaut prouvé. Ctrl+C n'est pas interprété si l'événement n'atteint pas le port de cette fenêtre.

**Test courant unique :** `tests/current/R8_FALLOUT_KEY_POLL_SAFE.asc`, bandeau `R8-FALLOUT-KEY-POLL-01`. Identique au chemin Open/DB/Load/Swap validé, mais attend la touche avec `Aga Key` + 500 `Aga Wait Vbl` maximum puis Close. Tenter Espace, puis cliquer dans la fenêtre AGA et Espace si nécessaire. Distinguer touche reçue (`RAWKEY>=0`) d'absence d'événement (`RAWKEY=-1`). **Ce nouveau test n'a pas encore été exécuté sous WinUAE.** Ne pas relancer l'ancien test qui peut rester en attente illimitée.

R8 0.5.9 **inchangée**, aucun correctif binaire ni nouveau token, PR #4 Draft, pas de merge sur `main`. Voir `tests/README.md` et `docs/R8_INPUT_FOCUS_AUDIT.md`.

---

## État WinUAE confirmé à la reprise du 10/11/2026

**Retour utilisateur : `M5_R8_ILBM_SINGLE_SWAP.asc` fonctionne sans problème.** Enregistrer **PASS utilisateur**, avec limite explicite : le nom a couvert plusieurs révisions ; on n'a pas de nouvelle capture attestant laquelle a tourné. La copie versionnée dans `tests/passed/` est celle du test `Open -> DB -> IFF Load -> un Swap -> 50 VBL -> Close`, sans `Aga Wait Key`.

Les précédents PASS Open/DB/Close, un Swap sans IFF, et Fallout Load/Close sans Swap restent acquis. **Aucun PASS supplémentaire n'est attribué à Ctrl+C, `Aga Wait Key` après l'image, à l'affichage pixel à pixel ou au programme compilé.** `tests/current/` est sans test actif, le doublon renommé est dans `historical/`. Aucun nouveau test requis pour l'instant. Binaire R8 0.5.9 inchangé.

---

## Fallout R8 — loader sans Swap valide sous WinUAE (10/11/2026)

Retour runtime utilisateur : `tests/current/M5_R8_ILBM_LOAD_ONLY.asc` avec Fallout 640×512/4 plans : `OPEN=1`, `DB=1`, `IFF LOAD=1`, `Aga Screen Close` retourne, AMOS atteint `End`. **PASS interprété de la séquence Open/DB/Load/Close, sans Swap, sans attente clavier.** Aucun rendu visuel ou résultat compilé validé.

Prochain test ciblé : `tests/current/M5_R8_ILBM_SINGLE_SWAP.asc` (**un seul Swap, 50 VBL d'affichage, Close, sans Aga Wait Key**), avec jalons visibles à chaque retour. R8 0.5.9 inchangée, ne pas merger.

---

## Fallout R8 — blocage AMOS confirmé par l'utilisateur (10/11/2026)

**IMPORTANT : WinUAE n'a pas crashé : son pointeur souris continue de bouger, mais le programme AMOS est figé et Ctrl+C de l'extension n'agit plus.** Le précédent diagnostic « écran noir ou résultat masqué » était insuffisant ; traiter le symptôme comme un blocage du chemin de commande AMOS, pas un résultat de Print caché.

Le test `tests/current/M5_R8_ILBM_SINGLE_SWAP.asc` affiche les métadonnées Fallout puis n'atteint aucun retour exploitable. Il faut localiser la commande bloquante avant de modifier la Lib ou d'exécuter de nouveau un test IFF risqué.

Contrôle indépendant effectué sur le **vrai `Amiga fallout.iff` du dépôt** : BODY ByteRun1 57 687 octets, 2048 lignes de plan au total (512 lignes × 4 plans × 80 octets = **163 840 octets**), toutes les commandes ByteRun1 consommées intégralement, aucune erreur de flux ni octet restant. La suite historique Generic ILBM R2 inclut déjà le fichier avec CPU decode PASS, mais ses fonctions OS simulées ne couvrent pas la synchronisation réelle sous WinUAE. Ces constats ne démontrent ni l'absence de bug dans le décodeur machine ni l'origine du gel.

**Diagnostic non destructif prioritaire dans la session WinUAE déjà figée** : `Shift+F12` pour ouvrir le débogueur, commande `r` pour les registres et le `PC` 68000, puis `d` pour le désassemblage au PC. Demander la capture, sans redémarrer et sans modifier la mémoire. Vérifier si le PC reste sur une boucle de l'extension (loader/synchronisation) ou sur un appel système. Si le debugger n'est pas disponible, éviter les nouveaux essais identiques.

**R8 binaire inchangé** ; une seule branche `codex/intuition-input-r1`, PR #4 Draft, pas de merge sur `main`.


## Fallout IFF R8 : écran noir avant résultats visibles (10/11/2026)

Test `M5_R8_ILBM_SINGLE_SWAP.asc` avec Fallout (640×512, 4 plans, compression 1, ModeID 167936) : capture arrêtée après l'impression de PicInfo, sans image visible ni résultat terminal. **Le test imprime `OPEN` après l'ouverture de l'écran AGA**, donc ces messages peuvent être masqués : le point exact d'arrêt n'est pas identifié par la capture.

R8 reste **PASS 5/5 pour un Swap puis Close sans IFF** ; ne pas étendre ce PASS au loader ni considérer Generic ILBM R2 régressé sans preuve. Aucun changement de Lib, pas de merge.

Nouveau test isolé : `tests/current/M5_R8_ILBM_LOAD_ONLY.asc`. Il fait PicInfo → Open → Double Buffer → `Aga Iff Load` → `Aga Screen Close` → `Amos To Front`, **sans Swap et sans Aga Wait Key**. Le diagnostic est imprimé après la fermeture. Selon le résultat : `IFF LOAD=0` = rejet du chargement ; `IFF LOAD=1` = décodage exécuté mais rendu non testé ; absence de retour = blocage à isoler par instrumentation des étapes Open/DB/Load/Close. Faire un seul essai dans une session WinUAE saine.


## R8 0.5.9 — WinUAE : un Swap puis Close, PASS 5/5 (10/11/2026)

Retour utilisateur sur `tests/current/M5_DB_SYNC_R8.asc` : **5 exécutions consécutives sans crash**, écran 640×512×4 plans, **sans chargement IFF**. Capture : `OPEN=1`, `DB=1`, `SWAP=1`, `Aga Wait Key=68`, `Aga Screen Close` retourne et l'éditeur AMOS réapparaît normalement.

**PASS limité à une seule permutation et fermeture normale.** Plusieurs Swaps, Ctrl+C pendant un Swap, délais Safe/Disp extrêmes, IFF Fallout/Jeff-Flag et scénario compilé restent à valider. Lib R8 8 772 octets, SHA256 `112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2`, dans `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib`.

Test IFF isolé préparé : `tests/current/M5_R8_ILBM_SINGLE_SWAP.asc`, à lancer **uniquement après CI R8 validée**. PR #4 Draft, branche unique `codex/intuition-input-r1`, pas de merge.


## Validation runtime R7 — 10 novembre 2026 (5/5 PASS)

**Retour utilisateur confirmé sous WinUAE : cinq exécutions consécutives sans crash** du test `tests/current/M5_DB_POINTER_R7.asc`, à la géométrie Fallout 640×512×4 plans (ModeID 167936).

`OPEN RETURNED 1` ; `DB RETURNED 1` ; `Aga Wait Key = 64` ; `Aga Screen Close` terminé ; retour AMOS et `End` normaux.

**PASS limité au chemin Open → Double Buffer → Wait Key → Close, sans Swap, sans IFF Load.** Le chemin `ChangeScreenBuffer` puis fermeture reste non validé et potentiellement dangereux. Suite : [contrat Safe/Disp](M5_DB_SWAP_SYNC_DESIGN.md). Ne pas merger sur main.


## Validation CI R7 — 10/11/2026

**12/12 contrôles CPU dédiés PASS** sur GitHub Actions
[run 42814094313](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42814094313).
Binaire reproductible : **7 956 octets**,
SHA256 `e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce`.

Les tests exécutent le segment AP20 10 au niveau 68000 avec des
allocations simulées, vérifient les pointeurs `sb_DBufInfo`, les
ReplyPorts des deux ScreenBuffers, les erreurs partielles, l'ABI et la
fermeture **sans Swap**. Le loader Generic ILBM R2 et les 18 autres
segments sont bit-à-bit identiques à R6.

**Non validé sous WinUAE.** Ne pas lancer le test IFF/Swap sur R7.
Test AMOS isolé : `tests/current/M5_DB_POINTER_R7.asc`.


## R7 0.5.8 — allocation Double Buffer corrigée, runtime en attente

Le diagnostic sans Double Buffer (Fallout 640×512×4) a réussi 3 fois.
Le diagnostic avec allocation Double Buffer reste bloqué après l'affichage
des dimensions, sans preuve que la commande ait déjà été atteinte.

**Défaut source confirmé dans l'allocateur :** les deux accès
`ScreenBuffer.sb_DBufInfo` utilisent un `MOVEA.L $4A80(A0),A0` mal
encodé au lieu de `MOVEA.L 4(A0),A0` suivi du `TST.L`.
Les écritures des ReplyPorts peuvent donc viser une adresse erronée.

Sur la branche isolée `codex/intuition-input-r1`, le candidat R7
corrige les deux accès. Seul le segment AP20 10 change ; R6 reste
archivé, Generic ILBM R2 et PicInfo restent octet pour octet identiques.
Lib courante : `dist/AMOSPro_AGA.Lib`, archive
`dist/experimental/AMOSPro_AGA_M5_v0.5.8_DB_POINTER_R7.Lib`,
SHA256 `e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce`.

**CPU et runtime encore à valider.** R7 ne répare PAS la synchronisation
des notifications après un Swap : scénario Swap/Close toujours interdit.
[Détails](DB_POINTER_R7.md). Aucun merge sur main.


## WinUAE : contrôle écran seul confirmé (10 novembre 2026)

Retour utilisateur avec image Fallout (640 × 512, 4 plans, ModeID 167936, 16 couleurs) : **trois exécutions sans crash** de `M5_ILBM_INPUT_EXIT_DIAG.asc` (version sans Double Buffer, Swap, chargement ILBM ni dessin direct). `Aga Screen Open=1`, `Aga Wait Key` retourne 64, `Aga Screen Close` puis `Amos To Front` et `End` normaux. **Validation runtime PASS pour le chemin simple seulement.**

Cette observation ne valide PAS `Aga Double Buffer`, `Aga Iff Load`, `Aga Swap` ni le cleanup d'une permutation en vol. Le crash original reste attribué à un état non isolé. Prochain test minimal : `tests/current/M5_DB_NO_SWAP_EXIT_DIAG.asc` = Open → Double Buffer → Wait Key → Close → Amos To Front, **sans Swap, IFF Load, Pattern**. Un seul essai sur session propre avant de poursuivre ; pas de test Swap/Close sur R6.


## BLOCAGE R6 — Double Buffer / Swap / Close : risques de corruption mémoire

Retour utilisateur 10/11/2026 : Clown fonctionne plusieurs fois, Fallout 640×512 provoque un crash WinUAE, et le diagnostic à trois phases peut planter à la relance. Quatre minidumps hôtes : 0xC0000005 en lecture, même RIP. **R6 n'est pas validée pour les scénarios DB+Swap+Close.**

La source `build_m4b_r6b_r4.py` contient un défaut réel : après `ChangeScreenBuffer`, les réponses `SafeMessage` et `DispMessage` ne sont plus suivies ; `close_nonblocking` fait `WaitBlit`, puis libère ScreenBuffers/ports sans attendre l'achèvement de la permutation. Le cleanup Ctrl+C partage le risque. Ne pas confondre avec la validation du clavier R6 ni modifier Generic ILBM R2 sans preuve.

**Diagnostic initial enchaîné remplacé par un écran seul, sans DB/Swap/IFF Load.** Pas de merge. Détails : [M5_DB_SWAP_CLOSE_INCIDENT.md](M5_DB_SWAP_CLOSE_INCIDENT.md).


## Incident de validation WinUAE — ILBM + Aga Wait Key (10/11/2026)

**Ne pas déclarer le scénario ILBM intégré PASS. Ne pas merger sur main.**

Retour utilisateur :
- `Jeff-Flag.iff` : PicInfo 736x482, 4 plans, CAMG 102404 (`$00019004`), ByteRun1 ; capture affiche `OPEN = 0`, puis WinUAE 6.0.3 provoque un **crash natif** avec minidump. Cette image est déjà dans l'inventaire statique ILBM.
- `Amiga fallout.iff` : l'écran AGA s'ouvre, mais l'appui sur une touche dans la version adaptée du test ILBM provoque également un crash natif WinUAE. Ainsi l'échec `OPEN=0` n'explique pas tous les crashs.
- Le test spécifique Intuition Input R3–R6 est distinct et avait validé les cycles simples ; **aucune preuve que le décodeur ByteRun1 soit responsable**.

Le test historique `tests/current/M5_GENERIC_ILBM.asc` contient
`Amos To Front` **avant** `Aga Screen Close`, et l'utilisateur l'a adapté avec `Aga Wait Key`. Le contenu exact du test adapté n'est pas encore connu, donc cette séquence est un **suspect**, pas une cause démontrée.

**Nouveau diagnostic sans changement de binaire :**
`tests/current/M5_ILBM_INPUT_EXIT_DIAG.asc` pour exécuter séparément :
1. Open / Pattern / Wait Key / Close sans DB ;
2. Open / Double Buffer / Wait Key / Close sans loader ;
3. Open / Double Buffer / IFF Load / Swap / Wait Key / Close.

Ordre volontaire du diagnostic : `Aga Wait Key -> Aga Screen Close -> Amos To Front`.
On vérifie uniquement la sortie par touche normale, pas Ctrl+C.
Ne pas combiner les phases en cas de crash ; redémarrer WinUAE après un plantage.

**Données nécessaires pour attribuer un crash WinUAE hôte :** minidump
`winuae_x64_6.0.3_R_2026.11.10_12.41.43.dmp`, à examiner au minimum avec
`tools/inspect_winuae_dump.py` (exception, contexte RIP et configuration).
Le minidump ne donne pas automatiquement le PC 68000 invité.
Conserver séparément la capture, le test .asc réellement exécuté et les logs.

**Statut : diagnostic en cours, aucune correction ILBM ou clavier appliquée.**


## Candidat courant — Intuition Input R6 0.5.7

Retour runtime utilisateur sur R5 : **Ctrl+C interrompt bien AMOS**, mais
Workbench reste affiché à la place de l'éditeur. R6 exécute l'appel
natif AMOS `EcCalD AMOS_WB,1` entre le cleanup R3 et le Break natif R5.

`Aga Screen Close`, Double Buffer, Generic ILBM R2 et PicInfo restent
identiques au R5. Segments 0–16 inchangés.
Lib `dist/AMOSPro_AGA.Lib` et archive
`dist/experimental/AMOSPro_AGA_M5_v0.5.7_INTUITION_INPUT_R6.Lib`.
7 948 octets ; SHA256 :
`729fc13efbaa710a371048353368ffe3dd5af0a23d0043d1e6ee3bcf2e5330d9`.

**Statique PASS ; tests CPU R6 et restauration visuelle WinUAE en attente.**
[Diagnostic détaillé](INTUITION_CTRL_C_R6.md). Historique ci-dessous.


## Candidat expérimental courant — Intuition Input R5 (0.5.6)

Suite au retour runtime R4, **Ctrl+C ne provoquait pas le Break AMOS** :
seul le code C (51) était retourné. R5 force l'appel au test natif
`Rjsr L_Test_PaSaut` après nettoyage AGA et restauration des registres.
Ctrl seul reste ignoré par `Aga Wait Key`, conformément au R4 ;
fermeture de l'écran en boucle simple confirmée depuis R3.

Candidat : `dist/AMOSPro_AGA.Lib` (archive R5 0.5.6).
SHA256 : `3de03160c458f5c6990e18e450ef9d0a34ada950b59d83dd8cc2fbac271f29c5`.
**Statique PASS ; CPU CI et Ctrl+C runtime NON VALIDÉS.** Ne pas merger.

[Diagnostic et validation R5](INTUITION_CTRL_C_R5.md).
Les sections « candidat courant » antérieures ci-dessous sont historiques.


## Candidat courant — R2 0.5.1

R1 rejeté après le défaut runtime du dernier plan. R2 synchronise le Blitter avant
le décodage avec écriture, sans changer palette/décodeur/Swap.
[Détails et SHA256](GENERIC_R2.md) ; 41/41 tests CPU et Blitter différé PASS,
validation visuelle R2 en attente. Les sections R1 ci-dessous sont historiques.

## Candidat courant — Generic ILBM R1 0.5.0

`dist/AMOSPro_AGA.Lib` = candidat générique expérimental, 6436 octets.
SHA256 : `b9bcf0efc444edc6d284988feabebcc33cd7ad88b21f1231ff155380f1b5941a`.
Base exclusive R5 0.4.6 ; R5R1/R5R2 restent rejetés. R5 et LAST_GOOD inchangés.
41/41 images PASS au décodeur Python et à l'exécution 68000 avec appels OS simulés.
**AMOS interprété/compilé et rendu visuel : à valider, aucun PASS revendiqué.**
Test unique : `tests/current/M5_GENERIC_ILBM.asc`.
Voir [architecture, limites et reproduction](GENERIC_ILBM.md) et [inventaire](ILBM_INVENTORY.md).

## Historique antérieur (les mentions « courant » ci-dessous sont historiques)

## Base de référence

**M5.2 R4 0.4.5**

SHA256 :

`b09a94bd4e1ce1487e2776c39e1dd3f75752dcf6f472261af178f47b584b2178`

### Runtime confirmé

- Clown.iff — PASS ;
- MYGIRL.IFF — PASS ;
- DBZ01 / INTRO / KNIGHT03/07/08 / RANMA06 — PASS ;
- KEKKO.IFF — BODY correct mais palette 16 couleurs incorrecte.

## Diagnostic KEKKO verrouillé

- Open/Close 16 couleurs — PASS ;
- P0 = 266241 — PASS ;
- P1 = 282856 — PASS ;
- P2 = 2319534 — PASS ;
- P3 = 158428 — PASS.

Les quatre bitplanes du back-buffer correspondent exactement au BODY source. Le décodeur 4 plans n'est donc pas en cause.

Le diagnostic temporaire `Aga Plane Map` est abandonné. Aucun nouveau token diagnostic n'est conservé.

## Cause ciblée

Le loader R4 applique le CMAP couleur par couleur avec `SetRGB32()`.

L'Autodoc graphics.library précise que `SetRGB32()` ne modifie pas une couleur considérée comme inutilisée. Ce comportement est inadapté au chargement complet d'une palette ILBM basse profondeur.

## M5.2 R5 0.4.6 — candidat courant

`dist/AMOSPro_AGA.Lib`

Archive :

`dist/experimental/AMOSPro_AGA_M5_v0.4.6_M52R5.Lib`

Taille : **4560 octets**

SHA256 :

`33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715`

### Delta R5

- aucun changement BODY ;
- aucun changement Double Buffer / Swap / Close ;
- aucun nouveau token AMOS ;
- le segment public `Aga Iff Load` garde la même taille ;
- 256 couleurs conserve le chemin `SetRGB32` déjà validé ;
- les palettes inférieures à 256 couleurs utilisent `LoadRGB32` via un helper interne sans token.

## Runtime R5

- KEKKO.IFF : **palette visuellement correcte** sous R5.
- Le crash observé avec Clown.iff depuis le test KEKKO n'est pas une régression valide : ce test ouvrait volontairement un écran 320×256×16 alors que Clown est 320×200×256.

## Test courant

`tests/current/M5_R5_MULTI_FORMAT.asc`

Le test ouvre l'écran depuis `Aga Pic Info` puis fait Open -> Double Buffer -> IFF Load -> Swap -> Close.

À retester d'abord avec `Clown.iff`, puis DBZ01 et KEKKO.


## M5.2 R5R1 0.4.7 — garde-fou mismatch PASS

Objectif : un IFF incompatible avec l'écran courant doit être refusé sans aucune écriture palette/BODY.

Le loader compare avant chargement :

- largeur BMHD ;
- hauteur BMHD ;
- profondeur BMHD ;
- masking ;
- compression ;
- présence/validité de l'écran courant.

En cas d'incompatibilité, `Aga Iff Load()` suit le chemin d'échec existant et renvoie `0`.

Candidat :

`dist/AMOSPro_AGA.Lib`

SHA256 :

`ec18e5d4fdb02a7e2ab312c09ae23fcefd87acfe4768e7402d5d3d0e66318e25`

Test courant :

`tests/current/M5_R5R1_MISMATCH_GUARD.asc`

Cas volontaire validé : Clown.iff chargé dans un écran 320×256×16 -> `IFF LOAD = 0`, message d'erreur et aucun crash.


## CI R5R1

La première CI R5R1 a échoué uniquement parce que le builder recalculait mal la cible de la branche d'échec du garde-fou. Le binaire runtime validé n'était pas en cause.

Correction builder : la cible est prise depuis le vrai opcode BNE à `start+4`, pas depuis le mot de déplacement à `start+6`.

Le builder reproduit maintenant exactement le candidat runtime SHA256 `ec18e5d4fdb02a7e2ab312c09ae23fcefd87acfe4768e7402d5d3d0e66318e25`.

## Test courant

`tests/current/M5_R5_MULTI_FORMAT.asc`

Ordre : Clown.iff -> DBZ01.IFF -> KEKKO.IFF.


## Régression observée sous R5R1

- Clown.iff : PASS avec le test multi-format.
- KEKKO.IFF : palette à nouveau incorrecte avec le test multi-format.

Aucune nouvelle modification de la Lib n'est faite avant isolation A/B.

## Test courant A/B

`tests/current/M5_R5R1_KEKKO_AB.asc`

Ce test reprend le même chemin direct 320×256×16 que le test KEKKO qui avait validé la palette sous R5. Il est exécuté avec la Lib R5R1 actuelle.

Interprétation :

- KEKKO correct -> le garde-fou est innocent ; le problème vient du chemin PicInfo/multi-format.
- KEKKO faux -> la régression vient bien de R5R1 et il faut rendre le garde-fou totalement transparent sur le chemin valide.


## R5R1 régression confirmée

Le test A/B direct KEKKO sous R5R1 reproduit la mauvaise palette. Le chemin PicInfo n'est donc pas responsable.

Cause identifiée : le garde-fou R5R1 utilisait D0 comme registre de travail et rendait D0 modifié, alors que le bloc BMHD R5 d'origine ne touchait pas D0. Le scan de chunks/palette réutilise ensuite ce registre.

## M5.2 R5R2 0.4.8 — candidat courant

Base : R5 0.4.6, où KEKKO était correct.

Correctif unique :

- sauvegarde/restauration de D0, D6 et A0 dans le garde-fou ;
- résultat du garde transmis uniquement par le flag Z ;
- aucun changement palette/BODY/Swap ;
- aucun nouveau token ;
- segment public Aga Iff Load toujours de même taille.

`dist/AMOSPro_AGA.Lib`

SHA256 :

`4f447bce27fa7db1e86a8fb0d53d4e125e5bf7c6cf83474b4be61a3bf4eda377`

Test courant :

`tests/current/M5_R5R2_MULTI_FORMAT.asc`

Priorité : KEKKO.IFF. Aucun autre diagnostic avant ce verdict.


## Repli décidé — retour à R5 0.4.6

R5R1 0.4.7 et R5R2 0.4.8 sont **rejetés**.

Motif : les deux variantes de garde-fou ont réintroduit la palette incorrecte sur KEKKO alors que R5 0.4.6 l'affichait correctement.

État courant volontairement conservateur :

- `dist/AMOSPro_AGA.Lib` = **M5.2 R5 0.4.6** ;
- SHA256 = `33092d2affbc8fd1d74762cc56cb50d465b34ef71677bfaaa10b408a70cc3715` ;
- KEKKO palette correcte sous cette version ;
- aucune nouvelle modification du loader ;
- garde-fou mismatch retiré du candidat courant ;
- développement M5.2 mis en pause jusqu'à reprise méthodique.


## Intuition Input R1 — branche expérimentale

Branche : `codex/intuition-input-r1`.

Implémentation candidate :
- Window Intuition RAWKEY attachée au Screen AGA;
- `Aga Key`;
- `Aga Wait Key`;
- propagation Ctrl+C vers le mécanisme AMOS natif `BitControl/T_Actualise`;
- cleanup des messages IDCMP avant `CloseWindow`;
- état runtime étendu de 36 à 40 octets avec `Window*` à `+36`;
- assertions builder : segments Generic ILBM R2 (entrée 13) et PicInfo (entrée 14) byte-for-byte identiques au `main` de départ.

Statut : **CPU/statique à valider par CI puis runtime AMOS obligatoire**. Ne pas merger sur `main` avant le PASS explicite du test Ctrl+C réel.


## Intuition Input R1 rejeté / R2 candidat

Retour runtime R1 : Ctrl+C interrompait AMOS mais pouvait laisser l'écran AGA/Window ouverts, car le Break était posé avant le cleanup complet. R1 reste archivé et ne doit plus être présenté au test.

Candidat courant : **Intuition Input R2 0.5.3**.

Correction R2 :
- drain/reply IDCMP ;
- fermeture Window Intuition ;
- libération éventuelle des deux ScreenBuffers ;
- suppression des Safe/Disp MsgPorts ;
- libération DBState ;
- fermeture Screen ;
- fermeture graphics.library et intuition.library ;
- remise à zéro de l'état partagé ;
- seulement ensuite positionnement de BitControl AMOS.

SHA256 candidat R2 : `0825ff7c575dce243bfd4bf8a0dafc6fdfd75165b8e11a3595471f624fab9746`.

Validation CPU : PASS, y compris Ctrl+C avec Double Buffer actif. Validation runtime AMOS encore obligatoire.

## Intuition Input R3 — correction CloseScreen (0.5.4)

R1 et R2 ont un défaut runtime confirmé : le BSR vers CloseWindow remplaçait
CLR.L DBState* dans un chemin sauté lorsque DBState*=0. CloseScreen recevait
alors un Screen qui possédait encore sa Window Intuition.

R3 accroche la fermeture au MOVEA.L DBState*(A2),A4 d'entrée, avant le test
conditionnel du DBState. Le helper vide/repond aux messages IDCMP, ferme
la Window, recharge A4, puis laisse le code original libérer le Double Buffer,
le Screen et les bibliothèques. Même correction dans le cleanup d'extension.

Le test Unicorn exécute le segment public Aga Screen Close complet avec
DBState nul/non nul et reproduit explicitement le défaut R2.

Candidat courant : dist/AMOSPro_AGA.Lib (identique à l'archive
dist/experimental/AMOSPro_AGA_M5_v0.5.4_INTUITION_INPUT_R3.Lib).
SHA256 : feb012b30b1adf89b3e0609e19e9a8e475be6fcd375b355c69f0d69b2d37a884.
Validation : 26 tests CPU PASS ; comportement AMOS/WinUAE encore à valider.
Ne pas merger sur main sans ce test runtime.


## Intuition Input R4 0.5.5 — Ctrl seul / Aga Wait Key

**Retour runtime R3 :** `Aga Screen Close` fonctionne en boucle simple.
**Problème R3 restant :** Ctrl seul génère RAWKEY `$63` (99) et
termine immédiatement `Aga Wait Key`, empêchant le test de Ctrl+C.

**R4 ne change que le segment AP20 18 :** `Aga Wait Key` ignore
Ctrl seul, répond à IDCMP et poursuit son polling coopératif.
`Aga Key` conserve son contrat brut : Ctrl peut retourner 99.
Le traitement de C+`IEQUALIFIER_CONTROL`, le cleanup R3 et la
propagation Break AMOS restent inchangés.

La modification est une branche vers un stub de 20 octets ajouté en
fin de segment 18 ; aucun déplacement des branches PC-relatives
précédentes. Segments 0–17 (dont Generic ILBM R2 et PicInfo) strictement
identiques au R3. Assertions dans le builder reproductible.

**Candidat courant :** `dist/AMOSPro_AGA.Lib`.
Archive : `dist/experimental/AMOSPro_AGA_M5_v0.5.5_INTUITION_INPUT_R4.Lib`.
Taille : 7896 octets. SHA256 :
`fbcaec00f30e6a7c03abc692225dac1f95dbbdb537353674fa6939c1087de9f2`.

Vérification locale des octets, du HUNK, de la table AP20 et des cibles
de branches : PASS. **Suite CPU Unicorn R4 et Ctrl+C runtime AMOS :
encore à valider.** Ne pas merger sur `main`.
