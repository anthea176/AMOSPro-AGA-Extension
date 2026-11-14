# Référence intégrée du milestone C2P — vraie image AGA (14/11/2026)

**Statut : démonstration IFF intégrée WinUAE PASS (capture et journal utilisateur du 14/11/2026). Gate C Compiler et Gate D physique NON TESTÉES.**

L'objectif est un **vrai programme graphique intégré**, pas un simple rapport ni une capture du test synthétique R79 : montrer le fichier `iff-TEST/AGA_DEMO_320x256_256c.iff` intact, le réafficher en chunky via C2P, puis appliquer et vérifier sur **ses vrais pixels** les commandes `Aga C2P Blit` et `Aga C2P Zoom`.

## Références durables

- [Programme AMOS](../examples/c2p_iff_showcase/C2P_IFF_SHOWCASE.asc) — distinct de l'unique `tests/current/C2P_R79_ZOOM_01.asc`, conservé inchangé.
- [Guide de test français](../examples/c2p_iff_showcase/README.fr.md) — installation WinUAE, sélection IFF, `RAM:C2P_IFF_SHOWCASE.TXT`, critères et sécurité des banques.
- [IFF source](../iff-TEST/AGA_DEMO_320x256_256c.iff) — SHA256 `1820df9bcd77ae111b55927981482ce90c67da06d74646f6b6d92082f00db2db`, **80 776 octets**.
- [Compagnon chunky](../iff-TEST/AGA_DEMO_320x256_256c.chk) — SHA256 `3f4df7bc229d36ab5a2711913fa8798d1d11bfe82a6792a98e5be67ad470b694`, **81 920 octets**, identique aux indices décodés depuis le `BODY` de l'IFF.
- [Image finale attendue](../examples/c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png) — PNG indexé 320×256×256 couleurs, **83 029 octets**, SHA256 `919b166c1c815df2fe08bb0d0d8c3fdbb6224bdd8b9c0bcb08e40ae3b8cedadb`. Elle vient du même IFF, de sa palette RGB complète et des mêmes coordonnées Blit/Zoom, sans prise de capture WinUAE.
- [Oracle Python statique](../tools/test_c2p_iff_showcase.py) — sans Pillow requis dans la CI, valide l'IFF, la banque chunky, les coordonnées du code AMOS, **14 indices** et tous les pixels du PNG golden contre une composition indépendante.

## Déroulement de l'exemple

| Phase | Ce qui doit apparaître | API et vérifications |
|---|---|---|
| 1. IFF original | Image fantasy AGA / Extension intacte | `Aga Pic Info`, `Aga Screen Open`, `Aga Double Buffer`, `Aga Iff Load`, `Aga Palette Load/Get`, `Aga Swap` |
| 2. Conversion | Exactement la même image reproduite par le pipeline chunky | `Bload` des indices dans banques 12/13, `Aga C2P Open(12)`, `Aga C2P Convert`, `Aga Swap` |
| 3. Montage | Original en fond + 3 copies et 7 échantillons Zoom (×1.5, ×2, réduction, non-entier, quatre clips) | `Aga C2P Blit`, `Aga C2P Zoom`, comparaison **14 pixels**, refus des appels invalides, `Convert`, `Swap` |
| 4. Cycle C2P | Montage identique après fermeture et réouverture du contexte | `Aga C2P Close`, double Close, Convert/Zoom refusés après Close, ReOpen, Blit/Zoom, Convert/Swap, Échap |
| 5. Fermeture | Retour à AMOS avec bilan et journal `RAM:` | `Aga C2P Close`, `Aga Screen Close`, `Amos To Front`, `Erase 13`, `Erase 12`, Chip/Fast Free, `End` |

**Les couleurs sont celles de l'IFF original.** Les zones pixel 0 restent opaques. `Amos To Back` précède l'attente Échap, conformément au correctif de focus R77/R78.

## Conditions de validation

Le programme de démonstration doit afficher une composition visuellement conforme au [PNG attendu](../examples/c2p_iff_showcase/EXPECTED_C2P_SHOWCASE.png) et produire :

```text
TEST C2P-IFF-SHOWCASE-R79
VERSION R79 V0.13.24 CANDIDATE
RESULT  1
VERDICT PASS
IFF_OK  1
PALETTE_OK  1
RAW_OK  1
C2P_BASE_OK  1
BLIT_OK  1
ZOOM_OK  1
PIXEL_CHECK_OK  1
PIXEL_CHECK_COUNT  14
INVALID_CALLS_OK  1
REOPEN_OK  1
ESC_OK  1
SCREEN_CLOSE_COUNT  1
ERR  0
CLOSE RETURNED
```

