# C2P-2 — contrat approuvé et implémenté pour `Aga C2P Convert` (14/11/2026)

> **STATUT : contrat explicitement approuvé par l'auteur le 14/11/2026.** Implémentation native `Aga C2P Convert` en candidate R75 v0.13.20, 54 144 octets, 66 commandes / 73 AP20 ; **Gate A CPU native 24 scénarios PASS**. La R74 Open dispose déjà de ses Gates A/B interprétées PASS ; **Gate B R75 réelle, Gate C Compiler et Gate D physique NON TESTÉES**. R73 reste `LAST_GOOD` protégée. Ce contrat n'approuve **pas** `Aga C2P Close`.

## 1. Signature publique proposée

```amos
_OK=Aga C2P Convert
```

- **Fonction entière, sans paramètre** ; retour **1** uniquement si la conversion et la copie dans le back buffer sont terminées avec succès ; **0** sinon, sans erreur AMOS ni Guru.
- Utilise la banque enregistrée dans `Aga C2P Open(Bank)`. **Pas de second numéro de banque, largeur, profondeur, palette ou mode** à fournir.
- Un appel convertit **l'image complète 320×256** à partir d'un tableau chunky **8 bits/pixel, 81 920 octets** (indice palette par octet). L'écran détermine la profondeur **4, 5, 6, 7 ou 8 plans** — 16, 32, 64, 128, 256 couleurs. Au-delà de l'indice maximal, seuls les bits utiles à cette profondeur sont significatifs ; aucun contrôle coûteux de chaque pixel n'est prévu.
- **Aucun changement de palette**, aucune transparence, aucun HAM, delta, zone partielle, mise à l'échelle ou Swap implicite. Un `Aga Swap` réussi, appelé séparément par le programme AMOS, affichera le résultat.

## 2. Préconditions et refus avant toute écriture graphique

1. CPU **68020+** ; écran privé AGA encore ouvert en **320×256**, avec la **même profondeur** que lors de `Open`.
2. `Aga Double Buffer` actif, un contexte C2P vivant (cookie `C2P1`, `DBState+24` = LibraryBase, `+28` = Context, `+32` = Bank, `+36` = Depth, `+40` = cookie). Tous les pointeurs sont validés avant d'être déréférencés.
3. **Rechercher la banque à chaque appel** via AMOS `Bnk.GetAdr`, et revérifier numéro, en-tête, type DATA/WORK, taille minimale **81 920 octets**, alignement et validité mémoire des premiers/derniers octets. Un `Erase`, `Load` ou `Reserve` a pu changer son adresse. **Ne jamais utiliser aveuglément le pointeur chunky passé à Open.** Banque disparue ou plus petite : retour `0`, contexte conservé pour un appel ultérieur valide.
4. Déterminer le véritable **back buffer inactif** : `A5+$1C8 → State`, `State+32 → DBState`, `DBState+8` est l'index frontal strictement 0/1 ; choisir `SB1` si front=0, sinon `SB0`, aux offsets `DBState+0/+4`.
5. **Correction vérifiée dans les sources : `ScreenBuffer.sb_BitMap` est à `ScreenBuffer+0`, et `sb_DBufInfo` à `+4`.** L'ancien diagnostic GDB/P2 disait `+4` pour le bitmap : **c'était faux**. La structure officielle `intuition/screens.h` et `src/generated/AMOSPro_AGA_R57_C1_NATIVE.s` confirment `+0`. Ne pas reprendre le mauvais offset.
6. Contrôler `BitMap` source/destination : profondeur égale à la profondeur de l'écran, largeur utile 320 (au moins 40 octets par rangée de plan), hauteur au moins 256, `Planes[0..Depth-1]` utilisables en **Chip RAM**, bornes accessibles, aucune confusion avec le bitmap frontal. La destination peut avoir des plans séparés **ou entrelacés** : on laisse `graphics.library` gérer le `BitMap` ; ne pas en déduire une contiguïté.
7. **Safe non bloquant** : `DBState+20` bit 0 indique un accusé Safe encore en attente. Si nécessaire, faire **un seul** `GetMsg(DBState+12)`, effacer bit 0 seulement si la réponse est arrivée ; sinon renvoyer `0`, **sans conversion ni copie**. Ne jamais `ReplyMsg` une notification Safe. `Aga Swap` garde son contrôle Safe/Disp distinct.

## 3. Séquence native proposée en cas de préconditions conformes

1. Vérifier le back buffer et son Safe **avant** d'engager le coût de la conversion.
2. Appeler `C2P_SetContextParameter(context,CHUNKY=4,Start(Bank))` sur **chaque appel**, même si le pointeur est identique. Le SDK v1.9 permet ce changement sur un contexte déjà initialisé ; **retour de l'appel = 0 si succès**.
3. Appeler `C2P_Chunky2Planar(context)` (LVO `-90`), dont **`D0=0` signifie succès**. Le résultat est écrit dans le bitmap **intermédiaire Chip** détenu par le contexte de `Open`. N'écrire dans aucun bitplane d'Intuition à ce stade.
4. Récupérer/vérifier le bitmap interne avec `C2P_GetContextParameter(context,BITMAP=5)`. Utiliser `graphics.library` et non des copies directes des planes pour la destination :
   `BltBitMap(C2PBitMap,0,0,BackBitMap,0,0,320,256,$C0,$FF,NULL)`.
