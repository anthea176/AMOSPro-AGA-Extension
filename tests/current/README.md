# M19 P2e.1 — Deux canaux AMAL vers deux Bobs AGA

**Campagne active WinUAE Runtime** : [M19_P2E1_AMAL_TWO_BOBS.asc](M19_P2E1_AMAL_TWO_BOBS.asc), **8800 octets**, Git blob `edcbbdc9d863dd96f6b5ad22abe44ba0d4c37aaf`.
**Lib à installer** : [dist/AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) **P2d**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes / 203 AP20, cible MC68020 minimum.
**LAST_GOOD protégée** : P1e, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`.

## Correctif visuel P2e.1 (21/11/2026)

**ASC actif modifié :** `M19_P2E1_AMAL_TWO_BOBS.asc`, **8800 octets**, Git blob `edcbbdc9d863dd96f6b5ad22abe44ba0d4c37aaf` (ancien essai source-only : 8430 octets). Le programme appelle désormais **`Amos To Back`** après préparation des deux pages pour faire apparaître l'écran AGA **sans bascule manuelle Amiga+A** ; `Amos To Front` reste au retour. Cause matérielle non prouvée avant essai utilisateur.

Les deux images de 16×16 ne sont plus des carrés opaques : **F (index 165)** et **L (index 90)**, silhouettes asymétriques avec `Make AGA Bob Mask I,0`. Leur pixel supérieur gauche reste opaque pour conserver le contrôle automatique des pixels, sans changer l'AMAL, les six compteurs ni le nombre de Swaps. **PREFLIGHT / Runtime du nouvel ASC à requalifier** ; le précédent PASS P2e.0 ne couvre pas cette modification.

**Démo indépendante de Flip :** [`examples/aga_bob_flip/FLIP_VISUAL.asc`](../../examples/aga_bob_flip/FLIP_VISUAL.asc) : une forme **F asymétrique 32×32** affichée simultanément en modes **0 normal, 1 H, 2 V, 3 HV**. Cette démo ne remplace pas l'unique ASC actif et n'est pas encore qualifiée Runtime/Compiler.

## Résultats

- **Préflight officiel antérieur : PASS** sur l'ASC de 8 430 octets, **nouvel ASC à requalifier en CI**, sans erreur ni avertissement, avec `tools/amos_preflight.py --strict-target` (script vérifié par Git blob `9f45b4088bb95a5d604b0548ba79a85a1da6a72e`). Contrôle structurel additionnel PASS.
- **P2e.1 Gate B Runtime : NON TESTÉE**, aucun journal d'exécution; **Gate C Compiler : NON TESTÉE**, réservée à l'exemple P2 global; Gate D physique NON TESTÉE.
- **P2e.0 Gate B Runtime : PASS** sur 240 cycles, 241 Swaps, 29 pixels et fermeture propre. [Log original CRLF](../../docs/evidence/M19_P2E0_AMAL_BRIDGE_RUNTIME_2026-11-21.TXT), SHA256 `5ea95d1335fa35f3a2fe743b84febf210b2b2d10fb481ff5fa76f4d0bf13e0fc`. [ASC P2e.0 exact, au commit précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/55ca846e9a44065b0e1ba3e8c9a68041ce37746e/tests/current/M19_P2E0_AMAL_BRIDGE.asc). Aucun déplacement vers `tests/passed/`.

## Exécuter le nouveau test

1. Installer **uniquement** la Lib P2d ci-dessus dans `APSystem`, puis relancer AMOS Pro sous WinUAE AGA avec CPU au moins 68020.
2. Dans un programme vierge : **Project → Merge ASCII** sur `tests/current/M19_P2E1_AMAL_TWO_BOBS.asc`. Laisser libres les banques AMOS **24, 27 et 28**.
3. Lancer en **Runtime**. Observer deux formes asymétriques F/L animées de 16×16, un vers `X 96..128, Y 100..116`, l'autre vers `X 192..224, Y 144..160`. Leurs couleurs alternent entre index **165** et **90**, avec l'index 0 transparent.
4. Après retour propre à AMOS, récupérer **`RAM:M19_P2E1_AMAL_TWO_BOBS.TXT`** avant un nouveau lancement. Noter toute erreur de syntaxe AMOS, Guru, freeze ou différence visuelle.

## Attendu, non encore observé

```text
PRG_STATE  1
RESULT  1
ERR  0
VALID_SAMPLES  240
SWAPS  241
BG0  1
BG1  1
PIX0  >0
PIX1  >0
CHG0_X/Y/A  >0
CHG1_X/Y/A  >0
CLOSE_RETURNED  1
VERDICT PASS
```

Le programme exige **PIX0≥2, PIX1≥2**, les six compteurs `CHG*` positifs et l'observation des images 1 et 2 par les deux Bobs. Les valeurs affichées sous `FLAG0_*` et `FLAG1_*` (issues de `Peek`) restent **diagnostiques** : le mot AMAL de P2e.0 valait `$0700` en fin de test, mais la validité des bits par frame n'est pas prouvée.

En cas d'échec, `ERR 13` indique une position AMAL hors domaine, `14` un écart getters, `15` un Swap refusé, `16` une capture échouée, `17` un pixel incorrect (`PIXEL_ID/VALUE/EXPECTED`), `19–21` une couverture insuffisante, `22/23` la préparation des fonds sur les deux pages. La fermeture et le diagnostic demeurent les objectifs même lors d'un échec récupérable.

[Contrat P2e.1](../../docs/M19_P2E1_AMAL_TWO_BOBS_DESIGN_2026-11-21.md).

