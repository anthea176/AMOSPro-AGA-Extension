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

## Etat de qualification source-only

- Commit 7ecae4d puis d1a4a9c : [oracle négatif P1h PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45491590241), cinq défauts reproduits dans les deux modèles AP20. Vraie fixture IFF, comparaison indépendante et registres volatils.
- Commit 31f3e5d : six nouveaux modules natifs P1i. [Gate contrat P1i PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492009978), 38 scénarios. [CPU/delivery PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492010167). Ni Runtime réel, ni Compiler réel, ni DMA validés.
- Commit 4957095 : constructeur complet P1i en mémoire, intégration native L2b Double Buffer/IFF Load/Swap (écran et appels OS simulés), 184 Pattern, 172 writers, 10 suites Bob exigés. [Gate complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492646401) lancée, résultat complet non acquis à la rédaction. Seule unité 207 peut changer, les 207 précédentes et les tokens sont verrouillés.
- CI historiques : gardes d'identité R82/R84, R87/R88, AP20, CBlock adaptées aux identités exactes ; requalification générale non acquise. Les gardes ne sont pas supprimées ; les archives et les binaires ne sont pas modifiés.

**Décision : P1i non livrée dans dist.** P1h rejetée reste le fichier de travail ; ne pas la relancer. LAST_GOOD L2b inchangée. Aucune modification ASC/IFF. Bloquer la livraison jusqu'à la Gate complète PASS et la résolution des CI encore en échec. L'intégration n'est pas un essai WinUAE ni une preuve de matériel Sprite.

## Livraison de la candidate corrigée

S1-P1i livrée, 142968 octets, SHA256 `2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3`, blob `c7e13993bc32e17cb96c8e8ee68e8b5a1dffeb1b`, 102 commandes / 208 AP20, MC68020+. [Gate A complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/45492646401) : 38 scénarios Sprite, chaîne native L2b Double Buffer/IFF/Swap/capture dans deux modèles AP20, 184 Pattern, 172 writers, 10 suites Bob. Seule unité 207 changée par rapport à P1h ; tokens et 207 premières unités byte-exacts. B/C/D P1i non testées ; LAST_GOOD L2b intacte.

Source qualifiée : commit 4957095, modules P1i du commit 31f3e5d. Résultat complet confirmé dans le job 138794718442 (21:39:46 UTC le 24/11/2026). Octets natifs 6126, SHA256 `8b4b9b2c664d152fea4d516c936877e87e133bc79cfb6dbdea8bc9953ba3a245`. Reconstruction indépendante du conteneur à partir de l'ancêtre P1h authentifié et du delta source VASM CI : SHA256 et blob Git identiques aux résultats Gate A. Autorisation auteur « continue jusqu a me fournir la lib corrigé... ». La décision de blocage source-only ci-dessus est levée pour cette identité exacte ; requalification historique globale non déclarée PASS. Le test reste strictement Runtime AGSP, aucun changement des ASC ni IFF, aucune promotion de LAST_GOOD.
