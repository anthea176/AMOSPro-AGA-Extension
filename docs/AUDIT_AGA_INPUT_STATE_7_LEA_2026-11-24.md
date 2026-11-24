# Audit P2d — passage 15 : sept LEA clavier/souris et saturation de la file

**24 novembre 2026 — main uniquement — source examinée `acbcb8fdacff7207071f34e221184204309ec5b0`.** P2d LAST_GOOD 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` (identité documentée, non recalculée ici). S1-P1e gelée. Analyse statique uniquement ; aucun essai ni correctif.

## 1. Fermeture de la vérification statique des sept sites historiques

[Incident R76](C2P_R76_RPG_REGRESSION_2026-11-14.md) : R74/R75 avaient déplacé le bloc input de 138 octets en conservant les anciens LEA, avec écrasement de code. Le passage 12 ne contrôlait que les fonctions Pressed/Released ; le présent passage compte chaque opérande source.

| Site historique | Source UNIT142 liée | Occurrences | Déplacement |
|---|---|---:|---|
| Open +$02E2 | [LEGACY_OPEN_HELPERS L117](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_LEGACY_OPEN_HELPERS_MC68020.s#L115-L122) | 1 | 12070 |
| Pressed +$0038 / +$0048 | [BLOCK_02D90 L23/L28](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_BLOCK_02D90_MC68020.s#L18-L34) | 2 | 12070 |
| Released +$0038 / +$0048 | [BLOCK_02DFA L23/L28](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_BLOCK_02DFA_MC68020.s#L18-L34) | 2 | 12070 |
| Traitement input +$003E / +$022C | [ENTRY_02E64 L27/L180](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_ENTRY_02E64_MC68020.s) | 2 | 12070 |

**Total 7/7 sites**, aucun 11932 ($2E9C) à ces emplacements. L'[INIT](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_INIT_ENTRY_MC68020.s) charge State = L_UNIT142_001C2 ; [master UNIT142](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P2D_UNIT142_EDITABLE.s#L22-L24) déclare 40 octets à cet endroit. Calcul : $001C2+$02F26=$030E8. Le corps ENTRY_02E64 annonce $02E64..$030E8 ; [master L123-L137](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P2D_UNIT142_EDITABLE.s#L123-L137) place immédiatement après lui **12 lignes de 12 octets nuls, soit 144 octets**, puis GetP. Open exécute DBRA avec D0=35, soit 36 CLR.L = 144 octets. Concordance exacte des adresses source et de la taille ; pas de destruction de code démontrée sur ces sites P2d.

**Limite :** lecture des sources liées, pas reconstruction/recalcul SHA ni exécution du test de mutants. [test_current_input_state_offsets.py](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/tools/test_current_input_state_offsets.py) vérifie également les opcodes et huit mutants sur l'ancêtre R82 et le préfixe R84. La branche P2d exige active == frozen ; la candidate S1-P1e n'est pas qualifiée par cette lecture. AGA-005 (compatibilité CI / identité) reste ouverte. Ne pas modifier les exigences SHA pour obtenir une CI verte.

## 2. File clavier/souris partagée : borne locale et risque de latence

Dans [ENTRY_02E64 L48-L59](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_ENTRY_02E64_MC68020.s#L48-L59), D7=63 borne le drain à 64 messages par appel ; avant chaque GetMsg le compteur de la file clavier (+24) est comparé à 16. A saturation, la routine retourne **sans lire le prochain message IDCMP**, quel que soit son type. La file de 16 RAWKEY est stockée à +80..+143, indices masqués à 15, et la voie de dépilage à partir de L_UNIT142_0307E réduit +24.

Les fonctions Mouse Pressed/Released appellent ce pump mais ne dépilent pas la file clavier. Conséquence statique conditionnelle : si la file reste pleine et que le programme ne la dépile pas via le chemin clavier, de nouveaux événements souris/focus en attente sur le port ne seront pas traités par ce pump. Ce n'est pas un blocage CPU : la routine retourne. Le choix de ne pas perdre de touches peut être intentionnel ; **latence/starvation à qualifier**, pas nouvelle anomalie Runtime confirmée. Distinguer Mouse Buttons (lecture directe) et fronts Pressed/Released (événements).

## 3. Critères complémentaires T14

- Gate A : sept opérandes + limite du bloc, canaries de code adjacents, 8 mutations historiques ; effectuer la vérification sur le futur binaire exact.
- Saturation clavier : 0/15/16 entrées, souris et focus derrière un RAWKEY, présence puis consommation d'une touche ; contrôler état des fronts, compteur et ReplyMsg.
- Fermer/reouvrir avec file pleine ; examiner remise à zéro Open, owner Window et file IDCMP ; conserver la preuve de l'ordre et de la terminaison.
- B/C : reproduire une scène menu/RPG avec clavier + souris, pas uniquement un test graphique.

**Résultat : 7/7 LEA concordants statiquement ; file partagée à qualifier.** Aucun nouveau test, aucune correction ; Sprite gelé. Audit ouvert, 19 scénarios inchangés.
