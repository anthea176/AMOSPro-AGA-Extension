# M19 P2e.1 — Deux canaux AMAL vers deux Bobs AGA (source-only)

## Situation au 21 novembre 2026

- **Base qualifiee :** P2e.0 Gate B Runtime PASS, 240/240 echantillons et 29 pixels, preuve du journal `M19_P2E0_AMAL_BRIDGE(2).TXT` (397 octets, SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`).
- **Lib de travail inchangée :** `dist/AMOSPro_AGA.Lib` **P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes et 203 AP20.
- **LAST_GOOD :** P1e, 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, protegee et non promue.
- **Nouvelle source :** [M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt](../tests/design/M19_P2E1_AMAL_TWO_BOBS_UNVALIDATED.txt), **8 420 octets**, SHA256 `f0054af6f44ec6cfbbb1dcc233322c516e3e026954f3149d3e60149177a35537`, encodage ASCII.
- **Statut : PREPARE / controle structurel local PASS**, pas le preflight officiel ; **Gate B WinUAE / Gate C Compiler / Gate D physique NON TESTEES**. Ne pas utiliser cette source comme preuve de fonctionnement.

## Objectif discriminant

Demontrer que **deux canaux AMAL originaux independants** (0 et 1) ecrivent chacun leur propre etat dans une zone memoire paire, que la boucle AMOS lit les deux et actualise **deux Bobs AGA persistants** depuis une banque AGBO commune, tout cela sur la bibliotheque **P2d existante**. Aucun hook, nouveau token ou nouveau binaire.

| Fonction | Canal 0 / Bob 1 | Canal 1 / Bob 2 |
| --- | --- | --- |
| Tampon AMAL | `Start(28)+0`, 8 octets | `Start(28)+8`, 8 octets |
| X logique | 96..128 | 192..224 |
| Y logique | 100..116 | 144..160 |
| Images AGBO | 1 (165), 2 (90) | 2 (90), 1 (165) |
| Taille des images | 16×16, opaque | 16×16, opaque |
| Mouvement | +32,+16 puis retour, 32 pas par trajet | +32,-16 puis retour, 32 pas |
| Controle pixel | Ancienne page affichée apres Swap | Idem, source separee |

La banque 28 contient 16 octets initialises par `Doke` ; `Synchro Off` precede les declarations `Amal n,... To adresse`. Un seul `Synchro` fait progresser les deux canaux. Le programme fixe les deux Bobs, appelle **un seul `Aga Swap` explicite par frame**, puis `Aga Wait Vbl`. L'initialisation des **deux pages physiques** precede les Bobs, comme dans P2e.0 ayant passe Runtime.

## Couverture du banc propose

- 240 cycles, cible `VALID_SAMPLES >= 200`, `SWAPS=1+VALID_SAMPLES`, pixels `PIX0 >= 2` et `PIX1 >= 2` ; controle des getters X/Y/Image pour les deux Bobs.
- Les six compteurs `CHG0_X/Y/A` et `CHG1_X/Y/A` doivent devenir non nuls, les images 1 et 2 doivent etre vues pour **chacun** des objets.
- `RAW0_LAST` / `RAW1_LAST` lus par `Deek`, `BYTE0_LAST` / `BYTE1_LAST` par `Peek`, et `FLAG0_X/Y/A` / `FLAG1_X/Y/A` sont **diagnostics non bloquants** : ne pas conclure a la validite du protocole de flags sans log de plusieurs cycles.
- Les pixels des deux Bobs sont controles par capture de l'ancien front devenu back apres Swap, avec X aligne sur 8. En cas `ERR 17`, `PIXEL_ID`, `PIXEL_VALUE` et `PIXEL_EXPECTED` identifient la divergence.
- Nettoyage : `Amal Off 1`, `Amal Off 0`, `Synchro On`, fermeture AGA, `Amos To Front`, puis liberation des banques 24/27/28.

## Prochaine porte : activation WinUAE apres decision explicite

**Ne pas executer directement la source .txt comme une campagne officielle.** L'unique ASC actif [P2e.0](../tests/current/M19_P2E0_AMAL_BRIDGE.asc) reste intact avec sa preuve PASS ; aucune archive ni mouvement automatique. Avant bascule : executer le `tools/amos_preflight.py --strict-target` **sur l'ASC exact**, confirmer qu'une seule campagne ASC sera active, puis tester avec WinUAE Runtime et conserver `RAM:M19_P2E1_AMAL_TWO_BOBS.TXT`.

Sortie attendue *si le test fonctionne* : `RESULT 1`, `ERR 0`, `BG0/BG1 1/1`, `PIX0/PIX1 >= 2`, six deltas `CHG*` > 0, `CLOSE_RETURNED 1`, `VERDICT PASS`. **Ce n'est pas un resultat observe.**

**Limites :** pas de collision, masques, priorite, debordement hors ecran, AMAL multibanques ou interaction Sprite DMA teste ; une capture pixel sur de petites regions ne prouve pas l'absence d'artefacts sur tout l'ecran. Les 16×16 de deux Bobs sont visibles pour permettre un controle utilisateur.

