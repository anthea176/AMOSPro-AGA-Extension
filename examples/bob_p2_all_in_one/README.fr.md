# Démonstration AGA — Bobs P2 ALL IN ONE

[English](README.md) · [Tous les exemples](../README.fr.md) · [Installation](../../INSTALL.fr.md)

**Exemple public validé en Runtime et avec AMOS Compiler sous WinUAE.** Le programme regroupe **P2a à P2e**, avec deux Bobs à silhouettes asymétriques **F et L** : animations AMAL, collisions, retournements H/V/HV, sélection de plans et mise à jour automatique en double buffering. **Aucune image, banque ABK ni ressource externe** n'est nécessaire.

## Fichiers et version exacte

- [**M19_P2_ALL_IN_ONE.asc**](M19_P2_ALL_IN_ONE.asc) — source ASCII **originale inchangée**, 25 056 octets ; Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`, tag `P2_FULL_V1_20261121`.
- Bibliothèque requise : [`dist/AMOSPro_AGA.Lib` M19 P2d](../../dist/AMOSPro_AGA.Lib), **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, **100 commandes / 203 AP20**, cible **MC68020/68EC020 minimum**.
- [Archive de test exacte](../../tests/passed/M19_P2_ALL_IN_ONE.asc) — **mêmes octets que l'exemple**, sans changement de noms, d'assets ou de logique. `LAST_GOOD` P1e **non remplacée**.

## Phases affichées

| Phase | Fonction | Contrôles du programme |
| --- | --- | --- |
| 1 — P2e / P2d | Deux canaux AMAL + deux Bobs 16×16, déplacements et images F/L | **240 cycles**, 29 pixels par Bob, 241 Swaps dont initialisation |
| 2 — P2a | `Aga Bob Col(A,B,Mode)` : rectangles, masques et absence de collision | **8 contrôles**, dont retour d'erreur sur mode invalide |
| 3 — P2b | `Aga Bob Flip(N,Mode)` : 0 normal, 1 horizontal, 2 vertical, 3 H+V | Deux formes **32×32**, **20 pixels** comparés, 4 orientations et transparence |
| 4 — P2c / P2d | `Aga Bob Planes(N,Masque)` et `Aga Bob Auto Update(1/0)` | **10 pixels** sur cinq masques de plans, désactivation Auto en fin de test |

L'écran AGA est affiché directement via `Amos To Back`, puis fermé et rendu à AMOS avec `Amos To Front`. Le programme **se termine automatiquement** et écrit son résultat dans `RAM:` ; il ne demande pas d'appuyer sur une touche.

## Installation et lancement

1. Installer la Lib **P2d** dans le slot AGA d'`APSystem` et **redémarrer AMOS Professional** ; sélectionner WinUAE AGA, CPU 68020 ou supérieur.
2. Ouvrir un programme AMOS **vierge**. Vérifier que les banques **24, 27 et 28** sont libres (elles seront utilisées et nettoyées par le programme).
3. Choisir **Project → Merge ASCII** pour importer `M19_P2_ALL_IN_ONE.asc`. Exécuter en Runtime ou compiler **ce même ASC inchangé** avec AMOS Compiler.
4. Après exécution, sauvegarder le journal `RAM:` pertinent **avant tout reset ou nouvel essai**.

| Mode | Journal |
| --- | --- |
| Interprété strict (`Prg State 0`) | `RAM:M19_P2_FULL_INTERPRETED.TXT` — non testé |
| Runtime (`Prg State 1`) | `RAM:M19_P2_FULL_RUNTIME.TXT` — **PASS** |
| Compilé (`Prg State -1`) | `RAM:M19_P2_FULL_COMPILED.TXT` — **PASS** |
| Mode inattendu | `RAM:M19_P2_FULL_UNKNOWN.TXT` |

## Résultats WinUAE du 21 novembre 2026

Les **deux journaux transmis par l'auteur** présentent exactement les mêmes contrôles, en ne différant que par `PRG_STATE` et `RUN_MODE`.

| Mesure | Runtime | AMOS Compiler |
| --- | ---: | ---: |
| `RESULT / ERR / VERDICT` | 1 / 0 / PASS | 1 / 0 / PASS |
| `VALID_SAMPLES / SWAPS` | 240 / 252 | 240 / 252 |
| `COL_CHECKS` | 8 | 8 |
| `FLIP_PIX0 / FLIP_PIX1` | 8 / 12 | 8 / 12 |
| `PLANES_PIX0 / PLANES_PIX1` | 5 / 5 | 5 / 5 |
| `AUTO_ENABLE / AUTO_DISABLE` | 1 / 1 | 1 / 1 |
| `SWAP_REFUSALS / SWAP_RECOVERED / RETRY_VBLS` | 121 / 121 / 121 | 121 / 121 / 121 |
| `CLOSE_RETURNED` | 1 | 1 |

**Preuves exactes, CRLF conservés :** [Runtime, 1 632 octets](../../docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT), SHA256 `864f6b17652033b99f06ec34df3ce85f3a1579bbb52c033d67d62e178852c627` · [Compiler, 1 633 octets](../../docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT), SHA256 `296f562f73a83d91f419d60a4538e35ef05d55f0c159012949fc5482ce88bf41`.

**Attention :** les **121 refus initiaux de `Aga Swap`** ont été **tous récupérés après un VBL supplémentaire** ; ce compteur n'est pas nul et le diagnostic ne doit pas disparaître des futures versions. Cette réussite ne valide pas les performances ni l'absence de défaut sur toutes les configurations.

**Statut : Gates B (Runtime) et C (vrai Compiler) PASS pour cet ASC et la Lib P2d testés sous WinUAE**, d'après les journaux fournis ; Gate D (matériel AGA physique) et interprétation stricte non testées. Aucune promotion de `LAST_GOOD`, aucune modification du binaire et aucune revalidation implicite des autres APIs.
