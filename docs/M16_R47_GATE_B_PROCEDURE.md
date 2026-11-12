# M16/R47 — Essai WinUAE expérimental `Aga Image Capture`

**État : préparation de la Gate B sous AMOS interprété. PAS ENCORE TESTÉE.** Version candidate R47 v0.12.2, **32 012 octets** et SHA256 `a550e9662cda1890aa8331c6e849e702300e6070e8e2caaf2fab9918613944d5`. **R46 C1 reste la bibliothèque officielle `LAST_GOOD`**. Le pont Compiler-safe a passé son audit structurel, mais les appels aux routines internes AMOS **n'ont encore jamais été testés sous WinUAE**. Un plantage reste possible ; utiliser **une configuration WinUAE de test / snapshot**, pas un Workbench ou disque de production.

## Fichiers

- [Bibliothèque R47 candidate](../dist/experimental/AMOSPro_AGA_M16_v0.12.2_IMAGE_CAPTURE_R47_CANDIDATE.Lib), **pas** le binaire officiel `dist/AMOSPro_AGA.Lib`.
- [Programme AMOS `M16_R47_IMAGE_CAPTURE_01.asc`](../tests/current/M16_R47_IMAGE_CAPTURE_01.asc), **une seule recette active**. Pas d'ABK préalable nécessaire : l'image est générée par les commandes 2D de l'extension.
- [Contrat et compte rendu des contrôles CPU](M16_AGAPIC_CAPTURE_DESIGN.md), [R46 C1 officielle inchangée](../dist/AMOSPro_AGA_LAST_GOOD.Lib).

## Procédure recommandée

1. **Dupliquer la configuration WinUAE et sauvegarder la bibliothèque AGA installée**, sans toucher à R46 C1 sur GitHub. Installer **temporairement dans la configuration de test seulement** la candidate expérimentale à la place de la bibliothèque chargée par AMOS ; redémarrer entièrement AMOS/WinUAE pour recharger l'extension. Ne pas utiliser le binaire natif R46 historique.
2. Dans AMOS, vérifier avec `List Bank` que **les banques 11 et 12 sont libres**. Le test ne les efface pas lorsqu'elles étaient préexistantes. Charger le `.asc` par **Project → Merge ASCII** dans un programme vide et lancer **en interprété seulement** pour commencer.
3. Contrôler l'affichage : motifs source en haut, copies capturées en bas (opaque, masquée, réimportée). Résultats attendus : `CAP 11 12 1 1`, `COLL 0 PRES 1`, tous les refus `0`, `DRAW O/M/RELOAD 1 1 1 RL 1`, **`RESULT 1`** et **`CLOSE RETURNED`**. Le test crée un fichier temporaire `RAM:M16_R47_CAPTURE11.abk` et efface à la fin **uniquement les banques qu'il a créées**.
4. **Ne compiler qu'après Gate B visuelle et fonctionnelle PASS.** Compiler un **nouvel exécutable** avec la candidate chargée, démarrer l'exécutable sous WinUAE, vérifier indépendamment le dessin et le retour à AMOS/Workbench. Un `Gate B PASS` ne prouve pas `Gate C PASS`.

**Si plantage / retour 0 inattendu :** relever l'instruction ou la ligne AMOS atteinte, le code de Guru et surtout le **PC fautif** sous WinUAE. Conserver la bibliothèque et le source exacts. Ne pas promouvoir ou remplacer `LAST_GOOD` par cette candidate. L'ABI des pseudo-appels AMOS `Rjsr` (GetAdr, Reserve, Eff, Change) sera examinée en priorité.
