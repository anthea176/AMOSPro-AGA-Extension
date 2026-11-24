# Passage 21 — Bilan de l'audit statique P2d et plan de correction proposé

**24 novembre 2026 — passage 21/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

**Clôture du périmètre de lecture planifié (21 passages). Audit de validation et chantier de correction restent ouverts.** La cartographie des 102 commandes, les 100 entrées publiques natives P2d, et les 19 scénarios sont documentés ; cela ne signifie ni 100 commandes validées en Runtime, ni couverture exhaustive de toutes les branches ASM. Les cas VM et le gel Sprite sont maintenus.

> **Addendum Runtime 24/11/2026 — AGA-011 :** T06A Runtime FAIL sur P2d-L2 : PROBE_COMPLETE=1, TARGET FRONT, ERR 50, back 17/17/17 inchangé, ancien front 64/128/192. Trois Swaps sans refus, fermeture correcte. Écriture de la page présentée confirmée, pas une simple modification de palette. Défaut bloquant 0.14.1 ; aucune preuve d'écriture du back sous Safe pending (non testé). [Preuve](evidence/T06_PATTERN_RUNTIME_FAIL_L2_2026-11-24.TXT). Classement proposé P0 pour le non-respect du contrat de page, et non pour une corruption mémoire démontrée ; qualification de Safe pending encore requise. Le tableau d'audit statique initial ci-dessous reste historique.

## 1. Registre de décision consolidé

| ID | Classement à la clôture de lecture | Constat / action proposée | Tests |
|---|---|---|---|
| AGA-001 | P0 statique confirmé, effet réel VM | IFF Load : BODY sur back sans acquisition Safe après Swap ; garde avant écriture, couleur séparée | T04/T12/T17 |
| AGA-002 | P1 structure conditionnelle, effet réel VM | Premier Bind B8 après premier Swap sans Bob : acquérir Safe avant sélection/capture | T01/T02/T05/T17/T18 |
| AGA-003 | VM, contrat | Clear → décor → Swap ; pas de bug établi pour séquence légale | T03/T06/T09 |
| AGA-004 | VM | Close/End/owner, timeout C2P et retry, ressources de curseur | T14/T16 |
| AGA-005 | P2 confirmé sur scripts/CI | Identités active S1 vs LAST_GOOD P2d et contrôle LEA | T07/T14 + CI ciblée |
| AGA-006 | VM, coordination des writers | Gardes locales constatées ; qualification transversale encore nécessaire | T05/T06/T13 |
| AGA-007 | VM | IFF deux passes : divergence/transaction tardive non démontrée | T12 |
| AGA-008 | P1 couverture | Essais croisés RPG et cycle moteur incomplets | T07/T08/T10/T11/T17/T18 |
| AGA-009 | P2 risque/latence, VM réel | R83 SafeWait borné ; drain IDCMP sans plafond fixe, pas de freeze démontré | T14 |
| AGA-010 | P0 statique confirmé, effet réel VM | Back Fill legacy SetRast sans Safe ; réutiliser discipline du Blit Fill sécurisé | T19/T05 |
| AGA-011 | P1 à qualifier | Screen Pattern via Screen.RastPort : bitmap réel après Swap à identifier | T06 |
| AGA-012 | P2 documentaire | Identité obsolète dans README tests/current ; mise à jour seulement hors gel autorisé | provenance |
| AGA-013 | P2 oracle confirmé | CLOSE_RETURNED=1 ne mesure pas les ressources libérées | T14 |
| AGA-014 | P2 ordre conditionnel statique, VM normal | Bank Free : slots modifiés avant retour de release ; tester refus et répétition | T10/T14 |

Les priorités P0 expriment ici une violation de discipline de sécurité graphique constatée dans le code, **pas une corruption réellement reproduite ni une fréquence mesurée**. AGA-003 reste VM ; AGA-011 n'est pas promue P0 sans identification du bitmap. Risque ABA sur banques et saturation mémoire/input restent des variantes de T10/T14/T08, non de nouveaux bugs confirmés.

