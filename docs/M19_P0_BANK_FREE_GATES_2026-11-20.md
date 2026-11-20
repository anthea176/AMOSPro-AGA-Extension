# M19 P0 — livraison de la Lib Bank Chip Select / Bank Free

**20 novembre 2026.** **P0 terminée et promue LAST_GOOD sur `main` par décision explicite**, **Gate A native PASS** ; **Gate B Runtime PASS fonctionnel d'après les journaux reçus** ([preuves et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C AMOS Compiler reportée**, Gate D non testée. M19 continue.

## Bibliothèque exacte

| Propriété | Valeur |
|---|---|
| Fichier | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) |
| Taille | **117 896 octets** |
| SHA256 | `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` |
| API | **89 commandes**, **185 entrées AP20**, cinq unités natives MC68020 `[142,153,156,177,181]` |
| Portée PC16 | maximum **31 092**, sous la limite du compilateur V2 |
| Nouvelle instruction | `Aga Bob Bank Free N`, token index184, signature `I0` |
| Git | [installation du binaire, commit `9fb051c`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/9fb051c304c79d30259dd9ba86f0fe7566566925) |

La chaîne [builder exact](../tools/build_m19_b8_s1_bank_free_in_memory.py) reconstruit B8 S1, puis la préparation Chip puis Bank Free avec vérification SHA et préfixes natifs historiques. L'entrée Bank Free est dispatchée via un [pont natif de cinquième unité](../tools/m19_b8_s1_bank_free_bridge_emit.py) vers BOBS ; il vérifie le callback B7/B8 original et ses marqueurs connus, sans adresse Runtime ou Compiler codée en dur. Le marqueur `GetP` est placé après le stub historique Update (code exécutable inchangé), comme l'exige AMOS pour l'instruction suivante.

**LAST_GOOD actuelle : P0**, byte-identique à la Lib active, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` ([commit](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf)). **Ancienne R84 :** 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, préservée par Git et reconstructible via le builder. L'ancienne B8 S1 reste reconstruisible : 116 104 octets, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`.

## Fonctionnement

**`Aga Bob Bank N`** sélectionne ou crée une banque AMOS DATA au format AGBO. Si elle est vide, **aucune allocation Chip**. Si elle contient des images et qu'un écran AGA valide est ouvert, prépare dès la sélection un cache Chip par identité/génération ; une sélection identique ne recopie pas. Une allocation échouée refuse et restaure l'ancienne sélection.

**`Aga Bob Bank Free N`** est une instruction **sans retour**. Elle refuse une frame en attente `READY`/`DIRTY`, contrôle les propriétaires et les 64 slots, puis désactive **seulement** les Bobs de la banque N. Elle attend `WaitBlit` avant de libérer les métadonnées et buffers Chip de cette banque. **La banque AMOS DATA et ses images restent intactes**, utilisables par `Save`/`Load`. Les autres Bobs et banques conservent leurs ressources. Appels répétés supportés ; une nouvelle sélection `Aga Bob Bank N` permet de recréer des Bobs. Une écriture `Poke` dans un AGBO préparé n'est pas couverte.

Le comportement existant B8 `Aga Bob Clear`, `Aga Bob Update`, `Aga Swap` et les contrôles SafePort/Close a été conservé dans le source en préfixe octet par octet.

## Vérifications obtenues

| Contrôle | Résultat |
|---|---|
| Préparation Chip | **Gate A PASS, 104 contrôles MC68020**, deux relocations |
| Bank Free | **Gate A PASS, 121 contrôles MC68020**, deux relocations, libération sélective, WaitBlit, propriétaire, refus READY, réactivation |
| AP20 | **PASS** : audit tokens, stubs, 89 commandes/185 entrées, 5 îlots, PC16, reconstruction SHA |
| Runtime WinUAE P0 | **PASS fonctionnel sur deux journaux reçus, byte-identiques** ; [analyse et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md) |
| Compilé AMOS P0 | **NON TESTÉ, reporté** |
| Matériel physique | **NON TESTÉ** |

[CI Gate A exécutée](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756). Les 225 contrôles exécutent le code MC68020 réel **dans Unicorn avec services OS, Graphics et Blitter simulés**. Ils ne sont **pas** une preuve de lancement sous AMOS/WinUAE ou d'acceptation par AMOS Compiler.

## Campagne Runtime exécutée — preuves des journaux

L'unique [ASC actif](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **12 837 octets**, conserve les **405 frames** de base B8 S1 (9 étapes, 403 Clear / 405 Update / 50 Bob Off), puis ajoute **3 phases Bank Free + réactivation**. Deux fichiers Runtime transmis le **20/11/2026** donnent tous deux `RESULT 1`, `ERR 0`, `FRAMES_OK 405`, `STAGES_OK 9`, `BANK_FREE_CALLS 3`, `BANK_FREE_REARM 1`, `CLOSE_RETURNED 1` et `VERDICT PATH_OK` ; tous les échecs sont à zéro. Les fichiers ont exactement le même SHA256 et aucun identifiant de lancement distinct. [Analyse détaillée et limites des preuves](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md). [Protocole reproductible](../tests/current/README.md). Le SHA indiqué dans le journal est une étiquette ASC, sans mesure du binaire installé. Aucun VBL artificiel ajouté dans la boucle de 45 frames.

**Les deux PASS Runtime B8 S1 historiques (405/405) ne sont pas transférables à P0** ; la qualification P0 ci-dessus repose exclusivement sur ses propres journaux. Le Compiler C reste reporté ; les essais visuels et la mesure de Chip RAM ne sont pas établis par les fichiers. Les fonctions Bob avancées et Sprites de M19 restent ouvertes ; M20 est en attente.
