# S0 — Sonde du ViewPort AGA, sans nouvelle bibliothèque

**Préparée pour M19 P2d — WinUAE Runtime/Compiler non encore exécutés.** Cette sonde AMOS est un test exploratoire distinct de `tests/current/` ; elle n'ajoute aucune API `Aga Sprite`, ne réserve aucun canal DMA et ne modifie aucun registre matériel.

## Démarrage sous WinUAE

1. **Faire un snapshot WinUAE avant l'essai** : `AREG(5)`, `LEEK` et `DEEK` lisent des structures privées du moteur AMOS et d'Intuition. Un mauvais pointeur peut provoquer un Guru malgré les gardes du banc. **Ne pas utiliser sur Amiga physique avant le premier Runtime validé.**
2. Utiliser l'environnement **AMOS Professional + AGA, CPU MC68020/68EC020 ou supérieur, Kickstart 3.0+**, avec exactement la Lib **M19 P2d promue** déjà installée dans `APSystem` : `dist/AMOSPro_AGA.Lib`, **136 020 octets**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`.
3. Dans un **programme AMOS vierge**, faire **Project → Merge ASCII**, sélectionner [**M19_S0_VIEWPORT_PROBE.asc**](M19_S0_VIEWPORT_PROBE.asc). Ne pas charger l'ASC comme un programme AMOS tokenisé.
4. Exécuter d'abord **en Runtime**, relever le retour AMOS et conserver le fichier `RAM:M19_S0_VP_RUNTIME.TXT`. Ne compiler ce même ASC qu'après avoir vérifié son premier résultat.

## Opérations réalisées

Le programme ouvre un écran AGA privé 320×256/256 couleurs, lit `AREG(5)` (base de données AMOS), puis vérifie `A5+$1C8 → état P2d → Screen*/Window*` et `Window.WScreen`. Il lit les dimensions écran, `Screen.ViewPort` à **+44**, les `ViewPort.Modes` à **+32** par rapport au ViewPort, et le bit **SPRITES = $4000** à l'ouverture, après `Aga Double Buffer`, après masquage/rétablissement du pointeur, puis après `Aga Swap`.

Pour vérifier que l'écran AGA est réellement visible, il dessine deux grandes silhouettes **F et L** asymétriques, appelle `Amos To Back`, présente une seule image et attend **90 VBL**. Il ferme ensuite l'écran AGA, restaure AMOS et produit un log. **Aucune nouvelle commande Sprite native, aucun appel `GetSprite`, aucune allocation DMA.**

| Exécution | Journal |
| --- | --- |
| Runtime (`PRG_STATE 1`) | `RAM:M19_S0_VP_RUNTIME.TXT` |
| Vrai AMOS Compiler (`PRG_STATE -1`) | `RAM:M19_S0_VP_COMPILED.TXT` |
| Interprété strict (`PRG_STATE 0`) | `RAM:M19_S0_VP_INTERPRETED.TXT` |

## Lecture des résultats

- `VERDICT PASS_CONTEXT_ONLY`, `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 1` : seules la lecture structurelle, la visibilité de ce banc et la fermeture ont réussi ; **ce n'est pas un PASS de moteur Sprite**.
- `MODES_OPEN/DB/CURSOR_HIDDEN/CURSOR_VISIBLE/SWAP` : mots `ViewPort.Modes` en **décimal**.
- `SPRITES_OPEN/DB/SWAP` : **0 ou 1** selon le masque `$4000`. **Ceci ne prouve pas qu'un canal est libre**. `SPRINS` et `UCOPINS` sont des pointeurs lus, non des allocations acquises par l'extension.
- `ERR 3/4/5/6/7` : l'hypothèse d'accès au contexte privé échoue. **Arrêter l'investigation directe** et transmettre le journal ou la capture WinUAE ; ne pas bricoler les offsets ni forcer `DOKE/LOKE` sur le ViewPort.
- Si `SPRITES_SWAP 0`, le drapeau n'est pas présent sur l'écran mesuré : **étudier la configuration Intuition avant toute implémentation matérielle** ; ne pas mettre `SPRITES` à 1 manuellement.

La source est accompagnée de [tests statiques dédiés](../../tools/test_m19_s0_viewport_probe_source.py) et d'une [CI de préflight](../../.github/workflows/aga-sprite-s0-viewport.yml). Ces vérifications **ne remplacent pas** une Gate B Runtime, une Gate C Compiler ou une Gate D matérielle. Les deux Lib P2d et l'unique banc P2 ALL IN ONE restent inchangés.
