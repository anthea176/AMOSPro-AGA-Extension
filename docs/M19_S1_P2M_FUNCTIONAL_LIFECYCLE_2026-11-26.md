# M19 S1-P2m — cycle de vie fonctionnel (26/11/2026)

## Déclenchement

Auteur : GO après le constat d'échec fonctionnel de P2l-c. Aucune promotion ni remplacement de la Lib active à ce stade. Les trois journaux Runtime originaux de P2l-c sont conservés tels quels dans `docs/evidence/`.

| Journal | RESULT / ERR | SPRITE_RC | Diagnostic close/front |
|---|---|---:|---|
| [Phase 1](evidence/M19_P2LC_P1_RUNTIME.TXT) | 1 / 0 | 1 | -267 / -264 |
| [Phase 2](evidence/M19_P2LC_P2_RUNTIME.TXT) | 1 / 0 | -123 | -267 / -264 |
| [Phase 1 relancée sans reset](evidence/M19_P2LC_P1_RUNTIME_3xSansRestart.txt) | 0 / 10 | -123 | non exécuté |

SHA256 journaux : phase 1 `1743f43e47b6ccfc2eb6bbfd62fc92c61a97c062cbdd2b6fc63dbecd7581dba0` ; phase 2 `1b331a25932bb759644809bbb2b5d32f1f52094c7bd1f8e3f4b23a5a102fd868` ; relance `81315ac2f8ecb51d07ee1fcd883406bd3e1bf34f1401cd130dcce474badb0a0c`. PRG_STATE=1, CPU_ATTNFLAGS=32823. Les deux PASS sont limités au scénario de quarantaine ; le dernier FAIL est le verdict fonctionnel. DIAG_START=-264 à la relance. Chip/Fast de la phase 1 : -200/-168 octets ; aucun bilan de fuite établi sur plusieurs lancements. C/D P2l-c non testées. CI post-activation P2l-c : 36 succès, 1 skipped.

## Fondement technique

Références AmigaOS V39/V40 : [FreeSprite et GetSprite, source historique](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/a/simplesprites.asm#L850) (blob 9795ab23dfb810f04511002fc05d20df48203027, révisions 39.x), [MrgCop](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/c/copper.c), [LoadView](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/c/loadview.c), [WaitTOF](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/a/waittof.asm), [layout Copper](https://github.com/Arquivotheca/amiga-os-src/blob/3.1/os-source/v40_src/kickstart/graphics/copper.i). Lecture seulement. Aucun code OS importé dans la Lib.

GetSprite réserve le canal et renseigne ss_num ; ChangeSprite/MoveSprite publient le descripteur et les pointeurs startup. FreeSprite retire le slot SimpleSprites et remplace les pointeurs Copper du canal par sprstop système. P2l-c exigeait à tort un View global inactif et une valeur WAIT particulière. L'existence d'un View et les 12 octets wait_forever ne constituent pas un critère de durée de vie d'une allocation Sprite privée.

S1-P2m utilise la libération OS des seuls canaux 2/3 acquis, vérifie la neutralité des slots et MOVE startup avant puis après deux WaitTOF, avec stabilité des bases, contrôles d'adresses et version V39/V40. Ce protocole est conditionné à l'exclusivité S1, sans publication externe de pointeurs ni Copper utilisateur. TypeOfMem ne constitue pas une preuve générale de taille d'allocation. Il n'est pas présenté comme une preuve de tout état possible du DMA matériel. Les tests réels restent obligatoires. V39 non testé en Runtime.

## Correctif source

- `M19_S1P2M_RETIRE_MC68020.s` : plus de republication du blank privé. Flags 4 = canaux rendus, confirmation pending ; 20 = retraite confirmée ; seuls 0 (privé) ou 20 permettent FreeVec. Un échec avant ChangeSprite, après GetSprite, est distinct d'une publication tentée.
- `M19_S1P2M_RECLAIM_MC68020.s` : libération sous transaction, racine vidée avant FreeVec. Close/End conservent l'attente Safe/Disp et le reçu réel Intuition CloseScreen ; le retry d'un écran fermé ne touche pas l'ancien ViewPort.
- `M19_S1P2M_PUBLIC_MC68020.s` : Off libère le record et le Chip ; un prochain Sprite repart d'une banque sélectionnée encore valide. Déplacements actifs sans dépendance au payload AMOS préservés. Bank Free ne fait jamais Erase ; retour 1 si nettoyage effectué/absence. Une erreur réelle reste 0 ou négative ; aucune quarantaine comptée comme succès.
- Registre de même nom, schéma v3 incompatible avec les anciens schémas. Reset à froid unique lors du changement de Lib, pas entre cycles/relances. Pas de reprise forcée des anciennes allocations en quarantaine.
- Builder source : vérification de l'identité exacte P2l-c, overlay Close/End historique paramétré sans changer son comportement par défaut, préfixe UNIT207 conservé, tokens 105/214 identiques, seules UNIT142/207 et route Bank Free modifiables. Pas de commande de diagnostic publique supplémentaire ; -19000 retiré du chemin fonctionnel. Plafond WORD/PC16 et réserve PC16 contrôlés. Les autres unités, ABK et LAST_GOOD restent intacts.

## Critères impératifs

Gate A : assemblage VASM MC68020, intégration AP20 dans les deux modèles, 100 cycles + 10 Close/End avec un Sprite encore actif, mémoire privée sans perte, source effacée pendant Move, timeout DB, CloseScreen refusé, références persistantes et modifiées pendant le fence, allocations/receipts refusés, Bank Free et propriétaire/schéma incorrects, régressions 184 Pattern + 172 SafePort + 10 suites Bob et capture. Reconstruction identique deux fois, préflight ASC strict. Aucun résultat A revendiqué avant CI verte.

Gate B : même Lib/ASC exacts, 100 vrais affichages/déplacements/Off et 10 réouvertures et fermetures avec Sprite actif (un ASC, pas de mode quarantaine). 100 Off, 100 Move, 10 AutoClose, 10 Open, 10 Close, Bank Free=1, erreurs 0, pertes mémoire intra-écran 0, pertes cumulées après le premier Close 0. Mesures avant logs, chaque écran enregistré. Au moins trois lancements successifs sans redémarrage, conserver les trois logs avant écrasement ; comparer aussi Chip/Fast avant/après et entre lancements (le premier Close sert de référence stabilisée, ce n'est pas une preuve de fuite nulle au tout premier passage). Vérification visuelle de l'affichage et de sa disparition. Gate C : vrai Compiler seulement après B fonctionnelle ; D distincte.

État : sources en qualification, ni Lib ni ASC installés pour P2m, résultats A/B/C/D non acquis. Ne plus demander de relance du test P2l-c.
