# M19 S2c-P0d — changement de frame attachée (source-only)

27/11/2026, auteur « ok go ». Socle S2r actif, 154352 octets, SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a`. [Builder](../tools/build_m19_s2r_in_memory.py). [P0c PASS 420 + 114](M19_S2C_P0C_ATTACHED_LIFECYCLE_2026-11-27.md). Cible MC68020. Aucun binaire actif, ASC, ABK ou LAST_GOOD modifié.

## Contrat et provenance

- [Lifecycle P0c](../src/native/m19_s2/M19_S2C_ATTACHED_LIFECYCLE_MC68020.s), parent `bb2b9636c5c6c779b0891139ab4739c53ebf6f41`, blob `f70b59483e898d02e3ae918812b2588aa7625cb0`. [Nouvelle routine](../src/native/m19_s2/M19_S2C_ATTACHED_FRAME_MC68020.s), incluse dans ce composant ; cinq entrées précédentes inchangées en position (+0/+4/+8/+12/+16), Change à +20. Le contrôle des références accepte E0/O0 ou E1/O1, jamais une paire mixte sauf pendant deux appels OS cachés.
- [S2a historique](../src/native/m19_s2/M19_S2B_FRAME_CHANGE_MC68020.s) : deux WaitTOF, corroboration du contexte et références, préparation détachée, métadonnées après publication. [P0c/V40](M19_S2C_P0C_ATTACHED_LIFECYCLE_2026-11-27.md) : Move even propage à odd attaché, Y=257 cache les deux, ChangeSprite appelle MoveSprite.
- A0 reçu exact verrouillé, A1 Gfx, A2 allocation P0b distincte, D0 extent exact. D0=1 succès ou 0 refus ; D1=raison (8 incompatible). Le caller possède et garde épinglées les deux allocations et les structures OS ; aucune déduction de propriété par TypeOfMem. Hauteur 1..256, 4..15 couleurs, hotspot zéro, génération, compte opaque et les 48 octets de palette identiques. Refus d'alias, extent, source non Chip, pointeur/numéro déjà publié, ID hors limites ou POS/CTL/terminateurs non nuls. Pas de FreeVec ni de mutation banque ici.
- Vérifier références exactes, table SimpleSprites, CopInit, ViewPort, ColorMap et débuts LOF/SHF stables. Deux WaitTOF avec l'ancienne paire toujours visible ; revalidation source et palette. Copier exactement 2*(8+4H) octets vers la paire inactive. Basculer ensuite par Move even caché Y257, Change even et odd cachés, contrôle des deux références et neutralité, ATTACH odd, Move even à la position originale. Confirmer les nouvelles références et coordonnées, puis commit ID et état31.
- Un refus de scratch avant publication laisse état31, l'ancienne image et les données actives intactes. Référence incertaine ou échec de publication laisse état15 ; pas de Move/Change ultérieur, Retire ou quarantaine selon reçus. Ne jamais libérer l'allocation visible sur un simple échec. Aucun pointeur scratch conservé après retour.
- Deux WaitTOF par Change => plafond théorique d'environ 25 changements/s à 50Hz pour un appel séquentiel (hors coût CPU et appels OS). Trois changements séquentiels coûtent au moins six frontières vidéo. Pas de VBL supplémentaire pendant la courte séquence cachée ; pas de garantie de commutation atomique des canaux au niveau du faisceau. Une future optimisation batch/fence nécessitera qualification distincte, aucun affaiblissement du retrait. Ce modèle n'est pas une preuve DMA réelle.

## Tests

[Banc](../tools/test_m19_s2c_attached_frame_cpu.py), [workflow](../.github/workflows/m19-s2c-attached-lifecycle-gate-a.yml). MC68020 Unicorn et vasm épinglés, services OS simulés. Alternances dans les trois paires, hauteur 1/16/255/256, 4/15 couleurs ; modèle V40 de propagation even/odd, copie exacte inactive et préservation des pixels actifs/source/voisins, contrôle ID seulement après succès, refus alias/hauteur/palette/génération/pointeurs/terminateurs, modifications du contexte pendant WaitTOF, défauts hide/Change even/odd/reveal, retrait après échec et trois paires actives. Régressions P0c et S2b inchangées. Gate A composant à relever ; pas d'intégration publique, AP20, WinUAE ou matériel physique. Suite : adapter le capture/commit 2/4 plans et le registry versionné, Close/End, construire candidate en mémoire et mesurer réserve PC16 avant autorisation de livraison.

## Gate A composant — PASS

[CI 46069964921](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46069964921), source `b9147043a6b3817784635fb1b63910ef23233f3a`, job 140744276184, log du 27/11/2026 :

```text
S2C_ATTACHED_LIFECYCLE_CPU_PASS 420 checks; modeled OS only
S2B_RETIRE_PAIR_CPU_PASS 114 cases; no real DMA or multi-record integration
S2C_ATTACHED_FRAME_CPU_PASS 330 changes; 138 additional cases; modeled OS, no DMA proof
```

Assemblage VASM MC68020, Unicorn 2.1.4, protection paire canonique avant/après et [politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46069964920). Les 330 alternances incluent 90 changements sur trois paires actives et les hauteurs 1/16/255/256 ; les 138 cas complémentaires incluent les refus et échecs injectés. La CI historique [S2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46069964938) et [Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46069964918) restaient en cours au relevé. Aucun test d'affichage réel, d'atomicité raster ou de vitesse réelle ; les deux WaitTOF par appel limitent le débit séquentiel. Le nouveau composant n'est pas encore lié dans la Lib active. S2r, LAST_GOOD, ASC et ABK identités Git inchangées. Prochain lot : raccordement capture/commit public 2/4 plans et registre versionné avec retrait Close/End ; budget AP20 et qualification intégrée avant livraison.
