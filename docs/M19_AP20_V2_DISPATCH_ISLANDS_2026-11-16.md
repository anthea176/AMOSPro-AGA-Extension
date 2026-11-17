# M19 — Refonte AP20 V2 : îlots locaux de dispatch (expérience source-only)

## Résultat postérieur : Gates B et C PASS (17/11/2026)

Le **17 novembre 2026**, deux journaux WinUAE ont été fournis : **Gate B Runtime `PRG_STATE 1` / `RESULT 1` / `ERR 0` PASS**, **Gate C vrai AMOS Compiler `PRG_STATE -1` / `RESULT 1` / `ERR 0` PASS**. L'auteur a confirmé sans ambiguïté que **la capture de l'écran AGA à quatre Bobs provient de la version COMPILÉE**. Elle valide visuellement la Gate C pour ce scénario (masque, clipping, Swap, Close). [Rapport et empreintes des trois pièces](M19_AP20_V2_GATES_BC_2026-11-17.md).

**L'hypothèse du dispatch V2 à îlots entrelacés est donc validée en Runtime et avec le vrai Compiler pour le chemin du banc actuel**, pas pour toutes les commandes ni pour une future cinquième unité native. Gate D et Bobs persistants/End non testés ; aucune promotion de `LAST_GOOD`. Les mentions « Gate B/C non testées » dans les anciennes sections ci-dessous documentent l'état avant réception des preuves.

## Mise à jour 17/11/2026 — bascule de test expressément autorisée

Le palier expérimental source-only présenté ci-dessous a reçu l'autorisation explicite d'installer sa **candidate exacte** comme `dist/AMOSPro_AGA.Lib` de test, **sans promotion de `LAST_GOOD`**. Bibliothèque attendue : **96 908 octets**, SHA256 **`34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`**, builder SHA-pinné [`tools/build_m19_ap20_islands_in_memory.py`](../tools/build_m19_ap20_islands_in_memory.py). L'unique programme actif devient [`tests/current/M19_AP20_ISLANDS_01.asc`](../tests/current/M19_AP20_ISLANDS_01.asc), reprenant le test de Bob Blit visuel validé sous P0d. Le protocole des Gates B/C et les chemins de logs sont dans [`tests/current/README.md`](../tests/current/README.md).

**Gates réelles de cette candidate : B (Runtime) NON TESTÉE, C (vrai Compiler V2) NON TESTÉE, D physique NON TESTÉE.** Gate A CPU020 PASS sur la candidate mémoire exacte ([CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879479)). La première compilation réelle devra vérifier si le Compiler V2 accepte les unités AP20 entrelacées avec les stubs et le déplacement des marqueurs `GetP`. Les commandes P0f de Bobs persistants ne font **pas** partie du test actif (cleanup `End` toujours à finaliser).

**Référence préservée :** P0d 91 300 octets / SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` dans l'historique Git, ainsi que par builder déterministe ; le seul `LAST_GOOD` R84 67 904 octets / SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` reste inchangé. Aucun nouveau dossier `dist`, aucune archive ni autre branche. Les passages « protection P0d active » ci-dessous documentent le checkpoint avant l'autorisation, **pas le statut après bascule**.

**Date : 16/11/2026.** Dépôt autorisé : `anthea176/AMOSPro-AGA-Extension`, branche `main`. Cible : **MC68020 / 68EC020 minimum**. **Aucune autorisation de bascule de bibliothèque ni de promotion `LAST_GOOD`.**

## Objet et hypothèse à vérifier

La candidate P0f est bloquée par la portée signée de `Rbsr` côté interpréteur : **32 576 octets** au plus, **190 octets** de marge selon le garde existant. Continuer à déporter quelques centaines d'octets entre BOBS et AGA ne règle pas durablement ce problème.

La nouvelle approche place **les stubs publics AP20 à proximité du dispatcher V2 de l'unité native qu'ils visent**. L'entrée spéciale n°0 reste à sa place ; son groupe cible est placé en premier. Les indices publics dans la table des tokens sont remappés. Le `GetP` de chaque commande paramétrée est réintroduit comme marqueur distinct juste avant son nouveau stub. Les unités natives, leur dispatcher V2 de 34 octets, leur code et leurs offsets internes restent **strictement inchangés**. Les contrôles de bornes et de PC16 portent sur les octets de la candidate reconstruite.

