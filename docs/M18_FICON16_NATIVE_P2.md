# M18/P2 — noyau natif Fast Icon 16×16 AGA 8 plans (chemin aligné)

**Prototype interne 68000** : [émetteur natif](../tools/m18_ficon16_native_aligned_emit.py), [test CPU réel Unicorn](../tools/test_m18_ficon16_native_aligned.py). Source : [contrat P1 du format Unity](M18_FICON16_SOURCE_P1.md).

## Périmètre réellement codé

Le noyau reçoit **un slot déjà validé de 288 octets** : 16 lignes de 1 mot de masque préservation + 8 mots planaires (8 bitplanes, 256 couleurs). Il lit la source au CPU depuis **Fast ou Chip**, écrit les mots directement dans les 8 bitplanes Chip du back buffer **déjà validé par l'appelant**, sans Blitter, allocation, compression, Swap, attente VBL, palette ni écriture du front. Modes 0 opaque (couleur zéro visible) et 1 masqué (couleur zéro transparente selon les mots de masque Unity). Y est pixel-exact avec clipping, X est pixel-exact **seulement si déjà multiple de 16**, sinon retour 0 sans écriture ; **aucun arrondi silencieux**. Les mots voisins au bord droit sont protégés via un masque de dernier mot.

**ABI interne, PAS une signature AMOS :** A0 pointe vers 288 octets de source, A1 vers une table de 8 pointeurs Chip; D0=X, D1=Y, D2=BytesPerRow, D3=mode 0/1, D4=largeur écran, D5=hauteur écran. Retour D3=1 succès/no-op ou 0 rejet, D2=0. Sauvegarde des registres AMOS habituels, pile équilibrée, A3 intact. Une future enveloppe publique devra valider la banque AMOS existante, la taille, les masques canoniques, les 8 pointeurs, la propriété du buffer inactif et le Safe non bloquant **avant de transmettre la source au noyau**.

**Non encore implémenté :** chemin général X non aligné, wrapper AP20, lecture banque par numéro/ID via Bnk.GetAdr, création/gestion de cache Chip, staging Fast→Chip, backend Blitter masqué, double-buffer avec cache indépendant, allocation/libération et chronométrage WinUAE. Il s'agit d'une **première primitive du futur Fast Icon natif**, et **pas de R61 installable**.

## Validation

Le test CPU vérifie dans Unicorn M68000 les sorties sur quatre icônes à masque varié, plusieurs positions alignées avec clipping, modes opaque et masqué, comparaison octet pour octet des 8 bitplanes avec le modèle indépendant P1, mémoire sentinelle, source immuable, pile/ABI et rejets avant toute écriture. Des instructions native/ABI critiques restent à qualifier par le CI GitHub avant de considérer Gate A PASS.

**États distincts :** contrôle statique/emission en environnement local, Gate A CPU réelle **en attente du workflow** (consulter son exécution et ne marquer PASS qu'après succès), Gates B interprété et C compilé WinUAE **non effectuées**, Gate D Amiga physique **non effectuée**. Aucun test de débit réel ou comparaison CPU/Blitter autorisé à ce stade.

**Protection :** R60 0.13.5 LAST_GOOD, `dist/AMOSPro_AGA.Lib`, les ASC historiques et `tests/current/` restent inchangés. Aucun nouveau token, aucun R61, aucune branche.
