# M19 P0e — Répartition AP20 V2 BOBS/AGA et nettoyage Screen Close : Gate A

**Date : 16 novembre 2026.** Dépôt unique `anthea176/AMOSPro-AGA-Extension`, **branche `main`**. Cible du nouveau natif : **MC68020/68EC020 minimum**. Aucun changement de bibliothèque active autorisé par ce jalon.

## Résultat vérifié

**La contrainte d'assemblage AP20 PC16 est débloquée pour le premier palier public.** Les commandes source-only `Aga Bob N,X,Y,I` et `Aga Bob Off N` restent représentées dans le nouveau binaire **en mémoire** ; le moteur de Bobs persistants avec `Draw` n'est **pas encore livré**.

L'ancien pont natif complet de **502 octets** ajouté au groupe BOBS faisait atteindre **32 760** à la distance RBSR maximale (seulement 6 octets libres). La nouvelle organisation déporte sa logique générique dans **AGA**, à côté des 64 objets, et conserve uniquement un relais dans **BOBS**. L'ancienne P0d reste le **préfixe strictement identique** dans les deux unités.

| Propriété | Ancien palier public P0e | Nouveau P0e réparti | Nouveau avec reset Close |
| --- | ---: | ---: | ---: |
| Taille candidate mémoire | 94 232 | 94 508 | **94 532** |
| SHA256 | `a1aab227dd8c1e19be88f11878513f341edfc92bf19f33520a029625a3827969` | `ca7dae58934056e4baf7cd3515a02363b05db75ece934afcd721988a952783ec` | **`8185ae2d056da209a88c0b91e315d1cbb97acabadf7b55352e8cd7a348c1b207`** |
| Commandes / entrées AP20 | 85 / 95 | 85 / 95 | 85 / 95 |
| Groupe natif BOBS | 23 652 | 23 444 | **23 468** |
| Groupe natif AGA | 58 912 | **59 382** | **59 382** |
| BOBS ajoutés à P0d | 540 octets | 332 octets | **356 octets** |
| Pont générique déplacé dans AGA | Non | 470 octets | 470 octets |
| Registre privé (dans AGA) | 2 332 | 2 332 | 2 332 |
| Plus grande distance RBSR / PC16 | 32 760 | 32 552 | **32 576** |
| Marge de contrôle (< 32 766) | 6 | 214 | **190 octets** |

Les valeurs de taille et SHA sont vérifiées **octet pour octet** par les deux builders. La structure HUNK/AP20, les jetons et les marqueurs `GetP` sont reconstruits puis relus. **Aucune modification des entrées natives originales R84/P0d**, ni de leurs octets AGA/C2P/IFF.

## Architecture de relocation