Cette voie **réutilise la résolution native de `Rbsr` par AMOS et AMOS Compiler** ; elle ne fait pas encore appel à une table de pointeurs propriétaire. L'acceptation par AMOS Compiler V2 d'une succession de **stubs / unité native / stubs / unité native**, plutôt que d'un bloc de stubs suivi de toutes les unités, est **une hypothèse critique encore non validée sur le vrai Compiler**.

## Fichiers livrés sur `main`

- [Remappeur d'îlots AP20](../tools/ap20_v2_island_dispatch.py) — source MC68020 et contrôle fail-closed des stubs, groupes et offsets.
- [Builder P0f en mémoire](../tools/build_m19_ap20_islands_in_memory.py) — contrôle SHA de la P0d active, R84 protégée et de la source P0f ; aucun fichier binaire écrit.
- [Tests statiques + Unicorn MC68020](../tools/test_ap20_v2_island_dispatch.py) — génération synthétique et candidate réelle, contrôle CPU du dispatcher avec placements interpréteur et Compiler **modélisés**, sans OS ni WinUAE.
- [Workflow Gate A M19](../.github/workflows/m19-p0a-r88-get-gate-a.yml) — exécute le builder et le banc après les régressions précédentes.

## Premier résultat de reconstruction, avant Gate A complète

| Point | P0f source | Candidate expérimentale à îlots |
|---|---:|---:|
| Taille | 96 744 octets | **96 908 octets** |
| SHA256 | `6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45` | `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56` |
| Commandes | 85 | **85 inchangées** |
| Entrées AP20 | 95 | **178** (dont 83 marqueurs `GetP` déplacés) |
| Portée maximale PC16 | 32 576 | **854 octets** |
| Unités natives | 4 | **4, octet pour octet** |
| Groupes natifs AP20 | 91, 92, 93, 94 | 153, 156, 177, 142 respectivement |

Les tailles et empreintes ci-dessus sont celles du **builder source-only affichées en CI**, pas celles d'un binaire installé ou testé sous AMOS. Le premier passage CI avait échoué sur une assertion de test incorrecte (`85` tokens au lieu de `86`, car l'entrée initiale factice est comptée). Cette assertion a été corrigée ; **le banc de dispatch MC68020 du HEAD corrigé a passé sa Gate A ciblée**. Cette preuve n'exécute pas l'AMOS Compiler réel ; les routines natives cibles sont seulement rejointes, pas rejouées dans leur intégralité. Le calcul PC16 est une preuve structurelle seulement.

## Verrous pour accepter l'architecture

1. **Gate A CPU020** : tests de branches/dispatcher et ABI (dont entrée n°0, `GetP`, fonctions, registres, pile), contrôle HUNK/AP20, unités source identiques, valeurs de portées négatives et identité des tokens sur **la candidate exacte**. Une reconstruction sans erreur ne suffit pas.
2. **Gate B WinUAE** : interpréteur/Runtime, `Prg State 1`, mêmes commandes P0d, ouverture, Blitter, clipping/masque, `Swap` explicite, fermeture, absence de Guru.
3. **Gate C vrai AMOS Compiler V2** : compilation neuve `Prg State -1` sur **la même** bibliothèque, vérifier expressément la découverte et la copie des unités AP20 entrelacées, tous les liens `Rbsr`, `GetP`, `Screen Open/Close`, `End`, retour à AMOS, pile/ABI et rendu. Une simulation de l'assemblage Compiler n'est pas cette Gate.
4. **Extension** : après preuve C, ajouter une unité native de taille significative **sans déplacement du code existant**, et retester la même campagne. Les routines internes nouvellement créées devront résoudre leurs références inter-unités de façon indépendante de PC16.

## Protections

- `dist/AMOSPro_AGA.Lib` **P0d 91 300 octets** SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` reste l'**unique candidate installable**, avec Gates B/C précédemment rapportées sur son propre test.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` **R84 protégée**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.
- `tests/current/M19_P0D_BOB_BLIT_01.asc` reste seul et inchangé.
- Aucun changement d'API P0d, `Draw`, `End`, archive, nouvelle branche, ZIP ou binaire installable.

**Statut vérifié : expérimentation source-only livrée. Gate A ciblée et workflow M19 complet PASS** ([run 43973879479](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879479), commit `0639440`) ; politique CPU/chemins PASS ([run 43973879253](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879253)). **Gates B/C/D des îlots NON TESTÉES**, aucune promotion ni bascule.
