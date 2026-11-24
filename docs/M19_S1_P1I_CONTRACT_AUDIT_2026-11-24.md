# S1-P1i — Audit des contrats natifs et requalification (24/11/2026)

Base auditée : main bb2999fe28423c030f3d2d306acdf0efec5a389f. P1h 142720 octets, SHA256 900646cc208cc99095c81c209276579a28dbcbbcbd43dd10c4e93be35d2e05eb. L2b LAST_GOOD 136708 octets, a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc. Runtime P1h : ERR 9, CAPTURED 0 ; ListBank 29 AGASPRT, 32 octets (preuve auteur). Aucune image capturée. Auteur « ok fait ca » après audit et plan de qualification. Cible MC68020+, aucun changement API, AGSP v1, ASC/IFF, autre branche, archive ou LAST_GOOD.

| ID | Contrat | Preuve / risque | Correctif |
|---|---|---|---|
| S1-001 | DB+20 bit0 = Safe pending | P1h inverse le bit ; DB neuf refusé, pending lu | Port +12, GetMsg seulement pending, effacer bit0 seul, WaitBlit ; aucun Swap |
| S1-002 | Cur_Banks = adresse de la cellule propriétaire | A5 identique entre programmes | Lier et revalider la cellule, pas seulement A5 |
| S1-003 | Echec sélection instruction | Ancien numéro conservé, risque écriture ancienne banque | Invalider sélection avant nouvelle tentative |
| S1-004 | Publication transactionnelle | Snapshot effectué trop tard ; taille/génération non revalidées | Owner, pointeur, taille, génération attendus dès capture, recheck avant publication |
| S1-005 | Mémoire | TypeOfMem après lectures, ne prouve pas une allocation | Contrôles avant accès, allocation AMOS de confiance, bornes et tailles explicites |
| S1-006 | Préférence Chip de banque | Remplacement systématique DATA publique | Conserver bit Chip et allocation correspondante |
| S1-007 | ABI services | Mocks préservent trop de registres | D0/D1/A0/A1 volatils, exécution complète des deux stubs AP20 |
| CI-001 | Reproductibilité | bb2999f : 24/27 workflows FAIL, racine commune R82 SHA obsolète | Registre de la lignée exacte, conserver preuves négatives, requalification |

Références : [AMOS365 +B.s](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BB.s#L1195-L1336), [AMOS365 +Lib.s](https://github.com/marc365/AMOS-Professional-365/blob/3e8f53196b80cbb2e01342a89a3545d080bf0de4/%2BLib.s#L7888-L7907), [L2b SafePort](../src/native/m19_p2d_l1/M19_L1_SAFEPORT_TAIL_MC68020.s), [DB/Swap](../src/native/m19_p2d/M19_UNIT142_BLOCK_00BA2_MC68020.s), [transaction Bob](../src/native/m19_p2d/M19_P1E_EDIT_BOOTSTRAP_MC68020.s).

## Qualification par étapes

1. Nouveau banc indépendant : vraie IFF versionnée, bitmap front différent du back, ABI volatils, vrais stubs AP20 BSR.W / JSR absolu, défauts P1h attendus et observables. Sources historiques figées.
2. Nouvelles sources P1i : aucune réécriture du noyau pixel/AGSP. Tester les mêmes cas positifs/négatifs.
3. Intégration des vraies routines héritées L2b ; Gate A complète de la candidate, identité source, 207 unités précédentes byte-exact, CI historiques + CPU/delivery. AMOS Runtime/Compiler distincts.
4. Livraison conditionnée aux résultats.

**Etat initial :** audit statique, registre SHA lignée Sprite centralisé pour R82. Aucun PASS P1i revendiqué. Ne pas relancer P1h. T06A, ASC Sprite et IFF inchangés. Aucun changement de dist.
