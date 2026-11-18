# M19 B7-m1 — cycle de vie des Bobs persistants : Gate A MC68020 (18/11/2026)

## Résultat

**Gate A native PASS** sur le binaire source-reproductible **M19 P0j-b7-m1**. [CI dédiée 44404123651](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44404123651), après correction d'une coordonnée du banc CPU020 (viewport simulé de 65 pixels, pas 320). Journal final : `M19 B7-m1 PERSISTENT BOB LIFECYCLE MC68020 GATE A PASS`, **194 contrôles fonctionnels comptabilisés sur deux implantations AP20**.

Les instructions Motorola **MC68020 réellement émises** sont exécutées sous **Unicorn**, dans les implantations indépendantes `interpreted` et `compiled` (ce second nom désigne **uniquement le placement/relocation native**, **pas une compilation AMOS**). AMOS, Exec, Intuition, graphics.library, les messages Safe/Disp et les effets DMA sont **simulés**. Aucun WinUAE/Compiler réel n'a été invoqué.

## Provenance verrouillée

- **Lib inchangée :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **102 360 octets**, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`, 86 commandes, 181 sections AP20, quatre unités natives.
- **Reproduction :** `tools/build_m19_p0j_end_lifecycle_in_memory.py::build_multiframe()` reconstruit un binaire **strictement égal en octets** à la Lib installable ; le test refuse tout décalage taille/SHA.
- **Banc ajouté :** [`tools/test_m19_b7m1_bob_lifecycle_gate_a.py`](../tools/test_m19_b7m1_bob_lifecycle_gate_a.py), source `AGA_NATIVE_MIN_CPU: MC68020`, accompagné du [workflow en lecture seule](../.github/workflows/m19-bob-lifecycle-gate-a.yml). **Aucun émetteur, builder, ASC actif, Lib, `LAST_GOOD` ou archive modifié.**

## Scénarios réellement vérifiés

| Scénario MC68020 | Vérification |
|---|---|
| **Off / On** | Deux Bobs actifs, puis `Aga Bob Off 1` : seul Bob 2 opaque émet un Blit ; `Aga Bob Off 2` : Draw réussit sans peintre actif. Réactivation des mêmes IDs depuis les banques 10 et 11 : un Blit masqué + un opaque ; validation des enregistrements source et de leurs coordonnées (y compris clipping) |
| **Progression vers 64** | IDs **1, 4, 8, 16, 64**, répartis dans les banques 10 (masquées) et 11 (opaques). Nombre d'opérations Blitter correspondant à chaque étape et ordre des masques/opacités cohérent ; sélection de banque conservée pendant Draw ; Swap réussi après chaque frame |
| **Réduction** | Après 64, `Off` sur IDs 17..64 : exactement 16 Bobs restants, sans dessin des IDs désactivés |
| **Identité de banque** | Une génération périmée pour un Bob **inactif** est ignorée. La même corruption sur la banque d'un Bob **actif** provoque `Draw=0` **avant peinture DMA**, sans modification de sélection |
| **Sécurité Swap** | Après une frame refusée, `DIRTY` interdit `Aga Swap` avant le véritable `ChangeScreenBuffer`, même après réparation de la génération sans fermeture ; pas de récupération implicite dangereuse |
| **Close/End** | Fermeture nettoyant les ressources natives, End rétablissant les callbacks d'origine ; deux ScreenBuffers et deux ports libérés au plus une fois dans le modèle |

**Limites explicites :** l'absence de Bob fantôme visible ne peut pas être attestée **sur écran** par ce test natif sans restauration visuelle réelle ; la démo et le futur test fonctionnel doivent la montrer. Le dispositif CPU simule les opérations Blitter et les services du système. Le test `compiled` ne prouve **aucune Gate C**.

## Statut et suite sans benchmark

- **Gate A B7-m1 (moteur) : PASS** — tests antérieurs B7-m1 multiframe (793 contrôles) + nouveaux scénarios cycle de vie (194 contrôles comptabilisés).
- **Gate B du nouvel ensemble Off/On/1..64 : NON TESTÉE**. Les précédentes Gates B sur quatre Bobs et décor texturé restent **PASS pour leur propre scénario**, sans validation implicite des nouveaux cas.
- **Gate C : NON TESTÉE** sur B7-m1 ; **Gate D : NON TESTÉE**.
- **Prochaine étape :** préparer **un seul ASC fonctionnel** (pas de FPS) couvrant Off → Draw/Swap, réactivation, plusieurs banques, puis fermeture/réexécution ; privilégier d'abord les 4 Bobs connus avant le scénario 64. Aucun changement de Lib nécessaire pour ce test des commandes existantes.

Aucune promotion `LAST_GOOD` ni nouvelle API. Un seul dépôt : `anthea176/AMOSPro-AGA-Extension`, branche `main`.
