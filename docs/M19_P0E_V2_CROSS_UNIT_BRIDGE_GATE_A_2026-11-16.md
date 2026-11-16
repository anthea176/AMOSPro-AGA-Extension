# M19 P0e — pont natif BOBS → AGA, relocation V2 : Gate A MC68020

Date : 16/11/2026. Dépôt unique `anthea176/AMOSPro-AGA-Extension`, branche `main`.

## Décision et statut

**Le pont natif privé est développé et testé. Gate A MC68020 PASS.** Il relie le registre P0e des objets persistants installé *virtuellement* dans l'unité AGA au groupe BOBS de la P0d, sans pointeur absolu figé, sans désassemblage du binaire officiel, sans nouvelle API publique et sans remplacer la `.Lib` active.

- [Émetteur du pont](../tools/m19_p0e_v2_object_bridge_emit.py), cible **MC68020/68EC020 minimum**. Appende **502 octets de vrai code natif** au préfixe BOBS P0d byte-exact. Les cinq entrées privées sont `object_bridge_put_selected`, `object_bridge_put`, `object_bridge_off`, `object_bridge_read`, `object_bridge_reset`.
- [Builder source vérifié](../tools/build_m19_p0e_v2_bridge_in_memory.py) : construit le binaire uniquement **en mémoire**, dans la chaîne source exacte P0d → P0e, avec audit AP20, provenance des unités, offsets, marqueurs V2 et **contrôle d'empreinte stricte**. **Aucun fichier .Lib alternatif créé**.
- [Banc MC68020](../tools/test_m19_p0e_v2_object_bridge_native.py) : **60 contrôles PASS**, deux placements d'unités distincts simulant l'interpréteur et le Compiler V2 ; **le vrai code assembleur de l'initialisation AGA ancienne est exécuté** avant les appels entre unités. Tests ABI de tous les registres AMOS conservés, A7 équilibré, retour D2/D3, propriétaire A5, sélection réelle de banques 10/11, mémoire inchangée après refus, signatures altérées, manque de mémoire mappée, AGA fermée et CPU sans AFF_68020.
- [CI complète M19 Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43966602587) : **PASS**. CPU/désassemblage du code réellement émis, services Exec/graphics/Intuition **simulés** ; **ce n'est pas WinUAE Runtime ni le vrai Compiler**.

## Calcul des adresses sans hypothèse de placement

La **source AGA historique est conservée octet pour octet**. Lors de `Aga Screen Open`, l'initialisation native stocke le pointeur vers l'état AGA à **`A5+$1C8`** ; cet état est situé à l'offset **`$1C2` (450)** dans sa propre unité AGA V2 (dispatcher compris).

Dans la candidate P0e, l'ancienne unité AGA pèse **56 580 octets** et le nouveau registre privé commence juste à sa fin. Le pont calcule donc :

```text
P0e_object_put = (A5+$1C8).L + (56580 - $1C2)
               = AGA_State + 56130
```

Ce décalage est **interne à l'unité AGA** : que le groupe BOBS soit situé à 0x100000 et AGA à 0x300000, ou les deux à d'autres adresses, la relation reste identique. Avant tout `JSR (A4)` vers l'entrée choisie, le pont exige :

1. CPU >= MC68020 et propriétaire AMOS `A5` non nul/alignment correct.
2. Pointeur `AGA_State` valide et mappé (`Exec TypeOfMem`), **Screen** encore ouvert.
3. Prologue source figé de l'ancien callback AGA End à `AGA_State-$168`, contrôlé contre sa signature exacte.
4. Entrée `object_put` mappée, borne finale du registre P0e mappée, signature native de 16 octets exacte et additions de pointeurs sans overflow.
5. Entrée privée sélectionnée par un offset natif **issu du code source**, jamais par une adresse arbitraire fournie par le programme.

Les fonctions internes du registre P0e continuent de contrôler les numéros d'objets, banques, images, positions, propriété `A5`, états actifs et écriture du descripteur atomique.

