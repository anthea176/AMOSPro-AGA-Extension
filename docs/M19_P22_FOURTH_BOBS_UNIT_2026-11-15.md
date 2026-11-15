# M19 P2.2 — Quatrième unité native AP20 « BOBS » : témoin de faisabilité

**Date : 15 novembre 2026 — PHASE D'INFRASTRUCTURE / PAS ENCORE UNE API DE BOBS.** L'auteur a approuvé le démarrage d'un bloc BOBS natif autonome. Ce jalon implémente un **nouveau quatrième groupe AP20 avec un témoin 68k exécutable**, pour qualifier d'abord le dispatcher, le chargeur et le Compiler. **Il n'implémente pas encore `Aga Bob Batch` et n'affiche aucun Bob.**

**Dépôt :** `anthea176/AMOSPro-AGA-Extension`, branche **`main` uniquement**. Bibliothèque `R84 v0.13.29 LAST_GOOD` et `dist/AMOSPro_AGA.Lib` protégées et **inchangées** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.

## 1. Pourquoi un quatrième bloc ?

Le benchmark [P2.1 sur 68020 14 MHz, JIT OFF](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md) démontre que le cache Z BASIC économise **5,8 / 15,6 / 30,4 %** du temps de composition à 4/8/16 Bobs. Il reste **132 ms/composition à 16 Bobs** dans le scénario 320×256×8 plans. L'objectif d'une future commande `Aga Bob Batch(Bank,Count)` est de réduire les appels BASIC→AP20 et les coûts du dessin, pas de dupliquer immédiatement toutes les opérations de gestion d'objets.

R84 dispose de **trois unités natives** : C2P **5 558**, IFF **2 508**, AGA/AGAPIC **56 580 octets**. Le plafond vérifié du Compiler V2 est **65 534 octets par unité** ; la marge restante du groupe AGA n'est que **8 954 octets**. Un bloc `BOBS` indépendant ne remplit donc pas davantage ce groupe. **Il ne prouve pas automatiquement que ses routines pourront appeler les moteurs d'images AGA** : les références PC-relatives et l'ABI de ces routines doivent être étudiées avant toute composition native mixte AGAPIC/FICON8.

## 2. Prototype de routage, in-memory et binaire expérimental isolé

[Constructeur `tools/build_m19_p22_fourth_unit_probe.py`](../tools/build_m19_p22_fourth_unit_probe.py) :

- Lit **R84 active et `LAST_GOOD`**, vérifie leur identité octet pour octet, taille et SHA attendu ; **ne les réécrit jamais**.
- Préserve la table des **76 commandes** R84, leurs tokens/signatures et les **trois corps natifs inchangés**. Décale de +1 uniquement les indices des groupes cibles pour ajouter une nouvelle entrée publique et appose `GetP` à la dernière ancienne entrée, devenue non terminale.
- Ajoute **un groupe indépendant** `BOBS`, avec un dispatcher Compiler V2 **34 octets** et un témoin 68020 **6 octets**. Il fournit uniquement la fonction expérimentale `Aga Bob Probe` qui **renvoie 1** en D3, **0 en D2**, sans lire d'arguments ni dessiner.
- Produit **77 commandes, 87 entrées AP20, 4 unités** : index public nouveau **82**, groupes C2P **83**, IFF **84**, BOBS **85**, AGA **86**. Les 3 corps natifs historiques restent 5 558 / 2 508 / 56 580 octets ; groupe BOBS témoin **40 octets**.
- Le constructeur ne dépose aucun fichier par défaut. L'option `--output` accepte **seulement** `build/m19-p22/AMOSPro_AGA_M19_P22_4UNIT_PROBE.Lib` ; elle **refuse tout chemin `dist/`**, `LAST_GOOD` ou binaire actif. Ce fichier est **TEST ONLY**, non publié comme nouvelle version.
- `Aga Bob Probe` n'est **pas** une commande de production et ne figure pas dans les 76 signatures publiques officielles. Aucune API `Aga Bob Batch` n'est encore figée.

