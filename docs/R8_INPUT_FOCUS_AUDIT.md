# R8 0.5.9 — audit Intuition RAWKEY après Fallout

## Clôture partielle du diagnostic (10/11/2026)

Le relevé PC a identifié une boucle interne `LGoto` sur une entrée de longueur zéro, et R8 présentait un défaut de dépilement A3 dans `Aga Pic Info`. Le correctif minimal R9 donne **4/4 PASS utilisateur** sur Fallout (PicInfo/Open/DB/Load/Swap/Wait Key/Close, retour à AMOS). Il n'y a donc **aucune preuve actuelle de défaut du focus Intuition** dans ce scénario. Ne pas ouvrir de chantier clavier sur la seule base des diagnostics R8. Tests compilés et autres scénarios restent ouverts.

---

## Cause immédiate du gel identifiée — aucun défaut clavier démontré

Le diagnostic mémoire WinUAE `PC=$4019CAB8`, `A3=$403DFA96`, `(A3)=$0000` correspond à `LGoto` (`+ILib.s`, lignes 2795–2808) : boucle infinie sur les structures de contrôle AMOS. La logique `GetMsg/WaitTOF` et le focus de la fenêtre ne sont **pas** les responsables identifiés par ce relevé.

L'analyse binaire montre une violation ABI dans `Aga Pic Info` R8 : elle restaure A3 et annule le retrait d'un argument de la pile. R9 expérimental réduit uniquement la sauvegarde/restauration de ce registre pour laisser A3 avancer de 4 octets. Voir `docs/PICINFO_A3_R9.md`. **Pas de validation runtime R9** à ce stade.

---

## CORRECTION APRÈS CAPTURE — l'hypothèse focus n'est PAS prouvée

Le nouveau test `R8_FALLOUT_KEY_POLL_SAFE.asc` est resté visible sur `IMAGE 640 X 512 PLANS 4`, avec souris mobile et curseur texte actif, Ctrl+C/Amiga+A inopérants. **Ce texte est imprimé avant** `Aga Screen Open`, `Aga Double Buffer`, `Aga Iff Load`, `Aga Swap` et la boucle de polling. Aucun retour des quatre commandes n'est imprimé.

**Le compteur de 500 VBL est local à la boucle clavier, pas un watchdog de l'ensemble du test.** Puisque nous ne savons pas si le polling a été atteint, nous ne pouvons pas incriminer `Aga Key`, `Aga Wait Key`, le port IDCMP ou le focus. Le test est **NON CONCLUANT et retiré de `current/`**.

Prochaine observation utile : **WinUAE Shift+F12, `r`, `d` pendant le gel** ; aucune nouvelle variante AMOS avant PC/désassemblage. La Lib et le loader restent strictement inchangés.

---

Date : 10 novembre 2026. Branche : `codex/intuition-input-r1`. **Analyse sans modification de binaire.**

## Faits observés, sans extrapolation

- R7 640×512/4 : Open/DB/Close sans Swap 5/5 PASS.
- R8 : Swap/Close sans IFF 5/5 PASS.
- R8 + Fallout : Open/DB/IFF Load/Close sans Swap retourne 1 et revient à AMOS.
- La capture la plus récente du test **original** `M5_R8_ILBM_SINGLE_SWAP.asc` prouve `OPEN=1 DB=1 LOAD=1 SWAP=1 KEY=68 CLOSE RETURNED`, après passage dans **`Aga Wait Key`**. Un essai fonctionnel, **pas une garantie de stabilité**.
- Une capture précédente, sous le même titre, ne montrait que PicInfo. Les valeurs Open/DB/Load étaient imprimées après l'ouverture AGA et pouvaient être masquées. L'instruction bloquante n'est pas prouvée.

## Audit source 68000/Intuition

`tools/build_intuition_input_r1.py`, fonction `input_routine(wait)` :
- entrée : lit `STATE_WINDOW` puis `Window.UserPort` (+86) ;
- `GetMsg` non bloquant ; si `IDCMP_RAWKEY` key-down, `ReplyMsg`, retourne le code dans D3 ;
- si aucun message et `wait=True`, appelle `graphics.library/WaitTOF` et repart sur `poll` **sans compteur limite** ;
- Ctrl+C dépend du message RAWKEY C+qualifier Control : en l'absence de message sur ce port, aucun Break n'est déclenché par la routine ;
- `Aga Key` utilise le même chemin de lecture, mais **retourne -1** si aucun message.

La fenêtre est créée par `open_window_helper()` avec `WINDOW_FLAGS=$00021900` (`WFLG_BACKDROP|BORDERLESS|ACTIVATE|NOCAREREFRESH`), et `IDCMP_RAWKEY=$400`. Ces bits sont corrects. **Mais `WFLG_ACTIVATE` ne garantit pas que la fenêtre soit déjà active lors du retour d'OpenWindow**, et Intuition peut retarder son activation. Le clavier est envoyé à la fenêtre active ; une perte de focus ou une activation différée après les changements de premier plan reste plausible. **Ce n'est pas une cause démontrée**.

Références officielles :
- https://wiki.amigaos.net/wiki/Window_Communication
- https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node0390.html
- https://d0.se/include/intuition/intuition.i

## Nouveau test sans risque d'attente clavier infinie

`tests/current/R8_FALLOUT_KEY_POLL_SAFE.asc` :
- PicInfo → Open → Double Buffer → IFF Load → un Swap, comme le scénario R8 ;
- `Amos To Back`, puis `Aga Key` dans une boucle bornée par **500 VBL** ;
- retour à AMOS et `Aga Screen Close` en sortie de boucle, qu'une touche soit reçue ou non ;
- affichage du code brut `RAWKEY` et du nombre de polls ;
- demande de presser Espace, puis de cliquer dans la fenêtre AGA et Espace si rien ne réagit.

Interprétation : `RAWKEY>=0` indique une réception de message dans cet essai ; `RAWKEY=-1` indique une absence de message jusqu'à la limite (compatible avec perte de focus, sans preuve définitive). Un blocage malgré cette borne demande d'investiguer les autres commandes ou `Close`. Aucune nouvelle version `.Lib`, aucun token, aucun correctif `ActivateWindow` imposé sans validation.

## Validation restant ouverte

1. Exécuter le **test unique** dans WinUAE interprété, en utilisant une nouvelle copie du fichier ; noter le bandeau exact et `RAWKEY`.
2. Si l'absence de message est confirmée malgré une touche et qu'un clic change le résultat, envisager une réactivation ciblée `ActivateWindow` à l'entrée de `Aga Wait Key`, sans appel en boucle et avec préflight CPU.
3. Valider ensuite Ctrl+C et le scénario compilé, séparément. Ne pas attribuer de PASS avant exécution.
