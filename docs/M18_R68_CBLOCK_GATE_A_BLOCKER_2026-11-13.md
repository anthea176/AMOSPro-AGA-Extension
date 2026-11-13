# M18/R68 — Gate A BLOQUÉE : retour de pile sur Draw

**13 novembre 2026. Diagnostic natif Unicorn M68000, non WinUAE.**

## État et limites

- Le prototype P0 de copie CPU8/CPU16/Blitter est validé séparément (modèle hôte et noyau natif standalone). **Il ne valide pas l'API AP20 R68.**
- Les trois wrappers expérimentaux `Aga C Block Capture`, `Draw` et `Restore` sont codés sur `main` dans [l'émetteur](../tools/m18_cblock_bank_emit.py) ; [le builder déterministe](../tools/build_m18_r68_cblock.py) ne génère la candidate qu'en mémoire. Aucun binaire R68 publiable dans `dist/`.
- **Gate A R68 globale = FAIL** ; **aucune Gate B WinUAE** et aucune Gate C Compiler réelle. Aucun ASC de test R68 dans `tests/current/`.
- **R67 v0.13.12** (`dist/AMOSPro_AGA.Lib`, 43 180 octets, SHA256 `ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5`) reste la seule bibliothèque candidate, Gates A/B PASS ; R63 `LAST_GOOD` protégée.

## Résultats effectivement obtenus

1. Le test [`test_m18_r68_cblock_gate_a.py`](../tools/test_m18_r68_cblock_gate_a.py) construit R68 en mémoire, exécute les wrappers en M68000, simule la disposition interpréteur et celle du Compiler V2, et intercepte les services AMOS/Exec/graphics (pas de DMA réel).
2. **La création de banque Chip et deux captures successives CPU8 passent les contrôles déjà atteints** : `Bnk.Reserve` une fois, `Bnk.Change`, en-tête `AGACBLK `, copie des pixels et recapture sans réallocation. La mémoire allouée est initialisée avec des octets non nuls par le simulateur, le wrapper nettoie le padding à la création.
3. Lors du premier `Draw(11,32,22,Method=0)`, le test quitte le code avec **A7 = `$EFFF84` au lieu de `$F00004`**, bien que PC revienne au STOP prévu. L'ABI du wrapper n'est **pas** valide.
4. La trace du code chargé indique le prologue du noyau valide (`48e7efee4fefff00`) à l'offset étiqueté `copy_core=1624`, mais le premier PC consigné dans sa plage est **`1834`** (210 octets plus loin). La trace du `JSR (A4)` émis à l'offset 1580 n'a pas été déclenchée. Cela suggère un **chemin d'exécution incorrect avant l'entrée normale du noyau** ; la cause exacte n'est pas encore établie. Ne pas attribuer l'échec avec certitude au BSR, à JSR ou à l'algorithme de copie.
5. Le run [GitHub Actions 43467195100](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43467195100) confirme le FAIL ; aucune preuve de performance CPU8/CPU16/Blitter n'a été produite.

## Consignes de reprise

- **Inspecter la transition du PC juste avant l'entrée anormale à `copy_core+210`**, en remontant au code de validation de banque propre à `Draw`, plutôt que de modifier encore la routine P0 testée.
- Vérifier le véritable saut `JSR`, les branchements sur les en-têtes, les marqueurs de relocation et l'équilibre de pile sur `Capture` puis `Draw`/ `Restore`; tester un `Draw` isolé avec une banque préchargée valide pour distinguer le chemin d'état/réutilisation.
- Valider ensuite les erreurs, les canaries et les contenus pixel/plan sur les deux dispositions native et Compiler simulée.
- L'étape R68 native reste accessible **uniquement en lancement manuel** du workflow `Artifact integrity` (condition `workflow_dispatch`). **Le push sur `main` ne déclenche plus le Gate A expérimental FAIL**, mais conserve les contrôles R67 et P0.
- **N'installer aucune candidate R68**, ne pas créer de nouvel ASC actif avant Gate A PASS ; préserver R67 et R63 LAST_GOOD, uniquement `main`, aucune PR/branche, **aucun Compiler AMOS manuel avant la fin M18**.
