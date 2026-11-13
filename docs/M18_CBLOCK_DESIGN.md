# M18 — CBlock AGA au pixel près : proposition de contrat

**Statut au 13/11/2026 : ÉTUDE / CONTRAT PROPOSÉ, aucune API CBlock implémentée ni validée.** M18/R67 v0.13.12 reste la seule candidate (`dist/AMOSPro_AGA.Lib`, 43 180 octets, SHA256 `ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5`, Gates A/B PASS). **R63 `LAST_GOOD` est protégée.** Aucun changement de bibliothèque, token AP20, programme ASC actif ou banque historique par cette étude. Une seule Gate C manuelle AMOS Compiler à la **fin de M18**, pas avant.

## 1. Origine : ce que fait réellement AMOS Professional

- `Get Cblock number,x,y,width,height` : capture/compacte une zone de l'écran courant.
- `Put Cblock number` ou `Put Cblock number,x,y` : restaure à la position d'origine ou à une nouvelle position.
- `Del Cblock` avec ou sans numéro : libère les blocs temporaires.
- La documentation AMOS décrit une compaction **priorisant la vitesse**, avec **coordonnées/largeurs horizontales alignées sur 8 pixels**, notamment pour restaurer les fonds des fenêtres de dialogue.
- Le code 68000 historique utilise un **RLE d'octets de bitplanes** : octet direct si inférieur à `$C0` ; à partir de `$C0`, marqueur `$C0..$FF` suivi d'une valeur répétée. Le compteur encodé est sur 6 bits (`n = (token AND $3F) + 1`). Il opère sur les lignes/planes, et le source historique utilise `LSR.W #3` pour X et Width. Ces particularités sont des **constats sur la source consultée**, non des obligations pour notre API AGA.

Références :

