# M16/R48 — Isolement contrôlé de la tokenisation et de l'ABI

**R48 est un outil de diagnostic uniquement : elle ne capture AUCUNE image.**
La R47 présente un appel qui provoque sous AMOS `Non dimensioned array`, bien que sa signature à six paramètres soit structurellement valide ; les versions précédentes contiennent déjà des commandes à 6 et 8 paramètres. La cause exacte n'est pas démontrée.

La bibliothèque R48 garde volontairement **le même token `Aga Image Capture`, ses 6 paramètres, l'entrée AP20 n°56, ses 58 entrées, 51 commandes et la même taille totale de 32 012 octets que R47**. Toutes les anciennes routines sont byte-for-byte inchangées ; seule la nouvelle routine 68000 est remplacée par un stub sans effet de bord qui vérifie **D3=-1 et A3=(16,16,16,16,11)**, renvoie 1 si l'ABI est conforme, sinon 0. Aucune banque, aucun écran, aucune allocation, aucune bibliothèque système ni pseudo-`Rjsr` AMOS ne sont utilisés dans le stub.

Un résultat `Non dimensioned array` **avec R48** renforcerait fortement la piste de reconnaissance du token ; un résultat `RESULT 1` en interprété distinguerait la tokenisation/ABI du code natif R47 et orienterait vers les appels aux banques. **Les tests hôtes (Gate A) ne démontrent pas la compatibilité WinUAE.** R48 ne doit jamais être promue comme extension utilisable, ni compilée, ni installée hors environnement de test. Conserver R46 C1 officielle `LAST_GOOD`.

[Test interprété unique](../tests/diagnostics/M16_R48_TOKEN_ABI_PROBE_01.asc) · [builder reproductible](../tools/build_m16_r48_token_probe.py) · [tests de CPU simulé](../tools/test_m16_r48_token_probe.py).

## Candidate reproductible et essai WinUAE

- [Binaire R48 de diagnostic](../dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib) — **32 012 octets**, SHA256 `c30cfcc33ee50bb1f18c36225ccd7a5a6df7860e11201608d1801a0095687028`, Gate A CPU/CI PASS ([workflow](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43253092738)). Le binaire est dans l'archive expérimentale : **ne pas le substituer à la bibliothèque officielle sur GitHub**.
- Utiliser une **configuration WinUAE isolée avec sauvegarde** ; y installer temporairement la R48 à la place de la bibliothèque AGA dans le même slot, quitter puis redémarrer AMOS. Charger [M16_R48_TOKEN_ABI_PROBE_01.asc](../tests/diagnostics/M16_R48_TOKEN_ABI_PROBE_01.asc) par **Project → Merge ASCII** dans un programme vide, lancer en **interprété seulement**. Il n'est pas nécessaire d'ouvrir un écran ou de préparer des banques.
- **Attendu si token reconnu et ABI correcte** : `BEFORE R48 CALL`, `AFTER R48 CALL 1`, `RESULT 1`. Si `Non dimensioned array` se reproduit, relever cette erreur telle quelle ; elle n'est pas un PASS. Si WinUAE plante, conserver minidump/PC, ne pas compiler.
- R48 n'effectue **aucune capture** ; même si le diagnostic PASS, **ne pas la promouvoir** et ne pas lancer les exemples de capture réelle avec elle. R46 C1 reste `LAST_GOOD`. M16 ouvert.

## Gate B interprétée — PASS utilisateur (12/11/2026)

Capture WinUAE communiquée : `R48 TOKEN/ABI PROBE`, `BEFORE R48 CALL`, `AFTER R48 CALL 1`, `RESULT 1`. **L'ABI AP20 et le token avec six paramètres sont donc validés sous l'interpréteur.** Cela n'implique aucune capture d'image. La R48 est archivée ; la suite R49 isole l'appel interne `Rjsr Bnk.GetAdr` ; [procédure R49](M16_R49_GETADR_PROBE.md). `LAST_GOOD` R46 C1 inchangée.
