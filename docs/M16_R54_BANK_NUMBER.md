# M16/R54 v0.12.9 — extensions additives par numero de banque

## Objectif

Offrir des appels plus simples, **sans casser aucun des exemples AMOS existants** :

| Ancien appel (conserve) | Nouveau raccourci (ajoute en R54) |
|---|---|
| `_OK=Aga Image Draw(Start(Bank),Length(Bank),X,Y,Mode)` | `_OK=Aga Bank Image Draw(Bank,X,Y,Mode)` |
| `_OK=Aga Font Bank Select(Start(Bank),Length(Bank))` | `_OK=Aga Bank Font Select(Bank)` |

**Aga Image Capture conserve ses SIX arguments** : `_OK=Aga Image Capture(Bank,X,Y,Width,Height,TransparentIndex)`. AMOS supporte aussi des commandes avec plus de cinq arguments ; les anciennes affirmations contraires etaient erronees et sont corrigees dans `EXTENSION_SOURCE_RULES.md`.

Les nouveaux wrappers sont deux fonctions natives 68000 (index AP20 57 et 58) qui resolvent le numero de banque par `Rjsr Bnk.GetAdr` **index 797** (source `+ILib.s` puis `+Lib.s`), reconstruisent la convention d'arguments des anciennes commandes, puis executent un **`BSR.W` direct et borne** vers les anciennes routines natives indices **55** (image) et **49** (font) dans le meme monolithe Compiler-safe. Anciennes entrees et tokens inchanges, hormis les marqueurs `GetP` de chaînage AP20 indispensables a l'ajout.

## Validation et livraison

- **R53 source heritee :** Gate A CPU/CI PASS ; Gates B/C WinUAE **PASS utilisateur** sur le test AGAPIC Image Capture, `RESULT 1`, `CLOSE RETURNED`, sans perte nette de Chip RAM. Gate D physique non testee.
- **R54 : Gate A CPU/CI PASS** ([run 43268287202](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43268287202)) : 53 commandes, 60 entrees AP20, monolithe **30 160 octets**, nouveaux wrappers **152 + 110 octets**, 12 cas Unicorn avec validation `Bnk.GetAdr`, transfert ABI vers les anciennes routines, conservation de A3/SP et des registres, et copie/relogement du stub Compiler hors de l'unite native.
- **R54 : Gate B AMOS interprétée PASS (capture WinUAE et rendu utilisateur confirmé), Gate C AMOS Compiler PASS (même programme compilé avec la R54, confirmation utilisateur) ; Gate D sur Amiga AGA physique NON TESTÉE.** Les résultats concernent le scénario de test, pas l'intégralité des 53 commandes.
- Bibliothèque officielle promue : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **32 364 octets**, SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, identique à l'[archive R54 figée](../dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib).
- Test utilisateur passé et archivé sans modification : [`tests/passed/M16_R54_BANK_NUMBER_01.asc`](../tests/passed/M16_R54_BANK_NUMBER_01.asc) ; ressources ABK et licence conservées dans `tests/current/`.
- **R54 `LAST_GOOD` officiellement promue**, identique à `dist/AMOSPro_AGA.Lib` et à l'archive R54 ; **R46 C1 reste figée** dans son archive Compiler-safe.

## Consignes pour le test

Copier la R54 sous le nom exact `AMOSPro_AGA.Lib` dans l'APSystem WinUAE de test, garder le meme slot, puis redemarrer AMOS. Importer le seul ASC de `tests/current/` dans un programme vierge. Les banques 10 et 25 sont chargees et **ecrasees** par le test (configuration jetable). Verifier `RESULT 1`, `CLOSE RETURNED` et les trois images / textes. Ensuite seulement recompiler depuis le nouvel environnement pour une Gate C distincte.

Les anciennes commandes et tous les `tests/passed/` historiques demeurent valides et n'ont pas ete modifies.

## Validation et clôture réelles (12/11/2026)

Le programme utilisateur R54 a affiché en interprété `DRAW NEW O/M OLD 1 1 1`, `FONT NEW/OLD/TEXT 1 1 1 1 1`, `INVALID IMG/FONT 0 0 NOS 0`, `RESULT 1`, `CLOSE RETURNED`. Rendu visuel confirmé correct. Chip Free de 1 787 856 à 1 800 592 octets (variation positive 12 736). L'utilisateur a ensuite confirmé explicitement : **« marche nickel en compilé »** sur la R54. **Gates A/B/C PASS sur ce scénario**, Gate D Amiga réel non testée ; pas de qualification exhaustive de toutes les commandes.

[Régression complète prépublication PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43271260029), R46 C1 archivée sans altération et test R54 archivé à l'octet près. `LAST_GOOD` égale `dist/AMOSPro_AGA.Lib` égale l'archive R54 au SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`. Après cette promotion, la CI du commit de publication est contrôlée séparément.
