# M16/R47 — Essai WinUAE expérimental `Aga Image Capture`

**État au 12/11/2026 : Gate B FAIL au premier essai utilisateur sous AMOS interprété/WinUAE.** Version candidate R47 v0.12.2, **32 012 octets** et SHA256 `a550e9662cda1890aa8331c6e849e702300e6070e8e2caaf2fab9918613944d5`. **R46 C1 reste la bibliothèque officielle `LAST_GOOD`**. Le pont Compiler-safe a passé son audit structurel, mais les appels aux routines internes AMOS **n'ont encore jamais été testés sous WinUAE**. Un plantage reste possible ; utiliser **une configuration WinUAE de test / snapshot**, pas un Workbench ou disque de production.

## Incident observé : processus WinUAE en crash

La seule sortie visible est le titre AMOS `M16/R47 IMAGE CAPTURE TEST`, puis WinUAE x64 affiche `Crash detected` et indique l'enregistrement d'un minidump Windows `.dmp`. Aucun Guru Amiga ni PC fautif n'est disponible. Le test original ne comporte **aucun repère intermédiaire** entre son titre et ses opérations AGA : il est impossible de prouver que `Aga Image Capture` a été exécutée avant le crash. Les tests CPU/CI PASS restent inchangés, mais ne remplacent pas cette Gate B **FAIL**. Conserver le `.dmp` et les logs WinUAE, ne pas compiler, ne pas réinstaller aveuglément la candidate ; identifier d'abord l'étape réellement fautive. Les indices `Rjsr` concordent avec les définitions numérotées du source AMOS Professional 365, mais cette concordance ne valide pas l'ABI du runtime installé. **R46 C1 reste `LAST_GOOD`.**

La procédure ci-dessous est conservée comme recette expérimentale d'origine : **ne pas la répéter tant que la cause n'est pas cadrée**.

## Analyse du minidump Windows fourni (12/11/2026)

Fichier utilisateur : `winuae_x64_6.0.3_R_2026.11.12_16.12.24.dmp` (268 636 octets, minidump Windows, 16 streams, horodatage interne 15:12:25 UTC). Décodage direct des streams MINIDUMP (sans symboles WinUAE) : **exception Windows `0xC0000005` (access violation)**, paramètre 0 = `0` (**lecture**), adresse lue `0x622A709D`, adresse de l'instruction en faute `0x10559285`, dans `winuae64.exe` chargé à `0x10000000` (**offset `0x00559285`**). Contexte x64 : `RAX=0x622A709A`, `RIP=0x10559285`. Aucune preuve de fonction WinUAE symbolisée ni du PC Motorola 68000 : **ne pas interpréter le RIP Windows comme PC Amiga**. La proximité de RAX et de l'adresse de lecture est un indice, non une cause prouvée. Conserver la candidate R47 historique et effectuer un jalonnement AMOS ciblé, avec la bibliothèque R46 C1 de secours. **Gate B FAIL et Gate C non testée.**

## R47 — test d'isolement du premier crash (sans capture)

Pour éviter de relancer immédiatement le test long qui a fait planter **WinUAE lui-même**, commencer par [`tests/diagnostics/M16_R47_CRASH_ISOLATION_00.asc`](../tests/diagnostics/M16_R47_CRASH_ISOLATION_00.asc), avec **la même candidate R47**, exclusivement dans la configuration de test sauvegardée. Importer par **Project → Merge ASCII** et exécuter **en interprété**. Ce programme n'appelle **pas** `Aga Image Capture` et ne crée aucune banque : il affiche `S01 BEFORE DETECT`, `S02 DETECT RETURNED`, `S03 BEFORE OPEN`, puis tente `Aga Screen Open`/`Aga Screen Close`. En cas de réussite : `S05 OPEN/CLOSE RETURNED 1` et `RESULT 1`. Si crash : noter le **dernier Sxx effectivement affiché**. Cela sépare une défaillance déjà présente dans le pont AP20/des commandes existantes d'un problème spécifique à la capture ; ce test n'établit pas à lui seul la cause du crash. **Ne pas compiler et ne pas promouvoir R47.**

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
