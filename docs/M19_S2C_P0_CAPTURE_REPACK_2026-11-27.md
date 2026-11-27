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

## Gate A P0 — PASS

[CI 46062228480](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062228480), source `9f191412457310a7e276541072bf732278023e84` : les 6 groupes de tests S2c-P0 (avec sous-cas) passent ; 27 tests codec AGSP, 8 capture S1, 8 repack S1, 10 validateur natif, 9 politique CPU et 17 chemins de livraison PASS. [CPU/chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062228360) et [documentation](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062228229) PASS. Vérification paire canonique avant/après PASS. Pas de qualification d'affichage ni d'intégration publique.

## P0b — allocation Chip détachée pour deux canaux (source-only)

[Source](../src/native/m19_s2/M19_S2C_AGSP_CHIP_PAIR_MC68020.s) dérivée de [P2a](../src/native/m19_s1/M19_S1P2A_CHIP_PREPARE_MC68020.s) blob `fbf6a8e5d1568f2643940a471b30c7451185171d` ; [tests MC68020](../tools/test_m19_s2c_chip_pair_cpu.py), même workflow étendu. Deux SimpleSprite indépendants initialisés sans pointeur ni reçu OS, un bloc Chip privé de 96+4*(8+4*H) octets (144..4224). Flux E0/O0 : plans 0/1 et 2/3, WORD big-endian par ligne ; E1/O1 vierges pour futur staging. Toutes palettes et métadonnées copiées, aucune référence à la banque d'origine. Le format 2 plans conserve son chemin P2a historique. Allocation refusée pour largeur différente de 16, profondeur différente de 4, moins de 4 couleurs, image absente/malformée ou Chip non attestée ; FreeVec uniquement détaché sur échec. Tests sur toutes les couleurs 4..15 et hauteurs 1/16/255/256, reconstruction indépendante pixel par pixel, banques mixtes, guards, ABI et refus. **Gate A P0b à relever.**

Les [Autodocs ChangeSprite](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node0427.html) décrivent la hauteur SimpleSprite et la pose de SPRITE_ATTACHED sur posctl[1] impair après GetSprite/ChangeSprite. Contrôle et terminaison sont initialisés à zéro ici : pas de bit ATTACH préprogrammé, pas de preuve de publication ou retrait DMA. [Rappel AGA/OSPRM](https://arisamiga.github.io/amiga-bootcamp/01_hardware/aga_a1200_a4000/aga_sprites/) : les paires attachées partagent la tranche odd. Maintenir initialement la politique S2b base 16/16 et exiger compatibilité RGB24 de la palette déjà chargée (aucune écriture palette) ; à confirmer avec le code V39/40 et WinUAE. Le choix final des banques de palette/gestion de conflits et la publication de deux flux restent à qualifier. Garder 0/1 réservés et les 2/3, 4/5, 6/7 existants. Cette proposition ne promet pas trois palettes 15 couleurs indépendantes.

CI S2r : dernier contrôle Artifact integrity sur 5c20ee6 annulé par concurrence, nouveau run [46062228271](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062228271) en cours ; aucun nouveau changement du binaire, ne pas déclarer le PASS global définitif avant relevé.

## Gate A P0b — PASS

[CI 46062479398](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062479398), source `bfb55a2644d8026ead1650c3c49d6f1e569a6f33`, job 140719802788 : `S2C_DETACHED_CHIP_PAIR_PASS 74 4d1f3c49290d80682436133f582e9324f798426fe26bec859bcb2b721d478612`. Les 74 cas natifs (préparation, refus, allocation/rollback, ABI, source préservée, oracle des pixels) passent, ainsi que les 6 groupes S2c-P0 et les 53 tests S1. [Politique CPU/chemins PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062479373). Module source-only assemblé en CI, non lié dans une Lib. Le test ne publie aucun DMA et ne valide pas l'affichage attaché. Paire canonique S2r intacte avant/après.

Au dernier relevé : 17 workflows correctifs S2r PASS, 1 skipped, 3 annulés par concurrence (dont Artifact integrity relancé sur les sources suivantes) ; relevé du commit preuves b99c1b1 : 22 PASS, 1 en cours, seul échec documentaire corrigé et PASS sur f8044df. [Artifact integrity courant](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062479876) et [régression Sprite S2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46062479380) encore en cours. Pas de clôture CI globale revendiquée.

Prochain lot : publication OS des deux flux attachés et contrôle de la palette odd, puis intégration de la capture 2/4 plans dans le chemin transactionnel public. L'intégration devra prendre en compte le budget PC16, les deux descripteurs et les reçus de retrait. Ne pas activer une nouvelle Lib avant qualification intégrée et autorisation de bascule. S2r, LAST_GOOD, ASC, ABK et archives inchangés.
