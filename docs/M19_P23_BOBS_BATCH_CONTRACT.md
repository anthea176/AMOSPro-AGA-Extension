# M19 P2.3 — Contrat R86 natif Aga Bob Batch

Date : 15 novembre 2026. Candidat expérimental R86 v0.13.31 sur main uniquement. R84 LAST_GOOD figé, aucune promotion.

## API

`_OK=Aga Bob Batch(DescriptorBank,Count)` ; `Aga Bob Probe` reste disponible. Count transmis en D3, DescriptorBank en premier LONG à (A3)+. Renvoie D3=1 si tous les Bobs ont été dessinés, sinon D3=0 ; D2=0 (entier). 1 <= Count <= 256.

La banque DescriptorBank est une banque AMOS DATA existante (numéro 5..65535), de longueur exactement `16 + Count*20`. Sa représentation est **big-endian**. La banque ne doit pas être modifiée pendant l'appel.

| Offset | Taille | Champ |
|---|---:|---|
| 0 | 4 | Signature ASCII `BOB1` |
| 4 | 2 | Version = 1 |
| 6 | 2 | Stride = 20 |
| 8 | 4 | Count (LONG, égal au paramètre) |
| 12 | 4 | Réservé = 0 |

Chaque descripteur de 20 octets commence à `16 + i*20` :

| Offset | Taille | Champ |
|---|---:|---|
| +0 | 4 | Y signé 32 bits, autorisé -32768..32767 |
| +4 | 4 | X signé 32 bits, autorisé -32768..32767 |
| +8 | 4 | Numéro de banque source AMOS DATA (5..65535) |
| +12 | 4 | ID image : 0 pour AGAPIC, 1..4096 pour FICON8 |
| +16 | 2 | Kind : 1 AGAPIC, 2 FICON8 |
| +18 | 2 | Mode : 0 opaque, 1 transparent |

L'ordre physique des descripteurs est l'ordre de rendu : le BASIC trie Z puis encode les descripteurs de l'arrière-plan vers le premier plan. Le moteur ne trie pas, n'anime pas et ne lit pas AMAL.

## Rendu et gestion des erreurs

Les deux vrais moteurs natifs existants sont **réémis depuis leurs émetteurs source** dans l'unité BOBS, pour que leurs BSR.W internes restent intra-unité et compatibles Compiler V2. Le wrapper AGAPIC R54 est relocalisé vers le vrai décodeur AGAPIC v2 utilisé par R84 ; FICON8 réutilise l'émetteur R73 optimisé 020. Les unités C2P, IFF et AGA historiques demeurent octet pour octet identiques à R84.

L'en-tête, le nombre, les types, les coordonnées, modes et numéros de banques sont prévalidés avant le premier dessin. Chaque backend valide sa propre banque/image, le bitmap privé inactif, la profondeur et le Safe non bloquant avant ses écritures. **Un échec sur un Bob ultérieur peut laisser un frame partiellement dessiné dans le back buffer. Si le retour est 0, le programme ne doit PAS appeler Aga Swap et doit reconstruire le fond avant un nouvel essai.** Aucun write dans le front, Swap, Wait VBL, allocation, animation ou dessin en interruption. La palette ne change pas.

AGAPIC accepte les formats v1/v2 avec contraintes propres (notamment ModeID v2). FICON8 accepte seulement le format FICON8 à 8 plans. Les coordonnées sont clippées par les moteurs originaux.

## Qualification vérifiée (15/11/2026)

- **Gate A MC68020 : PASS**, 8/8 tests natifs Unicorn, avec oracle de pixels AGAPIC v1/v2 / FICON8, garde ModeID v2, clipping, modes opaque/transparence, ordre de dessin, erreurs, ABI et front buffer protégé. [CI dédiée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43700178749).
- **Gate B WinUAE Runtime : PASS**, `RESULT 1`, `ERR 0`, `PRG_STATE 1`, `VERDICT PASS`.
- **Gate C WinUAE Compiled : PASS**, `RESULT 1`, `ERR 0`, `PRG_STATE -1`, `VERDICT PASS`.
- **Mesures :** 13 ticks en BASIC et 13 en Batch dans les deux modes sur quatre itérations incluant le fond ; **aucun gain démontré**. Delta Chip/Fast nul pour chaque test.
- **Limites des contrôles WinUAE :** les compteurs `ORDER`, `MASK`, `CLIP` sont posés après retour positif et ne constituent **pas** un oracle pixel par pixel. La chaîne `LIBRARY R86_V0.13.31` dans les journaux est écrite par l'ASC et **ne prouve pas** à elle seule la SHA du binaire installé.
- **Gate D Amiga physique : non testée.** Aucun changement de `LAST_GOOD`, pas de promotion, branche, tag ou release.

Voir [rapport détaillé et deux journaux](M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md) · [test actif](../tests/passed/M19_P23_BOBS_BATCH_01.asc). Les règles d'erreur restent valables : un retour Batch=0 interdit de présenter un frame partiel et impose de reconstruire le fond avant réessai.

Depuis le passage au banc P2.4, l'ASC P2.3 qualifié est conservé dans `tests/passed/` ; [le test actuel P2.4](../tests/current/M19_P24_BOBS_PIXELS_BENCH_01.asc) vérifie séparément les couleurs de pixels et prépare un benchmark draw-only, **sans changer l'API R86**.
