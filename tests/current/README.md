# M19 — AP20 V2, CINQUIÈME UNITÉ : test Runtime et vrai AMOS Compiler

**Bascule de test expressément autorisée le 17 novembre 2026**, sur `main`. **Les deux fonctions `Aga Unit Five Sum` et `Aga Unit Five Tail` sont des PROBES TEMPORAIRES. Après le résultat des Gates B/C, elles devront être retirées de l'API publique, ainsi que le code de diagnostic sans utilité de production.** Ne pas les promouvoir, documenter comme nouvelles fonctionnalités AGA ni les garder dans la version finale.

## Candidate unique

- **Bibliothèque installable unique** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **138 044 octets**, SHA256 **`967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1`**.
- **Builder exact en mémoire** : [`tools/build_m19_ap20_unit5_in_memory.py`](../../tools/build_m19_ap20_unit5_in_memory.py) : **87 commandes dont 2 probes provisoires, 181 entrées AP20, 5 unités**, offset profond `$A034` (41 012), PC16 maximal 854 octets, groupe supplémentaire de 41 060 octets. **Gate A source/MC68020 PASS** ([CI 44135445819](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44135445819)).
- **Un seul ASC actif** : [`M19_AP20_UNIT5_01.asc`](M19_AP20_UNIT5_01.asc) ; dérivé du banc quatre Bobs validé, mais **nouveau programme de test à exécuter intégralement**, sans IFF/ABK externes.
- **Version précédente quatre unités** : 96 908 octets, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, **Gates B/C PASS** avec l'ancien ASC et sa capture **issue du compilé** ([rapport historique](../../docs/M19_AP20_V2_GATES_BC_2026-11-17.md)). Elle reste reproductible par son builder et récupérable via Git ; aucune seconde .Lib dans `dist/`.
- **`LAST_GOOD` R84** : **inchangée**, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. Pas de promotion ni d'archive automatique.

## Préparation sous WinUAE

1. Synchroniser le dépôt Windows sur `main`. Sauvegarder **hors dépôt** l'ancienne copie installée dans `APSystem` si nécessaire.
2. Installer **uniquement** `dist/AMOSPro_AGA.Lib` dans le slot d'extension AGA d'AMOS Professional, vérifier la taille **138 044 octets** et le SHA256 **de la copie effectivement installée** avec PowerShell : `Get-FileHash "CHEMIN\\AMOSPro_AGA.Lib" -Algorithm SHA256`. **Redémarrer** AMOS pour recharger les commandes.
3. Configuration de validation fonctionnelle : WinUAE **AGA PAL, CPU 68030 avec JIT activé**, en conservant les réglages RAM connus. Relever la version exacte d'AMOS Professional et de son Compiler V2. La **banque 24** doit être libre, sinon le test refuse de la réutiliser.
4. Dans un **nouveau programme AMOS vide**, faire **Project → Merge ASCII** sur `tests/current/M19_AP20_UNIT5_01.asc`. Ne pas charger l'ASCII comme un programme binaire AMOS.

## Scénario unique (mêmes opérations en Runtime et en compilé)

Le programme vérifie `Aga Detect` puis exécute en premier la **cinquième unité native** :
- `Aga Unit Five Sum` sans parenthèses : **`UNIT5_SUM 5222400`** (somme réelle de 40 Kio, soit `$004FB000`) ;
- `Aga Unit Five Tail` sans parenthèses : **`UNIT5_TAIL 5898757`** (offset natif non signé `$A034` > 32 Kio, constante `$005A0205`) ;
- `UNIT5_OK 1` si les deux contrôles réussissent. Sinon `ERR 13`, avec fermeture/nettoyage sans dessin.

Ensuite, comme dans l'ancienne Gate C, il ouvre un écran AGA **320×256×256**, crée deux images AGBO en banque 24, applique un masque indépendant, dessine quatre Bobs (dont clipping gauche/droite), rejette l'image ID 4000, fait **un seul Swap explicite**, observe le résultat puis ferme l'écran.

**Vérification visuelle** : fond bleu sombre, Bob rouge/orange avec trou transparent vers (103,72), Bob jaune opaque vers (180,110), rouge partiel à gauche et jaune partiel à droite. L'écran doit se fermer sans Guru, revenir à AMOS, et la banque 24 doit être supprimée.

## Gate B — AMOS Runtime WinUAE

Lancer le programme et récupérer **`RAM:M19_AP20_UNIT5_RUNTIME.TXT`**. Les points discriminants sont `RUN_MODE RUNTIME`, **`PRG_STATE 1`**, `UNIT5_SUM 5222400`, `UNIT5_TAIL 5898757`, `UNIT5_OK 1`, `RESULT 1`, `ERR 0`, `VERDICT PASS`.

## Gate C — véritable AMOS Compiler V2

Compiler un **nouvel exécutable à partir du même ASC**, puis le lancer sous WinUAE. Récupérer séparément **`RAM:M19_AP20_UNIT5_COMPILED.TXT`** : `RUN_MODE COMPILED`, **`PRG_STATE -1`** et les mêmes valeurs des deux probes. Il faut contrôler les quatre Bobs dans la **version compilée**, fournir une nouvelle capture et vérifier l'absence de Guru.

Les deux journaux doivent aussi indiquer `TEST M19_AP20_UNIT5_01`, `IMAGE_COUNT 2`, `BANK_LENGTH 1036`, `MASK_FLAG 1`, `BLIT1 1`, `BLIT2 1`, `CLIP_LEFT 1`, `CLIP_RIGHT 1`, `MISSING_IMAGE 0`, `SWAP 1`, `CLOSE 1`. La ligne `CANDIDATE SHA256` est une **chaîne fixe** dans l'ASC, **pas** le SHA de la .Lib chargée.

## Statut et suppression des probes après essai

**Gate A MC68020 PASS ; Gates B et C de cette candidate CINQ unités NON TESTÉES ; Gate D sur Amiga physique NON TESTÉE.** Les anciens journaux quatre unités ne remplacent pas cette nouvelle campagne.

**Après réception des journaux et du rendu B/C :** retirer **`Aga Unit Five Sum`** et **`Aga Unit Five Tail`** de la **table des tokens publics et des stubs de la bibliothèque de production**, supprimer ou remplacer leur charge native de 40 Kio non fonctionnelle, restaurer une API publique propre et reconstruire/tester la candidate suivante. Conserver les preuves source-only et le présent rapport dans le dépôt, sans maintenir les commandes de diagnostic dans une version destinée aux utilisateurs.

En cas de problème avec le vrai Compiler, relever précisément le stade où il échoue ; **ne pas maquiller l'échec par un ajustement AMOS BASIC**. La bibliothèque quatre unités historiquement validée reste récupérable à partir de Git. **Aucune promotion de `LAST_GOOD` ni modification des archives**.
