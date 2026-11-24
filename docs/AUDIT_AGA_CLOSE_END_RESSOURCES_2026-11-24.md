# Audit P2d — passage 10 : Close/End, callbacks, ports et validité des preuves de nettoyage

**24 novembre 2026 · `main` uniquement · source contrôlée `47aa2934beb6d14eb2fa77a19285fc933c595e41`.** Audit statique sans modification de code, de tests ni de bibliothèques. La candidate S1-P1e Sprite reste **GELÉE**. La référence de diagnostic reste P2d LAST_GOOD (136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`).

## 1. AGA-013 — `CLOSE_RETURNED=1` est un témoin de retour de contrôle, pas un audit de libération

Le [banc officiel P2](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/tests/current/M19_P2_ALL_IN_ONE.asc#L681-L711) effectue :

```amos
If _OPEN=1
   Aga Screen Close
   _CLOSE_RETURNED=1
   Amos To Front
End If
```

Le champ `CLOSE_RETURNED` est **positionné immédiatement après l'instruction `Aga Screen Close`** ; il ne lit **ni** l'état du Screen propriétaire, **ni** le `DBState` ou une valeur de retour API (Close est une instruction), **ni** les compteurs Alloc/Free, **ni** les callbacks ou les ports Safe/Disp. Par construction, ce champ confirme **uniquement que la ligne après Close a été atteinte**.

Les [journaux originaux B/C](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT) et [Compiler](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT) restent authentiquement **PASS de ce scénario** ; leur `CLOSE_RETURNED 1` **ne démontre pas** l'absence de fuite, de port non libéré, de double Free différé ni de vieux owner/callback après réouverture.

**Classement AGA-013 : P2 — défaut de couverture de l'oracle de test, confirmé dans l'ASC**, sans anomalie de fermeture native prouvée. Ne pas modifier l'ASC gelé pour améliorer artificiellement ce résultat. Enrichir les critères de T14 avant de produire une future sonde autorisée.

## 2. Le chemin natif de fermeture est réel, même sans root B8

- `Aga Screen Close` AP20 182 → BOBS+$0718E : [trampoline](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_B7_B8_DRAW_BRIDGE_MC68020.s#L163-L192) appelle d'abord `b7m2_close_reset_entry`, puis, si nécessaire, le callback B8. Un root B8 nul **n'évite pas** le Close historique.
- [`b7m2_close_reset_entry`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_B7_B8_DRAW_BRIDGE_MC68020.s#L97-L110) relaie le reset et `guarded_close_entry`. [`screen_close_bridge_entry`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_P0_SCREEN_PRECLOSE_MC68020.s#L66-L107) valide la cible native ancienne et appelle le Close après préfermeture du registre.
- [`L_LEGACY_CLOSE_CORE_001A6`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_SAFEWAIT_MC68020.s#L14-L68) consulte Safe/Disp, acquitte `GetMsg(-372)`, effectue au plus **301 évaluations** de sa condition de sortie, avec attente `WaitTOF(-270)` entre essais. **L'attente sur cette branche est bornée**, mais son délai réel et les autres chemins OS ne le sont pas automatiquement.
- [`L_LEGACY_CLOSE_CORE_00066`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_CLEANUP_MC68020.s#L6-L72) libère/ferme des ressources selon pointeurs non nuls et remet plusieurs champs d'état à zéro. Le simple fait de rencontrer des appels Free ne prouve pas leur correspondance 1:1 avec toutes les allocations dans toutes les erreurs.

**Limite :** l'entrée exacte est bien retrouvée et le code des gardes/Free visible ; **aucune trace Runtime ne démontre un retour au même niveau de Chip/Fast libre pour chaque combinaison de ressources**.

## 3. Drain de messages IDCMP : sortie sur port vide, sans compteur fixe dans cette boucle

Le [bloc `L_LEGACY_CLOSE_CORE_0012E`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_UNIT142_R83_CLOSE_CLEANUP_MC68020.s#L73-L97) dépile les messages d'un port par `GetMsg(-372)`, répond à chacun via `ReplyMsg(-378)`, puis continue jusqu'à `GetMsg=0`.

Il s'agit d'une **vidange non bloquante d'une file** : si la file est finie et cesse d'être alimentée, elle termine. Contrairement à la boucle SafeWait, **aucun nombre maximal d'itérations n'est prévu à cet endroit**. En présence d'un producteur qui réalimente sans interruption, le délai total n'a pas de borne établie par ce seul code ; **ce n'est pas une reproduction d'un freeze**, ni une justification pour supprimer les `ReplyMsg`.

**Statut : P2 de validation de latence/charge, non anomalie Runtime confirmée.** Couvrir dans T14 le port vide, une file finie et une injection de messages pendant la fermeture sur **Gate A simulée** ; aucune injection sur Amiga physique sans protocole sûr.

## 4. End et callback B8 : ordre et chemins de repli, pas de garantie globale

- [`M19_P0C_PROGRAM_END_CALLBACK_MC68020.s`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_P0C_PROGRAM_END_CALLBACK_MC68020.s#L8-L55) contrôle le pointeur et la signature du code source, vérifie le callback program-end installé, puis appelle `screen_preclose_entry` ; en cas de refus, quitte **sans supposer** que les ressources ont été purgées. En cas de succès, rétablit les callbacks antérieurs et exécute le Close natif.
- [`M19_B8_END_REGISTER_MC68020.s`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_B8_END_REGISTER_MC68020.s#L10-L55) valide les deux vecteurs AMOS End, restaure temporairement la cible B7, appelle le callback B8 seulement pour le propriétaire courant ; efface le root **uniquement sur succès de son callback**. Une voie `b8_b7_end_pending` réarme les vecteurs si la libération est refusée.
- [`p2d_close`](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/src/native/m19_p2d/M19_P2D_CONTROLS_MC68020.s#L156-L178) n'efface le mode Auto que sous des conditions d'identité/état, afin de ne pas casser un autre propriétaire ; **ne pas l'interpréter comme une fuite ou un reset garanti sans suivre la branche réellement empruntée**.
- Les [hooks historiques R74 C2P](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/tools/c2p_r74_open_emit.py#L173-L209) ont été conçus pour libérer le contexte avant le DBState, en vidant d'abord les champs owner et en appelant `WaitBlit` puis `DestroyContext`/`CloseLibrary`. [R77 Close explicite](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/47aa2934beb6d14eb2fa77a19285fc933c595e41/tools/c2p_r77_close_emit.py#L18-L51) respecte le même principe. **Le raccordement exact de tous les hooks à la P2d et leur couverture End/échec/Close restent à contrôler sur le binaire effectivement assemblé**, la documentation historique ne suffit pas.

**Conclusion :** plusieurs garde-fous de propriété et de retour d'échec sont **visibles statiquement**. Le cycle Close/End **n'est pas validé globalement** ; AGA-004 demeure VM.

## 5. Critères précis pour compléter T14, sans modifier le banc gelé

| Séquence de future sonde (non exécutée) | Critère de validation requis | Cause de FAIL |
|---|---|---|
| Close **sans B8**, après simple Open/DB | Retour au programme **et** écran/DBState libérés, ports Safe/Disp vides ou correctement détachés ; deuxième Close sans corruption | Un retour de contrôle seul est insuffisant |
| Close avec **B8 et callback End**, puis Open | Propriétaire/epoch/pools/snapshots remis à zéro ; aucun ancien pointeur de page réutilisé comme ressource vivante ; allocations/free équilibrées | Root B8 stale ou double Free |
| Close avec **C2P actif**, puis C2P Close/End | Contexte SDK détruit **une seule fois**, Chip bitmap libéré, banque chunky AMOS conservée si son contrat le prévoit | Contexte double-détruit ou fuite |
| Close avec **Copper/Font/IDCMP**, y compris retrait OS refusé | Liste Copper/Font/port propriété contrôlée, récupération sans attente non bornée, ownership conservé sur refus | Liste détachée mais vivante, police dangling, messages perdus |
| Safe pending jamais livré / file de messages alimentée pendant Close | Gate A : vérification du **budget d'attente Safe** et de la **terminaison de la vidange IDCMP** sous producteur contrôlé | Boucle interminable ou fermeture forcée avec DMA/port encore actif |
| Réouverture **même adresse OS éventuelle** | Identification par génération/owner et disponibilité mémoire, non simple égalité de pointeurs | ABA et réutilisation d'ancien état |

Instrumentation : **protocole d'injection validé, après autorisation**. Pour les futurs journaux B/C, enregistrer identité de la Lib réellement installée, `PRG_STATE`, résultats des deux ScreenBuffers, allocations Chip/Fast avant/après, nombre de callback invokes, et un identifiant unique de programme. Ne pas lire de pointeurs arbitraires sous AMOS.

## 6. État et gel

**Anomalie nouvellement classée : AGA-013 P2 (oracle de fermeture insuffisant) — preuve ASC**, pas défaut du moteur natif. La vidange IDCMP et les callbacks restent **validation manquante**, sans bug/crash avéré. Les logs P2d B/C de novembre sont **conservés comme PASS du banc intégral seulement**.

**Aucun nouveau test/compilation/émulation**, aucune modification de code natif, binaire, journal, ASC ou branche. **S1 Sprite GELÉE, P2d LAST_GOOD intacte.**

[Rapport transversal](AUDIT_TRANSVERSAL_AGA_2026-11-23.md) · [Registre de preuves](AUDIT_AGA_PREUVES_ET_CLOTURE_2026-11-24.md) · [Cahier des 19 tests](AUDIT_AGA_MATRICE_TESTS_2026-11-23.md).

## Addendum — L3 groupé Runtime L2b

Banc groupé T10B/T14B/T16A Runtime PASS sur L2b : 4/4 cycles, FAST_REFUSED=AGPC_OK=4, PIXELS_OK=24, CACHE_CHIP_MIN=384, C2P_OK=C2P_EXPLICIT=C2P_AUTO=4, COPPER_ON=4, COPPER_OFF=COPPER_AUTO=2, 4 Swaps/Close, aucun retry Capture/Swap, banques préservées 4/4, Mouse X=-1. Chip Free=1791304, Fast Free=138087696 aux quatre mesures après Erase ; CHIP_LOSS=FAST_LOSS=DIFF_CYCLES=0, MEM_STABLE=1, RESULT 1 ERR 0. Chemins normaux qualifiés ; aucun contrôle visuel de raster Copper ni injection OS, aucun Erase/Load ABA, aucun callback End testé. [Preuve](evidence/L3_FINAL_RUNTIME_PASS_L2B_2026-11-24.TXT). Journal original 682 octets, 36 CRLF, SHA256 `51d7d18e495dd56cbf9e66bf166fe8ac469e541d974c98a18f6bb64d47ad84b4`, blob `2e2f8af9259ae61846c9480d4853a24e2f1109c6`. [T14C](../tests/proto/l3_end/README.md) préparé : End/Font et réouverture ; injections/ABA non clos.

## Addendum T14C Runtime L2b — 24/11/2026

T14C Runtime L2b : RUN1 ERR0, PREP/FONT/BOB/C2P/COPPER_OK=2, CLOSE_OK=1, END_READY=1, RESULT=0 volontaire, READY_FOR_END. RUN2 RESULT1 ERR0, POST_END_OK=1, PREP/FONT/BOB/C2P/COPPER/CLOSE_OK=1, CLOSED_MOUSE_X=-1, zéro reprise Swap. Banques 12/24 de 81920/328 octets retrouvées avec marqueurs valides, puis Erase et réouverture réussis. Les journaux sont cohérents avec deux lancements consécutifs sans redémarrage (protocole demandé ; absence de redémarrage non instrumentée). Dans RUN2, Chip/Fast après End puis Close témoin sont exactement 1791304/138086736. RUN1 Close témoin : 1791304/138087336 ; delta inter-run Fast 600 octets, cause non mesurée (journal RAM et environnement Runtime), pas de fuite démontrée. T14C PASS du scénario, aucun correctif natif requis. Font système par retours, pas de pixel font/BankFont ; Copper sans oracle visuel ; pas de faute OS injectée, ABA ni inventaire Alloc/Free exhaustif. [BEFORE](../docs/evidence/T14_END_BEFORE_RUNTIME_L2B_2026-11-24.TXT) : 465 octets, 26 CRLF, SHA256 `4fc7b2a8c1b59df17e4ad6ea04a4ded3b9167fe03985803dcaa8fbb99762043c`, blob `e661eb7bf89d63daf2ae3edd38cd469d5fcfd806` ; [AFTER](../docs/evidence/T14_END_AFTER_RUNTIME_L2B_2026-11-24.TXT) : 476 octets, 26 CRLF, SHA256 `1abd067b1a9eb545eeea6471f863b726b0364e9dda56f59de9a2db1b9c54ce5c`, blob `38fef4ad93b53e3fc75e0504119c7bb744bdd4b2`.
