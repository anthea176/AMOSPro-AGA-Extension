# Test actif — M19 P0c / pont natif Aga Screen Close

**Bibliothèque unique de campagne :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **87 020 octets**, SHA256 `277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a`.
**Programme ASC actif unique :** [`M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc`](M19_P0C_SCREEN_CLOSE_BRIDGE_01.asc), dérivé du [design source](../design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc), sans changement dans les instructions BASIC (commentaires d'en-tête seuls adaptés).

**Cible native : MC68020 / 68EC020 minimum ; validation fonctionnelle WinUAE AGA PAL 68030/JIT ON.** MC68020/JIT OFF réservé aux benchmarks. **Gate A MC68020 PASS ; Gates B Runtime et C véritable AMOS Compiler NON TESTÉES.** Gate D physique NON TESTÉE.

## Scénario sans ressource extérieure

1. `Aga Detect` ; `Aga Screen Open(320,256,256,$00021000)`, affichage du motif, `Aga Screen Close` et `Amos To Front`.
2. Réouvrir, activer `Aga Double Buffer`, fermer **sans Swap en vol**.
3. Réouvrir et refermer après le Double Buffer.

Les trois fermetures doivent revenir à AMOS sans Guru ni gel. Aucun nettoyage Chip Bob ne peut être démontré : `program_end_arm_entry` reste une entrée **privée** non armée par une API publique.

## Gates B / C sous WinUAE

1. Synchroniser le dépôt `main` ; installer **exactement** la Lib canonique depuis `dist/AMOSPro_AGA.Lib` dans le slot d'extension AGA `APSystem` déjà utilisé. Sauvegarder l'ancienne Lib installée hors dépôt ; vérifier le SHA du fichier réellement installé et redémarrer AMOS.
2. Programme vide, **Project → Merge ASCII** avec l'ASC actif de ce dossier. Ne pas utiliser `Load` sur le texte source.
3. **Gate B Runtime :** lancer le banc et vérifier retour à AMOS. Consigner `RAM:M19_P0C_RUNTIME.TXT` et `PRG_STATE 1`.
4. **Gate C Compiler :** compiler **un nouvel exécutable** depuis le même ASC avec le vrai AMOS Compiler V2, exécuter, vérifier le retour à AMOS et conserver `RAM:M19_P0C_COMPILED.TXT` avec `PRG_STATE -1`.
5. Pour chaque mode : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `CLOSE_FIRST 1`, `CLOSE_WITH_DB 1`, `CLOSE_REOPEN 1` et ligne d'écran `LOG ... OPEN 0 CLOSE 0`, sans freeze ni Guru. Conserver captures, versions et configuration WinUAE.

**Contrôle facultatif des journaux :**
```powershell
python -B tools/check_m19_p0c_winuae_logs.py --self-test
python -B tools/check_m19_p0c_winuae_logs.py --installed-lib "CHEMIN_APSystem/AMOSPro_AGA.Lib" --runtime "M19_P0C_RUNTIME.TXT" --compiled "M19_P0C_COMPILED.TXT"
```
Le validateur de logs ne remplace **pas** les essais WinUAE. Voir le [protocole complet](../../docs/M19_P0C_GATES_BC_WINUAE_PREPARATION_2026-11-16.md).

## Protections et témoin P0b

- `dist/AMOSPro_AGA_LAST_GOOD.Lib` **R84 inchangée**, pas de promotion.
- P0b (82 376 octets, SHA256 `f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9`) : Gates A/B/C historiques PASS ; [preuve P0b](../../docs/M19_P0B_GATES_BC_2026-11-16.md), source exacte `tests/current/M19_P0B_MC68020_MASK_BANK.asc` dans le commit précédent (historique Git), **pas dans les tests actifs**.
- Le brouillon `tests/design/M19_P0C_SCREEN_CLOSE_BRIDGE_01_UNVALIDATED.asc`, les archives `tests/passed/` et `dist/experimental/` n'ont pas été modifiés.
