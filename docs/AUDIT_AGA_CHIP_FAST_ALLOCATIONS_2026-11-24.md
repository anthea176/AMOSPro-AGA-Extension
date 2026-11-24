# Passage 17 — Allocations Chip/Fast, caches et snapshots

**24 novembre 2026 — passage 17/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

## 1. Provenance et symétrie d'allocation

| Ressource | Source liée et comportement |
|---|---|
| Cache AGBO Chip | [M19_P0_CHECKED_REGISTRY_MC68020 L432-L629](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CHECKED_REGISTRY_MC68020.s#L432-L629) : taille bornée, paire AllocVec/FreeVec, validation de la nouvelle plage, copie, attente Blitter avant remplacement de l'ancienne, publication d'identité et libération ; échec de préparation ne valide pas la nouvelle allocation. |
| Registre privé | [M19_P0_CHECKED_REGISTRY_MC68020 L782-L860](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P0_CHECKED_REGISTRY_MC68020.s#L782-L860) : nœud 32 octets AllocVec avec MEMF_CLEAR ; parcours bornés et validation avant libération. |
| Fonds B8 | [M19_P2D_SUPPORT_TAIL_MC68020 L878-L927](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_SUPPORT_TAIL_MC68020.s#L878-L927) : deux AllocMem avec flags $10001 (PUBLIC/CLEAR, **ni Chip obligatoire ni Fast garantie**), taille BytesPerRow*Rows*Depth. Si la seconde réservation échoue, libération de la première. |
| Libération fonds B8 | [M19_P2D_SUPPORT_TAIL_MC68020 L981-L1068](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_SUPPORT_TAIL_MC68020.s#L981-L1068) : owner/écran, tailles mémorisées et FreeMem. Copies CPU des snapshots : ne pas imposer MEMF_CHIP à ces fonds sans justification. |
| Variantes Flip | [M19_P2B_PLANAR_MC68020 L178-L248](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_PLANAR_MC68020.s#L178-L248) : dimensions bornées, produit pixels <= 4 194 304, jusqu'à 9 plans avec masque, mesures, non-chevauchement, AllocMem MEMF_CHIP, TypeOfMem aux extrémités et FreeMem de taille correspondante en échec. |
| Cycle variante | [M19_P2B_VARIANT_ANCHOR_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_VARIANT_ANCHOR_MC68020.s) / [M19_P2B_FLIP_PUBLIC_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_FLIP_PUBLIC_MC68020.s) / [M19_P2B_CLEANUP_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2B_CLEANUP_MC68020.s) : identité mode/banque/image/payload/génération/pixels/masque ; remplacement préparé avant retrait ; mode zéro purge son cache ; nettoyage 64 slots et purge sélective. La libération s'appuie sur la fin des opérations Blitter synchrones des writers. |

TypeOfMem décrit une **zone mémoire** ; il ne prouve pas à lui seul que le propriétaire de l'allocation est vivant, que sa taille annoncée est exacte ou que tous les octets intermédiaires d'une plage arbitraire sont sûrs. Il faut conserver le contrôle logique des tailles, bornes et identités. Ne pas dégrader la sécurité des buffers pour contourner les refus.

## 2. Budget indicatif, non mesuré

Sur un bitmap 320x256, profondeur 8, BytesPerRow=40, un fond vaut 81 920 octets. Les deux fonds B8 demandent **163 840 octets** hors structures. Ceci n'inclut pas les deux bitmaps d'affichage, les banques DATA, les caches Chip ni les variantes masquées.

Lors d'un remplacement, ancien et nouveau caches peuvent coexister : le pic est supérieur à l'empreinte finale. Le nombre de slots (64) borne le nombre de variantes, pas leur somme mémoire pratique. Une limite logique d'image n'est pas une promesse de pouvoir réserver cette taille sur 2 Mio de Chip. Aucun benchmark, delta RAM réel ni fragmentation mesurée ici.

## 3. Compléments aux tests

- T08 : échec de la première puis de la seconde allocation B8, aucune publication partielle du root, tailles exactes, reprise avec mémoire suffisante.
- T10/T11 : remplacement et refus de nouveau cache, répétition de 64 variantes Flip, données AGBO conservées ; Fast/Chip réels, ready=0, pas de DMA vers une plage non Chip.
- T14 : cycles Open/DB/Close/End avec et sans fonds, après échec et nouvelle tentative ; journal des allocateurs et frees par identité, taille et propriétaire, Chip/Fast avant/après. Ne pas utiliser uniquement CLOSE_RETURNED comme preuve (AGA-013).
- Mesurer séparément allocation maximale disponible et total libre si l'environnement permet de le faire ; fragmentation et overhead OS distincts, aucune valeur supposée.

**Bilan :** appariements visibles et refus locaux positifs ; intégrité de tous les chemins en échec, saturation et fragmentation VM. AGA-004/008/013/014 à qualifier. Pas de P0 supplémentaire établi ; aucune optimisation ou migration mémoire décidée.

## Addendum Runtime L2b — 24/11/2026

T14A Runtime PASS sur L2b : 26/26 Open/Close, 13 simple + 13 DB, 104 opérations curseur, 13 Swaps, zéro refus/retry Fill, CLOSED_MOUSE_X -1. Les 13 mesures après paires (référence après échauffement) donnent Chip Free=1791304 et Fast Free=138107904, CHIP_LOSS=FAST_LOSS=DIFF_PAIRS=0, MEM_STABLE=1. Pas de fuite cumulative observée pour ce scénario ; pas de preuve sur fuite unique avant référence, End, B8/C2P/Copper ou refus OS injectés. [Preuve](evidence/T14_CLOSE_RUNTIME_PASS_L2B_2026-11-24.TXT). [T11A](../tests/proto/l3_cache/README.md) préparé pour restaging FICON/FICHIP et répétition allocation/libération, sans injection OS. Les autres chemins restent à qualifier.

## Addendum T11A Runtime L2b

T11A Runtime PASS sur L2b : 7/7 cycles (échauffement + 6), 14 Stage, 35/35 pixels, 7 refus slots non préparés, tailles des banques conservées après Close 7/7, pixels initial/avant Stage/après Stage/CPU/non prêt=165/165/90/90/17. CACHE_CHIP_MIN 1192 octets, 7 swaps/Close, zéro retry Fill/Swap, Mouse X=-1. Les sept mesures après Erase sont Chip Free=1791304 et Fast Free=138106392, aucune dérive après échauffement. RESULT 1 ERR 0 MEM_STABLE 1. T14A retransmis, journal strictement identique au blob déjà archivé f99ee10423c1c5f0c9a8e88e2bca4b91d0c9aded : ne pas dupliquer ni présumer un second lancement indépendant. [Preuve](evidence/T11_CACHE_RUNTIME_PASS_L2B_2026-11-24.TXT). Les chemins AGBO, AGPC, injections et autres cycles restent ouverts.
