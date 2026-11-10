# M8 — R23 0.8.7 : dispatcher IDCMP souris + clavier

## But et périmètre

**R23 0.8.7 — Gate A CPU/CI PASS (15 tests 68000, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42899343161)), Gate B AMOS interprété/WinUAE PASS** sur les scénarios clics rapides, FIFO clavier et Ctrl+C. Test AMOS exact [archivé](../tests/passed/M8_R23_IDCMP_QUICK_01.asc) sans modification après confirmation utilisateur du 10/11/2026. AMOS Compiler, matériel Amiga et stress non testés.

La R22 calcule les fronts à partir d'instantanés de `input.device/PeekQualifier()`. Un clic complet entre deux lectures est donc perdu. Le contrat R23 conserve **les mêmes instructions AMOS** :
- `_P=Aga Mouse Pressed`
- `_R=Aga Mouse Released`
- `_K=Aga Key`
- `_K=Aga Wait Key`

Les deux premières fonctions passent à la capture via `IDCMP_MOUSEBUTTONS` ; les deux dernières continuent à décoder leurs messages `RAWKEY`, après passage par une file de préservation clavier. Le but n'est pas d'ajouter de nouveaux tokens AP20.

## Événements officiels et gestion partagée

Sources : `intuition/intuition.h`, `devices/inputevent.h`, Autodocs `OpenWindow`.

| IDCMP Class | Code | Traitement |
|---|---|---|
| `IDCMP_MOUSEBUTTONS=$00000008` | `SELECTDOWN=$68`, `SELECTUP=$E8` | Front gauche (bit `1`) |
| idem | `MENUDOWN=$69`, `MENUUP=$E9` | Front droit (bit `2`), `WFLG_RMBTRAP` conservé |
| idem | `MIDDLEDOWN=$6A`, `MIDDLEUP=$EA` | Front central (bit `4`) |
| `IDCMP_RAWKEY=$00000400` | code brut + `Qualifier` | Touches pressées enregistrées en FIFO pour `Aga Key` / `Aga Wait Key` |
| `IDCMP_ACTIVEWINDOW=$00040000` | — | Remise à zéro des fronts/held, reprise active |
| `IDCMP_INACTIVEWINDOW=$00080000` | — | Invalidation des fronts ; aucun clic fantôme lors d'une reprise |

Le `NewWindow.IDCMPFlags` passe de `$00000400` à **`$000C0408`**. Le `NewWindow.Flags` avec `WFLG_RMBTRAP` reste inchangé.

### Dispatcher central

La routine 68000 commune, entrée AP20 privée, est appelée depuis :
- les fonctions `Aga Mouse Pressed` et `Aga Mouse Released` ;
- les routines déjà existantes `Aga Key` et `Aga Wait Key`, avec conservation de **leurs chemins d'origine Ctrl+C**.

**Aucune suppression silencieuse de RAWKEY :** la routine lit jusqu'à **64 messages par appel** sans attente. Elle copie `Class`, `Code` et `Qualifier` avant `ReplyMsg`, puis répond **exactement une fois** à chaque message `GetMsg`. Les touches `RAWKEY` descendantes sont mises dans une FIFO de **16 entrées** (ordre conservé). Quand la FIFO est pleine, le dispatcher cesse de retirer d'autres messages : les suivants restent dans le `UserPort`, plutôt que d'être perdus. Cela peut retarder les clics en cas de surcharge clavier.

`Aga Key` et `Aga Wait Key` reçoivent les touches conservées sous la forme d'une petite **structure locale synthétique** `IntuiMessage` : elles ne doivent **pas** appeler `ReplyMsg` une deuxième fois sur cette structure. Le décodage RAWKEY, les qualificatifs et les branches Ctrl+C qui existaient en R22 restent inchangés. **Ctrl+C confirmé sous WinUAE :** interruption à `_WAITK=Aga Wait Key` et fermeture correcte de l'écran Intuition (retour utilisateur). Cela ne prouve pas tous les scénarios d'interruption et de focus.

La capture souris mémorise les fronts DOWN et UP de façon indépendante. Un appui très bref DOWN+UP, déjà reçu par Intuition avant le prochain polling, fournit à la fois `Pressed=1` et `Released=1` (puis `0` à la consommation suivante). **Deux clics du même bouton dans un seul intervalle sont fusionnés dans le masque** : ce n'est pas une file/counter de clics multiples.

## États et ressources

- État privé de **144 octets** dans le HUNK de l'extension : fenêtre, masques pending DOWN/UP, état held, indices/count FIFO, focus, structure synthétique, 16 entrées de 4 octets.
- Initialisation à zéro par `Aga Screen Open` ; pas de `AllocMem` persistant.
- Aucun `Exec Wait` ni `WaitPort`, traitement borné et non bloquant.
- Perte de focus : purge de pending souris ; pas de faux appui au retour.
- `Aga Mouse Buttons` garde son contrat R22 d'état instantané global ; seuls Pressed/Released changent de source.
- `Aga Screen Close` continue à répondre aux messages résiduels avant fermeture. La file privée est réinitialisée lors de la nouvelle ouverture.

## Gates

