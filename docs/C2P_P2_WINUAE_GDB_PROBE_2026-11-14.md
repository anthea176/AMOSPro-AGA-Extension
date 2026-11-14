# C2P P2 - relever les bitmaps R73 sous WinUAE

**Statut : test préparé, aucune Gate B WinUAE P2 encore effectuée.**
`dist/AMOSPro_AGA.Lib` et `dist/AMOSPro_AGA_LAST_GOOD.Lib` restent R73 identiques, 51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.

## WinUAE 6.1 beta 18 ou plus récent avec GDB intégré

Le support GDB **n'est pas présumé sur un WinUAE antérieur**. Il a été ajouté dans la famille WinUAE 6.1 beta (2026). Démarrer WinUAE avec :

```text
winuae64.exe -s debugging_features=gdbserver -s gdb_port=2345
```

Ou ajouter à la configuration `.uae` les options `debugging_features=gdbserver` et `gdb_port=2345` si cette version les accepte. Le serveur écoute **127.0.0.1 seulement**.

1. Installer **R73 inchangée**. Importer **à nouveau** et exécuter le seul ASC actif `tests/current/C2P_P2_R73_BITMAP_01.asc` dans AMOS interprété. Le programme ouvre un écran privé 320x256, **256 couleurs**, appelle `Aga Double Buffer`, effectue au plus 20 essais non bloquants de `Aga Swap`, puis attend volontairement **Échap** via une boucle `Aga Key` non bloquante. `Alt+Tab` ou une autre touche ne déclenchent plus la fermeture de l'écran.
2. **Pendant l'attente de touche**, sur Windows, dans le dossier du projet, lancer la commande ci-dessous avec Python 3. Vérifier auparavant **la taille réelle de la Chip RAM configurée** dans WinUAE : l'exemple `0x200000` signifie 2 Mio, **à ne pas utiliser si votre configuration diffère**.

```powershell
python -B tools/c2p_p2_winuae_gdb.py --chip-ram-bytes 0x200000 --output c2p_p2_observation.json
```

3. L'outil stoppe momentanément le CPU via GDB, lit `A5+$1C8 -> State -> DBState -> SB0/SB1 -> BitMap` (en respectant `ScreenBuffer+4`), vérifie `Width=320`, `Height=256`, `Colors=256`, puis lit les deux `BitMap` et huit plans. Il confronte la région 0...Chip RAM déclarée à la *memory-map* RAM de WinUAE. Il **ne lit pas directement `TypeOfMem`**, ne modifie aucun octet, ne crée aucun contexte C2P. À la déconnexion GDB, le CPU reprend.
4. Partager `c2p_p2_observation.json` **et la sortie console**. Le verdict positif établira seulement la compatibilité structurelle déclarée, pas une vraie conversion ou la validation Safe/Swap. Si la commande renvoie `C2P P2 GDB PROBE FAILED`, transmettre le texte sans essayer des pointeurs au hasard.
5. Revenir dans WinUAE, appuyer sur **Échap** (RAWKEY `$45`, décimal `69`) dans la fenêtre AGA pour quitter explicitement. Vérifier `RESULT 1`, `CLOSE RETURNED` et Chip Free initial/final identique. Aucune Gate C Compiler requise à cette étape diagnostique.

**Sans GDB ou WinUAE 6.1 beta :** conserver R73 intacte et relever manuellement le contenu via le débogueur intégré `Shift+F12` (`r`, `m <address>`, `dm`). Ne pas supposer que A5 reste valide hors d'une routine AGA : le programme utilise maintenant la boucle `Aga Key` et `Aga Wait Vbl`. Si le relevé signale un A5 invalide, transmettre le message d'erreur plutôt que de deviner une adresse. Envoyer les captures du registre A5, de `A5+$1C8`, puis des pointeurs suivants pour conversion en JSON.

## Pourquoi une nouvelle ASC ?

Le test R73 de promotion est déjà validé ; il reste consultable **dans l'historique Git de `main` au commit `cf30d8d`**. Le test P2 est maintenant l'unique ASC actif ; aucune ancienne preuve de Gate B/C R73 n'est réécrite. R73 `LAST_GOOD`, les archives et `tests/passed/` restent inchangés.

## Résultat d'étape

Tests Python *synthétiques* du lecteur GDB et du checker : **18 scénarios locaux PASS**, ce qui ne prouve ni la connectivité avec le WinUAE de l'auteur, ni le fonctionnement C2P. **Prochaine décision après observation réelle :** conversion directe seulement si les deux bitmaps sont strictement contigus non entrelacés et que les plans sont prouvés en Chip RAM ; sinon étudier un allocation dédiée.
