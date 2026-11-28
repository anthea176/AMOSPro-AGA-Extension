# M19 S2c-P1d — diagnostic attaché, 28/11/2026

**28/11/2026 — P1d Gate B Runtime FAIL, diagnostic discriminant réussi :** `SPRITE_RC=-17104896` = `-$01050000`, stage 1/check 5/detail 0 : `ViewPort.Next` non nul avant acquisition. `ERR=10`, `CLEAN_ERR=0`, mêmes compteurs que P1c ; Chip 1791328 et Fast 138086880 identiques avant/après. P1d active (S2c-D1, 160812 octets, SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`), B FAIL, C/D non testées. Auteur « pook go » : correction P1e source-only engagée avec diagnostic conservé, parcours borné et read-only des successeurs ; pas de bascule avant Gate A PASS. ASC/ABK/LAST_GOOD inchangés. [Rapport](M19_S2C_P1E_VIEWPORT_CHAIN_2026-11-28.md).

Les statuts précédents ci-dessous sont historiques.

**28/11/2026 — S2c-P1d (titre interne S2c-D1) active sur main, autorisation auteur « go ».** [Gate A intégrée PASS 11/11](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896471), source `adcfa65d0f2e8ca402263eb3f0daee90d3471265` : 288 changements + 11 injections de défauts par modèle Runtime/Compiler, capture et régressions historiques PASS ; double reconstruction et préflight ASC strict PASS. Lib 160812 octets SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`, blob `551674f3598c8b0c10a581d9ac7a1f7cf1155659`. MC68020+, 105 commandes/219 AP20 ; UNIT213 seule modifiée (20216 octets, marge 45318), PC16 max 3658 avec réserve 16384. ASC 15459 octets et ABK 1460 octets strictement inchangés. P1c Runtime FAIL -153 conservée dans Git `8f490c4ee9f3609abd763e8ba2f03e4d97de49de`. P1d est un diagnostic, pas un correctif fonctionnel ; B/C/D P1d NON TESTÉES, CI post-activation à relever. LAST_GOOD L2b protégée, aucune promotion, nouvelle branche, archive ni release. [Rapport](M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md).

Les relevés antérieurs ci-dessous sont historiques.

**Construction P1d exacte observée dans la CI, pas d'activation :** source `adcfa65d0f2e8ca402263eb3f0daee90d3471265` ; 160812 octets SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`, blob `551674f3598c8b0c10a581d9ac7a1f7cf1155659`, 105 commandes/219 AP20, UNIT213 20216 (45318 libres), PC16 max 3658 y compris réserve 16384, UNIT142 et autres entrées byte-exactes. [CI intégrée P1d](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896471), [AGAPIC 392 PASS et identité](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896471/job/140788903118). [CPU et chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896500). Relevé : 3 jobs réussis, 0 échecs, 7 en attente/exécution ; Gate A complète à établir, B/C/D P1d non testées. P1c demeure seule Lib active, FAIL B.

**28/11/2026 — S2c-P1c Gate B Runtime FAIL** (`PRG_STATE=1`, ERR10, SPRITE_RC=-153, CLEAN_ERR=0). Écran 1 simple complet ; 150 Change/Move ; écran 2 premier attaché ID42/image9 refusé après le premier simple ; écran 3 non atteint. AGAPIC 4/4, capture AGSP 4 plans 4/4, refus 2/2, 2 Close, mémoire finale identique. S2c-P1c reste active (SHA256 `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb`), C/D non testées, LAST_GOOD protégée. Auteur « vaa y fait moi tous le diag » : P1d instrumentée source-only, Gate A et reconstruction à relever avant activation. Ne pas lancer le Compiler P1c.

## Preuve de l'échec P1c

[Journal original](evidence/M19_S2C_P1C_RUNTIME_FAIL_2026-11-28.TXT), 779 octets CRLF, SHA256 `294e99a64cceb68710c4f55ed85d74e95f185885e0d3b9191065223f0581db8a`. Source tag M19_S2C_MIXED_V1 ; attribution P1c par contexte, SHA installé non attesté. Les valeurs Fast par écran sont 138094488, finales 138095952 : écart transitoire de 1464 octets récupéré, pas de fuite finale démontrée. L'échec est un refus contrôlé, pas un Guru. L'ASC actuel montre que le deuxième Show de l'écran 2 est Aga Sprite(42,32,136,9). L'erreur -153 est mappée par s2c_acquire_public lorsque AGSP_S2C_ACQUIRE retourne reason2, avant ou après les deux GetSprite. La cause exacte reste inconnue.

## Candidate de diagnostic (titre interne S2c-D1)

- Builder source `tools/build_m19_s2c_in_memory.py`, option diagnostic=True ; adaptateur `tools/m19_s2c_diagnostic_emit.py`. MC68020. P1c par défaut doit rester identique. Reconstruction depuis P1a et filiation S2r authentifiées, assert AP20 : seule UNIT213 et le titre changent par rapport à P1c ; aucune nouvelle commande ; Close/End, ABK et ASC identiques.
- Aucune suppression de contrôle : chaque branche de refus du contexte, des tags palette et des conditions Acquire reçoit une raison distincte. Les valeurs comparées sont lues seulement aux adresses déjà vérifiées. RGB : code par composante, octets attendu/observé.
- Refus avant publication conserve la frame et les reçus selon le contrat précédent ; après publication incertaine, état15 et retraite commune. Quarantaine GetSprite inchangée. Les autres diagnostics lifecycle génériques sont conservés avec catégorie60 ; pas d'instrumentation exhaustive de tous les sous-contrôles de Move/Change/Retire. Aucune modification de palette, OS ni matériel.
- Tests : dix suites historiques sur le nouveau binaire, injections d'erreurs ViewPort, ColorMap, RGB premier/dernier composant, palette modifiée après les deux GetSprite et avant Move/Change ; double reconstruction et préflight ASC exact. [CI P1d](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2c-diagnostic-gate-a.yml). Résultat final : 11/11 jobs PASS, 22 injections validées dans les deux modèles. Candidate active après autorisation explicite « go ».

## Décodage du code public négatif

Pour un retour étendu : N=-RC ; stage=(N>>24), check=(N>>16)&255, detail=N&65535. Un retour court (ex. -153 pour le chemin simple) conserve son sens P1c.

| Stage | Étape |
| ---: | --- |
| 1 | Acquire avant ou pendant GetSprite |
| 2 | Acquire après les deux GetSprite |
| 3 | Show avant ChangeSprite |
| 4 | Show après ChangeSprite |
| 5 | Move avant MoveSprite |
| 6 | Change avant les deux fences (ou raison générique Change) |
| 7 | Change après les fences |
| 8 | Change après publication tentée |
| 9 | Contrôle après MoveSprite, commun Show/Move |

| Check | Contrôle | Détail |
| ---: | --- | --- |
| 1 | View actif != snapshot | — |
| 2 | Span View invalide | — |
| 3 | VP du View != attendu | — |
| 4 | Span ViewPort invalide | — |
| 5 | ViewPort.Next non nul | — |
| 6 | Modes != 0x5000 | Modes lus |
| 7 | DWidth != 320 | largeur lue |
| 8 | DHeight != 256 | hauteur lue |
| 9 | SprIns non nul | — |
| 10 | UCopIns non nul | — |
| 11 | ColorMap != snapshot | — |
| 12 | Span ColorMap invalide | — |
| 13 | Type ColorMap != 2 | type lu |
| 14 | Count != 256 | count lu |
| 15 | SpriteResolution != 1 | valeur lue |
| 16 | CopInit != snapshot | — |
| 17 | Span CopInit invalide | — |
| 18–21 | Quatre mots registre Copper de la paire | mot lu |
| 22 | SimpleSprites table != snapshot | — |
| 23 | Span table invalide | — |
| 24 | VideoControl erreur | retour, 16 bits faibles |
| 25 | GET 0x80000028 != 16 | 16 bits faibles lus |
| 26 | GET 0x80000029 != 16 | 16 bits faibles lus |
| 27 | GET 0x80000032 != 255 | 16 bits faibles lus |
| 28 | GET 0x80000034 != 4 | 16 bits faibles lus |
| 32–50 | Acquire : reçu, état, slots, blank, masque, descripteurs, GetSprite pair/impair, propriété | ancienne reason (1/3/4/5) |
| 60 | Raison lifecycle générique | 1 reçu, 2 contexte, 3 propriété, 4 GetSprite, 5 quarantaine, 6 publication incertaine, 7 géométrie, 8 frame incompatible |
| 64–108 | RGB non identique | attendu=detail>>8 ; lu=detail&255 |

Pour RGB : composante index=check-64 ; pen=17+index//3 ; canal R/G/B selon index%3. Pour Acquire, 32 reçu, 33 état, 34 table pair, 35 table impair, 36 Copper non neutre, 37 masque occupé, 38/39 pointeurs descripteurs, 40/41 Num initiaux, 42/43/44 refus ou résultat GetSprite pair, 45 reçu pair, 46/47/48 refus ou résultat GetSprite impair, 49 reçu impair, 50 ownership final.

## Reproduction

P1d étant qualifiée et activée, même SPRITE_PUBLIC.asc et AGSP_S2C_MIXED.ABK, WinUAE PAL AGA 68030 JIT ON, redémarrage complet. Conserver l'ancien journal hors RAM: avant relance ; envoyer le nouveau RAM:M19_S2C_RUNTIME.TXT même en FAIL. Aucune promotion, aucune branche secondaire. CI historique P0a corrigée fetch-depth:0 (erreur git show prédécesseur observée, pas un défaut Sprite). Le builder composant registre récupère désormais son parent S2r exact.
