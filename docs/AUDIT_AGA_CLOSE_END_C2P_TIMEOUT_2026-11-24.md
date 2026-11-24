# Audit P2d — passage 14 : Close/End, destruction C2P et sortie sur timeout

**24 novembre 2026 — main uniquement — source examinée `acbcb8fdacff7207071f34e221184204309ec5b0`.** P2d LAST_GOOD 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f` (identité documentée, non recalculée ici). S1-P1e gelée. Analyse statique uniquement ; aucun essai ni correctif.

## 1. Liaison effective des deux chemins natifs

Le [master UNIT142](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P2D_UNIT142_EDITABLE.s) inclut les modules ci-dessous. L'initialisation [INIT](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_INIT_ENTRY_MC68020.s) publie State à +456(A5) et les deux vecteurs End à +460/+464.

- Close public AP20 182 → trampoline B8 → reset B7-m2 → guarded_close_entry → screen_close_bridge_entry, qui vérifie le prologue à State+$638 puis l'appelle. Voir [pont P0](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P0_SCREEN_PRECLOSE_MC68020.s). [Target head](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_TARGET_HEAD_MC68020.s) branche vers $001DE : BSR $001EE puis branche $0012A.
- End historique : [entrée Core](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_ENTRY_MC68020.s) → [BRA target](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_MAIN_BRA_TARGET_MC68020.s) → $001E6 : BSR $001EE, puis [BRA core wait](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_TARGET_BRA_WAIT_MC68020.s) → $00190. [Source des deux branches et attente](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_TARGET_WAIT_MC68020.s).
- Les deux voies passent donc **réellement** par le [même helper C2P $001EE](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_TARGET_AUX_MC68020.s), avant leur boucle Safe/Disp. Cela complète le passage 10, qui s'appuyait en partie sur l'émetteur historique.

## 2. Ordre réel et conséquences d'un timeout

Le helper C2P valide DBState et cookie C2P1 à +40, sauvegarde Context (+28) / LibraryBase (+24), efface cinq longs +24..+40 avant appels destructifs. Si LibraryBase est présente, WaitBlit si graphics.library disponible, DestroyContext SDK (-60) si contexte présent, CloseLibrary Exec (-414). Le code n'efface pas la banque AMOS chunky ; correspond au [contrat R77](C2P_R77_CLOSE_CONTRACT_2026-11-14.md).

Les deux boucles Safe/Disp (Target et Core) ont 301 évaluations au maximum, jusqu'à 300 WaitTOF si la bibliothèque graphique est disponible. Une notification acquise efface son bit, pas nécessairement l'autre. Si la condition n'est pas satisfaite, retour direct par l'épilogue ; aucune fermeture Window/Screen, aucune libération DBState/ports sur cette branche. **Mais C2P a déjà été nettoyé**. La fermeture n'est pas atomique en cas d'échec de SafeWait : état résiduel possible écran/DB vivants avec C2P absent.

Ce résultat ne prouve ni une fuite ni une double destruction : le nettoyage C2P préalable et la remise à zéro avant Free sont des protections voulues. B7-m2 prévoyait déjà le reset des slots Bob *avant* Close, même si Screen reste ouvert ([rapport historique](M19_B7M2_CLOSE_RESET_GATE_A_2026-11-18.md)). Il ne faut pas imposer artificiellement un rollback intégral ni considérer le frame comme présentable après refus. AGA-004 reste VM ; AGA-013 (Close returned) reste défaut de couverture confirmé.

## 3. Nettoyage conditionnel après Close

[Guarded Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P1B_FRAME_GUARD_MC68020.s) ne remet à zéro le frame guard propriétaire qu'après contrôle de State et Screen nul. [P2b cleanup](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P2B_CLEANUP_MC68020.s) conditionne également la purge de ses 64 slots/cache à l'identité et à l'écran fermé. [P2d Close](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s) conserve le mode Auto si Screen existe encore. [B7 End](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_B7_END_MC68020.s) réarme ses deux vecteurs si Screen subsiste, sous les gardes visibles. Le callback B8 a sa propre condition de retour et de réarmement : ne pas déduire que tous les sous-systèmes ont le même état après refus.

Sur le chemin de succès, [cleanup Core](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_CLEANUP_MC68020.s) / [Target head](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_TARGET_HEAD_MC68020.s) libèrent buffers, ports et DB avant fermeture Screen ; le helper font/CloseScreen [52CA](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/acbcb8fdacff7207071f34e221184204309ec5b0/src/native/m19_p2d/M19_UNIT142_R83_HELPER_052CA_MC68020.s) appelle Intuition -66, puis le chemin appelant efface Screen sans contrôle D0 visible. Si un refus OS est injectable, vérifier explicitement cet état ; pas de refus OS reproduit ici. Ne pas conclure qu'un Screen nul prouve à lui seul la disparition de l'objet OS.

## 4. T14 : discriminer les trois états, sans ajouter de scénario

| Cas | Attendu à vérifier |
|---|---|
| Safe/Disp arrivés dans le budget | C2P détruit une fois, DB/Window/Screen nettoyés, owners/callbacks cohérents |
| Safe ou Disp reste pending | écran/DB préservés, C2P déjà absent, aucun free prématuré des buffers ; noter slots et vecteurs réellement conservés |
| Deuxième Close après réception tardive | terminaison propre sans double DestroyContext/CloseLibrary, allocations équilibrées |
| End-only puis relance | vérifier callbacks réarmés en cas de refus ; établir ce que l'hôte AMOS appelle réellement ensuite |
| Refus OS simulé de CloseScreen | distinguer Screen pointer cleared et véritable ressource OS libérée |
| C2P Close puis Screen Close/End | banque chunky conservée et pas de seconde destruction SDK |

Contrôles Gate A d'abord (OS/DMA simulés), puis B/C autorisées. Les résultats historiques R83 B/C avec deltas Chip/Fast nets nuls restent valides pour [leur seul scénario](C2P_R83_WINUAE_RUNTIME_COMPILER_2026-11-14.md), pas pour le timeout P2d combiné B8. **Aucune Gate nouvelle.** Aucun fichier natif, test, binaire ou journal changé.

## Addendum Runtime L2b

T10A Runtime PASS sur L2b : 5/5 cycles, 5 refus READY sans mutation, 5 Free CLEAN, 5 Free répétés sans effet, 5 réactivations, 5 conservations DATA octet pour octet, 30 pixels, 25 Update/30 Swap, 1 VBL de reprise, 0 retry Capture/Fill. FREE_CHIP_GAIN_MIN=264, 5 Close B8 actifs, Mouse X=-1. Chip Free=1791304, Fast Free=138105688 aux 5 mesures après Erase ; CHIP_LOSS=FAST_LOSS=DIFF_CYCLES=0, MEM_STABLE=1. RESULT 1 ERR 0. Pas de preuve de refus interne release forcé, DIRTY forcé ni ABA. AGA-014 reste à qualifier en injection native ; aucune modification native requise sur le chemin normal. [Preuve](evidence/T10_BANK_RUNTIME_PASS_L2B_2026-11-24.TXT). [T14B/T16A](../tests/proto/l3_integrated/README.md) prépare C2P et Copper actifs à la fermeture normale. End et timeout non exercés par ce banc.
