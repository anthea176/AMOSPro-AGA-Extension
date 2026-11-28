# S2c-P1d — diagnostic Runtime (campagne unique)

**28/11/2026 — S2c-P1d (titre interne S2c-D1) active sur main, autorisation auteur « go ».** [Gate A intégrée PASS 11/11](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46083896471), source `adcfa65d0f2e8ca402263eb3f0daee90d3471265` : 288 changements + 11 injections de défauts par modèle Runtime/Compiler, capture et régressions historiques PASS ; double reconstruction et préflight ASC strict PASS. Lib 160812 octets SHA256 `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026`, blob `551674f3598c8b0c10a581d9ac7a1f7cf1155659`. MC68020+, 105 commandes/219 AP20 ; UNIT213 seule modifiée (20216 octets, marge 45318), PC16 max 3658 avec réserve 16384. ASC 15459 octets et ABK 1460 octets strictement inchangés. P1c Runtime FAIL -153 conservée dans Git `8f490c4ee9f3609abd763e8ba2f03e4d97de49de`. P1d est un diagnostic, pas un correctif fonctionnel ; B/C/D P1d NON TESTÉES, CI post-activation à relever. LAST_GOOD L2b protégée, aucune promotion, nouvelle branche, archive ni release. [Décodage complet](../../docs/M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md).

**Important : ne remplacer que la Lib.** L'ASC et l'ABK sont identiques à P1c. Sauvegarder le précédent journal avant relance. L'échec -153 de P1c devrait maintenant donner un code détaillé pour le chemin attaché. Envoyer le journal complet même si RESULT=0. Le Compiler est différé tant que le défaut Runtime n'est pas isolé.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 160812 | `a1fefebd81763ac9b484d2fbc376e896d6ab5e0b19054bd023f4d0b280c5d026` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 15459 | `48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec` |
| [AGSP_S2C_MIXED.ABK](AGSP_S2C_MIXED.ABK) | 1460 | `6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246` |

ABK et ASC dans le même dossier ; banques AMOS 29 et 30 libres. Installer la Lib dans APSystem, même slot ; redémarrer complètement WinUAE sans Save State, vérifier le SHA de la copie installée. Configuration fonctionnelle : AGA PAL, 68030 JIT ON. Project > Merge ASCII dans un programme vierge. Pas de nouvelle Lib alternative.

## Gate B — Runtime (PRG_STATE=1)

1. Observer les rectangles AGAPIC, puis trois Sprites 16 pixels : écran 1 trois simples, écran 2 deux simples et un attaché, écran 3 trois attachés. Les palettes des simples correspondent à leur paire et les attachés à 17..31. Observer les alternances de frames, les déplacements, le retrait ciblé/réaffichage, l'absence de traînées et les fermetures avec objets actifs.
2. Attendu : OPENED=CLOSED=3, SHOWN=12, CHANGED=MOVED=450, OFF_COUNT=3, AUTO_CLOSE=9, SATURATION=3, FULL_RC=-206 ; AGAPIC_CAPTURE/META/NEGATIVE/DRAW=6 ; AGSP_CAPTURED=6, REFUSED=3, FREE_RC=1, OWN=0. SPRITE_RC/CHANGE_RC/MOVE_RC/OFF_RC/FREE_RC=1. RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_S2C_MIXED. Aucune perte nette Chip/Fast ni perte par écran ; toute variation temporaire est à relever.
3. Sauvegarder RAM:M19_S2C_RUNTIME.TXT hors RAM: et refaire une relance sans reset si PASS, avec journal distinct. Transmettre les logs et observations visuelles.

## Gate C — véritable AMOS Compiler (PRG_STATE=-1)

**Différé :** attendre le diagnostic Runtime et une décision explicite avant de compiler. Même ASC et ABK, construire un nouvel exécutable avec la Lib exacte. Mêmes critères et journal RAM:M19_S2C_COMPILED.TXT. Le modèle Compiler de CI est uniquement Gate A.

## Diagnostics

P1d renvoie un code négatif étendu dans SPRITE_RC, CHANGE_RC ou MOVE_RC : N=-RC, stage=N>>24, check=(N>>16)&255, detail=N&65535. Les checks RGB 64..108 identifient pen, canal, octets attendu/lu. [Table complète](../../docs/M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md). Les retours courts historiques sont inchangés pour les chemins non instrumentés.

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation, 17=banque 30 occupée, 18=Fill, 19=AGAPIC Capture, 20=Info, 21=refus, 22=Draw, 23=Erase, 24=Swap, 25=motif capture AGSP, 26=banque AGSP, 27=capture 1 ligne, 28=capture 16 lignes, 29=refus 16 opaques. CLEAN_ERR bit 64=nettoyage capture AGSP. Conserver les codes et le dernier affichage en cas de Guru.

Limites : largeur 16, trois objets maximum, pas de changement 2/4 plans pendant affichage (Off puis Show), même hauteur/palette par objet, hotspot nul ; deux WaitTOF par changement attaché, pas de preuve DMA physique. Aucun benchmark de vitesse ni Gate D.

[Rapport S2c](../../docs/M19_S2C_P1C_PUBLIC_MIXED_2026-11-27.md) · [Protocole S2r historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31735f84f0da50ea4ba324f9bc63bec9313cd47a/tests/current/README.md).
