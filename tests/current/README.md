# Test actif — M19 AP20 V2 ISLANDS : Runtime et vrai AMOS Compiler

**Après validation B/C du banc à cinq unités, les deux sondes temporaires ont été retirées de la seule bibliothèque active.** La version quatre unités décrite ci-dessous est revenue à son empreinte antérieure strictement identique. Les [Gates B/C de la cinquième unité](../../docs/M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md) restent documentées séparément. Aucune cinquième unité vide n'est distribuée.


**Bascule de test autorisée explicitement le 17 novembre 2026.** Objectif : vérifier le dispatch AP20 V2 par îlots et l'acceptation des entrées/groupes entrelacés par le véritable AMOS Compiler. **Ce test n'est pas une validation des Bobs persistants P0f ni des Sprites matériels.**

## Binaire et programme uniques

- **Bibliothèque canonique installable** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **96 908 octets** ; SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`.
- **Builder déterministe** : [`tools/build_m19_ap20_islands_in_memory.py`](../../tools/build_m19_ap20_islands_in_memory.py), source P0f SHA256 `6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45`. 85 commandes, 178 entrées AP20, 4 groupes natifs byte-exacts ; déplacement PC16 max 854 octets.
- **Seul ASC actif** : [`M19_AP20_ISLANDS_01.asc`](M19_AP20_ISLANDS_01.asc), dérivé du programme P0d validé et renommé uniquement pour l'identité de campagne, les messages et les journaux. Aucun fichier IFF ou ABK externe.
- **P0d historique** : 91 300 octets / SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`, toujours reproductible via son builder et récupérable au commit précédent (pas de bibliothèque alternative dans `dist/`).
- **`LAST_GOOD` R84** : inchangée, 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.

## Résultats réels reçus le 17 novembre 2026

**Gate B Runtime : PASS** (journal utilisateur `M19_AP20_ISLANDS_RUNTIME.TXT` : `PRG_STATE 1`, `RESULT 1`, `ERR 0`). **Gate C vrai AMOS Compiler : PASS** (journal `M19_AP20_ISLANDS_COMPILED.TXT` : `PRG_STATE -1`, `RESULT 1`, `ERR 0`). **La capture d'écran fournie par l'auteur provient précisément de la VERSION COMPILÉE**, avec les quatre Bobs, transparence et clipping conformes. La capture ne prouve pas l'affichage Runtime, attesté uniquement par son TXT.

**Rapport exact (SHA256 des deux TXT reçus et de la capture, limites) :** [Gates B/C du 17 novembre](../../docs/M19_AP20_V2_GATES_BC_2026-11-17.md). La chaîne `CANDIDATE SHA256` écrite par l'ASC **n'est pas un hachage indépendant** de la bibliothèque installée. Gates A/B/C PASS **pour ce scénario uniquement**, Gate D non testée. Aucun test des Bobs persistants ou d'une cinquième unité native.

## Préparation WinUAE

1. Synchroniser le clone Windows du dépôt sur `main`. Sauvegarder **hors dépôt** l'actuelle copie du slot `APSystem` avant remplacement ; ne pas toucher à `LAST_GOOD`.
2. Installer exactement `dist/AMOSPro_AGA.Lib` dans l'unique slot d'extension AGA d'AMOS Professional. Vérifier **96 908 octets** et l'empreinte **de la copie installée** avec PowerShell : `Get-FileHash "CHEMIN\\AMOSPro_AGA.Lib" -Algorithm SHA256`. Redémarrer AMOS, puis vérifier qu'il reconnaît ses commandes.
3. Démarrer WinUAE AGA PAL, **68030 + JIT activé** pour les Gates B/C. Relever version d'AMOS Professional, version exacte du Compiler V2 et configuration RAM/CPU. Vérifier que la banque AMOS **24 est libre** : le banc refuse une banque occupée et ne l'efface pas.
4. Dans un **programme AMOS vide**, utiliser **Project → Merge ASCII** pour importer `tests/current/M19_AP20_ISLANDS_01.asc` (ne pas faire `Load` sur le texte source).

## Gate B — Runtime

Exécuter dans AMOS Runtime, journal `RAM:M19_AP20_ISLANDS_RUNTIME.TXT` avec `RUN_MODE RUNTIME` et `PRG_STATE 1`. Le test ouvre l'écran AGA 320×256×256, prépare deux images AGBO, applique un masque indépendant à la première, dessine **quatre Bobs**, dont deux coupés aux bords, appelle un ID invalide (retour attendu 0) puis effectue **un seul Swap explicite**.

**Observation visuelle obligatoire** : sur fond bleu sombre, premier Bob rouge/orange à (103,72) avec transparence interne, deuxième jaune opaque à (180,110), Bob rouge rogné à gauche (X=-5,Y=170), Bob jaune rogné à droite (X=315,Y=200). Aucun écran vide, pixel parasite, freeze ou Guru. L'écran doit se fermer, revenir à AMOS et la banque 24 être nettoyée.

## Gate C — vrai AMOS Compiler V2

Depuis **le même ASC et la même bibliothèque** : compiler un **nouvel exécutable avec le véritable AMOS Compiler V2**, puis le lancer sous WinUAE. Vérifier les mêmes quatre Bobs, les couleurs/masques/clipping, l'absence de crash/freeze, la fermeture et le retour au système. Enregistrer séparément `RAM:M19_AP20_ISLANDS_COMPILED.TXT` avec `RUN_MODE COMPILED` et `PRG_STATE -1`. Un résultat `Prg State 0` correspond à l'interpréteur strict, **pas** à la Gate B.

Pour chaque journal : `TEST M19_AP20_ISLANDS_01`, `CANDIDATE SHA256 34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, `RESULT 1`, `ERR 0`, `VERDICT PASS`, `IMAGE_COUNT 2`, `BANK_LENGTH 1036`, `MASK_FLAG 1`, `BLIT1/2 1`, `CLIP_LEFT/RIGHT 1`, `MISSING_IMAGE 0`, `SWAP 1`, `CLOSE 1`. Un PASS écrit par l'ASC **n'est pas** une preuve du SHA installé ni une validation visuelle.

## Gates et points non encore couverts

**Gate A source/CPU MC68020 : PASS** ([CI M19](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43973879479)). **Gate B Runtime : PASS sur le journal reçu ; Gate C vrai Compiler : PASS sur le journal et la capture explicitement issue du compilé** ([preuves](../../docs/M19_AP20_V2_GATES_BC_2026-11-17.md)). **Gate D Amiga physique : NON TESTÉE.**

Ce scénario teste surtout **AGA + BOBS** ; il ne couvre pas exhaustivement les commandes C2P/IFF ni les nouvelles commandes P0f d'objets persistants, dont le nettoyage End n'est pas encore finalisé. Il vérifie le risque central de cette première bascule : accès aux commandes publiques et exécution d'un programme compilé avec les groupes AP20 entrelacés.

En cas d'échec au chargement/Compiler, **ne pas modifier l'ASC pour masquer un défaut natif** : relever le point d'arrêt, la configuration, les logs et restaurer localement la P0d validée si nécessaire. Aucune promotion de `LAST_GOOD` n'est autorisée par cette bascule.
