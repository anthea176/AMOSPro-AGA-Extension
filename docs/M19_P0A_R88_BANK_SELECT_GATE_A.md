# M19 P0a — intégration expérimentale `Aga Bob Bank` depuis R88

**Cible figée** : R88 v0.13.33, commit `7c575a02087d550611b8e966a7708b5f6a8c4b71` ; le SHA256 de `dist/AMOSPro_AGA.Lib` doit être `69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc` avant toute construction. R84 `LAST_GOOD` reste intouchable. **Aucune source, exemple ou build R89/R90 ne sert de base.**

## Première commande publique expérimentale

`Aga Bob Bank N` — **instruction, un argument entier**, `N=5..65535`. Elle choisit une banque `AGBO` v1 existante (ne l'efface pas et refuse les noms/formats étrangers) ou crée une banque vide canonique avec le remplacement transactionnel natif, sans réserver un numéro caché. L'identité de la banque sélectionnée est conservée dans une zone privée au groupe de code BOBS ; un futur `Get AGA Bob` devra comparer le numéro, le pointeur DATA et la liste `Cur_Banks` avant toute écriture.

**Limite volontaire** : la préparation Chip/DMA, la validation exhaustive de chaque image déjà chargée et `Get AGA Bob` ne sont **pas encore disponibles**. Il n'y a ni rendu Blitter, ni nouvelle image capturée, ni masque dans cette étape. Ne pas donner les lignes du contrat de conception pour un programme déjà utilisable en R88.

## Réalisation AP20

- `tools/m19_p0a_bank_select_emit.py` : émetteur MC68000 autonome, incluant la transaction sûre `m19_p0a_amos_bank_transaction_emit.py` et un payload vide `AGBO` v1.
- `tools/build_m19_p0a_r88_bank_in_memory.py` : lit la bibliothèque R88 active et vérifie les SHA R88/R84. Ajoute **une** instruction après les 78 commandes R88, préserve tous les tokens existants et les quatre unités natives R88, avec `GetP`, AP20 V2 et vérification des limites `BSR.W`. Ne produit aucun fichier `.Lib` ; n'écrit pas dans `dist`.
- `tools/test_m19_p0a_bank_select_emit.py` : contrôles locaux statiques et déterministes.
- `tools/test_m19_p0a_r88_bank_gate_a.py` : exécution **MC68000 réelle dans Unicorn** sur deux placements de code (interprété et disposition Compiler simulée) avec services AMOS 365 **mockés**. Teste création, nouvelle sélection, refus de banque étrangère, échec d'allocation, limites d'indices et préservation de l'ABI. Ni WinUAE ni AMOS Compiler réel.
- `.github/workflows/m19-p0a-r88-bank-gate-a.yml` : campagne dédiée et non intrusive.

## Statuts de validation

- Tests hôte et préflight : voir la sortie des scripts et les résultats du workflow ; ne pas confondre ces résultats avec la Gate A CPU.
- **GATE A CPU/AP20 BANK SELECT : PASS**, [workflow exact 43751680955](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43751680955) (commit `0b1eea12aabbb42caabe03e1eeced9e8dd24145b`). **20 cas MC68000** avec services AMOS simulés et deux placements natifs (interprété / disposition Compiler V2 simulée). Les 36 contrôles hôte et préflight statiques précédents sont également PASS.
- **Candidate construite uniquement en mémoire :** 76 408 octets, SHA256 `82060e0fedf3357f64426817348b218381dc8ed3b640552bd89c0ca433e79d74` ; **79 commandes, 89 entrées AP20**, groupe BOBS 8 374 octets, append R88 exact à l'offset **7004** (5186 était l'offset pré-R88), portée maximale BSR.W 17 410.
- **Portée limitée :** ces 20 scénarios CPU ne constituent pas un AMOS interprété réel, un AMOS Compiler réel ni une preuve de sécurité Chip DMA.
- **Gate B Runtime WinUAE : NON TESTÉE. Gate C AMOS Compiler : NON TESTÉE. Gate D physique : NON TESTÉE.**
- Aucune installation ni promotion n'est effectuée automatiquement, même en cas de Gate A PASS.

## Suite

Développer `Get AGA Bob I,X1,Y1,X2,Y2` avec capture pixel-exacte depuis le back buffer AGA Safe, copie plane-major non-RLE à largeur arbitraire, répertoire AGBO multi-images strictement validé, puis allocation et publication atomiques avec `Bnk.Change`. Ajouter séparément une Gate A CPU discriminante sur les cas 1×1, 17/31/32/37, 1/4/8 plans, banques Fast, `Erase`/`Load`, pénurie mémoire. **Ne pas enregistrer un token `Get` qui ne ferait que renvoyer échec**.
