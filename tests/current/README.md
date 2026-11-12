# Test AMOS actif — M16/R47 capture AGAPIC (NON VALIDÉ sous WinUAE)

**Un seul fichier `.asc` actif** : [M16_R47_IMAGE_CAPTURE_01.asc](M16_R47_IMAGE_CAPTURE_01.asc). Le programme n'a pas encore été testé sous AMOS interprété (Gate B) ni Compiler (Gate C). **R47 est expérimentale**, construite à partir de la bibliothèque R46 C1 Compiler-safe, et ne doit pas remplacer `LAST_GOOD` sans nouvelle validation. Test dans une **configuration WinUAE isolée avec sauvegarde**.

**Avant de lancer :** les banques AMOS **11 et 12 doivent être libres** (`List Bank`). Le programme ne supprime jamais une banque préexistante. Il crée deux banques AGAPIC par capture depuis le back buffer, teste collision et cas invalides, redessine via l'ancienne syntaxe encore active `Aga Image Draw(Start(bank),Length(bank),X,Y,Mode)`, puis effectue `Save`/`Erase`/`Load` sur `RAM:M16_R47_CAPTURE11.abk`. Il supprime ensuite seulement les banques qu'il a créées.

**Sortie attendue si WinUAE valide réellement la candidate :** `CAP 11 12 1 1`, `COLL 0 PRES 1`, tous les refus à `0`, `DRAW O/M/RELOAD 1 1 1 RL 1`, **`RESULT 1` et `CLOSE RETURNED`**. La source du programme est une recette à exécuter, **pas un PASS déclaré**. Si crash, noter l'étape, le PC et la configuration.

**Version officielle inchangée :** [R46 v0.12.1-C1](../../dist/AMOSPro_AGA.Lib) = [LAST_GOOD](../../dist/AMOSPro_AGA_LAST_GOOD.Lib), 29 964 octets, SHA256 `d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b`. Les [tests historiques validés](../passed/R46_C1_COMPILER_ALL_IN_ONE.asc) ne changent pas. [Contrat / tests M16](../../docs/M16_AGAPIC_CAPTURE_DESIGN.md).
