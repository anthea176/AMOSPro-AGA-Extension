# M16/R48 — Isolement contrôlé de la tokenisation et de l'ABI

**R48 est un outil de diagnostic uniquement : elle ne capture AUCUNE image.**
La R47 présente un appel qui provoque sous AMOS `Non dimensioned array`, bien que sa signature à six paramètres soit structurellement valide ; les versions précédentes contiennent déjà des commandes à 6 et 8 paramètres. La cause exacte n'est pas démontrée.

La bibliothèque R48 garde volontairement **le même token `Aga Image Capture`, ses 6 paramètres, l'entrée AP20 n°56, ses 58 entrées, 51 commandes et la même taille totale de 32 012 octets que R47**. Toutes les anciennes routines sont byte-for-byte inchangées ; seule la nouvelle routine 68000 est remplacée par un stub sans effet de bord qui vérifie **D3=-1 et A3=(16,16,16,16,11)**, renvoie 1 si l'ABI est conforme, sinon 0. Aucune banque, aucun écran, aucune allocation, aucune bibliothèque système ni pseudo-`Rjsr` AMOS ne sont utilisés dans le stub.

Un résultat `Non dimensioned array` **avec R48** renforcerait fortement la piste de reconnaissance du token ; un résultat `RESULT 1` en interprété distinguerait la tokenisation/ABI du code natif R47 et orienterait vers les appels aux banques. **Les tests hôtes (Gate A) ne démontrent pas la compatibilité WinUAE.** R48 ne doit jamais être promue comme extension utilisable, ni compilée, ni installée hors environnement de test. Conserver R46 C1 officielle `LAST_GOOD`.

[Test interprété unique](../tests/diagnostics/M16_R48_TOKEN_ABI_PROBE_01.asc) · [builder reproductible](../tools/build_m16_r48_token_probe.py) · [tests de CPU simulé](../tools/test_m16_r48_token_probe.py).
