# Passage 19 — B8 : transitions, propriétaires et récupération

**24 novembre 2026 — passage 19/21 · branche main uniquement · source figée [31455a5](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/31455a52ab497fc49131e48520642ad74899e436).**

P2d LAST_GOOD = 136 020 octets, 100 commandes / 203 entrées AP20. S1-P1e active = 142 000 octets, 102 commandes / 208 entrées AP20, gelée. Identités SHA256 documentées dans le [rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md), non recalculées lors de cette lecture. **Audit statique de la source liée : aucun rebuild, test, changement de Lib, correctif, ni nouvelle Gate.** VM = validation manquante.

## 1. Chaîne Swap et états

[M19_P2D_CONTROLS_MC68020](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s) : Auto ne change que depuis CLEAN, vérification owner State/Screen, passage direct au Swap si root absent et aucun Bob actif, sinon Update et éventuel premier Bind.

[M19_P1B_FRAME_GUARD_MC68020 L206-L295](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P1B_FRAME_GUARD_MC68020.s#L206-L295) : garde Swap distingue CLEAN=0, DIRTY=1 et READY=2 ; READY exige la même identité A5/State/DBState/index/Screen, DIRTY refuse ; l'état n'est remis à CLEAN que si la présentation retourne succès. READY n'est pas une permission d'écrire sur la page avant.

[M19_P2D_SERVICE_BODY_MC68020 L1402-L1598](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_SERVICE_BODY_MC68020.s#L1402-L1598) : Bind attache le pool à une identité, génération non nulle, bits valid par page physique ; échec capture invalide le fond concerné ; release sous contrôle du propriétaire et de la libération.

| Transition | Source / conséquence |
|---|---|
| Clear | [M19_P2D_SERVICE_GUARDS_MC68020 L255-L527](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_SERVICE_GUARDS_MC68020.s#L255-L527) : E102 arme DIRTY avant restauration ; après réussite cleared par page et retour CLEAN, pending réinitialisé. Un refus ne doit pas être assimilé à Clear réussi. |
| Début Update | E1E0 : si fond valide et pas cleared, restaure l'ancien décor ; capture du nouveau fond, garde page/epoch de transaction. |
| Fin Update | E3C4 : page/epoch, READY et valid contrôlés ; cleared et pending consommés. |
| Échec Update | E4C8 : DIRTY et pending annulé ; distinguer échec précoce sans mutation et échec après armement. |
| Acquisition système | [M19_P2D_SYSTEM_SERVICE_MC68020 L106-L138](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_SYSTEM_SERVICE_MC68020.s#L106-L138) : GetMsg Safe, effacement du seul bit0, WaitBlit, sélecteur. |
| API publique | [M19_P2D_PUBLIC_UPDATE_MC68020 L61-L195](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31455a52ab497fc49131e48520642ad74899e436/src/native/m19_p2d/M19_P2D_PUBLIC_UPDATE_MC68020.s#L61-L195) : premier Bind et enregistrement, release sur échec d'enregistrement ; Clear possède jusqu'à trois WaitTOF de reprise après premier refus sous préconditions (owner, fond valide, Safe pending). Maximum quatre tentatives sur ce chemin ; tous les refus ne sont pas retryables. |

## 2. AGA-002 maintenue, AGA-003 non transformée en bug

Le premier Swap **sans Bob** peut réussir après Double Buffer neuf. Il arme Safe/Disp (DB+20=3). Puis premier Bob/Update automatique, root encore absent : le sélecteur initial peut refuser parce que Safe pending avant même de dépiler le message disponible. Wait Vbl seul ne consomme pas le message. L'acquisition système après Bind ne résout pas ce problème d'amorçage. Voir [passage 11](AUDIT_AGA_AMORCAGE_DOUBLE_BUFFER_B8_2026-11-24.md) et [passage 13](AUDIT_AGA_SAFEPORT_WRITERS_2026-11-24.md).

**P1 structure conditionnelle confirmée ; aucun freeze CPU ou ERR15 RPG attribué automatiquement à ce chemin.** La correction proposée doit acquitter Safe avant sélection/copie de fond, sans effacer Disp, sans présenter une page DIRTY et sans forcer un root artificiel lors du premier Swap sans Bob.

Le contrat P2d reste Clear réussi → décor → Update/Swap. Les bits cleared/valid justifient que la simple écriture de décor hors contrat ne suffit pas à établir AGA-003. AGA-003 = VM de la séquence légale.

## 3. Qualification T01/T02/T03/T05/T08/T17/T18

- Racine absente/présente, Safe absent/arrivé/acquitté, deux identités de page, défaut d'allocation/enregistrement. Relever motif précis du retour au lieu d'un compteur unique.
- Injecter échec avant capture, après DIRTY, avant READY et refus ChangeScreenBuffer après READY. Vérifier qu'aucun Swap ne publie une page incomplète et qu'un READY refusé reste prêt à présenter sans redessiner.
- Tester Clear avec et sans fond valide, reprise bornée et restauration du nouveau décor sur les deux pages. Observer CRC des plans et non seulement RGB du ColorMap.
- Rejouer RPG et variantes EDGE sans réécrire leur oracle. ERR15 est l'épuisement de la reprise dans l'ASC, non un code moteur discriminant.

**Bilan :** protections et transitions locales retracées ; AGA-002 reste la cible de correction P1, AGA-003/004/008 restent VM. Aucun nouveau test ni modification de la machine d'états.
