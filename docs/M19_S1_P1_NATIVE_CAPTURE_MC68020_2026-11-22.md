# S1-P1 — Premier noyau natif MC68020 de capture AGSP (22 novembre 2026)

**Statut : source MC68020 isolé, candidat au test Gate A.** Ce code n'est **pas** une commande AMOS, n'est pas inclus dans AP20 ou P2d et ne constitue pas encore une capture AGSP depuis WinUAE. Aucun `Save/Load` réel AGSP n'est revendiqué. Cible CPU du source : **MC68020/68EC020 minimum**, assemblage avec `vasmm68k_mot -Fbin -m68020 -no-opt`.

## But de l'incrément

Partir des **vrais bitplanes planaires AGA** de l'écran privé, sans convertir un IFF sur PC, pour produire le **bloc de pixels AGSP v1 (2 bitplanes, largeur 16, hauteur 1..256) et sa palette locale RGB24 (48 octets)**. La fonction travaille sur un **descripteur déjà validé par le futur adaptateur AP20/AMOS** : pointeurs des plans du buffer sûr, `bytesPerRow`, dimensions, coordonnées, profondeur 1..8, index transparent et **copie stable de la ColorMap** sous forme de 256 triplets RGB8.

Le noyau :
- parcourt 16×H pixels en reconstruisant l'indice à partir des plans AGA ;
- utilise l'indice `TransparentPen` **exact** (une couleur noire opaque reste visible) ;
- fusionne seulement les indices IFF ayant **exactement le même RGB24** ;
- refuse la **quatrième couleur opaque** sans modifier l'image AGSP publiée ;
- remplit 2 plans non compressés en ordre `plane-major` et la palette locale 0 transparent, 1..3 opaques ;
- ne modifie ni le ScreenBuffer, ni la palette matérielle, ni Copper, ni DMA et ne crée pas de banque.

**Code** : [`M19_S1P1_AGSP_CAPTURE_MC68020.s`](../src/native/m19_s1/M19_S1P1_AGSP_CAPTURE_MC68020.s). **Tests** : [`test_m19_s1p1_native_capture.py`](../tools/test_m19_s1p1_native_capture.py) et [workflow dédié](../.github/workflows/m19-s1-p1-native-capture.yml). Résultats GitHub Actions à relever sur le commit exact ; ne pas déclarer PASS sur la base du source ou de la simple compilation Python.

## ABI privée, avant liaison AMOS

Entrée `A0 = descripteur` de 64 octets. Les nombres sont big-endian. Offsets :

| Offset | Type | Contenu |
| ---: | --- | --- |
| 0 | LONG × 8 | Pointeurs des plans 0..7, premiers `depth` valides |
| 32 | LONG | Pointeur snapshot RGB24 `256×3` |
| 36 | LONG | Pointeur tampon temporaire pixels `height×4` octets |
| 40 | LONG | Pointeur tampon temporaire palette `48` octets |
| 44 | LONG | `bytesPerRow` du BitMap source |
| 48 | WORD | Largeur de l'écran source 1..4096 |
| 50 | WORD | Hauteur de l'écran source 1..4096 |
| 52 | WORD | Profondeur de l'écran 1..8 |
| 54 | WORD | X de capture, origine écran |
| 56 | WORD | Y de capture, origine écran |
| 58 | WORD | Hauteur de capture 1..256, largeur fixe 16 |
| 60 | WORD | `TransparentPen` 0..255 |
| 62 | WORD | Réservé = 0 |

Sortie : `D0 = 1` succès et `D1 = 0..3` couleurs opaques. Refus : `D0 = 0, D1 = 0`. Préservation de `D2..D7, A2..A6`, usage de pile de travail locale. Aucun appel OS interne ni `GetP` direct. **Les sorties sont des tampons de staging, jamais une banque publiée : sur refus, le contenu des tampons est indéfini et doit être ignoré.**

### Vérifications à la charge du futur adaptateur natif

Le noyau vérifie la géométrie et les pointeurs non nuls, **pas la validité mémoire des intervalles**. Avant son appel, l'adaptateur AP20 devra :
1. Identifier le **bon BitMap du ScreenBuffer inactif** ayant reçu `Aga Iff Load` ; obtenir `Safe` et synchroniser `WaitBlit` (pas de swap implicite).
2. Vérifier la résidence et les plages complètes des bitplanes via `Exec.TypeOfMem` et les structures du ScreenBuffer, y compris stride et profondeur.
3. Construire un snapshot `RGB24` à partir de `ColorMap` avec `graphics.library/GetRGB32` (valeurs 32 bits left-justified), sur 256 couleurs, sans supposer un `CMAP` encore présent en mémoire.
4. Allouer les tampons de staging avec tailles vérifiées, préparer en-tête et répertoire AGSP, publier la banque AMOS seulement après conversion réussie.
5. Reprendre le code transactionnel **P2d vérifié**, jamais `Bnk.Reserve` destructif sur une banque active ; maintenir les autres images lors d'un remplacement. Tester `Save/Load` réel sous AMOS.
6. Empêcher toute libération Chip tant que des références Copper/DMA restent possibles. **Pas de Sprite affiché en S1-P1**.

## Ce que les tests CPU devront établir

Le [modèle AGSP v1](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) est oracle pour la sortie. Le banc exécute **les octets du véritable binaire assemblé** sur un CPU MC68020 Unicorn et compare sur :
- carré 16×16 ; capture non alignée X=13/Y=5 ; profondeur source 4 ou 8 ;
- transparent ≠0, deux indices IFF ayant le même RGB, noir opaque ;
- 4 couleurs opaques : retour 0 **sans écriture dans le tampon non publié** ;
- hauteur 256 ; arguments invalides ; protection par canaries et registres.

**Gates à distinguer** : source + test CPU donne une preuve de noyau **Gate A partielle** seulement. Aucune Gate A AP20/ABI globale, **Gate B Runtime WinUAE, C vrai Compiler ou D Amiga physique** n'est acquise tant que le noyau n'est pas raccordé, puis exécuté dans l'extension réelle.

**Sources protégées** : P2d 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. `dist/AMOSPro_AGA.Lib`, `LAST_GOOD`, `tests/current/M19_P2_ALL_IN_ONE.asc` et `tests/design/sprites_aga/SPRITE_PROBE.asc` ne sont pas modifiés.
