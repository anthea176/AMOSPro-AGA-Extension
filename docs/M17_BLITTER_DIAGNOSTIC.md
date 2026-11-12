# M17 — Diagnostic initial du Blitter AGA (12/11/2026)

## Statut et limites

**M17 est ouvert en phase d'étude/diagnostic uniquement. Aucun patch 68000, aucune candidate, aucun test runtime M17, aucune promotion.** La base sûre est [R54 v0.12.9 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) (**32 364 octets**, SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, 53 commandes / 60 entrées AP20, Gates A/B/C PASS sur le scénario R54 ; Gate D matérielle NON TESTÉE). L'[archive R46 C1](../dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib) et les versions antérieures restent figées. Travail exclusivement sur `main`.

Le diagnostic porte d'abord sur `Aga Blit Fill` / `Aga Blit Clear`, puis éventuellement `Aga Blit Copy`. **Aucune cause des performances n'est encore démontrée par profilage de R54.**

## Données WinUAE historiques, à ne pas réinterpréter comme des mesures R54

[Baseline archivée R44 interprétée et R46 C1 compilée](../benchmarks/RESULTATS_32C_BASELINE_R44_2026-11-12.md), programme [`graphics_32c_v2.asc`](../benchmarks/graphics_32c_v2.asc) conservé sans modification, écran PAL **320×256×32 couleurs (5 bitplanes)** :

| Charge V2 par passage | AGA (médiane interprétée) | Comparaison historique | AGA (médiane compilée R46 C1) |
|---|---:|---:|---:|
| `Aga Blit Fill(60,60,200,136,31)` répété 100 fois | **54 ticks** | `Bar` AMOS : **40 ticks** | **54 ticks** |
| `Aga Blit Clear(0,0,320,256)` répété 80 fois | **117 ticks** | `Blitter Clear` AMCAF (5 plans) : **58 ticks** | **117 ticks** |

Un tick AMOS vaut 20 ms. **Les surfaces Fill et Clear diffèrent fortement** (200×136 contre 320×256), et les moteurs ne partagent pas la même architecture d'écran/buffer ; les deux écarts ne prouvent pas que `WaitBlit` est l'unique responsable. Le programme ne contrôle que le **dernier retour** de chaque série AGA (`AGA ERR 0`) : il ne constitue pas un test de tous les pixels. L'empreinte de la bibliothèque effectivement installée et le profil WinUAE détaillé des essais historiques n'ont pas été relevés.

## Constat source : chemin historique M12/R27

Sources consultées : [émetteur Safe Copy/Fill](../tools/m12_blit_safe_r27_emit.py), [builder R27](../tools/build_m12_blit_safe_r27.py), [contrat M12](M12_SAFE_BLITTER_R27.md) et [contrat Fill R14](M6_BLITTER_R14.md).

1. Le code `emit_fill_safe()` valide **avant le premier DMA** l'écran, le double buffer, les coordonnées et dimensions, la profondeur physique, les pointeurs de tous les bitplanes et l'index de palette. Les rectangles hors bornes sont refusés, pas clippés.
2. Le garde `_emit_safe_guard()` vérifie l'état de l'ancien buffer frontal, avec au plus un `GetMsg(SafePort)` non bloquant si un message `Safe` est attendu. **Un refus retourne 0 sans dessin** ; le bit `Disp` est préservé. Il ne faut pas déplacer cette protection après un premier DMA.
3. La boucle `plane_loop` choisit, pour chaque plan, le minterm **`$F0` ou `$00`** selon le bit de couleur, appelle `graphics.library/BltBitMap` avec masque **`1 << plan`**, teste l'échec, puis appelle `WaitBlit` **après chaque plan**. Il y a donc dans ce chemin **un appel `BltBitMap` et un `WaitBlit` par bitplane** lorsque tous les appels réussissent (5 de chaque en profondeur 5).
4. Le `Clear` historique est un **wrapper vers Fill avec Pen=0** ; il hérite de la validation `Safe`. Le builder R27 ajuste son `BSR.W` lorsque la taille de Fill change. **R54 a un pont Compiler-safe monolithique** : avant toute optimisation, recontrôler les vrais octets/offsets de ses segments natifs plutôt que supposer une disposition R27 toujours valable.
5. Le motif d'attente par plan est justifié dans l'émetteur historique par la dépendance d'ordre entre opérations ; **le supprimer sans preuve de sécurité serait une régression potentielle**. Les registres conservés et la convention `A3`/`D2`/`D3` doivent rester intacts.

## Pistes à expertiser, pas des correctifs approuvés

- Mesurer séparément coût d'entrée AP20/contrôles CPU, garde `Safe`, coût du `BltBitMap` par plan et attente `WaitBlit`, avec instrumentation **hors** benchmark de référence. Établir si les appels sont limités par le CPU, la préparation graphics.library, ou la contention DMA.
- Étudier **sur documentation AmigaOS et tests ciblés** la possibilité de traiter plusieurs plans compatibles avec un même minterm en un appel, **sans présumer que le masque multi-plan est valide ou plus rapide**. Conserver le comportement des couleurs mixtes et de la couleur 0.
- Vérifier qu'aucune optimisation n'altère le bit `Safe`, le bit `Disp`, le retour 0/1, `Swap`, l'ordre des opérations ni la fermeture `Aga Screen Close`. Ne pas confondre accélération et absence de synchronisation correcte.
- Le monolithe Compiler-safe R54 compte **30 160 octets** pour une limite de **32 768 octets** par routine copiée (marge théorique **2 608 octets** avant contraintes de relocation) : budget à auditer avant tout nouveau code.

## Suite du chantier, sous les Gates du projet

**Phase actuelle : diagnostic source et identification des mesures pertinentes.** La phase d'implémentation requerra un contrat minimal pour Fill/Clear, un builder reproductible depuis le **R54 `LAST_GOOD`**, des tests CPU 68000/ABI et AP20/relocation (Gate A), puis **WinUAE interprété (B)** et **nouvel exécutable Compiler (C)** distincts. Gate D sur Amiga physique reste séparée. Aucun test M17 n'est déclaré PASS à ce stade.

Après une éventuelle candidate validée, **rejouer le fichier `benchmarks/graphics_32c_v2.asc` à l'identique** (mêmes charges, 3 passages, même profil CPU/WinUAE, dans les deux modes), contrôler pixels, retours, swaps et mémoire puis publier **un nouveau comparatif avant/après**, sans toucher au baseline existant. **Ne promouvoir aucune optimisation sans validation utilisateur et régression complète de publication PASS.**

[Roadmap M17](ROADMAP.md) · [règles source](../EXTENSION_SOURCE_RULES.md) · [reprise courante](NEXT_SESSION.md).
