> **RÉSULTAT REÇU — P2.6 Runtime et Compiled PASS.** Les journaux réels donnent une baisse de durée de **2,42 % Runtime** et **0,43 % Compiled** sur la somme des séries. [Mesures détaillées et ASC archivé](../benchmarks/RESULTATS_M19_P26_R87_DRAW_2026-11-15.md). L'ASC est maintenant dans `tests/passed/`. Le banc actif est **P2.7** ; ne pas confondre ce plan initial avec l'état courant.

# M19 P2.6 — R87 draw-only : performances BASIC contre Aga Bob Batch

Date : 15 novembre 2026. Branche **main uniquement**. Nouvelle campagne **PREPAREE**, **WinUAE Runtime et Compiled NON TESTES** sur cet ASC. Aucun gain revendiqué.

## Origine vérifiée et archivage

- Bibliothèque **R87 v0.13.32** : `dist/AMOSPro_AGA.Lib`, 73 184 octets, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. Ce binaire n'est pas reconstruit/modifié pour P2.6 ; l'API `Aga Bob Batch(DescriptorBank,Count)` et les 76 commandes R84 historiques restent identiques.
- R84 `LAST_GOOD` : **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` ; **ne pas toucher**.
- Le test **M19 P2.5 R87** a **PASS en Runtime et Compiled**, d'après les deux journaux envoyés : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `DRAW 3`, `REJECT 3`, `CAPTURE 2`, fermeture et deltas mémoire nuls. Empreintes SHA256 des fichiers transmis : Runtime `a60b9f15d972713cc848344b8e976050e396c8fd98590548951642cdfe7fba42` ; Compiled `aec78fb7c702f517dc7cbdc695fcb32780b74cb2a0a817ba6978a840780066f0`. Ces logs affichent la version attendue, **pas le SHA du binaire installé**.
- ASC P2.5 archivé **octet pour octet** dans [`tests/passed/M19_P25_R87_BOBS_SMOKE_01.asc`](../tests/passed/M19_P25_R87_BOBS_SMOKE_01.asc), Git blob `347e35d4e79b4afc331a732f33c448bbb61ddef9`. Ses résultats ne valident pas automatiquement le banc P2.6.
- **Nouveau et seul ASC actif** : [`tests/current/M19_P26_R87_DRAW_BENCH_01.asc`](../tests/current/M19_P26_R87_DRAW_BENCH_01.asc), **267 lignes**, blob Git `c6c03b24bb273027492776ba24e53193ec52198b`. Source dérivée de l'initialisation R87 smoke vérifiée, puis ajout des seuls blocs de préparation et timing. Préflight `amos-pro-aga-rules` et CI **à contrôler sur cette source exacte**.

## Ce qui est mesuré

| Variable | Valeur |
|---|---|
| Objets | **4 / 8 / 16** par rendu |
| Formats | AGAPIC v1/v2 (40×40) et FICON8 (16×16), mask=1 |
| Écran | 320×256 AGA, 256 couleurs, back buffer privé |
| Listes Batch | Trois banques BOB1 : 24 = 96 octets, 25 = 176, 26 = 336 |
| Ordre de dessin | Fixe, identique en BASIC et dans les descripteurs Batch |
| Préparation | Création banques, coordonnées, descripteurs et échauffement hors chrono |
| Méthode A | `Aga Bank Image Draw` et `Aga F Icon` appelées individuellement |
| Méthode B | Un appel `Aga Bob Batch(bank,count)` par rendu |
| Répétitions | **64** par méthode, par quantité et par passe |
| Passes | **A → B**, puis **B → A** |
| Mesures | **12 séries** de `Timer`, ticks PAL nominaux de 20 ms |
| Travail effectué | **3 584 Bobs par méthode** ; 3 584 appels individuels contre 384 appels Batch |
| Exclusions du chrono | Fill, Z-sort, VBL, Swap, captures, allocations et création de descripteurs |

Un `Aga Blit Fill` prépare le même fond avant chaque série, hors fenêtre chronométrée. Les objets sont redessinés sur le même back buffer inactif pendant la série, **sans présentation ni synchro imposée**. Les retours d'appels sont contrôlés et le test s'arrête sur toute erreur.

### Calculs à faire une fois les journaux obtenus

Pour chaque N = 4, 8, 16 et pour chaque méthode :

- `T_BASIC = PASS0_BASIC + PASS1_BASIC` ; `T_BATCH = PASS0_BATCH + PASS1_BATCH`, en ticks `Timer`.
- **Gain Batch (%)** = `100 × (T_BASIC - T_BATCH) / T_BASIC` (ne pas calculer si `T_BASIC=0`).
- **Temps par Bob composé** = `TICKS × 20 / (2 × 64 × N)` ms, dans chaque méthode.
- **Temps par appel natif** (Batch) = `T_BATCH × 20 / (2 × 64)` ms par commande groupée ; le temps par appel individuel = `T_BASIC × 20 / (2 × 64 × N)` ms.
- Regarder l'**écart entre les deux passes** avant de conclure : deux résultats trop différents indiquent du bruit ou un effet de chauffe/émulation. Si besoin, faire une *nouvelle campagne explicitement documentée* ; ne pas sélectionner seulement la meilleure passe.

Le résultat attendu n'est **pas** forcément un gain. Les durées de composition P2.1 (4: 56,67 ms ; 8: 81,33 ms ; 16: 132 ms) incluent d'autres opérations et **ne doivent pas être utilisées comme référence directe du dessin isolé**.

## Procédure WinUAE

1. Confirmer **MC68020 / 14 MHz / AGA PAL / JIT OFF**, R87 installée et redémarrer AMOS.
2. Ouvrir un programme vide → **Project → Merge ASCII** du seul ASC actif. Lancer en **Runtime**, puis récupérer `RAM:M19_P26_RUNTIME.TXT`.
3. Compiler le **même ASC** avec AMOS Compiler V2 ; lancer l'exécutable et récupérer `RAM:M19_P26_COMPILED.TXT`.
4. Exiger `RESULT 1`, `ERR 0`, `VERDICT PASS`, `BENCH_RUNS 12`, `BASIC_CALLS 3584`, `BATCH_CALLS 384`, `BASIC_BOBS 3584`, `BATCH_BOBS 3584`, `CLOSE_RETURNED 1`. Reporter **chaque tick brut** et les modes séparément. Une erreur ou un Guru doit rester FAIL.

**Limite** : ce banc mesure le dessin et l'orchestration, **pas** l'équivalence pixel par pixel, le tri Z ni le FPS affiché. Les tests natifs R87 avaient un oracle pixel pour AGAPIC/FICON ; le nouveau banc ne crée pas de nouvelle preuve pixel Runtime. Il ne faut pas prétendre le contraire.

**Aucune promotion de R84 `LAST_GOOD`**, aucun changement de branche, tag ou release.
