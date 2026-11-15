# M19 P2.1 — Dernier benchmark A/B : tri Z BASIC vs cache Z

**Statut : nouveau programme de test préparé, non encore exécuté dans AMOS/WinUAE.** Test prévu directement sur **WinUAE AGA PAL, MC68020 à 14 MHz, JIT OFF**. `main` uniquement, bibliothèque **R84 v0.13.29 `LAST_GOOD` intacte**, aucune nouvelle commande native/AP20.

**ASC unique actif :** [`tests/current/M19_P21_ZCACHE_BENCH_01.asc`](../tests/current/M19_P21_ZCACHE_BENCH_01.asc). L'ancien [benchmark 4/8/16 validé](../tests/passed/M19_P2_BENCH_BOBS_01.asc) est archivé **avec son blob Git identique** (`4345d8728af1d6dba29a5936463219ac49b3b109`). [Résultat 68020 noJIT](RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) : tri répétitif ~4/15/59 ms par appel à 4/8/16 Bobs ; d'où cet essai final.

## 1. Principe

Le banc réutilise **exactement la préparation des 16 objets et leurs images du précédent ASC** : écran AGA privé 320×256 en 256 couleurs, double buffering, sources AGAPIC 24×24 et FICON8 16×16. Dans chaque groupe de quatre : un AGAPIC transparent, un AGAPIC opaque et deux FICON8 transparents. Sources partagées, positionnement identique pour chaque méthode.

**Deux méthodes, même rendu et mêmes frames :**

- **BASE (mode 0) :** reconstruire et retrier la liste `(Z, ID)` à chaque composition, comme le benchmark P2 précédent.
- **CACHE (mode 1) :** reconstruire la liste uniquement lorsque le cache est invalide (changement de Z, de visibilité ou de nombre d'objets actifs) ; conserver la liste pendant les frames suivantes.
- Avant les mesures, **5 contrôles du cache** vérifient l'ordre initial, le changement/restauration du Z de l'ID 1, le masquage/réaffichage de l'ID 4. Toutes les modifications de propriété sont suivies d'une **invalidation explicite**.
- **Deux passages** `P0/P1` sur **4, 8 et 16 Bobs**. P0 exécute BASE puis CACHE ; P1 **CACHE puis BASE** afin de réduire le biais d'ordre. Chaque méthode est chronométrée séparément, et les mêmes valeurs de mouvement `_RUN=1..N` sont utilisées. Aucun AMAL dans ce benchmark.
- Le rendu utilise toujours le **back buffer Safe** ; `Aga Blit Fill` redessine le fond, `Aga Bank Image Draw` ou `Aga F Icon` dessinent les objets, puis `Aga Swap` ne se produit qu'en phase de présentation. Aucun dessin en interruption.

## 2. Mesures, par charge, méthode et passage

| Phase | Répétitions | Mesure |
|---|---:|---|
| **SORT** | 120 demandes d'ordre | `SORT_TICKS` et `SORT_SORT_CALLS` (120 reconstructions BASE contre 1 CACHE) |
| **COMP** | 60 compositions | `COMP_TICKS`, `COMP_SORT_CALLS`, `COMP_DRAWS`, `COMP_SAFE_RETRIES` (60 tris BASE contre 1 CACHE) |
| **DISP** | 20 frames présentées | `DISP_TICKS`, `DISP_SORT_CALLS`, `DISP_SWAP_RETRIES` (20 tris BASE contre 0 CACHE) |
| **FILL** | 120 effacements en référence | `FILL_TICKS`, commun aux charges et méthodes ; pas de mesure CPU isolée |

Unité : `Timer` PAL, **environ 20 ms/tick nominal**. Temps estimé de composition par frame = `COMP_TICKS × 20 / 60`. Temps de présentation par frame = `DISP_TICKS × 20 / 20`. Le second chiffre **comprend attente VBL et Swap** : ce n'est ni un nombre de cycles CPU ni un objectif FPS matériel. Les retries Safe pendant une mesure faussent sa comparaison en temps de rendu pur.

**Validation structurelle attendue :** `CACHE_INVALID_TESTS 5`, `BENCH_CASES 12`, `FRAME_OK 240`, `DRAW_OK 9088`, `SORT_CALLS_TOTAL 1225`, `CACHE_BUILDS_TOTAL 17`, `CACHE_HITS_TOTAL 1188`, `SORT_FAIL/FILL_FAIL/DRAW_FAIL/SWAP_FAIL 0`, `CLOSE_RETURNED 1`, `RESULT 1`, `ERR 0`. Les compteurs de tris sont **vérifiés** par le programme ; le PASS ne présume **aucun gain de performance**, seul le journal décidera.

## 3. Lancement sous le profil noJIT

1. Démarrer ton profil déjà réglé **68020 à 14 MHz / AGA PAL / JIT désactivé** ; ne pas modifier les paramètres pendant la mesure.
2. Vérifier que les banques **11 à 23 sont libres**. Charger la R84 et importer [l'ASC actif](../tests/current/M19_P21_ZCACHE_BENCH_01.asc) depuis un programme AMOS vide via **Project → Merge ASCII**. La première instruction exécutable est `Set Buffer 20`.
3. Ne pas appuyer sur **Échap** : ce test la traite comme interruption volontaire (`ERR 41`). Une partie des mesures s'effectue **sans Swap** : l'écran peut rester fixe, c'est normal. La phase de présentation totalise **240 frames**.
4. À la fin, récupérer **`RAM:M19_P21_ZCACHE_RUNTIME.TXT`** et envoyer le journal complet. Le conserver hors de RAM: avant une éventuelle relance. `Prg State` nomme également les variantes `_INTERPRETED`, `_COMPILED`, `_UNKNOWN` si le mode diffère.

## 4. Ce que permettra ce dernier essai

Le rapport permet de chiffrer, à paramètres CPU identiques, le **gain réel du cache Z** à 4/8/16 objets, en distinguant le temps du tri du temps total de composition. Cela permet de décider si le gestionnaire BASIC suffit pour les objets peu nombreux ou si une optimisation **ciblée** des routines de dessin mérite étude. Aucune API native ni promesse de FPS n'est décidée avant les résultats. **AMOS Compiler et vrai Amiga restent non testés pour M19.**

[Historique benchmark 68020](RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) · [Plan M19](../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Test actif](../tests/current/M19_P21_ZCACHE_BENCH_01.asc)
