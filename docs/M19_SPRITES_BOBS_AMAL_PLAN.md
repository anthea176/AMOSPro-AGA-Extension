# M19 — Sprites AGA, Bobs logiciels et AMAL : plan valide

> **Décision auteur : plan approuvé le 14/11/2026 ; démarrage de P0 autorisé.**  
> **Statut au 15/11/2026 : P0, P1 et P2.0 PASS sous WinUAE Runtime dans leurs scénarios ; benchmark [4/8/16 Bobs](../benchmarks/README_M19_P2_BOBS_4_8_16.md) **PASS sur WinUAE Runtime 68020/14 MHz/JIT OFF et 68030/JIT**. [Résultats 68020](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) : le tri Z répété et le dessin sont coûteux à 16 objets. **P2.1 : dernier A/B cache Z Runtime WinUAE 68020/noJIT PASS (composition −5,8/−15,6/−30,4 % à 4/8/16 Bobs). [Rapport final](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md).** Aucune nouvelle API native approuvée ; Gates C/D M19 non testées.**  
> Dépôt `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**. Référence de départ : **R84 v0.13.29 promue LAST_GOOD** (76 commandes, 85 entrées AP20, MC68020 minimum). Le binaire `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure protégé.

## 1. Objectif

Intégrer des objets animés à l'**écran Intuition AGA privé** de l'extension, sans présumer que les commandes graphiques natives `Sprite` et `Bob` d'AMOS peuvent dessiner sur cet écran.

**Architecture retenue :** un modèle logique d'objet commun à terme, deux moteurs de rendu distincts (**Bob logiciel** et **sprite matériel AGA**) et **AMAL comme source facultative de mouvement/image**. Le rendu appartient exclusivement à la boucle principale.

**Règle impérative : aucun dessin, allocation, libération ou accès au back buffer AGA depuis une interruption.** `SYNCHRO OFF` précède la déclaration AMAL et les animations sont avancées manuellement par `SYNCHRO`. Aucune API publique n'est définie avant les prototypes et leur validation.

## 2. Capacités existantes à réutiliser

- Écran AGA privé Intuition, `Aga Double Buffer`, `Aga Swap`, `Aga Wait Vbl`, notifications `Safe`/`Disp` distinctes.
- Images AGAPIC v1/v2, `Aga Bank Image Draw`, `Aga Image Region` ; transparence et clipping selon les contrats existants.
- Icônes `FICON8` 16x16x8 avec `Aga F Icon` (CPU, banque source Fast/Chip), `Aga F Blit` (cache Chip préparé), `Aga F Icon Bank Create` et `Aga F Icon Bank Put`.
- `Aga Blit Clear/Fill/Copy` sécurisés `Safe`, écran arrière indépendant des écrans AMOS.
- Aucun besoin de `c2p.library` pour le premier test `FICON8`.

Les sprites matériels sont une autre famille : DMA/Chip, ressources et palettes matérielles, interactions avec Intuition/Copper. Leur disponibilité et leur comportement sur le ViewPort privé doivent être vérifiés, non déduits des capacités des Bobs.

## 3. Piste AMAL validée par documentation, pas encore par WinUAE

