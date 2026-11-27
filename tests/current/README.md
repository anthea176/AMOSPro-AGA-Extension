# S2c-P1c — campagne WinUAE active unique

**28/11/2026 — S2c-P1c, candidate de test active sur main, autorisation auteur « va y », puis « ok continu des que c bon ».** [Gate A intégrée PASS 11/11](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072322336), source `5efc907baadd7c736345a97464023e2695e15c6b` : deux modèles mixtes 288 changements chacun, 392 contrôles AGAPIC et régressions capture, Pattern, SafePort, Bob, DB/IFF/Swap PASS. [Campagne exacte et préflight strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46072461473). Lib 159844 octets SHA256 `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb` blob `7e8b5320c4098db053afb2bf8ce9f16bf611ff39` ; ASC 15459 octets SHA256 `48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec` ; nouvelle ABK AGSP_S2C_MIXED.ABK 1460 octets SHA256 `6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246`. 105 commandes / 219 AP20, MC68020+, UNIT142 63350, îlot Sprite 213 19246 octets, marge WORD 46288, réserve 16384 vérifiée. Titre binaire exact S2c-P2 (aucune retouche cosmétique). S2r préservée dans Git `31735f84f0da50ea4ba324f9bc63bec9313cd47a`. Gates B/C/D réelles S2c NON TESTÉES. CI post-activation à relever. LAST_GOOD L2b et anciennes ABK inchangées ; aucune promotion, branche, archive ni release.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 159844 | `00cdcc0de1f9f79aa1d7aac14b920875b5ed822521f7c30c223ea83f88f6a8bb` |
| [SPRITE_PUBLIC.asc](SPRITE_PUBLIC.asc) | 15459 | `48b9d1e47d63dd401482cfb0ecc8db0646aba68f173154c26ef2b5051f0496ec` |
| [AGSP_S2C_MIXED.ABK](AGSP_S2C_MIXED.ABK) | 1460 | `6f9a65305ca2a3ff7a65d8fc3af02afd75bc45810c94392733141bea434bc246` |

ABK et ASC dans le même dossier ; banques AMOS 29 et 30 libres. Installer la Lib dans APSystem, même slot ; redémarrer complètement WinUAE sans Save State, vérifier le SHA de la copie installée. Configuration fonctionnelle : AGA PAL, 68030 JIT ON. Project > Merge ASCII dans un programme vierge. Pas de nouvelle Lib alternative.

## Gate B — Runtime (PRG_STATE=1)

1. Observer les rectangles AGAPIC, puis trois Sprites 16 pixels : écran 1 trois simples, écran 2 deux simples et un attaché, écran 3 trois attachés. Les palettes des simples correspondent à leur paire et les attachés à 17..31. Observer les alternances de frames, les déplacements, le retrait ciblé/réaffichage, l'absence de traînées et les fermetures avec objets actifs.
2. Attendu : OPENED=CLOSED=3, SHOWN=12, CHANGED=MOVED=450, OFF_COUNT=3, AUTO_CLOSE=9, SATURATION=3, FULL_RC=-206 ; AGAPIC_CAPTURE/META/NEGATIVE/DRAW=6 ; AGSP_CAPTURED=6, REFUSED=3, FREE_RC=1, OWN=0. SPRITE_RC/CHANGE_RC/MOVE_RC/OFF_RC/FREE_RC=1. RESULT=1 ERR=0 CLEAN_ERR=0, VERDICT PASS_S2C_MIXED. Aucune perte nette Chip/Fast ni perte par écran ; toute variation temporaire est à relever.
3. Sauvegarder RAM:M19_S2C_RUNTIME.TXT hors RAM: et refaire une relance sans reset si PASS, avec journal distinct. Transmettre les logs et observations visuelles.

## Gate C — véritable AMOS Compiler (PRG_STATE=-1)

Même ASC et ABK, construire un nouvel exécutable avec la Lib exacte. Mêmes critères et journal RAM:M19_S2C_COMPILED.TXT. Le modèle Compiler de CI est uniquement Gate A.

## Diagnostics

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation, 17=banque 30 occupée, 18=Fill, 19=AGAPIC Capture, 20=Info, 21=refus, 22=Draw, 23=Erase, 24=Swap, 25=motif capture AGSP, 26=banque AGSP, 27=capture 1 ligne, 28=capture 16 lignes, 29=refus 16 opaques. CLEAN_ERR bit 64=nettoyage capture AGSP. Conserver les codes et le dernier affichage en cas de Guru.

Limites : largeur 16, trois objets maximum, pas de changement 2/4 plans pendant affichage (Off puis Show), même hauteur/palette par objet, hotspot nul ; deux WaitTOF par changement attaché, pas de preuve DMA physique. Aucun benchmark de vitesse ni Gate D.

[Rapport S2c](../../docs/M19_S2C_P1C_PUBLIC_MIXED_2026-11-27.md) · [Protocole S2r historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31735f84f0da50ea4ba324f9bc63bec9313cd47a/tests/current/README.md).
