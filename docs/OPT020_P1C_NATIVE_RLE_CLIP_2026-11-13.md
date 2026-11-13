# OPT020/P1c — décodage RLE et géométrie de clipping en code 68EC020/68020

**Ouverture : 13 novembre 2026. État initial : sources et CI soumises, résultat CPU en attente.** Travail sur la seule branche `main`, **R68 `LAST_GOOD` strictement protégée**.

Sources : [décodeur natif + clipping](../tools/opt020_p1c_rle_clip_emit.py) · [exécution Musashi](../tools/opt020_p1c_native_runner.py) · [orchestration AGAPIC](../tools/opt020_p1c_region.py) · [tests](../tools/test_opt020_p1c_rle_clip_native.py) · [workflow P1/P1b/P1c](../.github/workflows/opt020-p1.yml).

## Progression par rapport à P1b

P1b exécutait les écritures planaires 1–8 plans et `BFEXTU/BFINS` sur un 68020 émulé, mais **décodait le RLE et sélectionnait les pixels visibles en Python**. P1c apporte trois **véritables sous-routines Motorola natives**, exécutées séparément dans Musashi sous **68EC020 et 68020** :

| Routine | Paramètres machine | Résultats et protections |
|---|---|---|
| `emit_rle_row_020` | `A0` début ligne RLE, `A1` fin exclusive, `A2` table de pointeurs déjà allouée, `D0.l` nombre de groupes 1–256, `D1.l` taille groupe 2–18 octets pairs | Décode les **paquets littéraux et répétés AGAPIC v1** en pointeurs, refuse les débordements de ligne, les groupes excessifs et les octets finaux résiduels. `D3=1` succès, `0` refus. N'effectue **aucune écriture de bitmap** |
| `emit_clip_x_020` | `D0..D5` : X du groupe, bornes source/rectangle, X de destination, largeur bitmap, largeur de l'image | Calcule les indices visibles dans le groupe, `D6=left`, `D7=right`, 0–16 exclusif ; 0/0 quand rien ne doit être dessiné. Intersections faites en arithmétique LONG signée |
| `emit_clip_y_020` | `D0..D3` : Y source, Y initial du sous-rectangle, Y destination, hauteur écran | `D6` présence (0/1), `D7` Y destination quand visible |

**Provenance du format :** le décodeur lit directement les octets de lignes issus de [`m16_agapic.py`](../tools/m16_agapic.py) : bit 7 du contrôle pour répétition, longueur `(control & 0x7F)+1`, taille de groupe `2*(Depth+MaskFlag)`, chaque plan en mot **big-endian**. Une répétition produit plusieurs pointeurs vers un seul groupe ; un littéral avance le pointeur source de `group_bytes` pour chaque groupe. Les comptes ne peuvent dépasser les groupes attendus.

### Sécurité mémoire

- L'enveloppe de test vérifie les **tableaux de pointeurs à capacité connue**, les canaries, `A3/A5/D5`, le retour `RTS`, l'équilibre de pile, la source inchangée, les bornes de chaque pointeur retourné et l'absence de lecture au-delà des lignes RLE.
- Une entrée invalide peut avoir produit une **table de pointeurs partielle**, mais jamais un dessin : l'assembleur retourne un échec. Le contrat de l'appelant est **valider avant de peindre**, ne jamais réutiliser la table après un échec.
- Le modèle de région effectue le **contrôle complet d'AGAPIC v1 avant toute écriture** via `parse_payload` ; ce validateur Python demeure une dépendance expérimentale et doit être remplacé par une validation 020/Aga native complète **avant un branchement AP20**.
- Le décodeur machine ne valide pas encore **l'en-tête global, les offsets de lignes, les bits de padding de la dernière colonne, l'ownership de la banque DATA, la profondeur et la sélection du back buffer `Safe`**. Ces préconditions restent obligatoires pour le futur wrapper.
- Le clipping natif fournit les bornes ; les **groupes complets** sont peints par le noyau multiplan P1b en `BFEXTU/BFINS`, les **fragments** sont encore écrits par une boucle scalaire Python pour éviter toute écriture hors ligne.

### Périmètre de la qualification

Le banc compare les adresses et mots RLE décodés à l'implémentation AGAPIC historique, les intervalles X/Y à un oracle mathématique indépendant, et les bitplanes finaux au modèle de pixels. Il inclut 1/2/4/8 plans, masques pleins/vides, source index couleur 0, groupes répétés et littéraux, dernier groupe partiel, clipping gauche/droite/haut/bas, et refus de corruption. **La CI est la seule preuve réelle de ce prototype** ; l'existence du code ne suffit pas pour annoncer PASS.

## Limite de l'étape

**Ce n'est toujours pas une extension 68020 autonome complète.** Un répartiteur Python appelle les trois sous-routines et la voie P1b, gère les zones mémoire et les petits fragments. L'ABI AP20, la relogeabilité Compiler V2, la gestion `Safe` du bitmap Intuition, le chargement de banque AMOS et les cas limites sur machine restent à intégrer **avant** toute nouvelle candidate R69.

**Aucun binaire `.Lib`, ASC actif, archive validée ou `LAST_GOOD` n'est modifié.** Une fois P1c qualifiée, la suite est un adaptateur de validation AP20/020 indépendant (sans déplacer la R68), puis le benchmark WinUAE JIT OFF et seulement une candidate unique si les tests et les gains le justifient.
