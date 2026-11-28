# S2c-P1e — correction ViewPort (campagne Runtime unique)

**28/11/2026 — S2c-P1e Gates B Runtime et C Compiler fonctionnelles PASS** (PRG_STATE=1/-1, RESULT=1 ERR=0 CLEAN_ERR=0, PASS_S2C_MIXED). Chaque mode : 3 Open/Close, 12 Show, 450 Change, 450 Move, 3 Off, 9 retraits auto, 3 saturations -206, AGAPIC 6/6, AGSP 4 plans 6/6 et 3 refus. Chip/Fast sans perte nette ; Fast temporaire 1464 octets récupérée. Attribution à la Lib active par contexte, SHA installé, visuel complet, relance indépendante et D non attestés. L'auteur demande de renforcer le contraste des prochaines campagnes. S2c-E1 reste active (160896 octets, SHA256 `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310`), aucune promotion de LAST_GOOD. [Preuves](../../docs/M19_S2C_P1E_RUNTIME_COMPILER_2026-11-28.md).

**Chantier suivant : 0.15.0-alpha.1 (M19 S2d)** : capture/repack puis affichage Sprite 16/32/64px ; largeur commune par contexte, API existante, couleur franche et motifs asymétriques. Source-only jusqu'à preuve Gate A et bascule explicitement autorisée. Cible publique 0.15.0 ; objectif final 1.0.0. Ne pas renommer les binaires historiques. [Plan](../../docs/M19_S2D_WIDE_SPRITES_0_15_0.md).

Campagne S2c conservée à l'identique : les consignes antérieures de Compiler différé sont historiques. Aucun nouvel ASC/ABK actif avant la prochaine bascule.

**28/11/2026 — S2c-P1e (titre interne S2c-E1) active sur main, autorisation auteur « ben go... ».** Gate A complète par preuves combinées sur le même binaire exact : [premier run](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46123061368), 8 suites historiques PASS, 288 changements + 11 injections P1d + 15 scénarios ViewPort réussis dans chaque layout avant assertion erronée du dernier scénario ; [requalification](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826), jobs ciblés [fences-compiled](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826/job/140915600110) et [fences-runtime](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826/job/140915600178) PASS avec retour -104595462, aucune staging/publication et retraite des deux canaux, peer intact. Correction du seul test `817f26311e231730768f2711cd5dbb37320939d5`, aucune modification native depuis `25cf6e9d7d625b60599eef1749814f1aed472da8`. La CI initiale reste FAIL et le second passage intégral est en cours à ce relevé ; ne pas les annoncer comme runs intégralement verts. CPU/chemins et documentation PASS. Double reconstruction et préflight ASC strict PASS. Lib 160896 octets SHA256 `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310`, blob `9110fe94f0d937207038d77d6df250b99392c54c`. MC68020+, 105 commandes/219 AP20 ; UNIT213 seule modifiée par rapport à P1d (20298 octets, marge 45236), PC16 max 3658 avec réserve 16384. ASC 15459 octets et ABK 1460 octets byte-exacts. P1d historique B FAIL check 5 (`8e17d6f524f320832f7c7489cf27fe4f92b084df`). P1e B/C/D réelles NON TESTÉES ; CI post-activation à relever. LAST_GOOD L2b protégée ; aucune promotion, branche, archive ni release. [Rapport](../../docs/M19_S2C_P1E_VIEWPORT_CHAIN_2026-11-28.md).

**Ne remplacer que la Lib.** ASC et ABK identiques à P1d. Version interne S2c-E1, redémarrage complet sans Save State. Sauvegarder le précédent journal hors RAM:. Le défaut ViewPort.Next non nul est corrigé ; un autre refus éventuel reste diagnostiquable. Envoyer le journal complet même si RESULT=0. Compiler différé jusqu'à réussite Runtime.

## Fichiers à utiliser ensemble

| Fichier | Octets | SHA256 |
| --- | ---: | --- |
| [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib) | 160896 | `7a4060cb3df1b40cad223af4640ee4be3e19ebb6add9dc0d4ab44aaf2ae1f310` |
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

P1e conserve les codes négatifs étendus de P1d dans SPRITE_RC, CHANGE_RC ou MOVE_RC : N=-RC, stage=N>>24, check=(N>>16)&255, detail=N&65535. Les checks RGB 64..108 identifient pen, canal, octets attendu/lu. [Table complète](../../docs/M19_S2C_P1D_DIAGNOSTIC_2026-11-28.md). Check 5 : détail 0 = boucle directe/tête, 1 = span invalide, 2 = dépassement 16 successeurs (ou cycle interne). Une mutation détectée par le premier garde de références après WaitTOF renvoie stage6/check60/detail6 et retire le Sprite. Les retours courts historiques sont inchangés pour les chemins non instrumentés.

ERR 10=Show, 11=Change, 12=Move, 13=Off, 14=mémoire, 15=re-show, 16=saturation, 17=banque 30 occupée, 18=Fill, 19=AGAPIC Capture, 20=Info, 21=refus, 22=Draw, 23=Erase, 24=Swap, 25=motif capture AGSP, 26=banque AGSP, 27=capture 1 ligne, 28=capture 16 lignes, 29=refus 16 opaques. CLEAN_ERR bit 64=nettoyage capture AGSP. Conserver les codes et le dernier affichage en cas de Guru.

Limites : largeur 16, trois objets maximum, pas de changement 2/4 plans pendant affichage (Off puis Show), même hauteur/palette par objet, hotspot nul ; deux WaitTOF par changement attaché, pas de preuve DMA physique. Aucun benchmark de vitesse ni Gate D.

[Rapport S2c](../../docs/M19_S2C_P1C_PUBLIC_MIXED_2026-11-27.md) · [Protocole S2r historique](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/31735f84f0da50ea4ba324f9bc63bec9313cd47a/tests/current/README.md).
