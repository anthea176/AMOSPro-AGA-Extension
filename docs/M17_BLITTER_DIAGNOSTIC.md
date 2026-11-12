# M17 — Diagnostic initial du Blitter AGA (12/11/2026)

## R57 0.13.2 — Gates B/C WinUAE PASS après Guru R56

**Faits utilisateur :** benchmark V2 R56 sous AMOS interprété **PASS** (`AGA ERR 0`, clôture sans erreur, Bar G 40/41/41, Clear G 59/58/58). En compilé, `Software Failure 8000000B` (Line-F), **Gate C R56 FAIL**. Le programme compilé de l'auteur utilise `Do / Wait Vbl / Loop` et non le `Wait Key` du test historique. Le PC de faute n'est pas disponible.

**Relecture des octets :** R56 conservait 620 octets du helper Fill R55, inutilisés, et ajoutait 580 octets du nouveau code : monolithe **31 360 octets**, sans dépasser la limite **32 768**. Les 59 stubs publics restaient identiques ; seuls deux octets de déplacement du `BRA.W` Fill changeaient dans le code existant. Le test CPU ne reproduit pas entièrement la transformation d'AMOS Compiler. **Ne pas conclure à un défaut de taille sans preuve.**

**R57 :** nouvelle implémentation `RectFill`/`SetRast` de 580 octets **à l'emplacement 30128**, ancien helper R55 de 620 octets remplacé (40 NOP de remplissage). **Saut Fill, BSR de Clear, stubs, dispatcher, offsets et taille du monolithe 30 780 octets = R55**. Aucun nouveau token, 53 commandes / 60 entrées AP20. [Binaire actif](../dist/AMOSPro_AGA.Lib) **32 980 octets**, SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0` ; [ASC actif unique](../tests/current/M17_R57_RAST_FILL_01.asc) avec boucle VBL. Pas de deuxième bibliothèque ni de branche. `LAST_GOOD` R54 inchangée.

**Validation :** [CI R57 Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43286230339) : 111 scénarios CPU, pixels, double buffering, Safe, ABI, branchement de Clear et égalité des stubs Compiler R55. **Gate C R57 compilée/WinUAE PASS sur capture utilisateur du 12/11/2026** : `M17-R57-RAST-FILL-01`, `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`, aucun Guru. **Gate B R57 AMOS interprété/WinUAE PASS** (capture utilisateur du 12/11/2026) : `M17-R57-RAST-FILL-01`, `IMAGE 320 X 256 PLANES 8`, `OPEN 1 DB 1 LOAD 1`, `DONE 40 C 14 F 13 P 13`, `C0 13 F0 13 P0 13 SWAP0 0`, `SAFEERR 0 SWAPERR 0 DRAWERR 0`, `CLOSED -1 RESULT 1`, `CLOSE RETURNED`. Le message de l'éditeur `Program interrupted at line 169` indique l'arrêt manuel dans la boucle finale `Do / Wait Vbl / Loop` (`Wait Vbl` ligne 169), **pas un plantage**. Gate B du test actif et Gate C du test compilé PASS indépendamment. Gate D Amiga physique non testée. **Gate D physique NON TESTÉE.** Le symptôme Line-F compilé de R56 disparaît dans la R57 sur ce scénario, conformément à l'hypothèse de placement, **sans preuve définitive du mécanisme exact**. **Benchmark V2 R57 compilé maintenant PASS**, mesures détaillées dans [`RESULTATS_32C_R57_COMPILER_2026-11-12.md`](../benchmarks/RESULTATS_32C_R57_COMPILER_2026-11-12.md) ; ne pas refaire les anciennes validations R54/R55 ni le test compilé R57.

### Performances R57 compilée (capture utilisateur)

- `BAR 100 G` : **41/40/41 ticks** (médiane **41**) contre R55 compilée **54/54/54** (médiane **54**), **−24,1 %** du temps.
- `CLEAR 80 G` : **58/58/58 ticks** (médiane **58**) contre R55 compilée **115/116/115** (médiane **115**), **−49,6 %**.
- `AGA ERR 0` ; `V2 FINISHED - CLOSE RETURNED`. BAR AMOS natif médiane **41**, CLEAR AMCAF **57** ticks.
- Ces chiffres comparent uniquement les exécutions **compilées** R55/R57, sans revendiquer de gain matériel réel ni de réglages WinUAE strictement identiques documentés. Gate B interprétée R57 PASS sur son test actif (capture utilisateur), Gate D physique non testée. R54 LAST_GOOD inchangée.

**Bilan :** l'optimisation M17 apporte désormais une accélération Fill/Clear mesurée en compilé. [Tableau complet](../benchmarks/RESULTATS_32C_R57_COMPILER_2026-11-12.md).

### Nouvelle mesure M17 — Copy R57 contre AMOS Screen Copy

