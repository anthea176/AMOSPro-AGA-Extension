# AMOS Compiler — pont V2 32 Ko → ~64 Ko (phase expérimentale)

**12 novembre 2026 — candidate R58 v0.13.3 de validation du Compiler V2 sur `main`.** Unique [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **42 264 octets**, SHA256 `c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b`, **53 commandes, 62 entrées AP20** et bloc monolithique de **40 038 octets**. `Aga Probe` atteint désormais l'offset natif **40 000**. La `LAST_GOOD` protégée est **R57** (SHA256 `aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0`), promue indépendamment par l'auteur. **Gate A CPU/CI PASS ; capture WinUAE R58 conforme reçue le 12/11/2026, mode interprété/compilé à préciser pour qualifier séparément les Gates B/C ; Gate D physique NON TESTÉE.**

## Pourquoi le plafond actuel est de 32 Ko

Le [pont historique C1](../tools/compiler_relocation.py) emploie un dispatcher de **32 octets** contenant `ADDA.W D0,A0` : l'offset de chaque stub `Rbsr` est donc **signé** en 68000. Le builder refuse `len(code)+32 >= 32768`. En R57, le segment final mesure **30 780 octets** dont 30 748 de code et 32 de dispatcher.

Les [sources AMOS Professional 365 du Compiler](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s#L1976-L1982) chargent les tailles AP20 comme nombre de **mots 16 bits**, converti par `LSL.W #1`. À ce stade une borne conservative est **65 534 octets (32 767 mots)** ; 65 536 octets déborderait le calcul WORD. Le [linker](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BAPComp.s#L2020-L2093) gère les appels `Rbsr` et certains sauts trop longs via relais absolus.

## Prototype V2 — indépendant de la production

- [Émetteur V2 expérimental](../tools/compiler_bridge_v2_probe.py) : dispatcher **34 octets**, ajout de `MOVEQ #0,D0` avant `MOVE.W (A0)+,D0`, remplacement de `ADDA.W` par `ADDA.L`. Base PC après `LEA 14(PC),A0` recalculée : 20 + 14 = 34.
- [Test du pont](../tools/test_compiler_bridge_v2_probe.py) : AP20 synthétique pour offsets **0, 30 000, 32 766, 32 768, 40 000, 65 496** ; limite **65 534** ; refus **65 536**, double enveloppe C1/V2 et offsets impairs. Vérifie aussi tous les **59 segments natifs et stubs exacts de R57** en mémoire avec SHA R57/R54 et fabrique une cible fictive à l'offset **40 000** sans publier le binaire.
- **CPU réel 68000 simulé dans Unicorn en CI** : exécute le dispatcher V2 avec appels pseudo-`Rbsr` résolus en **BSR.W** et **JSR absolu**, puis vérifie D0/A0/D2, la pile et le retour depuis la cible. Exécute le code 68000, pas une simple arithmétique Python.
- L'ancien pont [C1](../tools/compiler_relocation.py) reste inchangé et reproductible pour les versions précédentes. Le [builder R58 V2](../tools/build_m17_r58_compiler_bridge.py) est séparé ; l'exporteur natif refuse toute V2 non conforme au SHA et au builder exact. **R58 est une candidate de test, pas une release validée.**

**Gate A ciblée V2 — CPU 68000 + AP20 PASS sur CI** : [Artifact integrity, run 43299842904](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43299842904), job `verify` et étape `Experimental Compiler V2 68000 bridge Gate A (in-memory only)` **success**. Logs : `STATIC PASS: V2 AP20 offsets [0, 30000, 32766, 32768, 40000, 65496] MAX 65534 R57 REPACK PASS` et `M68000 CPU PASS: 14 68k ABI/stack/call tests, real R57 preserved, no generated files`. La CI complète conclut **success** ; le contrôle final `Ensure no official or historical Lib was written` est PASS. **Cela ne constitue pas une Gate B ou C WinUAE**, ni une validation par le Compiler réel au-delà de 32 Ko.

## Retour utilisateur WinUAE — 12/11/2026

Capture du programme actif `M17-R58-COMPILER-BRIDGE-01` : les deux appels `Aga Probe` reviennent (`FAR AGA PROBE RETURNED` puis `FAR PROBE AFTER CLOSE RETURNED`), les opérations écran/Blitter/Swap affichent `1`, `CLOSED -1`, `RESULT 1`, `CLOSE RETURNED`, et aucun Guru n'est visible. Le résultat fonctionnel **de cette exécution affichée est PASS**. Le PC à l'offset 40 000 est établi indépendamment par le traçage CPU de Gate A ; le texte `OFFSET 40000` imprimé par l'ASC ne constitue pas à lui seul une preuve de PC sous WinUAE.

**Limite de preuve :** le même ASC imprime exactement ces lignes en interprété et depuis un exécutable Compiler. La capture ne permet donc pas, isolément, de classifier une Gate B ou Gate C. Préciser si l'utilisateur a lancé l'interprété ou un **exécutable compilé après installation de R58** ; obtenir l'autre mode si nécessaire avant de marquer A/B/C PASS. La promotion de `LAST_GOOD` exige en outre l'approbation de l'auteur et la régression complète sur le HEAD exact, conformément aux règles. **R57 `LAST_GOOD` reste inchangée.**

## Risques restant à lever avant validation de R58

1. **Compiler réel** : valider qu'une routine AP20 d'au moins **40 Ko** est effectivement chargée et relogée par AMOS Compiler sans plantage. Le code AMOS365 suggère une possibilité, pas une validation.
2. **Appels internes** : les `BSR.W`, `BRA.W` et accès PC relatifs à l'intérieur de notre monolithe peuvent encore déborder après croissance ; le dispatcher V2 ne les modifie pas.
3. **Placement** : l'incident R56 a démontré qu'un changement de placement apparemment valide peut planter en compilé ; les Gates B et C devront être indépendantes.
4. **Outillage** : faire évoluer strictement `wrap_native_ap20()`, `unwrap_native_parts()`, l'auditeur/exporteur et les tests de provenance seulement après décision explicite, sans casser la reproductibilité C1/R54/R57.

**Candidate publiée et Gate A confirmée :** [CI du binaire R58 actif — PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43302842699) ; [test CPU 68000 avec trace PC à 40 Ko](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43302242028). Les **59 segments natifs R57** sont intacts ; seul le token de l'instruction diagnostique existante `Aga Probe` est redirigé. [ASC actif unique](../tests/current/M17_R58_COMPILER_BRIDGE_01.asc). **Pour les Gates B/C :** installer R58 dans `APSystem`, redémarrer AMOS et Compiler, lancer le test interprété, puis **compiler un nouvel exécutable à partir du même ASC**. Attendu : `FAR AGA PROBE RETURNED`, `FAR PROBE AFTER CLOSE RETURNED`, `RESULT 1`, `CLOSE RETURNED`, sans Guru. **R57 `LAST_GOOD` reste protégée.**