5. La copie simple emploie le minterm **`$C0`** et le masque **`$FF`**. Le retour de `BltBitMap` doit être **Depth (4..8)** — **pas systématiquement 8**. Appeler `WaitBlit` **même si la fonction a annoncé moins de plans**, car le matériel a pu commencer à copier.
6. Après `WaitBlit`, retourner **1** si les `Depth` plans sont traités ; sinon **0**. Le buffer frontal, la palette et les états `Front/Swap` ne sont pas modifiés par la commande.

**Important sur les échecs :** toutes les erreurs détectées **avant le BltBitMap** laissent le back buffer inchangé. Si `BltBitMap` démarre puis signale un nombre de plans insuffisant, le back peut être **partiellement modifié** ; il faut attendre `WaitBlit`, retourner `0` et **ne jamais effectuer de Swap automatique**. Ne pas promettre une transaction graphique atomique que l'API OS ne garantit pas.

## 4. Mémoire, ressources et cycle de vie

- **Un seul contexte et un seul bitmap Chip interne** conservés de `Open` à la fermeture ; **aucune allocation de contexte par frame** et aucun bitmap C2P par buffer Intuition. C'est l'architecture autorisée après l'abandon du relevé GDB.
- La banque chunky peut résider en **Fast RAM** : le CPU de `c2p.library` la lit ; le Blitter ne travaille qu'entre deux `BitMap` en **Chip RAM**.
- `Convert` n'acquiert **aucune nouvelle ressource persistante**. Le nettoyage automatique **`Aga Screen Close` / sortie AMOS** de R74 reste propriétaire du contexte ; toujours `WaitBlit` avant `DestroyContext`.
- `Aga C2P Close` est un **jalon différent non approuvé**. L'absence de cette fonction en R75 envisagée n'empêche pas la fermeture automatique R74.

## 5. Tests exigés avant publication d'une candidate native

**Gate A CPU/AP20 :** syntaxe/signature et ABI D3/D2/A3, refus sans contexte et après `Screen Close`, CPU000 refusé, état de profondeur modifié, banque effacée/réallouée/déplacée, taille insuffisante, back/front non confondus, retour `0` quand Safe pas prêt, bonne reconnaissance de `ScreenBuffer+0` (et rejet du `+4`), un seul appel `GetMsg`, pas de `ReplyMsg`, erreurs `SetParameter` / `Chunky2Planar` / nombre de plans blités, appel obligatoire de `WaitBlit`, canaries et branches relogeables Compiler V2.

**Gate B réelle WinUAE/AMOS interprété :** **un seul ASC actif** remplacera `tests/current/C2P_R74_OPEN_01.asc` ; prévoir mire 8 bits définie dans la banque, **cinq profondeurs** 16/32/64/128/256 couleurs, au moins **deux images et deux swaps** par profondeur, comparaison de couleurs/positions, refus lorsque Safe indisponible, refus après fermeture, mémoire Chip avant/après, `RESULT 1` / `CLOSE RETURNED`. Pas de GDB ni de PowerShell.

**Gate C Compiler :** attendre l'intégration du jalon C2P retenu et faire **un seul nouveau test compilé global** à la fin, conformément à `EXTENSION_SOURCE_RULES.md` ; pas de compilation répétée pour chaque fonction. **Gate D matériel** toujours séparée.

## 6. Sources vérifiées

- SDK **`c2p.library` v1.9** fourni par l'auteur : `sdk/C/c2p_context.h`, `sdk/fd/c2p.fd`, `sdk/docs/c2p.autodoc`, `sdk/docs/howto.txt`, `src/c2p_context.c` : `CHUNKY=4` modifiable après initialisation, `BITMAP=5`, `Chunky2Planar` retour 0 si succès, allocation Bitmap Chip avec `TYPE=1`.
- AmigaOS 3.x : [`struct ScreenBuffer` officielle](https://amigadev.grimore.org/Includes_and_Autodocs_3._guide/node0602.html) et [`graphics.library/BltBitMap`](https://developer.amigaos3.net/autodocs/graphics.library/BltBitMap.html) : masque, minterm, nombre de plans retournés et `WaitBlit`.
- Extension existante : `tools/c2p_r74_open_emit.py` et `src/generated/AMOSPro_AGA_R57_C1_NATIVE.s` (DBState, sélection du back, états Safe/Disp, ScreenBuffer+0), [Gate B réelle R74](C2P_R74_WINUAE_GATE_B_2026-11-14.md).

**Décision : contrat validé le 14/11/2026, code natif implémenté et testé Gate A.** Voir [bilan technique R75](C2P_R75_NATIVE_GATE_A_2026-11-14.md). L'exécution de l'ASC R75 sous WinUAE reste la Gate B à effectuer. `Aga C2P Close` n'est ni approuvée ni développée.