- **Préflight CPU** : **PASS 15 cas 68000** (GitHub Actions #42898784421) : structure HUNK/AP20, registres ABI, FIFO clavier avec saturation, souris DOWN+UP avant une lecture, focus, un ReplyMsg par message, conservation des anciennes branches Ctrl+C. Ce test ne prouve pas le véritable Break sous AMOS.
- **Gate A candidate** : binaire reproductible **13 088 octets**, SHA256 `899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23`. Préflight R23 PASS ; **CI complète PASS** ([run #42899343161](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42899343161)), avec instantanés des tests IFF synchronisés sur l'inventaire actuel sans restaurer les images supprimées.
- **Gate B WinUAE : PASS sur les scénarios testés.** [`tests/passed/M8_R23_IDCMP_QUICK_01.asc`](../tests/passed/M8_R23_IDCMP_QUICK_01.asc) : clics rapides gauche/droit avant la lecture, deux ESPACE conservées, `Aga Wait Key` retourne `WAIT=16` (A AZERTY), `RESULT=1` ; fermeture/réouverture conforme. **Ctrl+C testé séparément** à `_WAITK=Aga Wait Key` : interruption propre et écran Intuition fermé. Le rapport ne certifie pas la gestion de tous les événements de focus.
- **Gate C / D** : AMOS Compiler et Amiga physique non testés.

**Interdictions :** ne pas toucher à `dist/AMOSPro_AGA_LAST_GOOD.Lib`, aux archives R22/R21/R20/R19/R18, ni aux sources IFF ajoutées sur `main` par l'utilisateur. Ne pas annoncer R23 PASS WinUAE sur la base des seuls tests CPU.

## Livrables R23

- `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib`, **13 088 octets**, SHA256 `899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23`.
- **Test WinUAE validé et archivé** : [`M8_R23_IDCMP_QUICK_01.asc`](../tests/passed/M8_R23_IDCMP_QUICK_01.asc), image originale `iff-TEST/AGA_TESTCARD_320x256_256C.iff` (320×256×8).
- Test : initialisation, puis **200 VBL sans lecture souris/clavier**, durant lesquelles cliquer gauche puis droit rapidement et presser **ESPACE deux fois**. Après cette période : `PRESSED=3`, `RELEASED=3`, deuxième lecture `0/0`, `KEYS=64,64,-1` ; une touche quelconque valide `Aga Wait Key` (qui peut aussi renvoyer des modificateurs RAWKEY). Puis `REOPEN=1`, `RESULT=1`, retour normal sous AMOS.
- **Retour utilisateur WinUAE du 10/11/2026, test initial SHA Git `e4bc98083a686e904fd773946fe3e4df3da625ae` :** `OPEN=DB=LOAD=SWAP=REOPEN=1`, `BEFORE=-1/-1`, `INIT=0/0`, `PRESSED=3`, `RELEASED=3`, `AGAIN=0/0`, `KEYS=64,64,-1`, `WAIT=100`, `CLOSED=-1/-1`, `CLOSE2=-1`, `BASE=0/0`, `RESULT=0`, `CLOSE X2 RETURNED`. Retour normal. `WAIT=100` décimal = RAWKEY `$64`, **Alt gauche**, code autorisé par le contrat de `Aga Wait Key`. La première version du test imposait à tort ESPACE `64`, la révision courante accepte une touche RAWKEY valide (`WAIT>=0`) ; elle reste à rejouer. Le code 100 ne prouve pas que l'utilisateur ait volontairement appuyé sur Alt. **Binaire inchangé.**
- **Deuxième capture validée :** Deuxième capture WinUAE (10/11/2026) : sur la mire originale 320×256×8, `OPEN=DB=LOAD=SWAP=REOPEN=1`, `BEFORE=-1/-1`, `INIT=0/0`, `PRESSED=3`, `RELEASED=3`, `AGAIN=0/0`, `KEYS=64 64 -1`, `WAIT=16` (`$10`, position Q en QWERTY / A en AZERTY français, touche **A** confirmée par l'utilisateur), `MOUSE=(204,160)`, `CLOSED=-1/-1`, `CLOSE2=-1`, `BASE=0/0`, `RESULT=1`, `CLOSE X2 RETURNED`. Capture du récapitulatif final uniquement : pas de preuve visuelle du menu pendant l'appui droit. Ctrl+C testé ensuite séparément : arrêt à `_WAITK=Aga Wait Key`, fermeture correcte de l'écran Intuition. La bibliothèque est inchangée par rapport au premier essai ; la différence `WAIT 16` correspond à la touche **A** d'un clavier AZERTY. Ce scénario passe maintenant `RESULT=1`. Le test exact est maintenant archivé dans `tests/passed/`.
- **Limites** : FIFO clavier 16, dispatcher 64 messages par appel ; plusieurs clics du même bouton avant lecture fusionnés dans le masque. Focus réel et stress à valider sous WinUAE ; Ctrl+C a passé le scénario d'interruption et fermeture. R22 archive WinUAE PASS et `LAST_GOOD` R10 inchangées.

## Sources et outils

- [Émetteur R23](../tools/m8_idcmp_r23_emit.py)
- [Builder R23 reproductible](../tools/build_m8_idcmp_r23.py) et [bibliothèque R23 validée sur ces scénarios](../dist/AMOSPro_AGA.Lib)
- [Préflight CPU R23](../tools/test_m8_idcmp_r23_preflight.py)
- [Statut M8](M8_STATUS.md) et [roadmap](ROADMAP.md).