**Benchmark Copy interprété et compilé PASS**, mêmes quatre géométries sur 3 passages, `AGA ERR 0`, `COPY BENCH FINISHED - CLOSE RETURNED`. [Rapport brut](../benchmarks/RESULTATS_COPY_32C_R57_2026-11-12.md). En **compilé**, médianes AMOS/AGA : aligné **35/69** ticks, non aligné **131/129**, grande zone **206/206**, recouvrement **173/172**. En interprété, petit aligné **35/69** également. L'écart du petit rectangle n'est donc pas principalement lié au mode interprété. **Prochaine phase : diagnostic ciblé de `Aga Blit Copy` / `BltBitMap` / `WaitBlit` et des chemins AMOS alignés**, avant décision de code ; aucune preuve d'une cause unique, ni changement R57 ou `LAST_GOOD`.


---

## R56 0.13.1 — remplacement Fill/Clear par graphics.library RastPort

**Version de travail :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) **33 560 octets**, SHA256 `df0bf2400eb9dc87e69e94f4472c05c8a7d57b496ef792a11125f7419d75ffef`, 53 commandes / 60 entrées AP20, monolithe 31 360 octets. **Un seul test AMOS :** [`tests/current/M17_R56_RAST_FILL_01.asc`](../tests/current/M17_R56_RAST_FILL_01.asc). `main` uniquement ; aucune autre copie R56. `LAST_GOOD` figé R54 inchangé.

**Motif :** le [benchmark compilé R55](../benchmarks/RESULTATS_32C_R55_COMPILER_2026-11-12.md) a mesuré Fill **54/54/54** ticks et Clear **115/116/115** ticks (R46 C1 54 et 117 ticks médians) ; la réduction des appels à `BltBitMap` n'a pas produit d'accélération mesurable robuste.

**Nouveau chemin 68000 :** conserve les gardes pré-DMA R55 (screen, BitMap, dimensions et profondeur 1–8, pointeurs de tous les plans, pen, `Safe` non bloquant), puis utilise un **RastPort temporaire de 128 octets sur la pile** (`InitRastPort`, `rp.BitMap` = bitmap du back buffer). Les appels AmigaOS sont `SetRast(rp,pen)` **uniquement** si X=Y=0, W = `BitMap.BytesPerRow*8`, H = `BitMap.Rows` ; sinon `SetAPen`, `SetDrMd(JAM1)`, `RectFill(rp,x,y,x+w-1,y+h-1)`. `WaitBlit` est systématique avant libération du RastPort. Les appels utilisent les LVO officiels **−198, −234, −306, −342, −354, −228** et les registres documentés. Aucun nouveau token. `Clear` reste le wrapper original de Fill, y compris `BSR.W`.

**Limite de contrat :** `SetRast` et `RectFill` retournent **void**, contrairement au compte de plans de `BltBitMap`. Le `1/0` public confirme ici validation et lancement synchronisé via `WaitBlit`, **pas une détection possible des échecs matériels internes partiels**. Équivalence des pixels et synchronisation soumises à la Gate B. Le helper natif R55 est encore présent mais l'entrée Fill pointe sur R56. Aucun gain de performance revendiqué avant mesure réelle.

**Validation :** [GitHub Actions 43282947214 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43282947214) : **171 scénarios** dans un émulateur CPU 68000 avec appels graphiques simulés (pen/couleurs mixtes, dimensions physiques exactes ou élargies, sous-rectangles, Copy inchangée, ABI/pile A3, Safe/Disp, double buffer, frontières et pointeurs invalides). **Gates B interprété WinUAE / C nouvel exécutable Compiler WinUAE / D Amiga physique : NON TESTÉES R56.** Rejouer le seul test actif, puis le benchmark V2 inchangé.

---

## R55 — Emplacements uniques imposés par l'auteur (12/11/2026)

**Branche : `main` uniquement. Version courante : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) R55 v0.13.0**, 32 988 octets, SHA256 `97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad`, 53 commandes / 60 entrées AP20, monolithe 30 780 octets. **Test actif unique : [`tests/current/M17_R55_BLIT_GROUP_01.asc`](../tests/current/M17_R55_BLIT_GROUP_01.asc)** ; aucun binaire R55 dans `dist/experimental/` et aucun workflow qui y dépose une copie. Les autres ressources historiques sont inchangées.

**R54 reste le `LAST_GOOD` figé**, SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, Gates A/B/C validées selon leurs scénarios. **R55 Gates A CPU/CI, B WinUAE interprété et C WinUAE compilé PASS sur le test utilisateur ; D matériel NON TESTÉE.** Gate B documentée par capture (`DONE 40`, `C 14 F 13 P 13`, `SAFEERR 0`, `SWAPERR 0`, `DRAWERR 0`, `CLOSED -1`, `RESULT 1`, `CLOSE RETURNED`) ; Gate C confirmée explicitement par l'auteur, **sans capture**. Après ces validations, le seul test courant a reçu un `Wait Key` final pour pouvoir photographier l'affichage en compilé ; cet ajout n'a pas été testé indépendamment et ne modifie pas la bibliothèque. Essayer le seul ASC courant avec `examples/demo.iff`, puis le benchmark `benchmarks/graphics_32c_v2.asc` inchangé ; recompiler à nouveau pour Gate C. Pas de promotion sans accord de l'auteur.