## 2. Ordre proposé de correction, non autorisé par ce document

| Lot | Contenu et résultat attendu |
|---|---|
| L0 — reproductibilité | Cibler les deux identités existantes dans la CI, contrôler SHA, AP20/ABI/LEA. Rejouer la référence P2d à l'identique sur environnement isolé, archiver FAIL et PASS. Ne pas modifier le banc historique. |
| L1 — sécurité SafePort | Corriger AGA-001 et AGA-010 sans changer les signatures ni confondre Safe/Disp ; Blit Fill plein bitmap possède déjà SetRast sûr. Qualifier AGA-011 puis corriger si la cible réelle l'exige. Gate A avec message absent/arrivé/acquitté ; vérifier non-mutation en refus selon le contrat, B/C T04/T05/T06/T12/T19. |
| L2 — progression B8 | AGA-002, acquisition avant premier Bind ; root non créé inutilement, READY/DIRTY préservés, pas de Wait Vbl magique ; T01/T02/T03/T08/T17/T18. |
| L3 — cycle et ressources | T10/T11/T14/T16 : banques, ABA, cache, échecs d'allocation, Close/End/C2P timeout, callback et owner. Corriger AGA-004/009/014 seulement selon preuves ; rendre l'oracle AGA-013 discriminant. |
| L4 — régression 2D | T07 inchangé et cas croisés T03/T06/T09/T10/T11/T12/T13/T14/T16/T17/T18 ; Gate A, B puis C avec identité du candidat exact ; historique non écrasé. |
| L5 — décision auteur | Comparer résultats et limites, autorisation explicite avant promotion LAST_GOOD ; aucun redémarrage Sprite ou Dual Playfield avant décision. T15 reste gelé ; Gate D à part. |

L0 est un prérequis de mesure, non une permission implicite d'éditer CI. L1 est le premier lot de **correction native**. Pour Back Fill instruction sans retour, choisir et documenter un comportement de refus ou d'attente bornée conforme au contrat avant code ; ne pas convertir discrètement la syntaxe publique. Favoriser le changement minimal, isolé et réversible. Ne pas rendre le socle « vert » par suppression d'assertions, modification de l'ASC, retries aveugles ou transfert de PASS d'une autre Lib.

## 3. État des livrables et critères pour la vraie clôture

- [Rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), [matrice commandes](AUDIT_AGA_MATRICE_COMMANDES_2026-11-23.md), [matrice tests](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md) complétés.
- Derniers rapports : [16 banques](AUDIT_AGA_BANQUES_INTEGRITE_2026-11-24.md), [17 mémoire](AUDIT_AGA_CHIP_FAST_ALLOCATIONS_2026-11-24.md), [18 Bobs](AUDIT_AGA_BOBS_COLLISIONS_CLIPPING_2026-11-24.md), [19 B8](AUDIT_AGA_B8_TRANSACTIONS_RECUPERATION_2026-11-24.md), [20 ABI/CI](AUDIT_AGA_COMPILER_ABI_CI_2026-11-24.md).
- 19 scénarios spécifiés, **zéro nouvel essai exécuté durant l'audit**, T15 suspendu ; historique B/C P2d exact conservé, aucun PASS nouveau.
- Avant qualification finale : chaque anomalie critique corrigée ou explicitement démontrée non applicable, VM restantes attribuées à un test ou une décision justifiée ; journal et SHA du candidat ; régression intégrée et vrais modes B/C ; promotion distincte approuvée par l'auteur.

**Décision actuelle : STOP au développement natif, pas STOP à la documentation.** Lecture planifiée terminée ; correction, exécution des tests, modification de scripts, promotion et Sprite nécessitent une nouvelle autorisation. Branches : main uniquement. Les deux Lib, tests, preuves et sources restent intacts.
