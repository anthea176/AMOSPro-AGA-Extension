# Intégrité des bibliothèques `AMOSPro_AGA.Lib`

Un incident historique a montré qu'un binaire pouvait être publié tronqué tout en conservant un en-tête HUNK annonçant sa taille initiale. Pour chaque candidat, les vérifications préliminaires portent sur :

1. Structure HUNK/AP20 complète, table de tokens et entrées, tailles et offsets cohérents.
2. SHA256 de l'archive de base et du candidat ; reproduction identique du binaire depuis le builder.
3. Comparaison byte-for-byte des segments précédemment validés sauf delta explicitement autorisé.
4. Tests CPU/ABI, conservation des registres et pile de paramètres AMOS, contrôles de bornes, synchronisation et chemins d'échec.
5. Exécution de la CI GitHub `.github/workflows/artifact-integrity.yml` correspondant au HEAD réellement testé.

**La Gate A ne prouve ni le fonctionnement sous WinUAE ni sur Amiga physique.** Les Gates B (AMOS interprété), C (Compiler) et D (matériel) sont documentées séparément dans le STATUS du jalon. Aucun succès d'un simple modèle Python ne certifie un binaire R16.

**Situation M7 :** les scripts `tools/m7_copper_contract.py` et `tools/test_m7_copper_contract.py` contrôlent la future grammaire Copper et des interdictions de registres. **Ils ne génèrent pas de `.Lib`** et n'installent aucune `UCopList`. Voir [M7_STATUS](M7_STATUS.md).

Les **archives versionnées restent figées**. `LAST_GOOD` correspond **obligatoirement à la dernière `.Lib` validée en AMOS/WinUAE (Gate B confirmé par l'utilisateur)** et doit être promu dans le même commit que la clôture du test. Une simple Gate A CPU/CI n'autorise pas la promotion. La candidate distribuable est toujours **`dist/AMOSPro_AGA.Lib` directement dans `dist/`**, sans sous-dossier ni renommage, et **R28 est candidate tandis que R27 est `LAST_GOOD`**. Se reporter aux [règles source](../EXTENSION_SOURCE_RULES.md), au [build](BUILD.md) et à l'[état courant](NEXT_SESSION.md).
