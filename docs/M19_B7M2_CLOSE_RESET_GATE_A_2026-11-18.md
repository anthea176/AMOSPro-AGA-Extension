# M19 B7-m1 relance WinUAE FAIL / B7-m2 correctif de source (18/11/2026)

## Deux journaux reels fournis par l'auteur

Le premier lancement Runtime (Prg State 1) a termine avec RESULT 1, ERR 0,
FRAMES_OK 405, STAGES_OK 9, OFF_COMMANDS_ISSUED 50, zero erreur Fill/Copy/Draw/Swap
et VERDICT PATH_OK. L'auteur confirme un affichage correct des neuf etapes,
notamment Off 2/3/9, reactivate et 64 Bobs. Les 349 reprises VBL sont des
attentes, pas des erreurs de rendu.

Le second lancement du meme ASC, sans Erase All, echoue au tout premier
Aga Bob Draw : RESULT 0, ERR 14, FRAMES_OK 0, STAGES_OK 0,
DRAW_FAILS 1, SWAP_FAILS 0. CLOSE_RETURNED 1 et BANKS_ERASED 2
ne prouvent PAS la remise a zero des slots natifs. Le journal ne contient
pas de code natif detaille qui attribuerait un motif unique au refus.

Conclusion de Gate B : les neuf etapes visuelles du PREMIER lancement
sont PASS. Le cycle de vie reutilisable et la relance sont FAIL.
Gate B globale M19 Off/On NE DOIT PAS etre declaree PASS.

## Source du defaut auditee

La base P0e utilisait public_aga_p0e_close_entry :
relay_reset_entry puis screen_close_bridge_entry, pour reinitialiser
les 64 slots avant la destruction de l'ecran.

Depuis B5, le token public Screen Close a ete redirige vers
guarded_close_entry, qui utilise directement screen_close_bridge_entry
sans relay_reset_entry. B6/B7/B7-m1 conservent ce raccordement. L'ancienne
table contient donc encore potentiellement des IDs 3..16 actifs a la
fin de 405 frames. Ces entrees peuvent devenir perimees quand les banques
AMOS 24/25 sont detruites puis recreees.

L'absence de reset est verifiee dans la chaine source. Le motif exact
du refus Draw n'est pas instrumente dans le journal WinUAE. Il reste
a prouver qu'il n'existe aucune cause concurrente.

## Correctif B7-m2 (source-only, sans bascule)

- Nouveau suffixe MC68020 b7m2_close_reset_entry : garder l'ABI de
  Screen Close, refuser CPU invalide, appeler relay_reset_entry
  AVANT guarded_close_entry, uniquement si le reset reussit.
- Nouveau builder en memoire depuis build_multiframe() strictement
  identique a la Lib B7-m1 installee. Un seul stub AP20 existant est
  recible : l'instruction publique Screen Close. Pas de nouveau token,
  banque, API, source R88, copie de Lib ou archive.
- Nouveau test CPU020 : reproduire la retention des 16 slots par B7-m1,
  puis verifier 64->16->0 au Close, la position du reset AVANT le
  vrai Close natif, le second Open/Draw/Swap, la securite des erreurs,
  Safe/Disp en attente et l'End non destructif. Modele sous Unicorn :
  les services AmigaOS et DMA restent simules.

La remise a zero est volontairement AVANT le Close historique, comme en
P0e. Si Safe/Disp retarde la fermeture, les slots sont desactives meme
si l'ecran reste ouvert ; aucun retour implicite a un etat presentable
n'est revendique. Le traitement End-only sans appel Close n'est pas
change par ce correctif : ce parcours est a qualifier separement.

## Protection et Gates

B7-m1 reste la seule Lib de travail : 102 360 octets,
SHA256 838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403.
Le programme ASC reste le seul test actif (10 866 octets,
SHA256 faed496a977a151850255f39f0ac134bd80014975b6dcd7942b27b351c05645d).
R84 LAST_GOOD reste protegee.

Gate A B7-m2 : execution CI a confirmer dans le workflow M19 ;
Gate B de B7-m2 : NON TESTEE tant que la candidate n'a pas ete
explicitement autorisee comme unique Lib de travail ;
Gate C vrai Compiler et D materiel : NON TESTEES.

Aucune promotion, compilation Amiga ou essai WinUAE n'a ete realise
pendant ce travail source-only.
