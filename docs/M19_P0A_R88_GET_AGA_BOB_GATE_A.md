# M19 P0a — `Get AGA Bob` multi-images, candidat dérivé exclusivement de R88

## M19 P0a — MC68020 exclusif : Gate A 74/74 PASS

**Décision utilisateur du 15/11/2026 : aucun nouveau noyau 68000/68010, aucun fallback, aucune double voie CPU000/CPU020.** Implémentation MC68020/68EC020 exclusive de `Aga Bob Bank N` et `Get AGA Bob I,X1,Y1,X2,Y2`, capture par **`BFEXTU` + `BFINS`** (champs de bits de largeur variable 1..16, sans lecture au-delà de X2). Les deux points d'entrée refusent un CPU inférieur avant de manipuler la banque ou la mémoire AGA. Seule la base figée R88 est conservée comme patrimoine ; les parties nouvelles sont 68020 exclusivement.

**GATE A CPU MC68020 PASS**, [exécution GitHub Actions 43754375272](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43754375272), commit exact `27fb718c127ed82cd610a3f5d622274046f82fa7` : **52 scénarios Get + 22 Bank**, deux dispositions CPU020 (interprétée et Compiler V2 simulée) sous Unicorn, **44 tests hôte/statiques PASS**, décodage Capstone M68K_020, préflight de la transaction et préservation des pixels / images / masques. Les anciennes Gates A CPU000 restent un **historique obsolète pour ce chantier** et ne servent pas de preuve 020.

**Candidate uniquement en mémoire :** 79 660 octets ; SHA256 `e98a1a17a5e1de579dd100c5cdeba2b8372f62f175274a4412ddeea21034e3b0` ; **80 commandes / 90 entrées AP20**. Aucun écrit dans `dist/`, R88 v0.13.33 et R84 `LAST_GOOD` inchangées, ASC actif intact. **Gate B WinUAE, Gate C vrai Compiler, Gate D physique : NON TESTÉES.** La préparation Chip pour le moteur d'affichage Bob reste à coder ; ne pas prétendre que les Bobs sont déjà affichables sous AMOS. Source de règles : [`EXTENSION_SOURCE_RULES.md`](../EXTENSION_SOURCE_RULES.md).


**État actuel : GATE A CPU MC68020 PASS sur le candidat exact listé ci-dessus ; Gates B/C/D NON TESTÉES. La section Gate A 68000 antérieure ci-dessous est historique et supplantée.**

## Gate A validée — 15 novembre 2026

- **Exécution CI confirmée :** [run GitHub Actions 43753489991](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43753489991), commit exact `8352aaef331caeccac5cd45aa0631614846568d0` ; **toutes les étapes PASS**, y compris l'invariance des fichiers protégés.
- **Get AGA Bob : 50 cas CPU MC68000 PASS** sous Unicorn (deux placements de code : interprété et disposition Compiler V2 simulée), pixels de 1/4/8 bitplanes comparés à l'oracle de référence, capture 1×1, dimensions et décalages non alignés, insertion triée, remplacement, conservation de l'image et du masque des autres entrées, échec d'allocation, buffer Safe indisponible, Chip invalide, arguments invalides, références périmées.
- **Aga Bob Bank : 20 cas CPU PASS** avec le constructeur de la même lignée, SHA256 de l'étape précédente `82060e0fedf3357f64426817348b218381dc8ed3b640552bd89c0ca433e79d74`.
- **42 tests hôte et structure native PASS** (11 + 14 + 7 + 4 + 6), dont contrôle de l'adressage par `ADDA.L D1,A1` du padding.
- **Candidate exacte, produite en mémoire :** 79 640 octets, SHA256 `988a1d2151fd9c53c03d047af3eac23c5dc8ba4c1152ca2338635c9410deb526`, 80 commandes / 90 entrées AP20 ; groupe BOBS 11 568 octets, capture native 3 194 octets, déplacement maximal 20 616 octets.
- **Contrat Safe R88 conservé :** bit 0 à 0 = buffer immédiatement utilisable ; bit 0 à 1 = attendre le message Safe, sans accepter un message absent. Les services AMOS et OS restent simulés lors de la Gate A.
- **Protection :** `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, le builder R88 original, `tests/current/` et `tests/passed/` sont inchangés. Aucune installation, promotion ou validation WinUAE/Compiler réel.

## Base autorisée et limites

- Référence binaire stricte : R88 v0.13.33 `dist/AMOSPro_AGA.Lib`, SHA256 `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc`, commit historique `7c575a02087d550611b8e966a7708b5f6a8c4b71`.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` : R84, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, non modifiée.
- Aucun exemple, builder ou source R89/R90 n'a été utilisé ; les nouveaux modules `P0a` sont ceux développés depuis R88.
- Bibliothèque candidate **reconstruite exclusivement en mémoire** : aucun `dist/` changé ; aucune installation WinUAE ni promotion.

## Commandes de l'expérience

- `Aga Bob Bank N` : sélectionne ou initialise de manière non destructive la banque DATA `AGBO`, n° 5..65535.
- `Get AGA Bob I,X1,Y1,X2,Y2` : instruction à **5 entiers** sans `To`, `I=1..4096`, coordonnées **inclusives**. Lit les bitplanes du back buffer privé **Safe** et `WaitBlit`; crée ou remplace l'image dans la banque `AGBO` active. Largeurs arbitraires, données **plan-major**, mask **absent** pour l'image capturée, opaque pour la couleur 0.

L'opération vérifie la sélection encore active, les en-têtes AMOS et AGBO, le répertoire complet, la contiguïté des données, les limites d'image, les masques préexistants, le padding nul, le contenu physique `BitMap` en Chip, les dimensions et la profondeur. La transaction finale crée une **nouvelle allocation AMOS** avant tout changement de liste, notifie `Bnk.Change`, puis libère l'ancienne banque. L'échec avant publication conserve l'ancien contenu, et le scratch Exec est toujours libéré.

Les masques des **autres images** sont recopiés inchangés. Pour l'image remplacée, le masque précédent disparaît délibérément : une nouvelle capture est opaque jusqu'à `Make AGA Bob Mask` (commande P0b non intégrée).

## Tests proposés

Depuis la racine du dépôt :

```sh
python -B tools/test_m19_p0a_get_bob_emit.py
python -B tools/build_m19_p0a_r88_get_in_memory.py
python -B tools/test_m19_p0a_r88_get_gate_a.py
```

La dernière commande exige `unicorn==2.1.4` et `capstone==5.0.9`. Les deux placements simulés (interprété / disposition compilée) exécutent réellement le **code MC68000** avec services AMOS/Exec/graphics simulés ; il ne s'agit **ni** d'un lancement AMOS sous WinUAE **ni** d'un exécutable produit par AMOS Compiler.

[Workflow GitHub Actions](../.github/workflows/m19-p0a-r88-get-gate-a.yml). Aucune sortie **Gate B/C** n'est revendiquée par ce document.

## Suite autorisée seulement après Gate A

Préparer l'ASC unique `tests/current/` **pour la candidate exacte**, installer uniquement dans `dist/AMOSPro_AGA.Lib` après accord et validation, essayer dans WinUAE (Gate B), puis AMOS Compiler (Gate C). Conserver R84 LAST_GOOD ; aucune promotion automatique.