## R55 — Implémentation Fill/Clear, preuves CPU/CI (12/11/2026)

**Statut post-diagnostic : implémentation ciblée effectuée sur `main`, Gate A CPU/CI PASS ; Gates B (AMOS interprété/WinUAE), C (nouvel exécutable Compiler/WinUAE) et D (Amiga physique) NON TESTÉES.** [GitHub Actions Gate A R55 — PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43276651112) sur le commit `f27a776934cd5e92762fee892cc02504b45d5a89`. Le builder reproduit **en mémoire** le binaire courant dans `dist/AMOSPro_AGA.Lib` ; **R54 reste `LAST_GOOD`** sans modification. Cette section complète le diagnostic historique conservé plus bas.

**Fichiers ajoutés :** [émetteur 68000 groupé](../tools/m17_blit_group_r55_emit.py), [builder Compiler-safe en mémoire](../tools/build_m17_blit_group_r55.py), [suite de tests CPU](../tools/test_m17_blit_group_r55.py). La CI quotidienne [Artifact integrity](../.github/workflows/artifact-integrity.yml) intègre `python -B tools/test_m17_blit_group_r55.py` puis `python -B tools/build_m17_blit_group_r55.py`.

### Contrat de l'optimisation

- **Aucune nouvelle commande/token AMOS, aucune signature modifiée.** La R55 conserve les 53 commandes et 60 entrées AP20 de R54. `Aga Blit Copy` est conservée octet pour octet ; `Aga Blit Clear` reste le wrapper historique de 38 octets, y compris son `BSR.W` de déplacement **−572** vers l'ancien point d'entrée Fill.
- **Relocation sans décaler le code existant :** les 4 premiers octets de l'ancienne entrée native Fill sont remplacés par un `BRA.W` vers la nouvelle routine, **ajoutée à la fin de la dernière entrée native**. Les anciennes positions natives et les 59 stubs `Rbsr` restent identiques ; l'enveloppe finale est reconstruite en mémoire avec `wrap_native_ap20()`. La limite du monolithe inférieur à 32 Kio est contrôlée.
- **Validation et sécurité identiques :** géométrie, profondeur 1–8, pointeurs de **tous** les bitplanes, indice couleur, contrôle `Safe` sans attente bloquante ni écriture si refus. Le helper 68000 conserve les conventions AMOS `A3`/`D2`/`D3`, l'équilibre de pile et les registres non volatils, contrôlés par Unicorn.
- **Blits groupés :** `FullMask=(1<<Depth)-1`, `SetMask=Pen&FullMask`, `ClearMask=FullMask^SetMask`. Appeler `BltBitMap` avec minterm `$00` pour `ClearMask` non nul, puis minterm `$F0` pour `SetMask` non nul. Résultat **un ou deux appels** et autant de `WaitBlit` ; précédemment un appel/attente **par bitplane**. Source et destination restent le même back `BitMap` validé.
- **Retour strict :** le helper calcule le nombre de bits à 1 du masque et exige que le compte de plans renvoyé par `BltBitMap` soit **exactement égal** ; une opération partielle ou nulle retourne 0 après `WaitBlit`. Le code ne déclare pas une atomicité du dessin après un échec partiel.

### Preuves et limites des tests

La nouvelle suite Gate A inspecte l'identité R54, la reproductibilité du builder, les tokens, stubs et offsets, le branchement de Fill, le `BSR.W` de Clear, la taille et les instructions 68000, puis exécute les **octets natifs produits** sous Unicorn avec simulations strictes de `BltBitMap`, `WaitBlit` et `GetMsg(SafePort)`. Les 510 combinaisons (1–8 plans, toutes les couleurs) sont vérifiées par modèle de masques ; des cas échantillonnés contrôlent les pixels et la mémoire après émission CPU, les deux buffers, les erreurs, les retours partiels et la préservation de l'ABI. `Aga Blit Copy` est rejouée comme non-régression.

**Ne pas confondre :** la CI ne mesure ni l'accélération, ni la compatibilité visuelle WinUAE, ni un exécutable AMOS Compiler R55. Les **Gates B/C testeront le binaire courant `dist/AMOSPro_AGA.Lib` et l'ASC unique dans `tests/current/`**, puis un programme nouvellement compilé (ne pas réutiliser l'ancien exécutable). Rejouer sans modification le benchmark [`graphics_32c_v2.asc`](../benchmarks/graphics_32c_v2.asc) en interprété et compilé, trois passages, mêmes paramètres WinUAE et contrôle visuel. **Aucune promotion de R55 avant résultat et accord utilisateur.**

---

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
