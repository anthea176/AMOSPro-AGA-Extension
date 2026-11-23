# S1-P1c — Publication transactionnelle AGSP dans les banques DATA AMOS (23/11/2026)

**Statut : source MC68020 autonome et banc de tests Gate A CPU.** Cette routine n'est pas encore liée à un nouveau token AP20, n'implémente pas Get AGA Sprite, et ne modifie ni P2d ni LAST_GOOD.

## Source et mécanisme

[Source Motorola](../src/native/m19_s1/M19_S1P1C_AGSP_BANK_COMMIT_MC68020.s) · [tests CPU](../tools/test_m19_s1p1c_amos_bank_commit.py) · [CI](../.github/workflows/m19-s1-p1c-amos-bank-commit.yml).

La routine reprend **l'ABI AMOS Professional 365 réellement utilisée dans le source P2d P1e**. Les indices Main sont **Bnk.GetAdr 797**, **Lst.Cree 91**, **Bnk.Change 819**, **Lst.Del 93**. Adresse de tête des banques : **A5+$05EA**. Un nœud DATA a 24 octets de préfixe : pointeur de chaîne 4, taille 4 (payload+16), numéro 4, flags 2, réserve 2, nom 8. Le nom de banque AGSP est exactement **AGASPRT** suivi d'un espace. Aucun Bnk.Reserve destructif.

Entrée : **A0 → requête de 16 octets**, offsets : 0 pointeur vers payload AGSP v1 complet et validé, 4 longueur du payload paire (32..16 Mio), 8 numéro de banque LONG 5..65535, 12 zéro. A5 = contexte AMOS Main vivant. Retour : **D3=1** en cas de succès, **D3=0** en cas de refus, D2=0 type entier ; tous les autres registres de l'ABI sont préservés.

Séquence :
1. Vérifier numéro de banque, pointeur et enveloppe AGSP, plus les extrémités mémoire par Exec.TypeOfMem. Un **contrôle de toutes les plages, du non-recouvrement et de tous les pixels/répertoire est une précondition stricte du wrapper**, pas une propriété supposée de TypeOfMem.
2. Par Bnk.GetAdr, vérifier l'ancien numéro si présent ; refuser les banques d'un autre nom/type.
3. Allouer un **nœud dans une liste privée** avec Lst.Cree ; remplir ses métadonnées DATA et copier le payload déjà validé sans toucher à la banque active.
4. Revalider l'adresse Bnk.GetAdr et la tête Cur_Banks, parcourir la liste avec une limite de 65 535 liens, identifier exactement le nœud à remplacer ; **une seule écriture LONG** publie le nouveau nœud.
5. Appeler Bnk.Change **tant que l'ancienne allocation est encore vivante** ; libérer ensuite seulement l'ancien nœud via Lst.Del. Sur refus avant publication, libérer uniquement la nouvelle allocation temporaire.

## Vérification native de la totalité du payload AGSP

Nouveau [validateur strict MC68020](../src/native/m19_s1/M19_S1P1C_AGSP_VALIDATE_MC68020.s) avec [tests CPU indépendants](../tools/test_m19_s1p1c_agsp_validate.py). Entrée **A0 = payload entièrement alloué**, **D0 = longueur exacte et paire** ; sortie **D0=1/0**, **D1=nombre d'images si succès**. Préserve D2..D7/A2..A6, ne modifie aucun octet. Le wrapper devra le faire réussir **avant** de donner le même payload au publisher.

Il vérifie tous les en-têtes, la génération, les réserves, les identifiants croissants, les profondeurs 2/4, largeurs 16/32/64, dimensions, strides, offsets contigus, palettes RGB24 par image, absence de doublons RGB24 et entrées inutilisées à zéro. Il reconstruit les **indices de chaque pixel de chaque bitplane** et exige la numérotation locale 0 transparent, 1..N opaques dans l'ordre de première apparition. Toute corruption doit refuser sans publication et sans lecture hors du payload si le tampon est alloué selon la longueur fournie.

Les deux routines publication et validation restent **modules natifs de développement**, non liés à AP20 et non installés. La Gate C de la sonde AMOS DATA demeure volontairement sautée.

## Limites et preuve

Le banc exécute le binaire vasm -m68020 dans Unicorn MC68020, et simule les vrais indices de service AMOS Main/Exec avec des hooks de mémoire. Sont vérifiés : insertion dans une liste vierge, banque étrangère préservée, remplacement avec notification avant libération, refus de contenu erroné, manque de mémoire et changement de liste pendant le staging. **C'est une Gate A CPU partielle avec services simulés.**

La sonde DATA AGSP existante a passé **Gate B Runtime** sur WinUAE (fichier .ABK sauvegardé octet identique), mais **cela ne démontre pas encore que ce publisher est connecté à l'AMOS réel**. Le Compiler de cette sonde est **volontairement NON TESTÉ**, par décision explicite de l'auteur : pas de demande supplémentaire de Gate C pour cette sonde.

**Prochaine intégration sans arrêt de chantier :** wrapper AP20 natif qui alloue/stabilise les tampons, prépare les deux modules de capture et le repack, valide le payload AGSP, appelle le publisher, puis lance le premier test **Runtime** de Get AGA Sprite. La fermeture/détachement DMA Sprite reste hors S1-P1c et bloquante pour l'affichage hardware. Les prototypes seront uniquement sous tests/proto ; examples est réservé aux fichiers distribués.

## Pipeline natif de capture complet (S1-P1c)

[Orchestrateur MC68020](../src/native/m19_s1/M19_S1P1C_CAPTURE_PIPELINE_MC68020.s) et [tests CPU](../tools/test_m19_s1p1c_pipeline.py) : cinq modules assemblés dans un seul binaire VASM. Enchaînement : bitplanes AGA/ColorMap RGB24 → pixels Sprite 2 plans → repack multi-images → validateur strict → commit transactionnel AMOS. Le chemin doit échouer sans publier de banque en cas de buffer Unsafe, trop de couleurs, erreur d'allocation ou mauvais numéro de banque.

L'appelant fournit un **descripteur privé de 72 octets**, déjà alloué et validé, avec les zones tampon. Offsets 0..35 = requête pont S1-P1b ; +36 banque LONG ; +40 image WORD ; +42/+44 hotspots ; +46 réservé ; +48/+52 ancien payload et longueur ; +56 requête de repack ; +60 buffer de destination détaché ; +64 capacité ; +68 requête de publication. Retour **D3=1/0**, D2=0. **Ce n'est pas un token AP20 installé** : préparation des allocations par une vraie commande AMOS, stabilisation de l'écran et WinUAE Runtime sont encore à réaliser. Aucune modification P2d/LAST_GOOD.
