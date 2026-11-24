# L3 — T10A AGBO Bank Free et mémoire B8

24/11/2026, candidat P2d-L2b inchangé (136708 octets, SHA256 `a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc`, blob `2809b4b409eea9e234df1b96bf2b08bd393d8c85`). LAST_GOOD P2d protégée. [ASC](T10_BANK_MEMORY.asc), 8300 octets ASCII LF, SHA256 `114d4bb2b041a6ee8f490243a52c49df8cfbbae5e228513cf6a7f8b4fb11ee09`, blob `9141bfdd859980d2a7e6db948ea750fe95b342ba`. Préflight local amos_preflight.py PASS sur les octets exacts ; Gate B NON TESTÉE. Aucun patch natif, pas de modification de l'ASC courant ni de Compiler.

Même WinUAE 68030/JIT ON/AGA PAL, projet vierge, Merge ASCII, Runtime. Banques **24, 25 et 27 libres**. Aucun fichier externe ni AMCAF. Journal RAM:T10_BANK_RUNTIME.TXT.

## Protocole

Une itération d'échauffement + quatre mesurées. Open/DB, capture de deux images AGBO 16x16 opaques (165 et 90), deux fonds unis 17, slots Bob 1 (banque24,96,100) et Bob 2 (banque25,160,100). Contrôle du nombre d'images et taille <=1024, copie de chaque octet DATA dans un tableau réservé avant les mesures. Pas de modification de banque pendant la transaction.

1. Update manuel, frame READY. Appel Bank Free 24 : doit être refusé (instruction sans retour), les deux getters doivent rester valides, Chip/Fast et tous les octets des deux banques identiques.
2. Après Swap réussi (CLEAN), Bank Free 24 : getter du Bob1 absent (-32769), Bob2 intact, banques DATA inchangées ; relever le gain Chip libre. Deuxième Free : mêmes slots/banques, aucun nouveau delta Chip/Fast.
3. Deux Update/Swap avec le seul Bob2. Lire par capture CBlock CPU 8x1 sur le back (ancienne page affichée), d'abord la frame antérieure à Free (165/90), puis la frame avec seul Bob2 (17/90).
4. Resélectionner 24 et SET Bob1 ; deux Update/Swap, pixels 165/90. Fermer avec Bobs et deux fonds B8 actifs ; Mouse X=-1 et les deux banques DATA toujours byte-identiques. Erase seulement les banques initialement libres, jamais si Close ne confirme pas la fermeture. Relever Chip/Fast après chaque cycle avant écriture du journal.

Source API : README.fr.md, contrat M19_P0_BANK_FREE_GATES_2026-11-20.md ; séquences Get/Update/Swap et oracle CBlock de M19_P2_ALL_IN_ONE.asc et du banc historique B8. Contrôles natifs de READY/CLEAN dans M19_B8S1_BANK_FREE_MC68020.s et M19_P1B_FRAME_GUARD_MC68020.s. Pas de VBL entre Update réussi et appel Bank Free READY ; reprise bornée du Swap, Fill et Capture. VBL après Swap réussi pour stabiliser la lecture de l'ancienne page. Aucune reprise d'Update en erreur, aucun Swap après une erreur détectée.

Attendu : RESULT 1, ERR 0, CYCLES 5, READY_REFUSAL_OK=CLEAN_FREE_OK=REPEAT_FREE_OK=REARM_OK=BANKS_PRESERVED=5, PIXELS_OK 30, UPDATES 25, SWAPS 30, CLOSE_RETURNED 5, CLOSED_MOUSE_X -1. FREE_CHIP_GAIN_MIN >0, CHIP_LOSS=FAST_LOSS=DIFF_CYCLES=0, MEM_STABLE 1, VERDICT PASS. Si fonctionnel mais gain Chip non positif ou variation mémoire après échauffement : REVIEW ; MEM_STABLE n'est mis à 1 que si les deux conditions sont remplies. ERR10..17 initialisation, 21/22 mutation mémoire inattendue, 30/31 Update/Swap, 40..44 getters/banques, 50/51 pixels, 60 Close. PHASE_LAST localise le stade. Les trois paires de pixels sont des échantillons, pas un contrôle exhaustif du raster.

Le banc couvre le cas normal T10 AGBO et une partie de T14 avec B8, pas DIRTY forcé, refus allocateur/release injecté, ABA Erase/Load même adresse, AGPC, End, C2P, Copper. Le gain mémoire n'est pas un inventaire des allocations Exec. Aucune preuve Compiler/D ajoutée.

## Résultat T10A — Runtime PASS

T10A Runtime PASS sur L2b : 5/5 cycles, 5 refus READY sans mutation, 5 Free CLEAN, 5 Free répétés sans effet, 5 réactivations, 5 conservations DATA octet pour octet, 30 pixels, 25 Update/30 Swap, 1 VBL de reprise, 0 retry Capture/Fill. FREE_CHIP_GAIN_MIN=264, 5 Close B8 actifs, Mouse X=-1. Chip Free=1791304, Fast Free=138105688 aux 5 mesures après Erase ; CHIP_LOSS=FAST_LOSS=DIFF_CYCLES=0, MEM_STABLE=1. RESULT 1 ERR 0. Pas de preuve de refus interne release forcé, DIRTY forcé ni ABA. AGA-014 reste à qualifier en injection native ; aucune modification native requise sur le chemin normal. [Journal](../../../docs/evidence/T10_BANK_RUNTIME_PASS_L2B_2026-11-24.TXT). Journal original 729 octets CRLF, SHA256 `d96e0c2e648b04026dfe63b827a12eaea679f52484a7c803285032c7b9b66a16`, blob `4bb7d04e7fde648c718b7b0de393c1f084641a3f`. Suite [banc groupé](../l3_integrated/README.md).
