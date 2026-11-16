# M19 P0f — Identité de banque AGBO par Bob : Gate A MC68020

**16 novembre 2026.** Dépôt unique **`anthea176/AMOSPro-AGA-Extension`**, branche **`main`**. Cible native **MC68020/68EC020 minimum**.

## Résultat : la commande expérimentale Aga Bob utilise la banque vérifiée

Le premier palier natif **P0f source-only** vérifie et mémorise l'identité de la banque source de chaque Bob au moment de sa définition, indépendamment de la banque sélectionnée ensuite. **Ce n'est pas une bibliothèque installable.** Le premier `Aga Bob Draw` et le nettoyage au callback `End` n'existent pas encore.

- [Émetteur du cachet d'identité](../tools/m19_p0f_bank_stamp_emit.py) : deux entrées privées `stamp_capture` et `stamp_verify`, chacune avec contrôle CPU020, `TypeOfMem`, service réel source-audité **`Bnk.GetAdr`** (mocké en Gate A), header DATA AGBO v1, limites d'allocation, génération et identité de `Cur_Banks`. Enregistre **16 octets** par identité : adresse payload, génération AGBO (+24), pointeur de la liste AMOS, taille payload. Vérifie la même banque indépendamment de `bank_active_state`. **Aucune réserve de banque, allocation Chip, modification de sélection ni DMA.**
- [Banc identité](../tools/test_m19_p0f_bank_stamp_native.py) : **50 cas MC68020 PASS** sur deux implantations ; banque absente/vide, deux banques, changement de génération/taille/liste, Erase, remplacement après recapture, vérification avec une autre banque sélectionnée, ABI et garde CPU.
- [Émetteur par objet](../tools/m19_p0f_object_identity_emit.py) : **64 cachets de 16 octets**, à côté du registre Bob original (qui reste à 24 octets/objet). `identity_bind` valide et capture d'abord le cachet sur une pile privée, appelle ensuite **l'ancien `object_put` source-pinné**, puis publie le cachet si et seulement si l'insertion réussit. `identity_check` refuse un Bob inactif ou une banque remplacée, et ne recopie les 24 octets du Bob au destinataire que si tout est valide. `identity_clear` efface les cachets, encore **privé et non relié à Close/End**.
- [Banc natif transactionnel](../tools/test_m19_p0f_object_identity_native.py) : **44 cas CPU020 PASS** sur deux implantations. Les échecs ne modifient ni l'ancien objet ni son cachet ; la désactivation et le reset rendent le cachet inatteignable via `identity_check`.
- [Raccordement public source-only](../tools/build_m19_p0f_public_bound_in_memory.py) : modifie **seulement deux octets** de l'immédiat du relais `put_selected` dans BOBS pour que **`Aga Bob N,X,Y,I`** appelle désormais `identity_bind` en AGA. Les 83 commandes historiques P0d, le Blitter Safe/Chip, le callback End P0d, `Aga Bob Off` et le wrapper `Aga Screen Close` restent inchangés. Le builder original P0e, sans ce paramètre, reste byte-exact.
- [Banc de la commande expérimentale](../tools/test_m19_p0f_public_bound_native.py) : **40 cas CPU020 PASS**, deux placements AGA/BOBS différents, vraie initialisation AGA source-pinnée, création/déplacement, changement des banques 10/11, Off, garde CPU, valeurs invalides, preuve qu'une mutation du contenu AGBO provoque un refus au prochain contrôle. Le vrai AMOS Compiler et la DMA sont **simulés/non testés**.

## SHA et limites AP20

| Jalon (en mémoire uniquement) | Taille | SHA256 |
| --- | ---: | --- |
| P0e split + reset Close (source inchangée) | 94 532 | `8185ae2d056da209a88c0b91e315d1cbb97acabadf7b55352e8cd7a348c1b207` |
| P0f banque : cachet natif privé dans AGA | 95 236 | `817bc44cb7aee2e7aae106929f0116012dddc2386f083f1c102e331c7c7cb8c6` |
| P0f 64 cachets transactionnels privés | 96 756 | `c0af63868fcca9f719b5a160a2394a6e15d4404c3890317cd08ef9efad6ca0c7` |
| **P0f commande Aga Bob reliée** | **96 744** | **`6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45`** |

Les deux derniers binaires ont des titres de provenance différents, d'où des tailles totales différentes : le code AGA/BOBS reste celui produit par les builders. **85 commandes / 95 entrées AP20**, plus grande distance interpréteur **32 576**, **190 octets** de marge PC16, groupe AGA **61 604 octets**, sous la limite V2 de 65 534. Aucun token `Draw` supplémentaire.

[CI M19 Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43971958606) : **PASS**, tous les tests historiques P0d/P0e et les nouvelles sources P0f ; [politique CPU et chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43971958546) : vérifier statut de run courant. **Gates B Runtime WinUAE, C vrai AMOS Compiler et D matériel P0f NON TESTÉES.**

## Limites de sécurité explicitement non résolues

1. **ABA mémoire :** vérifier `payload_ptr + génération + Cur_Banks + taille` refuse les remplacements courants, mais **ne peut pas prouver** qu'une allocation n'a pas été effacée puis réallouée à **exactement la même adresse avec la même génération**. Un jeton d'époque contrôlé par les mutations de banques ou un contrat de chargement explicite est nécessaire pour une garantie stricte.
2. **Image existante :** le contrôle de banque prouve l'intégrité globale de base, mais `identity_bind` n'inspecte pas encore la présence de l'ID d'image exact. Le futur Draw doit continuer d'utiliser le validateur AGBO **par image** de P0d et refuser sans DMA les IDs absents.
3. **Draw/Blitter :** `identity_check` est privé. Le futur `Aga Bob Draw` doit d'abord parcourir les objets et distinguer les inactifs des actifs périmés, puis dessiner dans le **back buffer Safe** en réutilisant le staging Chip par banque, sans Swap implicite ni création de banque absente. Les copies mémoire doivent être synchronisées avant `Erase/Load`.
4. **Screen Close / End :** l'ancien reset P0e de `Aga Screen Close` rend les objets inactifs, donc les anciens cachets sont inatteignables, mais **n'efface pas encore la table des cachets**. Le callback `End` P0d est déjà installé après préparation Chip : ajouter un second hook concurrent le ferait refuser. Il faut une intégration source unique et vérifiée, jamais écraser les slots d'un autre hook. **Ne pas installer P0f avant cette correction.**

## Protections

- **Seule bibliothèque active P0d :** `dist/AMOSPro_AGA.Lib`, 91 300 octets, SHA256 `bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be`, déjà validée en Runtime/Compiled **sur sa propre campagne**.
- **Un seul ASC actif** : `tests/current/M19_P0D_BOB_BLIT_01.asc`, non modifié.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, **intacte**.
- Aucun changement de branche, aucun ZIP, aucune publication ni bascule de candidate.
