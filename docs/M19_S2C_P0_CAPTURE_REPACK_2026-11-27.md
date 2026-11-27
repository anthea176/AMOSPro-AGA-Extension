# M19 S2c-P0 — capture et repack AGSP 2/4 plans (source-only)

27/11/2026. Auteur « ok go » après S2r fonctionnelle et correction CI ; démarrage composant isolé. Aucun changement de binaire actif ni intégration publique avant Gate A complète et autorisation de livraison.

## Socle et autorité
- S2r-P1 : 154352 octets, SHA256 `7e1dbfc26f9ae455b7cd8eca01a272c1ea1c7b83ad5a0739f631fd766959553a`, [builder](../tools/build_m19_s2r_in_memory.py), [B/C fonctionnelles](M19_S2R_RUNTIME_COMPILER_2026-11-27.md). Runtime : 128 octets Fast transitoires récupérés ; D non testée. CI corrective [5c20ee6](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/5c20ee6fca24b5248a7510c29d6586dfac3bfc0f) : 17 PASS, 1 skipped, 2 annulés par concurrence et 1 encore en cours lors du relevé ; contrôle canonique et documentation réparée PASS. Qualification complète à relever avant intégration S2c.
- [AGSP v1](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) demeure inchangé. Sources d'origine [capture](../src/native/m19_s1/M19_S1P1_AGSP_CAPTURE_MC68020.s) blob `0aeadf892e4e7732ccfb58a96450fb253e4c217a` et [repack](../src/native/m19_s1/M19_S1P1B_AGSP_REPACK_MC68020.s) blob `7123d710d19ee77a7acf11e7ea95de3e938cf5cb`, non modifiées. Cible MC68020 minimum.

## Contrat S2c-P0
| Couleurs RGB24 opaques distinctes | Plans AGSP | Capture largeur 16 |
| --- | --- | --- |
| 0..3 | 2 | Préserver le format S1 exact |
| 4..15 | 4 | Préparer le futur affichage attaché |
| >=16 | — | Refus avant écriture du stage |

- Transparence par indice source exact, RGB24 opaques dédupliqués, noir opaque admissible, premier ordre d'apparition, aucune quantification.
- [Capture native](../src/native/m19_s2/M19_S2C_AGSP_CAPTURE_MC68020.s) : même descriptor 64 octets et retour D0/D1 ; appelant doit désormais fournir une capacité stage de 8*H octets, source stable et spans non aliasés. Seuls 2*H*depth octets sont écrits, puis palette locale 48 octets. H 1..256. Garde de fin, ABI et refus testés.
- [Repack natif](../src/native/m19_s2/M19_S2C_AGSP_REPACK_MC68020.s) : même request 40 octets, profondeur dérivée du nombre de couleurs ; taille 2*H*depth et offsets recalculés, conservation des images anciennes et de leur format, ID triés et génération incrémentée. Même validateur complet existant accepte déjà 2 et 4 plans. Pas de mutation banque AMOS ni de retour public nouveau.
- [Banc](../tools/test_m19_s2c_capture_repack_cpu.py) : oracle AGSP host indépendant, 0..15 couleurs, seuil 3/4, noir/duplication RGB, capture non alignée, transparence non nulle, hauteur max, transitions 2/4, insertion/remplacement, capacité insuffisante, refus 16 couleurs, gardes et registres. [Workflow](../.github/workflows/m19-s2c-capture-repack-gate-a.yml) : assemblage vasm MC68020 et Unicorn épinglé, régressions S1 historiques sans modification. État initial : code déposé, Gate A composant à relever.
- Pas encore de Get AGA Sprite public 4 plans : adapter les allocations, bridge/capture/commit et requalifier les transactions. Pas de changement de l'API installée.
- Étape suivante : préparer les deux flux Chip de 16px (plans 0/1 et 2/3), qualifier le bit ATTACH du canal impair et les appels OS/attachement réels, le partage de tranche de palette AGA, curseur et bitplanes. Ne pas promettre trois palettes 15 couleurs indépendantes ; les canaux pairs/impairs partagent des sélections BPLCON4. Conserver le contrat de palette exact sans écriture arbitraire, refuser les conflits avant publication. Revoir registry/Change/Move/Off/Close/End et deux reçus de retrait, sans libérer la Chip encore référencée. Réserve PC16 S2r supplémentaire seulement 2594 octets avant réserve de 16384 ; nouvel îlot à étudier avant intégration. S2d 32/64 hors périmètre.

S2r et LAST_GOOD, ASC, ABK et toutes archives restent inchangés. Aucun résultat DMA, Runtime ou Compiler S2c revendiqué.