- [Émetteur du pont privé d'origine](../tools/m19_p0e_v2_object_bridge_emit.py) : nouveau mode source `aga_side=True`, qui **supprime réellement** la lecture PC-relative de `bank_active_state` (valable uniquement dans BOBS). Le mode original reste inchangé et son builder SHA-pinné continue de PASSER.
- [Émetteur de la version répartie](../tools/m19_p0e_split_bridge_emit.py) : **332 octets de relais et de wrappers publics** ajoutés à BOBS. Les quatre appels privés utilisent le vrai état AGA installé à `A5+$1C8` pour retrouver la partie native déportée à `AGA_State+58462+offset` ; vérifications CPU, `Exec TypeOfMem` de l'état et de la cible, signature d'entrée MOVEM et absence de dépassement de pointeur. `put_selected` lit **la banque active réelle du groupe BOBS** avant l'appel.
- Le pont générique de **470 octets** réside à la fin du groupe AGA, après le registre P0e de **2 332 octets**. Il conserve ses propres contrôles de propriétaire, de pointeurs, de signature native `End`, et des 64 emplacements. Les deux groupes peuvent être relocalisés **séparément** sans devoir être physiquement voisins.
- [Builder AP20 réparti](../tools/build_m19_p0e_split_public_in_memory.py) : remappe les quatre indices de groupes existants de **+2** pour les deux nouveaux jetons source-only, mais conserve les octets natifs historiques. Exige **214 octets de marge**, 85 commandes / 95 entrées et l'empreinte exacte `ca7dae...`.

### Nettoyage avant `Aga Screen Close`

- [Émetteur natif](../tools/m19_p0e_split_close_emit.py) : nouveau wrapper **24 octets** qui commence par `relay_reset_entry`, puis appelle le **vrai pont de fermeture P0d**. La table de 64 objets est vidée pendant que `AGA_State` et l'écran sont encore vivants, **avant** le nettoyage Chip/Blitter et l'ancienne fermeture AGA.
- [Builder de fermeture](../tools/build_m19_p0e_split_close_in_memory.py) : redirige **seulement le stub public n°8** `Aga Screen Close` vers le wrapper, et conserve **son véritable marqueur GetP original** (une première assertion incorrecte a été corrigée, sans changer l'API). Le builder exige le SHA exact `8185ae...`, **94 532 octets** et une distance PC16 maximale **32 576**.
- Si le reset refuse un propriétaire, un CPU incompatible ou une ancre AGA invalide, la fermeture destructrice **n'est pas appelée**, et la table reste intacte.

## Preuves natives

| Contrôle | Preuve | Portée |
| --- | --- | --- |
| [Répartition native MC68020](../tools/test_m19_p0e_split_bridge_gate_a.py) | **56 cas PASS**, deux placements de groupes AGA/BOBS indépendants | Exécute l'initialisation AGA d'origine et les opérations source Set/Off, lecture, reset, changement de banque 10/11, signature invalidée, pointeurs refusés, ABI, registres et pile |
| [Reset Close natif](../tools/test_m19_p0e_split_close_gate_a.py) | **16 cas PASS**, deux placements | Exécute **réellement les instructions de l'ancien AGA Screen Close** après reset de la table ; vérifie l'absence de fermeture si le reset échoue |
| [Génération / longueur / PC16](../tools/build_m19_p0e_split_close_in_memory.py) | **PASS**, empreinte et décalages figés | Les deux nouveaux tokens et le stub Close sont structurellement valides dans AP20 V2 |
| [CI M19 Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43969689292) | **PASS** | Execution via Unicorn **MC68020**, Capstone 020 ; fonctions Exec/AMOS/graphics **simulées** |

**Limites des preuves :** aucune compilation ni exécution WinUAE de la candidate P0e. Les tests ne valident pas `Aga Bob Draw`, le retour graphique réel, ni le callback de fin de programme `End`. **Gate B, Gate C et Gate D P0e : NON TESTÉES.** Seule la P0d active est déjà validée par l'auteur en Runtime et Compiler, sur son test propre.

## Bloquants pour le prochain palier

1. **`Aga Bob Draw`** doit parcourir les objets actifs de 1 à 64 dans l'ordre, dessiner via la **chaîne P0d Safe/Chip/Blitter** dans le back buffer, laisser **l'unique `Aga Swap`** au programme et retourner un échec sans présenter le buffer si une banque n'est plus valide.
2. **Association aux banques et sécurité Erase/Load :** l'objet P0e stocke actuellement **le numéro de banque mais pas une identité figée de l'allocation/génération** (la sixième Long du descripteur est réservée). Avant Draw, il faut enregistrer cette identité lors de `Aga Bob`, la comparer au contenu réel de la banque AMOS, refuser toute source remplacée et contrôler les nouvelles allocations/Chip/staging. **Ne jamais créer silencieusement une banque absente pour dessiner un objet.**
3. **`End` :** le callback historique P0d `program_end_arm/bridge` possède déjà les hooks AMOS ; un hook concurrent casserait l'armement P0d. Intégrer le reset des objets sans remplacer les hooks non propriétaires, ni faire échouer les appels publics P0d `Aga Bob Blit`. Le reset sur `Aga Screen Close` **ne remplace pas** cette validation.
4. **Budget PC16 :** marge actuelle **190 octets**, donc code Draw lourd à déporter dans AGA ; BOBS conserve les minuscules relais source-validés. Ajouter chaque nouveau stub avec test des déplacements, en particulier l'entrée réservée n°0.
5. **Tests de rendu :** vérifier sous MC68020 les deux banques et plusieurs objets partageant une seule copie Chip, transparence indépendante, clipping 1/17/31/32/37, pixel couleur 0 opaque, double buffering et aucune présentation implicite, avant une nouvelle autorisation de bascule et les Gates B/C WinUAE.

## Protections

- Bibliothèque installable **P0d toujours active** : `dist/AMOSPro_AGA.Lib`, **91 300 octets**, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`.
- ASC actif unique **inchangé** : `tests/current/M19_P0D_BOB_BLIT_01.asc`.
- **`LAST_GOOD` R84 protégée** : `dist/AMOSPro_AGA_LAST_GOOD.Lib`, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.
- Aucun binaire P0e installé, aucun fichier `.Lib` expérimental, aucun archivage de tests, aucune promotion, aucune autre branche ni dépôt.
