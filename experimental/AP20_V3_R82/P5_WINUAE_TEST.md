# P5 — trois vrais modules natifs R82 / WinUAE TEST ONLY

Branche : `experiment/ap20-v3-multiunit-64k`. Ne remplace pas R82 LAST_GOOD.

## À installer

1. Dans une **copie WinUAE** AGA / MC68020+, garder `LIBS:c2p.library` 1.9.
2. Sauvegarder l'ancien `APSystem/AMOSPro_AGA.Lib` **dans cette copie**.
3. Copier `AMOSPro_AGA_V3_R82_3UNITS_TEST.Lib` comme
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

Seules les Gates A (CPU/CI) sont actuellement PASS.
Les résultats WinUAE Runtime / Compiler P4 **ne valident pas
automatiquement P5**. Aucune fusion, promotion, ou publication.
