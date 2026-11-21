# M19 P1b — Hot Spot Safe Blitter, candidate WinUAE installée

**21 novembre 2026. Branch `main` uniquement.** L'utilisateur a demandé « go jusqua la lib », autorisant la livraison de P1b dans l'unique Lib canonique `dist/AMOSPro_AGA.Lib` et l'extension du programme de campagne. **Aucune promotion `LAST_GOOD`.**

## Livrable installé

| Élément | Version / SHA |
| --- | --- |
| `dist/AMOSPro_AGA.Lib` | **119 176 octets**, SHA256 `2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4`, blob Git `8bc11d556971ea7a90bd57b00f231ca26cac0958` |
| `dist/AMOSPro_AGA_LAST_GOOD.Lib` | **P0 protégée**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, blob Git `6e23a1dc783145adb41f1a9b02fc6fc8f3b80ff2` inchangé |
| Source | [Builder P1b](../tools/build_m19_p1b_hotspot_in_memory.py), [raccord natif](../tools/m19_p1b_hotspot_draw_emit.py), [primitive signée](../tools/m19_p1b_hotspot_origin_emit.py), dérivés des builders sources P1a/P0 |
| API | **92 commandes / 188 entrées AP20** préservées ; groupes `[142,153,156,177,181]`, PC16 maximal **31 444** |
| Nouveau code | **352 octets natifs** dans groupe BOBS 177 ; branchement `BRA.W` ancien modifié sur son seul déplacement 16 bits après point source-pinné `explicit_image_resolve_entry` |
| ASC unique | [`tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **17 566 octets ASCII LF**, neuf étapes/405 frames P0/P1a + quatre phases P1b |
| Ressource | [`tests/current/M19_P1B_HOTSPOT_BANK26.abk`](../tests/current/M19_P1B_HOTSPOT_BANK26.abk), **200 octets**, 8×6×8 plans, masque indépendant, hotspot (+4,+3), SHA256 `8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325` |
| Journal de test | `RAM:M19_P1B_HOTSPOT.TXT` |

**Provenance du binaire :** l'action GitHub a généré deux fois le candidat **en mémoire** depuis le builder source épinglé, contrôlé sa longueur, SHA256 et la source native. Le blob binaire exact a été créé dans Git puis committé comme **seule Lib installable active**, sans extraire/réassembler depuis un désassemblage. [Commit de livraison](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/2af4844d803430a550a825a309a2862b51f5e9d6).

## Raccord fonctionnel

Le chemin `explicit_frame_draw_entry` continue de parcourir les Bobs 1..64 et de valider banque/source/image. À l'intérieur de `explicit_safe_blit_entry`, après `explicit_image_resolve_entry`, le branchement local source-identifié est redirigé vers le pont P1b append-only :

1. `explicit_bank_lookup_entry` revalide l'original AGBO et son `generation` ; aucun hotspot n'est lu depuis la copie Chip des pixels.
2. L'entrée de répertoire AGBO v1 de **40 octets** est recherchée par son **image ID**, non par son rang. `hotspot_x` et `hotspot_y` signés 16 bits sont aux offsets +28/+30 ; le helper MC68020 calcule en 32 bits `draw_x=Bob.x-hotspot_x`, `draw_y=Bob.y-hotspot_y`.
3. Origine et image entièrement hors écran = **no-op réussi**, sans Blitter ni Swap implicite. Image visible = passage des coordonnées **de dessin** ajustées au Safe Blitter/WaitBlit historique (masque/opaque, clips et buffer arrière).
4. Les coordonnées stockées dans P0e et renvoyées par `Aga X Bob(N)` et `Aga Y Bob(N)` sont les **valeurs logiques de l'ancre**, inchangées. Les API et GetP antérieurs restent byte-identiques.

## Validation et limites

- [Gate A MC68020 intégrée — PASS, 98 contrôles](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44836896149). Vrais octets natifs sur deux placements mémoire, services OS/Intuition/Blitter **simulés** ; mesures de pixels/masques après render, clipping signé, 64 Bobs, absence de Blit hors écran, sortie sans Swap, préflight image invalide avant DMA, cache Chip réutilisé.
- [Gate A isolée — PASS, 258 cas](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44835297656) pour l'origine hotspot, accompagnée du modèle écran double buffer/masques.
- [Action builder et ABK SHA exacts — PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44837269625) ; produit le binaire 119176 et l'ABK 200 depuis les sources.
- Le chemin canonique `dist/AMOSPro_AGA.Lib` et le `LAST_GOOD` sont ensuite vérifiés byte-identiques dans Git. Les historiques R82/R84 sont reconstruction-source et non un remplacement de `LAST_GOOD`.
- **Gate B P1b Runtime WinUAE : PASS fonctionnel.** Voir les résultats ci-dessous. **Gate C vrai Compiler : NON TESTÉE. Gate D matériel : NON TESTÉE.** Gate B P1a déjà PASS fonctionnel sur la *précédente* bibliothèque, sans transfert de preuve à P1b.
- Le champ `LIB_SHA256` du journal ASC est une **étiquette littérale** et **ne prouve pas** le binaire physiquement chargé dans WinUAE.
- La suite CI `Artifact integrity` historique n'est **pas** globalement PASS lors de la première bascule P1b : certains anciens bancs ont des listes de SHA active autorisées à moderniser en conservant leurs sources historiques.

## Protocole WinUAE utilisé

[**Consignes exactes du seul ASC de campagne**](../tests/current/README.md). Après `git pull origin main`, installer la nouvelle Lib, placer l'ABK dans le répertoire courant AMOS, avoir banques 24/25/26 libres, `Project → Merge ASCII`, puis deux Runtime sans redémarrer entre les deux et sauvegarder deux journaux.

Attendus : **405 frames de régression + 4 phases hotspot**, `QUERY_VALUES_OK 42`, `HOTSPOT_GETTERS_OK 12`, `HOTSPOT_FRAMES_OK 4`, `HOTSPOT_LOAD_ERR 0`, `BANKS_ERASED 3`, `ERR 0`, `RESULT 1`, `VERDICT PATH_OK`. Contrôle visuel indispensable du Bob à l'origine `(106,97)` pour X/Y logiques `(110,100)`.

## Résultats Runtime WinUAE

**Gate B P1b PASS pour le banc Hot Spot.** L'auteur confirme deux lancements dans la même session AMOS, sans redémarrage ni `Erase All`, et les observations visuelles suivantes.

| Position logique | Rendu confirmé |
| --- | --- |
| (110,100) | Origine du dessin (106,97) |
| (2,2) | Bob partiellement visible en haut à gauche, origine (-2,-1) |
| (32767,32767) | Bob entièrement invisible |
| (140,90) | Bob réactivé et dessiné à (136,87) |

Les fichiers fournis `M19_P1B_HOTSPOT1(2).TXT` et `M19_P1B_HOTSPOT2(2).TXT` sont identiques octet pour octet (1 363 octets CRLF chacun, SHA256 brut `de8fefb214615ca21e48bda82b0a39d1cf8748555399451dcb1d3ba252f05d40`). La confirmation de la relance vient de l'auteur.

| Vérification | Valeur dans chaque journal |
| --- | --- |
| Mode / état AMOS | `RUNTIME` / `PRG_STATE 1` |
| Résultat / erreur / verdict | `1` / `0` / `PATH_OK` |
| Régression | 405/405 frames, 9/9 étapes, 64 Bobs à l'étape 8 |
| Fill / Copy / Clear / Update / Swap | Zéro échec, 403 Clear et 405 Update réussis |
| Bank Free | 3 Clear, 3 Update, 3 Swap et une réactivation |
| Getters P1a | 42/42 valeurs |
| Banque hotspot | 26, métadonnées (4,3), erreur de chargement 0 |
| Phases hotspot | 4/4 Clear, Update et Swap, 12/12 valeurs de getters |
| Fermeture | `CLOSE_RETURNED 1`, `BANKS_ERASED 3` |
| Relances VBL | 364 |

Le rendu est documenté par l'observation de l'auteur sous WinUAE. Le SHA de la Lib P1b a été vérifié sur `main`. Le SHA inscrit dans le journal est une constante de l'ASC. Les journaux ne contiennent aucune mesure mémoire Chip/Fast ni mesure de performance.

**Gates C (véritable AMOS Compiler) et D (Amiga physique) à tester.**
