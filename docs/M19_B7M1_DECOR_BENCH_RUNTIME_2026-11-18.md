# M19 B7-m1 — comparaison décor non uniforme et Bobs (18/11/2026)

## Objectif, source et autorisation

Le [premier benchmark Fill A/B/C](M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md) a passé WinUAE Runtime (720/720 frames, ERR 0) : Fill complet A/B **239–240 ticks** contre effacement local C **122–123 ticks**. Les **719 attentes VBL de retry** dans le journal interdisent d'imputer ce gain au seul matériel Blitter. L'auteur a confirmé « ça fonctionne nickel » et a autorisé le nouveau test avec un véritable décor en arrière-plan (« ok allons y »).

**Lib inchangée :** M19 P0j-b7-m1 MC68020+, [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, 86 commandes, 181 entrées AP20, quatre unités natives. `LAST_GOOD` R84 intacte ; pas de nouvelle Lib, API, compilation AMOS ou changement de branche.

**ASC actif unique :** [`tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc`](../tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc), **9 624 octets**, SHA256 `8a3aa82a637334558d918ea0626c9ca661d5f78a1e67ed40ad99ed5a3b1f1904`. Son nom historique est conservé pour les workflows. L'ASC A/B/C Fill de 7 555 octets demeure [consultable sur l'ancien commit](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/2d019a555447ab3cd294d1c4b4e69928d7afd9db/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc).

## Pourquoi le décor est construit en mémoire d'écran

La commande vérifiée `Aga Blit Copy(sx,sy,dx,dy,w,h)` copie **du back buffer vers ce même back buffer** (documentation [M6 Blitter R13](M6_BLITTER_R13.md)). Une copie directe depuis un ancien Bob ne reconstruirait donc pas le fond original. Le banc prépare sur **chacune des deux pages AGA** un motif visible, non uniforme, multicolore, en bande témoin **y=0..63**. Cette bande reste intacte et fournit une source originale constante : les quatre Bobs se déplacent **uniquement dans la zone y≥64**.

Le décor couvre tout l'écran par répétition verticale de la bande, aux mêmes coordonnées X. Le motif contient des panneaux bleus/verts, des traits métalliques et des accents dorés, créés avec `Aga Blit Fill` lors de l'initialisation **hors chronométrage**. Il ne nécessite **aucun fichier IFF supplémentaire**. Il constitue un décor graphique texturé pour tester la restauration, **pas une illustration IFF de jeu**.

La partie basse y=64..255 est composée de trois segments de 320×64 copiés depuis le témoin. Les quatre Bobs sont capturés dans les banques AMOS **24 et 25**, deux images rouges masquées **17×15** et deux jaunes opaques **37×8**. Les mouvements (120 frames aller-retour) incluent clipping horizontal et changement de ligne de tuile.

## Protocole A/B/C

| Runs | Cas | 120 frames par run |
|---|---|---|
| 1 et 6 | **A — décor complet + quatre Bobs** | Trois `Aga Blit Copy(0,0,0,y,320,64)` pour y=64,128,192 + quatre Bobs + `Aga Swap` |
| 2 et 5 | **B — décor complet seul** | Même décor complet + `Aga Swap`, sans `Aga Bob Draw` |
| 3 et 4 | **C — restaurations locales + quatre Bobs** | Deux pages réinitialisées lors des deux premiers swaps ; ensuite quatre anciennes emprises de Bobs restaurées depuis le témoin du **back buffer courant** avant chaque nouveau Draw/Swap |

La restauration C conserve **huit coordonnées X/Y par page** (16 valeurs), clippe les rectangles contre les limites de l'écran, puis les **divise à y modulo 64** pour ne jamais lire hors de la bande témoin. Des zones anciennes peuvent se chevaucher : les quatre Bobs sont toujours repeints après restauration. L'indice logique de page ne change **que si le Swap réussit**. Tous les refus de Copy/Fill/Swap sont réessayés au plus 40 fois, avec VBL uniquement sur refus. Un Draw refusé ou une copie impossible stoppe le parcours avant Swap.

Les deux pages sont initialisées au démarrage (hors chronométrage), puis six séries de 120 frames sont mesurées dans l'ordre **A → B → C → C → B → A**. `Timer` vaut 50 ticks/s. Les fenêtres chronométrées incluent les appels BASIC, Blitter, Draw, Swap et **attentes Safe/Disp éventuelles** ; pas de création de banque, de décor témoin, de fermeture ni de pause finale. Chaque run journalise `RUN_TICKS`, `RUN_WAITS`, `RUN_COPIES`, `RUN_COPY_PIXELS` et `RUN_FRAMES`. Le dernier champ mesure la **surface logique copiée** en pixels, pas le trafic réel du bus Chip.

**Log :** `RAM:M19_B7M1_DECOR_BENCH.TXT`. Envoyer ce journal avec une observation visuelle de la série C. Calculer le FPS depuis les ticks bruts, sans attribuer le résultat à un composant isolé.

## Préflight et preuve limitée

- **AMOS PREFLIGHT PASS** : `amos_preflight.py --strict-target --fail-on-warnings` sur les **9 624 octets ASCII exacts**. Les 21 tests de non-régression du préflight passent.
- **STATIC PASS** : [`tools/test_m19_p0j_b7_anim_asc_static.py`](../tools/test_m19_p0j_b7_anim_asc_static.py) SHA-pinne l'ASC, vérifie la structure des boucles, les commandes de copie, la fermeture et le journal.
- **Pixel oracle Python PASS : 720 compositions** sur deux pages virtuelles 320×256, **84 découpages de frontières y=64** et 2 480 opérations Copy simulées. Le modèle peint un décor non uniforme, restitue l'image masque/opaque et compare **chaque frame** à un rendu de référence complet, tout en garantissant la conservation du témoin.
- **Gate B du nouveau scénario : NON TESTÉE. Gate C Compiler réelle : NON TESTÉE. Gate D matériel : NON TESTÉE.** Le modèle Python ne simule ni la vraie DMA AGA, ni Intuition, ni l'attente Safe/Disp, ni le comportement physique de BltBitMap.

## Critères de verdict

`RESULT 1`, `ERR 0`, `FRAMES_OK 720`, `COPY_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, fermeture appelée, banques 24/25 effacées, **absence de traînées** pendant C et retour propre à AMOS, y compris au deuxième lancement sans `Erase All`.

`PATH_OK` seul **ne garantit pas** un rendu correct : vérifier visuellement la continuité du motif derrière les trous des Bobs masqués, les bordures de tuiles à y=128 et y=192, le clipping gauche/droite et l'absence de scintillement. Si C est visuellement corrompu, classer C **FAIL**, même si le log affiche zéro erreur.

Le code ne requiert aucune IFF externe, aucune nouvelle bibliothèque ni aucun essai AMOS Compiler. [Instructions courtes](../tests/current/README.md).