### Banque sélectionnée

**`object_bridge_put_selected`** récupère le numéro de banque dans le **vrai `bank_active_state` du groupe BOBS**, après le garde CPU. Le programme source peut alors définir un objet sous la banque 10, sélectionner la banque 11 et définir un autre objet : le premier conserve **10**, le second **11**. Les quatre autres entrées acceptent l'ABI native du registre ; la variante `put` prend explicitement son numéro de banque en D1.

**Restriction avant API publique :** il faudra encore vérifier que la banque actuellement sélectionnée est effectivement la banque AMOS vivante, après `Erase/Load` ou réallocation, avant de publier l'objet. Le futur `Aga Bob Draw` devra revalider identité/génération AGBO et Chip pour chaque objet, jamais conserver les pointeurs des anciennes allocations.

## Identité du candidat **privé et non installable**

| Propriété | Valeur |
| --- | --- |
| Base officielle P0d, toujours active | 91 300 octets ; SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be` |
| Registre P0e privé (AGA) | 2 332 octets dans le groupe AGA |
| Nouveau pont BOBS | 502 octets MC68020 |
| Candidate source-only totale | **94 144 octets** |
| SHA256 exact | **`f49037880fe75a3314364642336b3e5fb8f9e7854214cc1a23049fbc1becd0de`** |
| Unité BOBS V2 | 23 614 octets |
| Unité AGA V2 | 58 912 octets (inférieure à 65 534) |
| Table publique | **83 commandes / 93 entrées AP20 inchangées** |
| Déplacement PC16 maximal P0d → P0e | **32 196 → 32 698** |
| Marge résiduelle avant la limite de contrôle 32 766 | **68 octets seulement** |
| Gates B/C du NOUVEAU P0e | **NON TESTÉES** |

Le builder vérifie et fige **taille, SHA256, taille du pont et PC16**. **Aucune commande publique ne doit être ajoutée par simple append à BOBS** après ce jalon : **68 octets ne suffisent pas** pour exposer correctement `Aga Bob N,X,Y,I`, `Aga Bob Off N` et `Aga Bob Draw`. La suite nécessite une **restructuration contrôlée des groupes AP20/Compiler V2**, sans toucher à la base P0d validée tant que la nouvelle Gate A complète n'est pas passée.

## Actions restantes avant le premier objet public

1. Organiser les nouvelles **entrées publiques** dans des groupes V2 dont les branches interpréteur PC16 sont prouvées, sans ajout aveugle à BOBS.
2. Raccorder la commande de définition de Bob à `bridge_put_selected`, et `Aga Bob Off` à `bridge_off`, avec les vraies conventions des arguments AMOS/Compiler.
3. Créer `Aga Bob Draw` : parcourir 1..64 via `bridge_read`, vérifier/repréparer les banques en Chip, appeler **le peintre Safe/Blitter P0d** en respectant les masques et le clipping, puis laisser `Aga Swap` au programme.
4. **Cycle de vie :** intégrer `bridge_reset` au vrai `Screen Close` et à `End` AVANT destruction de l'état AGA. Le registre P0e actuel n'est pas encore nettoyé automatiquement ; ne pas activer cette version sans le pont de fermeture.
5. Exécuter la Gate A de la **nouvelle bibliothèque complète avec nouveaux tokens** avant **toute nouvelle autorisation de bascule** de `dist/AMOSPro_AGA.Lib` et de l'unique ASC actif, puis Gates B Runtime / C réel Compiler / D physique séparément.

## Protections

- **P0d active et fonctionnellement validée sous WinUAE en B/C par les journaux et la confirmation visuelle de l'auteur** ; voir [preuves](M19_P0D_GATES_BC_2026-11-16.md).
- `dist/AMOSPro_AGA.Lib` **inchangée**, un seul programme actif `tests/current/M19_P0D_BOB_BLIT_01.asc` **inchangé**.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 **inchangée** : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. Aucune promotion, autre branche, publication ou archive.