Les deltas Chip/Fast avant/après sont à relever **après la libération des banques, avant l'écriture du log**. Zéro est attendu en exécution propre ; si non nul, conserver les valeurs complètes et distinguer les ressources libérées d'un ancien lancement interrompu par Ctrl+C. **Les preuves logiques ne remplacent pas une inspection visuelle.** Une passe de ce seul exemple **ne couvre pas** la matrice 16/32/64/128/256 couleurs du test R79 courant.

## Validation WinUAE observée — 14/11/2026

Capture du montage final `image(20261114-152334).png` et journal `C2P_IFF_SHOWCASE.TXT` récupéré depuis `RAM:C2P_IFF_SHOWCASE.TXT`. IFF source : `DH6:iff-TEST/AGA_DEMO_320x256_256c.iff`, compagnon `.chk`. La capture montre les zones Blit/Zoom aux emplacements cohérents avec le programme, sans défaut évident. **Une comparaison intégrale pixel par pixel de la capture agrandie au PNG de référence n'a pas été réalisée.**

Journal réel : `RUN_MODE RUNTIME`, `PRG_STATE 1`, `RESULT 1`, `VERDICT PASS`, `IFF_OK 1`, `PALETTE_OK 1`, `RAW_OK 1`, `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1`, `PIXEL_CHECK_OK 1`, `PIXEL_CHECK_COUNT 14`, `INVALID_CALLS_OK 1`, `REOPEN_OK 1`, `ESC_OK 1`, `SCREEN_CLOSE_COUNT 1`, `ERR 0`, `CLOSE_RETURNED`.

Mémoire : **Chip Free 1 384 608 -> 1 384 608 (delta 0)** ; **Fast Free 130 438 400 -> 130 438 400 (delta 0)**. Aucune variation observée dans cet essai terminé proprement. Le log autonome ne contient pas de CPU/AttnFlags ; `PRG_STATE 1` signifie **RUNTIME** et ne prouve pas la Gate C Compiler.

**Verdict : Gate B fonctionnelle WinUAE PASS pour cet exemple IFF R79**, en plus du test R79 synthétique 5/5 profondeurs déjà validé. Les deux pièces ont été fournies dans la conversation, non versionnées dans le dépôt.

## Essai compilé de la démonstration (14/11/2026)

Le second journal utilisateur `C2P_IFF_SHOWCASE2.TXT` prouve cette fois l'exécution **COMPILED** (`PRG_STATE -1`), `RESULT 1`, `VERDICT PASS`, 14/14 vérifications de pixels, Blit/Zoom/Close/ReOpen et ESC réussis, `ERR 0`, `CLOSE RETURNED`. Chip Free **1 352 840 -> 1 352 840**, Fast Free **130 112 656 -> 130 112 656** (deltas 0/0). **Le showcase compilé est PASS.** Il est distinct de l'ASC courant à cinq profondeurs ; **la Gate C globale finale n'est pas automatiquement acquise**.

**Limite relevée :** ce showcase importe une banque chunky `.chk` générée sur PC. Ce fichier est un choix de fixture, **pas une condition technique de `Aga C2P Open`**. Une banque DATA/WORK peut être remplie directement par AMOS. Pour importer des images IFF sans compagnon, il manque une fonction native de décodage ILBM vers indices chunky (différente de `Aga Iff Load` qui dessine un bitmap planar). Une telle API reste **à concevoir et à approuver** ; ni la R79 ni la référence R73 n'ont changé.

## État de la bibliothèque

- Candidate **R79 v0.13.24**, `dist/AMOSPro_AGA.Lib`, SHA256 `ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab`, 57 344 octets ; C2P Open/Convert/Close/Blit/Zoom.
- La batterie native R79 (62 scénarios, CI complète) est PASS. Le journal utilisateur `C2P_R79_RUNTIME.TXT` du test **synthétique** courant indique `RESULT 1`, cinq profondeurs PASS et deltas mémoire Chip/Fast à 0. **L'exemple IFF intégré est distinct et maintenant confirmé sous WinUAE (capture et journal, 14/14 indices, deltas mémoire 0/0).**
- **AMOS Compiler Gate C reste à effectuer une seule fois à la fin du chantier** ; Amiga physique Gate D non testé.
- **R73 v0.13.18 `LAST_GOOD` est protégée**, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`. Pas de promotion, de release, de tag ni de modification de branche.

**Prochaine étape :** validation réelle de la Gate C Compiler selon la procédure prévue ; aucune clôture complète de C2P ni promotion de `LAST_GOOD` avant cette validation et l'accord de l'auteur.