**Retour du premier Gate A (commit aab2cec) : FAIL de portée BSR.W.** En ajoutant BOBS *après* le groupe AGA de 56 580 octets, le saut relatif depuis l'entrée 82 atteint **64 652 octets**, au-delà de la portée signée 16 bits du loader AMOS (`AMOS365 ILLEGAL GRouB`). **Correction : intercaler le petit bloc BOBS avant AGA**, sans modifier un seul octet des trois groupes historiques. C'est précisément le type de problème que la Gate A doit détecter ; la nouvelle disposition doit repasser les tests et ne vaut toujours pas une Gate C Compiler.

## 3. Qualification native Gate A en CI

[Test `tools/test_m19_p22_fourth_unit_probe.py`](../tools/test_m19_p22_fourth_unit_probe.py) :

1. Identité `LAST_GOOD` / active R84 et reconstructibilité binaire déterministe.
2. Préservation des tokens de 76 commandes, des trois corps C2P/IFF/AGA, des stubs R84 (seule rebase index de groupe attendue), ajout du token/entrée BOBS.
3. Longueur **≤ 65 534 octets par unité**, offsets 16 bits, décalages de chargement `Rbsr` en portée signée, rejet d'un routage vers groupe inexistant.
4. **Vrai cœur MC68020 émulé avec Unicorn** : dispatch d'un ensemble d'entrées historiques et de la nouvelle entrée 82, puis **exécution réelle de `MOVEQ #1,D3 / MOVEQ #0,D2 / RTS`** via le quatrième dispatcher. Vérification de D0/D1/D4, A3 et pile préservés.
5. Retour `inspect(parse(...))` de l'AP20 sans erreurs et absence de mutation de `dist/`, `tests/current/` et `tests/passed/`.

[Workflow dédié `m19-p22-fourth-unit-gate-a.yml`](../.github/workflows/m19-p22-fourth-unit-gate-a.yml). **Gate A est À EXÉCUTER / NON ENCORE DÉMONTRÉE** jusqu'à l'obtention d'une CI verte sur le commit contenant les sources. Une fois le Gate A PASS, la CI offre un **artefact expérimental téléchargeable** `M19_P22_4UNIT_PROBE_GATE_A_ONLY` (binaire autonome de test non destiné à la distribution).

## 4. Tests AMOS réels non encore réalisés

Le témoin AMOS [`tests/design/M19_P22_4UNIT_PROBE_01.asc`](../tests/design/M19_P22_4UNIT_PROBE_01.asc) est **en réserve** : il appellera l'ancienne commande `Aga Detect` et la nouvelle `Aga Bob Probe`, et écrira un log `RAM:M19_P22_4UNIT_RUNTIME.TXT`. **Ne pas le lancer avec la R84 seule** : `Aga Bob Probe` n'y existe pas.

**Ne pas remplacer le test actif** `tests/current/M19_P21_ZCACHE_BENCH_01.asc` validé Gate B sans nouvelle étape explicite ; rester à **un unique ASC actif**.

Après la Gate A : installer temporairement le binaire expérimental à la place de l'extension de travail **en conservant à part une copie de R84**, puis qualifier en **WinUAE/AMOS Runtime (Gate B)** et via un **nouvel exécutable AMOS Compiler (Gate C)**. Les deux sont **NON TESTÉES** ; ne pas confondre un dispatch Unicorn avec le chargeur réel. Restaurer la R84 officielle à la fin. Gate D Amiga physique non testée.

## 5. Étape suivante si les quatre unités sont confirmées

Définir la **véritable** fonction native `Aga Bob Batch(Bank,Count)` avec un format de descripteurs sécurisé. Choix non encore tranchés : références de banques et ownership, validation `Safe` (non bloquante), clipping, AGAPIC v1/v2 et FICON8, gestion des refus partiels, coûts/relocations des cœurs graphiques. Auditer d'abord les fonctions AP20 existantes avant de décider de les **réutiliser entre unités** ou d'embarquer des routines indépendantes.

**Aucun gain de Batch n'est revendiqué sans exécution réelle.** Le cache Z BASIC reste la solution fonctionnelle actuelle. Aucun nouveau benchmark BASIC n'est demandé ; la future Gate B du moteur pourra comporter un témoin chronométré intégré.

[État M19](M19_SPRITES_BOBS_AMAL_PLAN.md) · [Roadmap](ROADMAP.md) · [Contrat d'objets P2](M19_P2_OBJECT_MANAGER_CONTRACT.md)
