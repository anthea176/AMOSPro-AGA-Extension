# M19 P2a — Collision Bob–Bob MC68020 en un seul appel privé

**Date : 21 novembre 2026.** **Périmètre : source-only**, branche `main`, cible MC68020/68EC020 minimum. **Gate A de la chaîne native privée : PASS** sous Unicorn et AMOS/Exec simulés. **Aucune commande AP20**, aucun nouveau binaire, aucune modification de `LAST_GOOD` ou de l'ASC actif.

## Résultats

| Élément natif | Octets | SHA256 des octets émis | Validation |
| --- | ---: | --- | --- |
| [Noyau de collision](../tools/m19_p2a_collision020_emit.py) | 764 | `2546b269cad753c6b401c5d3cf3330e0f96545e64506a023d381b60c154450b7` | 9/9 |
| [Contrôles P0f de la paire](../tools/m19_p2a_pair_checked_read_emit.py) | 328 | `3e2cdedb603fb090f0bfd4b46cf3ecc1e3684ace2ddf922b7b3076c6efa6d5dd` | 9/9 |
| [Paire + images Chip P0j-b3](../tools/m19_p2a_pair_chip_resolve_emit.py) | 946 | `7ee9fa70673b8827bde31d12e1023982a7439f80c77c34e84d9c73438e678548` | 8/8 |
| [Descripteurs P1d/2×40](../tools/m19_p2a_pair_geometry020_emit.py) | 1 742 | `37e75c7f073ef0ef50b7572cc8173781b69308e8f78a9c97a13b21c4ce9b8d97` | 8/8 |
| [Hotspots originaux AGBO/P1b](../tools/m19_p2a_pair_hotspot020_emit.py) | 874 | `abdd2f4ad1d8785f9aef3d9573e1e7547fb83aa016e15c3ed3eebaff7c548fb7` | 8/8 |
| [**Requête unique MC68020**](../tools/m19_p2a_collision_query020_emit.py) | **484** | `c7bc01b85932eaa98bf9143733382e8c40f736f3989c12633775d63605609cb9` | **9/9** |

[CI intégrée P2a — PASS 91/91](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44905618103). Le total comprend 17 tests du modèle géométrique Python + 23 tests du raccord AGBO + 9 + 9 + 8 + 8 + 8 + 9 tests natifs sous Unicorn. Le rapport **ne** prétend **pas** à un AMOS Runtime WinUAE ni à une compilation AMOS.

## Appel privé

`p2a_collision_query_entry` :

| Registre / champ | Entrée |
| --- | --- |
| `D0`, `D1` | Deux IDs Bob différents, 1..64 |
| `D4` | `0` : rectangles visibles ; `1` : collision des masques AGBO pixel-exacte |
| `A1` | Adresse du contexte moteur privé, deux LONGs : pointeur dimensions écran (largeur/hauteur LONG) et pointeur de la table P1d 65×16 octets |
| `A4` | Adresse de la table interne de **7 pointeurs de code source-vérifiés** : paire Chip P2a, `identity_check` P0f, résolveur image P0j-b3, hotspots P2a, lookup P0j-b1, packer géométrie P2a, collision P2a |
| `A5` | Propriétaire AMOS courant |

**Retour numérique privé : `D2=0` ; `D3=1` collision, `D3=0` aucun contact, `D3=-1` données/callbacks/bank invalides.** `D0,D1,D4..D7,A0..A6`, notamment `A3`, ainsi que la pile sont préservés. Le premier banc a trouvé que la sauvegarde MOVEM historique n'incluait pas `A3` ; le prologue/épilogue le sauvegarde et le restaure explicitement avant la validation PASS finale.

Le cadre privé de **352 octets de pile** contient une paire de 120 octets (2 enregistrements P0e et 2 images Chip P0j), 8 octets de hotspots originaux signés et deux descripteurs de collision de 40 octets. **Aucune sortie partielle ni donnée persistante n'est publiée.**

### Ordre natif contrôlé

1. Contrôler le mode, les pointeurs de contexte et **sept callbacks internes** (non fournis par le programme AMOS).
2. Lire les deux Bobs actifs par le vrai P0f, résoudre leurs plans/masques Chip par P0j-b3 et relire les identités (refus atomique si source modifiée).
3. Relire les banques d'origine par P0j-b1 et les **hotspots AGBO WORD signés +28/+30** ; comparer l'entrée du répertoire à l'image Chip et vérifier une seconde fois les deux banques avant publication.
4. Construire les deux descripteurs de 40 octets en LONG : origine X/Y après hotspot ; largeur/hauteur, stride, masque ; intersection avec écran et les limites P1d globales et locales **à fin exclusive**. Une zone vide est une absence de collision, une zone enregistrée non canonique est rejetée.
5. Appeler les vrais **764 octets du noyau MC68020** en mode rectangle ou masque sans Blit, DMA, Swap, allocation, mutation des Bobs ou changement de banque sélectionnée.

Le banc vérifie les deux implantations V2, les vrais masques AGBO issus de banques 10/11, les hotspots signés positifs/négatifs/extrêmes, la géométrie et les limites globales/locales, les générations périmées et les changements tardifs de source, les IDs illégaux, le propriétaire invalide, le contenu des registres et l'absence de modification de la mémoire Chip ou des objets. Les résultats sont comparés au modèle Python indépendant.

## Provenance et limites de preuve

Source autoritative : `tools/build_m19_p1e_bank_edit_in_memory.py::build_p1e`. La P1e `dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent **124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, **même Git blob `5bb0c476c2b286495a1d0cf7d4415dbbc4eec369`**.

**Important avant l'API publique :** la table des callbacks et les pointeurs du contexte écran/P1d sont **fournis par le banc interne** (ce n'est pas encore la connexion à la mémoire propriétaire P1d de la Lib P1e). La préparation préalable du cache Chip pour les deux banques est obligatoire. Le contrat d'absence de réentrance et de stabilité de la source pendant le calcul doit être garanti par l'appelant. Les contrôles `TypeOfMem` des extrémités et les stamps n'éliminent pas un hypothétique ABA ni ne rendent sûrs des pointeurs AMOS arbitraires ; tous les buffers sont privés, cohérents et déjà validés à l'entrée. La machine émulée n'est ni WinUAE Runtime ni un Amiga physique.

- **Gate A source/CPU et chaîne privée intégrée sous Unicorn : PASS** (91 tests).
- **Gate A intégration dans la Lib/les tokens AP20 : NON TESTÉE**.
- **Gate B Runtime WinUAE : NON TESTÉE**.
- **Gate C véritable AMOS Compiler : NON TESTÉE** (non demandée).
- **Gate D matériel réel : NON TESTÉE**.

## Jalons suivants sans altérer P1e

1. Résoudre **depuis la vraie AGA State** du moteur le propriétaire de l'écran, les dimensions et l'adresse de la table P1d ; conserver les gardes sur génération/identité et éviter les accès à des données hors propriétaire.
2. Préparer le **contrat AP20** de la fonction numérique par paire (proposition `Aga Bob Col(A,B,Mode)`) et son banc WinUAE discriminant. Un jeton public ou une nouvelle `.Lib` ne doivent pas être intégrés sans validation des signatures, du routage des groupes, de la relocalisation et autorisation explicite.
3. Profil MC68020 masqué et règles de coût CPU sur grandes surfaces avant optimisation.

Aucune promotion ni bascule implicite.