- [Manuel AMOS Professional, chap. Icons and Blocks, ` Compacted blocks](https://amospromanual.dev/07-07-icons-and-blocks.html)
- [AMOS Professional 365, table des commandes et paramètres](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BLib.s#L706-L716)
- [AMOS Professional 365, capture/compaction et restauration](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BW.s#L12013-L12213)
- [AMOS Professional 365, liste de blocs et libération](https://github.com/marc365/AMOS-Professional-365/blob/master/%2BW.s#L12229-L12313)

Il ne s'agit **ni** de l'API `FICON8` d'AMOS Unity **ni** du format `AGAPIC` de notre extension. **Ne pas annoncer une compatibilité binaire avec les CBlocks AMOS historiques et ne pas copier leur code source** : adapter le concept de manière indépendante, conformément aux règles de l'extension.

## 2. Usage et décisions proposées

Priorité : **sauvegarder puis restaurer rapidement et sans perte un rectangle de fond AGA** (fenêtre de dialogue, panneau, HUD), ou le déplacer, au pixel près.

| Sujet | Proposition M18 |
|---|---|
| Surface source et destination | **Back buffer de l'écran Intuition AGA privé**, jamais l'écran AMOS ni Workbench |
| Profondeur | **1 à 8 bitplanes**, pour les profondeurs effectivement ouvertes par `Aga Screen Open` ; mémoriser la profondeur et exiger une correspondance pour restituer |
| Coordonnées | **Pixel exact**, X et largeur arbitraires, notamment X=1/7/15/31 ; aucun arrondi caché sur 8 ou 16 |
| Capture | Rectangle entièrement dans l'écran, sinon retour 0 sans banque créée ; pas de clipping à la capture |
| Restauration | **Écrasement opaque**, y compris l'index 0 ; clipping exact aux quatre côtés de destination sans modification des pixels hors rectangle |
| Palette | Conserver les **indices matériels** uniquement, ne pas modifier/sauver/appliquer la palette ; si la palette change, les couleurs affichées changent |
| Stockage | Une **banque DATA AMOS par CBlock** pour v1, préférentiellement en Fast RAM, compatible `Save/Load` ABK ; pas d'allocation Chip exigée pour la source |
| Rendu | Décodage CPU Fast/Chip → back buffer AGA Chip ; **aucun accès du Blitter à la Fast RAM**, aucune conversion C2P obligatoire ni staging `FICHIP8` |
| Double buffering | Travaille sur le back buffer logique courant, jamais automatiquement sur les deux tampons ; aucun `Swap` implicite |
| Durée de vie | `Erase Bank` / `Erase` côté AMOS ; pas de liste de CBlocks privée ni de pointeur conservé après fermeture |
| Performance | Codec RLE très léger avec **fallback RAW** lorsque la compression n'est pas profitable ; vitesse et mémoire à mesurer sous WinUAE avant de promettre un gain |

**Hors v1** : transparence/masque indépendant, blending, palette intégrée, capture du front buffer ou d'un écran AMOS, allocations multiples dans une même banque, gestion automatique de cache, variantes Blitter, accès depuis une interruption ou AMAL, compatibilité des banques CBlock historiques.

## 3. API AMOS proposée — NON ENCORE VALIDÉE

```amos
_OK=Aga C Block Capture(Bank,X,Y,Width,Height)
_OK=Aga C Block Draw(Bank,X,Y)
_OK=Aga C Block Restore(Bank)
```

- **Capture** : crée une banque DATA `AGACBLK ` (nom natif sur 8 caractères, espace final) si et seulement si le numéro est libre, dans la plage **5..65535**. Arguments Width/Height en **nombre de pixels**, strictement positifs ; X/Y signés. Retour `1` après écriture complète ; sinon `0`, **aucune banque existante remplacée/effacée**. La taille stockée dépend de la compression. Comme pour `Aga Image Capture`, `Bank` occupée est un refus, pas un remplacement.
- **Draw** : vérifie entièrement la banque par son **numéro**, son type DATA, son nom natif, son en-tête et le flux, puis restitue le rectangle à **(X,Y)** en mode **opaque**. Retour `1` si banque valide et opération réussie, y compris rectangle entièrement hors écran (no-op) ; `0` si mauvais type, taille, données, profondeur ou écran absent. Dessin partiellement hors écran clippé au pixel.
- **Restore** : mêmes contrôles et retour que `Draw`, mais à **(OriginalX,OriginalY)**, mémorisés à la capture. Pas de mémorisation du pointeur/écran initial.
- **Suppression** : employer `Erase Bank`/`Erase` natif AMOS, plutôt qu'introduire `Aga C Block Delete`. Pour recapturer avec le même numéro, libérer la banque auparavant.
- Ces trois signatures sont une **proposition de design seulement**. Ne pas ajouter de token ou modifier les tableaux d'API avant validation de la proposition.

Exemple d'usage prévu (**non exécutable avec la bibliothèque R67**) :

```amos
_OK=Aga C Block Capture(20,31,44,73,45)
' Modifier le fond du back buffer...
_OK=Aga C Block Restore(20)
' Ou restituer au pixel près ailleurs :
_OK=Aga C Block Draw(20,93,127)
Erase 20
```

## 4. Format de banque `AGACBLK` v1 — contrat de sérialisation proposé

Banque AMOS **DATA** portant exactement le nom à 8 caractères `AGACBLK `, payload interne autonome. Champs **big-endian** (68000). Une banque = un rectangle ; aucun pointeur absolu, aucun champ dépendant d'un écran ouvert. `Start(Bank)` et `Length(Bank)` doivent fonctionner après `Save / Erase / Load`.

| Offset dans le payload DATA | Taille | Champ | Valeur |
|---:|---:|---|---|
| 0 | 8 | Magic | ASCII `AGACBLK1` |
| 8 | 2 | HeaderSize | `40` |
| 10 | 2 | Version | `1` |
| 12 | 2 | Depth | `1..8` |
| 14 | 2 | Codec | `0` = RAW, `1` = RLE-CB |
| 16 | 4 | OriginalX | Entier signé 32 bits |
| 20 | 4 | OriginalY | Entier signé 32 bits |
| 24 | 4 | Width | Entier non signé 32 bits, >0 |
| 28 | 4 | Height | Entier non signé 32 bits, >0 |
| 32 | 4 | RawLength | `ceil(Width/8) * Height * Depth`, calcul vérifié sans overflow |
| 36 | 4 | PayloadLength | Taille exacte des données qui suivent |
| 40 | variable | Pixels | Aucun padding de fin non déclaré |

**Ordre des pixels** : **ligne par ligne, puis plan par plan** (`row=0, plane=0..Depth-1, puis row=1...`). Chaque ligne de chaque plan contient `ceil(Width/8)` octets **normalisés avec le premier pixel au bit 7**, même si X d'origine n'était pas aligné. Les bits inutilisés du dernier octet sont à zéro. Ce flux compact conserve donc exactement les W pixels, sans capturer des pixels voisins.

**Codec 0 — RAW** : concaténation directe de ces groupes, `PayloadLength == RawLength`.

**Codec 1 — RLE-CB** : chaque groupe `(ligne,plan)` est encodé indépendamment. Un token `$00..$BF` émet l'octet littéral. Un token `$C0..$FF` doit être suivi d'un octet de valeur et en émet exactement `(token AND $3F)+1` exemplaires. `$C0, value` permet donc d'échapper un littéral `>= $C0`. Runs découpés en groupes de 64 octets au maximum, choix déterministe. Les tokens ne doivent **jamais déborder la taille décompressée du groupe**. Le décodeur consomme exactement `PayloadLength` octets pour produire exactement `RawLength` octets, sans données résiduelles ni lecture hors banque.

**Sélection codec** : calculer les deux longueurs lors de la capture ; utiliser **RAW si RLE n'est pas strictement plus petit**, puis allouer exactement `40+PayloadLength`, avec toutes les additions et multiplications contrôlées. Format indépendant du CBlock AMOS standard, même si le principe des tokens RLE est analogue.

**Sécurité de lecture** : vérifier la banque, l'en-tête, la profondeur, les dimensions, la taille et **l'intégralité du flux RLE en prélecture** avant de modifier le moindre pixel du back buffer. Refuser tout tronquage, run hors ligne, tail-bit non nul, header incohérent ou surplus. Aucune écriture partielle sur erreur détectable. Les accès aux plans AGA, à leurs pitch/limites et à la Chip RAM doivent être contrôlés avant lecture/écriture.

## 5. Sémantique graphique et mémoire

1. **Capture** : écran AGA privé valide, back buffer prêt après `Safe` et `WaitBlit` lorsque nécessaire ; largeur/hauteur/position signées et overflow vérifiés **avant** réservation. Lire uniquement les 1..8 plans concernés, normaliser le rectangle à X=0 dans le flux de banque, sans créer de masque.
2. **Rendu** : contrôle préalable de la banque DATA et décodage validé ; back buffer prêt. Décompresser/placer les pixels au CPU, alignés ou non, avec masques **de bordure uniquement** pour préserver les voisins hors rectangle ; un pixel de valeur 0 **écrase** le fond. Un clipping partiel ne décale pas la source d'un pixel.
3. **Échecs** : aucune modification de l'écran/banque pour entrée invalide, banque occupée ou allocation impossible. Ni `Aga Swap`, ni `Aga Wait Vbl` implicite, ni modification de palette, de curseur, d'icônes `FICON8` ou de cache `FICHIP8`.
4. **ABI AP20 / Compiler** : conventions AMOS A3/D2/D3, pile et registres conservés ; tous les chemins inter-routines et l'état doivent rester relogeables selon `EXTENSION_SOURCE_RULES.md`. Pas d'hypothèse de contiguïté des segments ni d'accès Fast par DMA.
5. **Coût mémoire** : à titre de borne *RAW*, un rectangle 320×256×8 occupe **81 920 octets de données + 40 octets d'en-tête** (hors surcoût de banque AMOS) ; 16×16×8 en RAW = **256 + 40 octets**. Ce ne sont pas des mesures de compression ni de vitesse.

## 6. Conditions de validation après accord sur ce contrat

**Gate A — avant toute candidate** :
- modèle indépendant encode/décode (RAW/RLE), motifs uniformes, alternés, aléatoires et littéraux `$C0..$FF` ; tous les X modulo 8/16, W=1/7/8/9/15/16/17 et limites écran ; comparaison de **chaque indice** et de chaque bit de bordure ;
- corruption d'en-tête et du RLE, tailles maximales et overflow 32 bits, banque occupée, allocation refusée, dimensions nulles/négatives, type DATA erroné, profondeur différente, absence d'écran, collisions avec les banques voisines ;
- cœur natif 68000 exécuté et contrôlé en modèles interpréteur et Compiler V2 simulé ; audit AP20, pont Compiler, pile et allocation/libération ; reproductibilité de la seule bibliothèque candidate.

**Gate B — WinUAE en AMOS interprété** (seulement **après** réalisation des Gate A) :
- **un seul ASC actif dans `tests/current/`**, créé lors de la future révision ; jamais un ASC de conception prématuré ;
- écran AGA 320×256×256, puis au moins une autre profondeur réellement prise en charge ; capture d'un rectangle non aligné avec index 0, fond modifié, `Restore` et `Draw` à X arbitraire, clipping quatre côtés, second buffer distinct ;
- `Save / Erase / Load` de la banque, intégrité au pixel après relecture, refus non destructifs, mémoire Chip/Fast retrouvée après `Erase` ; `RESULT 1`, `CLOSE RETURNED` et **capture du rendu graphique** si possible.

**Performance** : mesurer séparément **capture/compaction** et **dessin/décompaction**, pour fonds unis, motifs et images bruitées, sur 68020/68030 WinUAE sans JIT. Comparer aux chemins `Aga Image Capture` / `Aga Image Draw` (AGAPIC), et à une copie Blitter Chip→Chip **en incluant préparation/staging**. Ne pas annoncer CBlock plus rapide sans ces résultats.

**Gate C — AMOS Compiler** : **une seule validation manuelle en fin de M18**, nouvel exécutable compilé avec la candidate finale. **Gate D** : Amiga AGA physique distincte. **Aucune promotion automatique**.

## 7. Points à valider avant implémentation

1. **Noms / signatures définitifs** : `Aga C Block Capture`, `Aga C Block Draw`, `Aga C Block Restore`. Un CBlock par banque est volontaire pour v1.
2. **Profondeurs** : proposition 1..8 plans selon capacités effectives de `Aga Screen Open` ; refuser une restitution sur une profondeur différente.
3. **Restauration hors écran** : proposition `Draw`/`Restore` complètement hors écran = no-op avec retour `1`, conforme à l'usage graphique des icônes ; capture hors écran = refus `0`.
4. **Format v1** : en-tête fixe 40 octets, RLE-CB octets planaires, fallback RAW, aucune transparence.
5. **Priorité** : restauration **pixel exacte et sûre** avant l'optimisation des performances ; garder les optimisations 68020+ et `c2p.library` hors chantier.

**Aucune implémentation ni publication R68 implicite** : validation explicite du contrat, puis seulement développement ciblé et Gate A. Les README publics, exemples utilisateurs et ASC actif seront mis à jour lorsque des commandes existeront réellement.