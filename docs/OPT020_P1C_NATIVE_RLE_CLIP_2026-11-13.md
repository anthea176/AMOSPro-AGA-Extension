# OPT020/P1c — décodage RLE et géométrie de clipping en code 68EC020/68020

**Validation réelle le 13 novembre 2026 : PASS sur 68EC020 et 68020**, [CI P1c 43492252934](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43492252934), 11/11 étapes réussies. Les routines RLE, clipping X/Y et peinture partagent un seul émulateur Musashi. Travail sur la seule branche `main`, **R68 `LAST_GOOD` strictement protégée**.

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

Le banc exécute toutes les sous-routines, y compris le peintre multiplan, **dans une seule instance Musashi**, car deux instances simultanées partagent certains états internes de retour. Ce détail est indispensable pour éviter un faux échec de test. Il compare les adresses et mots RLE décodés à l'implémentation AGAPIC historique, les intervalles X/Y à un oracle mathématique indépendant, et les bitplanes finaux au modèle de pixels. Il inclut 1/2/4/8 plans, masques pleins/vides, source index couleur 0, groupes répétés et littéraux, dernier groupe partiel, clipping gauche/droite/haut/bas, et refus de corruption. **La CI P1c confirme PASS** sur ces scénarios d'émulation CPU ; ce résultat ne constitue ni Gate B WinUAE ni Gate C Compiler ni preuve de performance Amiga.

### Résultats certifiés par la CI

[Exécution réussie sur le code du commit `08a3f34`](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43492252934).

| Test | 68EC020 | 68020 | Total |
|---|---:|---:|---:|
| Lignes RLE décodées exactement | 136 | 136 | **272** |
| Refus du décodeur RLE | 13 | 13 | **26** |
| Intersections horizontales natives contrôlées | 918 | 918 | **1 836** |
| Intersections verticales natives contrôlées | 150 | 150 | **300** |
| Régions AGAPIC confrontées à l'oracle planaire | 216 | 216 | **432** |
| Groupes entiers réellement peints par BFINS | 2 676 | 2 676 | **5 352** |
| Pixels des fragments rendus par repli scalaire | 12 908 | 12 908 | **25 816** |
| Lignes décodées durant les rendus complets | 1 488 | 1 488 | **2 976** |
| Refus de prévalidation non destructifs | 7 | 7 | **14** |

**Zéro erreur détectée** dans les comparaisons de bitplanes complets, les canaries, les bornes de ligne et de table, la pile ou les registres protégés. La première CI avait échoué au moment de combiner deux instances Musashi indépendantes : le mécanisme de retour est partagé. Le [correctif `08a3f34`](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/08a3f34bd3f5d7468b6146aa7b0f09a8f54bc689) regroupe les quatre sous-routines dans **une seule machine**, sans modifier leur logique de pixels.

| Binaire natif autonome | Taille | SHA256 |
|---|---:|---|
| Décodeur ligne RLE | 176 octets | `c73d081f803c79a6fd67abd401aa1a37b3566e87638585f796dc8b22f98872f9` |
| Clipping horizontal | 78 octets | `9f534893960967e75f3dffcdedbefd0c40286cb00b82f7a9d7edeb5439e8a4f7` |
| Clipping vertical | 26 octets | `43fa47029d50a064964ccba0baaa7c02eb5af410ae5f70703bd22acdab0775a1` |
| Peintre 8 plans P1b (déjà validé) | 36 octets | `74ef53d4f0e5d53fee8603553daea0cf2de834271b63475fa62c37bcca218138` |

**Qualification atteinte :** comportement des sous-routines CPU sous Musashi, pas un chemin AP20 020 complet. Le validateur de banque global et les fragments restent en Python ; ces composants doivent être portés/validés avant toute candidate installable.

## Limite de l'étape

**Ce n'est toujours pas une extension 68020 autonome complète.** Un répartiteur Python appelle les trois sous-routines et la voie P1b, gère les zones mémoire et les petits fragments. L'ABI AP20, la relogeabilité Compiler V2, la gestion `Safe` du bitmap Intuition, le chargement de banque AMOS et les cas limites sur machine restent à intégrer **avant** toute nouvelle candidate R69.

**Aucun binaire `.Lib`, ASC actif, archive validée ou `LAST_GOOD` n'est modifié.** Une fois P1c qualifiée, la suite est un adaptateur de validation AP20/020 indépendant (sans déplacer la R68), puis le benchmark WinUAE JIT OFF et seulement une candidate unique si les tests et les gains le justifient.

**Suite P1d (13/11/2026) :** les fragments partiels ont un [nouveau noyau BFINS dynamique](OPT020_P1D_FRAGMENT_AP20_PROBE_2026-11-13.md), avec tests 68EC020/68020 et une sonde de conventions AP20/Compiler V2 en mémoire. Résultat initial en attente ; P1c reste PASS et la Lib R68 reste protégée. L'intégration réelle à l'entrée native R60 n'est pas effectuée à cette étape.
