# AMOS Compiler — pont V2 32 Ko → ~64 Ko (phase expérimentale)

**12 novembre 2026 — diagnostic + prototype non installable.** Travail sur **main** uniquement. **Aucun changement** à R57 `dist/AMOSPro_AGA.Lib` ni à R54 `dist/AMOSPro_AGA_LAST_GOOD.Lib`, ni à `tests/current/`. **Aucune Gate B/C WinUAE revendiquée.**

## Pourquoi le plafond actuel est de 32 Ko

Le [pont historique C1](../tools/compiler_relocation.py) emploie un dispatcher de **32 octets** contenant `ADDA.W D0,A0` : l'offset de chaque stub `Rbsr` est donc **signé** en 68000. Le builder refuse `len(code)+32 >= 32768`. En R57, le segment final mesure **30 780 octets** dont 30 748 de code et 32 de dispatcher.

Les [sources AMOS Professional 365 du Compiler](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s#L1976-L1982) chargent les tailles AP20 comme nombre de **mots 16 bits**, converti par `LSL.W #1`. À ce stade une borne conservative est **65 534 octets (32 767 mots)** ; 65 536 octets déborderait le calcul WORD. Le [linker](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s#L2020-L2093) gère les appels `Rbsr` et certains sauts trop longs via relais absolus.

## Prototype V2 — indépendant de la production

- [Émetteur V2 expérimental](../tools/compiler_bridge_v2_probe.py) : dispatcher **34 octets**, ajout de `MOVEQ #0,D0` avant `MOVE.W (A0)+,D0`, remplacement de `ADDA.W` par `ADDA.L`. Base PC après `LEA 14(PC),A0` recalculée : 20 + 14 = 34.
- [Test du pont](../tools/test_compiler_bridge_v2_probe.py) : AP20 synthétique pour offsets **0, 30 000, 32 766, 32 768, 40 000, 65 496** ; limite **65 534** ; refus **65 536**, double enveloppe C1/V2 et offsets impairs. Vérifie aussi tous les **59 segments natifs et stubs exacts de R57** en mémoire avec SHA R57/R54 et fabrique une cible fictive à l'offset **40 000** sans publier le binaire.
- **CPU réel 68000 simulé dans Unicorn en CI** : exécute le dispatcher V2 avec appels pseudo-`Rbsr` résolus en **BSR.W** et **JSR absolu**, puis vérifie D0/A0/D2, la pile et le retour depuis la cible. Exécute le code 68000, pas une simple arithmétique Python.
- Les outils de production restent sur [le dispatcher C1 historique](../tools/compiler_relocation.py), **inchangé**. En particulier `is_compiler_wrapped()` et l'exporteur ne savent **pas encore traiter V2** : **interdiction d'utiliser ce prototype pour une release ou une candidate R58.**

**Gate A ciblée V2 — CPU 68000 + AP20 PASS sur CI** : [Artifact integrity, run 43299842904](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43299842904), job `verify` et étape `Experimental Compiler V2 68000 bridge Gate A (in-memory only)` **success**. Logs : `STATIC PASS: V2 AP20 offsets [0, 30000, 32766, 32768, 40000, 65496] MAX 65534 R57 REPACK PASS` et `M68000 CPU PASS: 14 68k ABI/stack/call tests, real R57 preserved, no generated files`. La CI complète conclut **success** ; le contrôle final `Ensure no official or historical Lib was written` est PASS. **Cela ne constitue pas une Gate B ou C WinUAE**, ni une validation par le Compiler réel au-delà de 32 Ko.

## Risques restant à lever avant toute candidate

1. **Compiler réel** : valider qu'une routine AP20 d'au moins **40 Ko** est effectivement chargée et relogée par AMOS Compiler sans plantage. Le code AMOS365 suggère une possibilité, pas une validation.
2. **Appels internes** : les `BSR.W`, `BRA.W` et accès PC relatifs à l'intérieur de notre monolithe peuvent encore déborder après croissance ; le dispatcher V2 ne les modifie pas.
3. **Placement** : l'incident R56 a démontré qu'un changement de placement apparemment valide peut planter en compilé ; les Gates B et C devront être indépendantes.
4. **Outillage** : faire évoluer strictement `wrap_native_ap20()`, `unwrap_native_parts()`, l'auditeur/exporteur et les tests de provenance seulement après décision explicite, sans casser la reproductibilité C1/R54/R57.

**Étape suivante si Gate A passe :** définir avec l'auteur la candidate unique à installer dans `dist/AMOSPro_AGA.Lib` et l'unique ASC `tests/current/`, puis la tester sous AMOS interprété et **dans un nouvel exécutable compilé**. R54 `LAST_GOOD` restera intacte tant que toutes les validations nécessaires ne seront pas acquises.