Le [manuel AMOS Professional, chapitre 7.6](https://amospromanual.dev/07-06-amal.html) décrit :

- `Amal canal,A$ To adresse` : écrit dans une **zone mémoire paire et valide**, indépendante d'un Bob/Sprite AMOS ; cette forme remplace l'affectation `CHANNEL` précédente.
- Format du tampon par canal : WORD à `+0` (bits 0/1/2 : X/Y/image modifiés), WORD `+2` X, WORD `+4` Y, WORD `+6` image A. Lecture possible avec `Deek`.
- `Synchro Off` **avant** de déclarer AMAL ; `Synchro` fait avancer les programmes depuis BASIC, sans exécution AMAL automatique par interruption. `Amal On` les active, `Amal Off` les retire.

**À vérifier en P0** : validité de l'adresse d'une banque DATA AMOS, écriture effective X/Y/A, cadence `SYNCHRO`, compatibilité avec l'écran privé, compilateur AMOS en phase finale seulement, absence d'accès après `Erase`.

Une banque mémoire utilisée pour ces tampons doit rester vivante et **ne jamais être libérée tant qu'AMAL est actif**.

## 4. Contrat fonctionnel cible (non-API)

| Domaine | Comportement visé |
|---|---|
| Objet | Identifiant, type `BOB` ou `SPRITE`, X/Y logiques, image/frame, visibilité, point d'ancrage, ordre de dessin |
| AMAL | Calcul des positions et images **dans le thread principal**, lecture d'un tampon par objet, aucun rendu implicite |
| Bob | Image masquée/opaque, clipping, même profondeur et mode vidéo que la cible, dessin **sur back buffer Safe seulement** |
| Sprite matériel | Gestion système `graphics.library`, allocation/libération explicites, ressources DMA réellement en Chip RAM ; collisions/limites avec Intuition à tester |
| Composition | Fond/décor d'abord, Bobs triés par ordre, textes/effets, attente fin Blitter, présentation par `Aga Swap` explicite |
| Double buffer | Un rendu n'écrit jamais dans un buffer non `Safe`. `Aga Wait Vbl` n'est **pas** une preuve de `Safe` ; `Disp` gère une autre notification |
| Persistance | Pas de pointeur de banque conservé au-delà d'un déplacement, `Erase`, `Close` ou changement de contexte |
| Nettoyage | `Amal Off` avant libération du tampon, désactivation/libération des sprites, fin des DMA, fermeture écran puis `Amos To Front`; gérer Ctrl+C/échecs |
| Interruptions | **Zéro dessin, zéro modification de buffer/bitmap, zéro allocation/libération** |

La position précise de la mise à jour des sprites matériels par rapport aux notifications `Disp` reste **à qualifier**. Le schéma de boucle n'autorise pas à confondre `Wait Vbl`, `Safe` et `Disp`.

## 5. Phases décidées

| Phase | Prototype / livrable | Preuve requise | État |
|---|---|---|---|
| **P0 — AMAL manuel et Bobs témoins** | Deux canaux AMAL mémoire et deux Bobs 16×16 via `Aga F Icon` | Runtime/WinUAE PASS (211 frames, aucun refus de dessin/Swap), correction visuelle du clignotement confirmée ; source P0 archivée | **TESTÉ / ARCHIVÉ** |
| **P1 — Bobs généraux** | Six images AGAPIC v1/v2 24×24, masquage/opaque, cadence 16/24 frames, ordre, clipping et double buffer en 8 plans | Gate B WinUAE Runtime PASS : 240 frames, 46 overlaps, pixel témoin 1, aucun échec de dessin/Swap ; [rapport P1](M19_P1_WINUAE_RUNTIME_2026-11-15.md). Autres profondeurs et Compiler non testés. | **TESTÉ / PASS RUNTIME 8 PLANS** |
| **P2 — Objets gérés** | [Prototype BASIC P2.0 archivé](../tests/passed/M19_P2_OBJECTS_01.asc) : IDs, AGAPIC/FICON8, frames, hotspot, visibilité, Z stable, AMAL manuel, destruction | **Gate B WinUAE Runtime 68030 PASS** : 240 frames, sources 6/4, 5 objets créés, 1 supprimé, rejets invalides, 4 clips, 0 erreur Draw/Swap, Chip/Fast stable. [Rapport](M19_P2_WINUAE_RUNTIME_2026-11-15.md). Pas de Gate C/D ni d'API native approuvée. | **P2.0 TESTÉ / PASS RUNTIME 8 PLANS** |
| **P2 bench — capacité des Bobs** | [Test 4/8/16 Bobs archivé](../tests/passed/M19_P2_BENCH_BOBS_01.asc), écran privé R84, sources partagées, mélange opaque/masqué/FICON8, tri Z BASIC, temps de composition et présentation distincts | **Gate B PASS** sur 68030/JIT et MC68020/14 MHz/JIT OFF (240 frames/9 088 dessins/0 erreur). Sur 68020 : tri ~4/15/59 ms et composition ~60/96/190 ms à 4/8/16. [Rapport](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md). Optimiser et re-benchmarker le tri Z avant API native. | **TESTÉ / PASS RUNTIME 8 PLANS** |
| **P2.1 — cache Z BASIC (dernier essai)** | [Banc A/B archivé, PASS](../tests/passed/M19_P21_ZCACHE_BENCH_01.asc) : tri systématique versus cache, même mélange 4/8/16 Bobs et deux passages inversés ; vérifications d'invalidation Z/visibilité | [Protocole 68020/14 MHz/noJIT](../benchmarks/README_M19_P21_ZCACHE_68020_NOJIT.md). **Gate B Runtime WinUAE 68020 PASS**, 240 frames, 9 088 dessins, 17 reconstructions / 1 188 réutilisations, gain de composition jusqu'à **30,4 %** à 16 Bobs ; [rapport](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md), avant toute décision d'API native. | **PASS RUNTIME 8 PLANS — DERNIER ESSAI TERMINÉ** |
| **P2.2 — Nouveau bloc BOBS natif** | Quatrième unité AP20 **indépendante** en expérimentation, `Aga Bob Probe` témoin uniquement ; 76 API R84 préservées, pas encore de rendu groupé | [Preuve de dispatch + tests CPU MC68020](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md). Gate A MC68020 **PASS**, [CI 43696972204](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43696972204). Candidat R85 [actif dans dist](../dist/AMOSPro_AGA.Lib), **Gates B Runtime et C Compiled du témoin PASS**, [journal et analyse](M19_P22_4UNIT_WINUAE_RUNTIME_COMPILED_2026-11-15.md), **R84 LAST_GOOD protégée**. `Aga Bob Batch` reste à implémenter. | **GATES A/B/C DU TÉMOIN PASS / BATCH NON IMPLÉMENTÉ** |
| **P3 — Sprites matériels** | Audit ViewPort/Intuition, pointeur, canaux disponibles, allocation système, 16 pixels puis déplacement | Gate A ciblée + Gate B WinUAE ; ressources/cleanup ; aucun registre DMA brut imposé | À étudier |
| **P4 — Extensions** | 32/64 pixels AGA, canaux attachés, cache/Blitter, Bobs optimisés et mélange Sprite/Bob | Benchmarks reproductibles sur MC68020+, étude mémoire et contraintes chipset | À étudier |

**P0 et P1 utilisent les commandes déjà présentes** tant qu'elles suffisent. Aucun numéro de version Rxx, aucune signature de nouvelle instruction et aucune date de livraison ne sont attribués.

## 6. Protocole P0 retenu

1. Conserver **R84 intacte**. Vérifier que les banques AMOS de test sont libres ; fabriquer en BASIC deux images de Bob 16x16/256 couleurs avec les API `FICON8` existantes (pas de ressource externe obligatoire).
2. Réserver 16 octets DATA pour deux tampons AMAL de 8 octets, lire leurs adresses avec `Start(Bank)` **seulement après `Reserve`** ; `Length(Bank)` sert au test d'existence des banques absentes.
3. `Synchro Off` avant les deux définitions `Amal 0/1,... To adresse`, puis `Amal On`. Définir deux trajectoires et des changements d'image A.
4. Ouvrir l'écran AGA privé `320x256x256` en double buffer. Dans une boucle BASIC : une attente VBL de cadence, **un `Synchro`**, lecture X/Y/A par `Deek`, dessin du fond par `Aga Blit Fill` après `Safe`, puis des deux Bobs par `Aga F Icon`, puis `Aga Swap` explicite. Les retries de dessin/swap sont bornés ; pas de boucle bloquante infinie.
5. En fin normale ou erreur contrôlée : `Amal Off` / `Synchro On`, fermeture écran, `Amos To Front`, `Erase` des **seules** banques créées ; rapport texte `RAM:M19_P0_AMAL_BOBS_<MODE>.TXT` (`RUN_MODE`, `PRG_STATE`, CPU signalé, RESULT, VERDICT, erreurs, compteurs, Safe/Swap, Chip/Fast avant/après, fermeture).
6. **Condition de PASS P0** : les deux objets sont visibles et mobiles, X/Y/A changent conformément à l'AMAL, aucun écran noir ou freeze, aucune écriture sur front/non-Safe, fermetures/banques correctes, rapport existant et conforme. Un préflight statique ne vaut pas Gate B.

Ce prototype peut utiliser les **Fast Icons comme Bobs logiciels témoins** : il ne s'agit ni des commandes `Bob` natives d'AMOS, ni d'un nouveau gestionnaire de Bobs.

## 6 bis. Définition de P1 — premier test logiciel

- **Test P1 historiquement actif** (désormais [archivé et figé](../tests/passed/M19_P1_AGAPIC_BOBS_01.asc)) ; l'unique ASC courant est le [témoin P2.2 du quatrième bloc](../tests/current/M19_P22_4UNIT_PROBE_01.asc) ; le [benchmark P2.1 cache Z](../tests/passed/M19_P21_ZCACHE_BENCH_01.asc) est désormais archivé sans modification. L'ancien [benchmark 4/8/16 PASS](../tests/passed/M19_P2_BENCH_BOBS_01.asc) est archivé à l'identique. Le [test P2.0 validé](../tests/passed/M19_P2_OBJECTS_01.asc) est également archivé sans modification. P0 est également archivé dans `tests/passed/`.
- **Banques :** 11 (16 octets pour 2 canaux AMAL), 12..17 (six AGAPIC 24×24, v1/v2, transparence de l'index 0 sauf l'image opaque 17), 18/19 (deux captures 1×1 de comparaison).
- **Boucle :** `Synchro Off` / AMAL en mémoire et `Synchro` manuel ; deux déplacements X/Y, sélection des images toutes les 16/24 frames et inversion de priorité tous les 60 ticks. Toutes les opérations graphiques se déroulent depuis BASIC, après préparation du back buffer `Safe`.
- **Images et masque :** `Aga Bank Image Capture` / `Aga Bank Image Draw` ; fond totalement redessiné à `Aga Blit Fill` puis objet opaque, deux Bobs masqués, objet fixe devant et quatre clips, Swap explicite.
- **Pixel témoin :** capturer 1×1 après ordre 12→14, puis après 14→12 ; comparer uniquement les données RLE v1. Différence prouvée = composition sensible à l'ordre **sur ce pixel**. L'inspection visuelle est nécessaire pour le reste.
- **P1 désormais validé :** Gate B WinUAE Runtime PASS sur 68030 (240 frames, pixel témoin 1, aucun échec Draw/Swap) selon [rapport P1](M19_P1_WINUAE_RUNTIME_2026-11-15.md). Le banc n'éprouve que **256 couleurs / 8 plans**, ni les sprites matériels, ni un gestionnaire d'objets.

## 6 ter. P2 — contrat de gestion d'objets proposé

Le document de référence [M19_P2_OBJECT_MANAGER_CONTRACT.md](M19_P2_OBJECT_MANAGER_CONTRACT.md) détaille : modèle logique avec banque source et frame, positions/hotspot, Z stable, visibilité, AMAL facultatif, ownership, fermeture, non-Safe et refus propres. Il **propose une validation P2.0 par prototype BASIC** avant toute API AP20 ; cette proposition n'est **pas encore validée comme spécification d'API**. Les autres phases conservent leurs portes de qualification indépendantes.

## 7. Conditions de validation et livrables

- **Gate A/P0 :** contrôle ASC statique (blocs IF/FOR, syntaxe plausible documentée, banque/adresses, un seul ASC, log RAM, aucun dessin en interruption). Ne pas annoncer une compilation AMOS ni un rendu réel depuis une analyse de texte.
- **Gate B :** exécuter **le seul ASC actif** sous AMOS/WinUAE avec R84, observer les deux Bobs, relever le fichier `RAM:`, confirmer le retour au programme sans blocage.
- **Gate C :** AMOS Compiler **au jalon final convenu**, pas à chaque étape fonctionnelle. **Gate D** matériel réel distinct et non présumé.
- **Fichiers de suivi :** ce plan ; `docs/ROADMAP.md` (statut M19) ; `docs/NEXT_SESSION.md` (état de reprise) ; `tests/current/README.md` (ASC courant).
- **Circuit unique :** uniquement `main`, un seul `dist/AMOSPro_AGA.Lib` si une future candidate native est autorisée, un seul `tests/current/*.asc`, archives et `LAST_GOOD` protégées. **Aucune modification native en P0.**

## 8. Références

- [Règles permanentes de source, builds et tests](../EXTENSION_SOURCE_RULES.md)
- [Roadmap](ROADMAP.md), [architecture écran/back buffer](ARCHITECTURE.md), [synchronisation Safe/Disp](M12_SAFE_BLITTER_R27.md)
- [Fast Icons et cache Chip](M18_FAST_ICON_CACHE.md), [contrat AGAPIC v2](M16_AGAPIC_V2_CONTRACT_2026-11-14.md)
- [Protocole RAM des tests](AMOS_RAM_TEST_LOGGING.md)
- [AMOS Professional — AMAL, canaux, `TO adresse`, `SYNCHRO`](https://amospromanual.dev/07-06-amal.html)

**Ce document fixe le plan approuvé et les limites de preuve.** Toute décision ultérieure portant sur de nouvelles commandes, API ou formats fera l'objet d'une validation explicite avant implémentation.
