# M19 P2e.1 — Deux canaux AMAL vers deux Bobs AGA (campagne Runtime)

## Activation de la campagne le 21 novembre 2026

**Unique ASC actif :** [tests/current/M19_P2E1_AMAL_TWO_BOBS.asc](../tests/current/M19_P2E1_AMAL_TWO_BOBS.asc), **8 800 octets** après correction visuelle, Git blob `edcbbdc9d863dd96f6b5ad22abe44ba0d4c37aaf`. Identique à la source de conception P2e.1, hors commentaire d'état de validation. L'ASC P2e.0 a quitté `tests/current` dans la même transition ; il reste dans [l'historique Git au commit 55ca846e](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/55ca846e9a44065b0e1ba3e8c9a68041ce37746e/tests/current/M19_P2E0_AMAL_BRIDGE.asc). Son log Runtime PASS original [est conservé](evidence/M19_P2E0_AMAL_BRIDGE_RUNTIME_2026-11-21.TXT), sans déplacer de test validé vers `tests/passed/`.

**PREFLIGHT antérieur PASS sur l'ASC de 8 430 octets** ; version corrigée de 8 800 octets en attente d'un nouveau préflight CI ; contrôle structurel complémentaire PASS. Les changements sont uniquement ASC et documentation ; **aucune nouvelle bibliothèque ni commande AGA**. Gate B Runtime de P2e.1 **NON TESTÉE**, Gate C et D NON TESTÉES.

## Situation au 21 novembre 2026

- **Base qualifiee :** P2e.0 Gate B Runtime PASS, 240/240 echantillons et 29 pixels, preuve du journal `M19_P2E0_AMAL_BRIDGE(2).TXT` (397 octets, SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`).
- **Lib de travail inchangée :** `dist/AMOSPro_AGA.Lib` **P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes et 203 AP20.
- **LAST_GOOD :** P1e, 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, protegee et non promue.
- **Nouvelle source :** [M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt](../tests/design/M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt), **8 420 octets**, SHA256 `f0054af6f44ec6cfbbb1dcc233322c516e3e026954f3149d3e60149177a35537`, encodage ASCII.
- **Statut de la source de conception avant bascule : PREPARE / controle structurel local PASS**. Le nouvel ASC actif a depuis un preflight officiel strict PASS ; **Gate B WinUAE / Gate C Compiler / Gate D physique NON TESTEES**. Ne pas utiliser cette source comme preuve de fonctionnement.

## Résultat Gate B négatif et prochain essai (21/11/2026)

Le journal `M19_P2E1_AMAL_RUNTIME.TXT` est **FAIL avec ERR 15 au second Swap de frame** ; `BG0/BG1 1/1`, `VALID_SAMPLES 1`, `SWAPS 2`, `CLOSE_RETURNED 1` ; aucun pixel contrôlé à ce stade. [Rapport et journal exact](M19_P2E1_RUNTIME_ERR15_DIAG_2026-11-21.md). La version diagnostique suivante a Git blob `a150f85f952b20c1292b143b5ae9c1b8d016d3e0` (10 421 octets), avec 4 tentatives bornées séparées d'un VBL et instrumentation des refus/récupérations ; ni nouvelle bibliothèque ni validation Runtime attribuée. Les paragraphes plus bas décrivent aussi l'histoire du banc et ne remplacent pas ce statut.

## Nommage des journaux restauré (21/11/2026)

Le nouvel ASC actif contient une sélection de journal par `Prg State`, conforme aux anciens témoins `M19_P25` et `M19_P2_OBJECTS` : `RAM:M19_P2E1_AMAL_INTERPRETED.TXT` en interprété strict, `RAM:M19_P2E1_AMAL_RUNTIME.TXT` en Runtime, `RAM:M19_P2E1_AMAL_COMPILED.TXT` en Compiler, `RAM:M19_P2E1_AMAL_UNKNOWN.TXT` si le mode est inconnu. Le fichier choisi est affiché au retour à AMOS et `RUN_MODE` est journalisé. **Source : 9 134 octets**, Git blob `ac151e107eda820594d16c7821f9e02592fa1b72`. Cette correction **n'est pas une validation Compiler** ; préflight sur l'ASC exact et essais WinUAE restent nécessaires.

## Correction du banc actif après retour utilisateur (21/11/2026)

Les rectangles 16×16 opaques sont remplacés par une **forme F (index 165) et une forme L (index 90)**, masquées par `Make AGA Bob Mask I,0`. La logique de capture et l'oracle du **pixel en haut à gauche** sont inchangés : ce pixel appartient à la barre verticale pleine de chaque lettre. Le retour utilisateur mentionne aussi l'écran AGA invisible sans **Amiga+A** : le banc appelle désormais `Amos To Back` après initialisation des deux pages physiques, puis toujours `Amos To Front` après fermeture. **Nouveau Git blob ASC : `edcbbdc9d863dd96f6b5ad22abe44ba0d4c37aaf` (8800 octets), non encore exécuté sur WinUAE.** Ne pas attribuer le PASS P2e.0 à cette nouvelle version.

Pour valider le Flip visuellement, une démo séparée [FLIP_VISUAL.asc](../examples/aga_bob_flip/FLIP_VISUAL.asc) affiche un F 32×32 orienté dans les quatre modes 0, 1, 2 et 3. Cette démo ne change pas la campagne P2e.1.

## Objectif discriminant

Demontrer que **deux canaux AMAL originaux independants** (0 et 1) ecrivent chacun leur propre etat dans une zone memoire paire, que la boucle AMOS lit les deux et actualise **deux Bobs AGA persistants** depuis une banque AGBO commune, tout cela sur la bibliotheque **P2d existante**. Aucun hook, nouveau token ou nouveau binaire.

| Fonction | Canal 0 / Bob 1 | Canal 1 / Bob 2 |
| --- | --- | --- |
| Tampon AMAL | `Start(28)+0`, 8 octets | `Start(28)+8`, 8 octets |
| X logique | 96..128 | 192..224 |
| Y logique | 100..116 | 144..160 |
| Images AGBO | 1 (165), 2 (90) | 2 (90), 1 (165) |
| Taille des images | 16×16, F masqué (index 0) | 16×16, L masqué (index 0) |
| Mouvement | +32,+16 puis retour, 32 pas par trajet | +32,-16 puis retour, 32 pas |
| Controle pixel | Ancienne page affichée apres Swap | Idem, source separee |

La banque 28 contient 16 octets initialises par `Doke` ; `Synchro Off` precede les declarations `Amal n,... To adresse`. Un seul `Synchro` fait progresser les deux canaux. Le programme fixe les deux Bobs, appelle **un seul `Aga Swap` explicite par frame**, puis `Aga Wait Vbl`. L'initialisation des **deux pages physiques** precede les Bobs, comme dans P2e.0 ayant passe Runtime.

## Couverture du banc propose

- 240 cycles, cible `VALID_SAMPLES >= 200`, `SWAPS=1+VALID_SAMPLES`, pixels `PIX0 >= 2` et `PIX1 >= 2` ; controle des getters X/Y/Image pour les deux Bobs.
- Les six compteurs `CHG0_X/Y/A` et `CHG1_X/Y/A` doivent devenir non nuls, les images 1 et 2 doivent etre vues pour **chacun** des objets.
- `RAW0_LAST` / `RAW1_LAST` lus par `Deek`, `BYTE0_LAST` / `BYTE1_LAST` par `Peek`, et `FLAG0_X/Y/A` / `FLAG1_X/Y/A` sont **diagnostics non bloquants** : ne pas conclure a la validite du protocole de flags sans log de plusieurs cycles.
- Les pixels des deux Bobs sont controles par capture de l'ancien front devenu back apres Swap, avec X aligne sur 8. En cas `ERR 17`, `PIXEL_ID`, `PIXEL_VALUE` et `PIXEL_EXPECTED` identifient la divergence.
- Nettoyage : `Amal Off 1`, `Amal Off 0`, `Synchro On`, fermeture AGA, `Amos To Front`, puis liberation des banques 24/27/28.

## Prochaine porte : Gate B Runtime WinUAE (campagne active)

L'ASC est actif sous `tests/current/` après préflight strict PASS. Ne pas charger le `.txt` de conception. **Project → Merge ASCII** de l'ASC puis **Runtime WinUAE** avec la Lib P2d inchangée ; récupérer `RAM:M19_P2E1_AMAL_RUNTIME.TXT` et comparer le résultat. Le vrai Compiler est reporté au futur programme global P2.

Sortie attendue *si le test fonctionne* : `RESULT 1`, `ERR 0`, `BG0/BG1 1/1`, `PIX0/PIX1 >= 2`, six deltas `CHG*` > 0, `CLOSE_RETURNED 1`, `VERDICT PASS`. **Ce n'est pas un resultat observe.**

**Limites :** pas de collision, masques, priorite, debordement hors ecran, AMAL multibanques ou interaction Sprite DMA teste ; une capture pixel sur de petites regions ne prouve pas l'absence d'artefacts sur tout l'ecran. Les 16×16 masqués des deux Bobs sont visibles pour permettre un contrôle utilisateur.

