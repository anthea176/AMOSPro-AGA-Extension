# P5 — trois vrais modules natifs R82 / WinUAE TEST ONLY

Branche : `experiment/ap20-v3-multiunit-64k`. Ne remplace pas R82 LAST_GOOD.

## À installer

1. Dans une **copie WinUAE** AGA / MC68020+, garder `LIBS:c2p.library` 1.9.
2. Sauvegarder l'ancien `APSystem/AMOSPro_AGA.Lib` **dans cette copie**.
3. Copier **`dist/AMOSPro_AGA.Lib` de la branche expérimentale** vers
   `APSystem/AMOSPro_AGA.Lib`, sans changer le slot 14.
4. Relancer AMOS365. Ne toucher ni à la configuration AMOS de référence,
   ni au binaire R82 `LAST_GOOD`.

## 1 — Vérification des trois unités

Dans un programme AMOS vide, `Project → Merge ASCII` avec
`P5_R82_3UNITS_SMOKE.asc`.

Le programme appelle **Aga Detect** (unité 82), **Aga C2P Open**
et **Aga C2P Close** avec paramètres/contexte invalides (unité 80),
et **Aga Iff To Chunky** avec une entrée invalide (unité 81).

Attendu : `RESULT 1`, `ERR 0`, `R82_DETECT -1`,
`C2P_OPEN_REJECT 0`, `C2P_CLOSE_REJECT 0`,
`IFF_REJECT 0`.

Journaux :
- `RAM:AP20_V3_P5_RUNTIME.TXT` (Runtime).
- `RAM:AP20_V3_P5_COMPILED.TXT` (nouvel exécutable compilé).

## 2 — Fonctionnalités graphiques

Sur **cette bibliothèque P5** (pas la P4), reprendre les bancs
réels R82/AGAPIC et C2P déjà validés en P4 :

- `tests/current/AGAPIC_R82_V2_BANK_PALETTE_01.asc` avec ses deux
  banques `R82_AGAPIC_V2_BANK10.abk` et
  `R82_AGAPIC_V1_BANK12.abk`.
- `examples/c2p_iff_showcase/C2P_IFF_SHOWCASE.asc` avec
  `iff-TEST/AGA_DEMO_320x256_256c.iff` et son `.chk`.

Le décodeur `Aga Iff To Chunky` (unité 81) devra encore passer un
cas **positif sur un fichier IFF valide** pour valider son traitement,
en plus de la vérification du dispatch.

## Limites

La Gate A CPU/CI et les **Gates B/C fonctionnelles AGAPIC + C2P sur P5 sont PASS**. Le décodage positif `Aga Iff To Chunky` du module 81 reste distinct et non testé ; Amiga physique / `PRG_STATE 0` non testés. Aucune fusion ni promotion.

## Résultats P5 reçus

- Runtime : smoke **PASS** sur capture utilisateur
  (`AGA -1`, `C2P OPEN 0`, `CLOSE 0`, `IFF REJECT 0`,
  `RESULT 1`, `ERR 0`, erreurs log 0).
- Compiler : smoke **PASS** dans le [journal P5 compilé](../../docs/experiments/evidence/AP20_V3_R82_3UNITS_P5_COMPILED_2026-11-14.TXT)
  (`PRG_STATE -1`, `RESULT 1`, `ERR 0`, Chip/Fast 0/0).
- Cette validation prouve le chargement des trois unités R82 et
  leurs dispatchers sous AMOS365. Les essais graphiques positifs sur P5
  restent distincts et non revendiqués.

## Chemin de livraison officiel sur la branche

`dist/AMOSPro_AGA.Lib` = bibliothèque P5 active (76 188 octets, SHA256 `db55149f19f2d4753232cb5768167f38c82e86c5e2613a056e093fa9c23897af`).
La R82 `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste immuable.
Dans AMOS Extension n°14, le titre attendu contient `THREE GENUINE NATIVE UNITS` ; si tu vois `TRUE SPLIT C2P/AGA`, la P4 est encore installée.

## Validation graphique P5 (14/11/2026)

**Deux bancs graphiques passent en Runtime ET en compilé avec la véritable bibliothèque P5 à trois unités.**

- [AGAPIC Runtime](../../docs/experiments/evidence/AP20_V3_R82_3UNITS_P5_AGAPIC_RUNTIME_2026-11-14.TXT) et [compilé](../../docs/experiments/evidence/AP20_V3_R82_3UNITS_P5_AGAPIC_COMPILED_2026-11-14.TXT) : RESULT 1, ERR 0, toutes fonctions du banc OK.
- [C2P Runtime](../../docs/experiments/evidence/AP20_V3_R82_3UNITS_P5_C2P_RUNTIME_2026-11-14.TXT) et [compilé](../../docs/experiments/evidence/AP20_V3_R82_3UNITS_P5_C2P_COMPILED_2026-11-14.TXT) : RESULT 1, ERR 0, 14/14 pixels, Blit/Zoom/Close/ReOpen OK.

Le smoke P5 ne doit plus être redemandé. Les conclusions antérieures « seules Gate A » sont historiques et remplacées par ce bilan. La R82 LAST_GOOD reste inchangée.
