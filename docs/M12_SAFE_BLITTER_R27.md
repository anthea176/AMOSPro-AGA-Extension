# M12 — R27 0.9.3 : sécurisation Safe des Blitters AGA

**11/11/2026 — prototype source uniquement, Gate A CPU/CI à confirmer, Gate B WinUAE NON TESTÉE.** La bibliothèque active reste **R26 0.9.2**, archivée et validée sous WinUAE pour le texte AGA et les 40 swaps [M11](M11_TEXT_R26.md). Aucune archive ni binaire courant, notamment `LAST_GOOD`, n'est modifié par cette étape.

## Problème vérifié dans R26

Après un `Aga Swap` réussi, le buffer anciennement affiché peut rester indisponible en écriture tant que la réponse **Safe** n'est pas reçue. L'ancienne fonction `Aga Text` de R26 gère elle-même cette notification, mais **`Aga Blit Copy`**, **`Aga Blit Fill`** et le wrapper **`Aga Blit Clear`** ne la gèrent pas directement. Le test [R26 à 40 swaps](../tests/passed/M11_R26_SAFE_SWAP_02.asc) employait donc un appel `Aga Text` servant de **sonde** avant chaque Blitter.

Ce protocole a passé les 40 images avec `DONE 40 PROBEOK 40`, `PROBE0 39 SWAP0 0`, erreurs nulles et `RESULT 1`. Ces 39 refus ne démontrent cependant pas que chaque retour `0` provenait exclusivement de Safe ; ce point reste une limite observée.

## Objectif R27 — aucune nouvelle commande AMOS

**Les signatures et les résultats restent identiques :**

```amos
_OK=Aga Blit Copy(sx,sy,dx,dy,w,h)
_OK=Aga Blit Fill(x,y,w,h,pen)
_OK=Aga Blit Clear(x,y,w,h)
```

La routine centrale `_emit_safe_guard`, insérée dans les émetteurs des fonctions **Copy (segment AP20 19)** et **Fill (segment 20)**, s'exécute **après validation de tous les paramètres/bitplanes, mais avant toute commande `BltBitMap`**. La fonction **Clear (segment 21)** appelle déjà Fill en interne : elle hérite de la protection, mais son déplacement relatif `BSR.W` vers Fill doit être **recalculé** lorsque le code Fill grandit.

1. Si `DBState+20` bit0 = 0 : pas de message Safe en attente, continuer immédiatement.
2. Si le bit0 = 1 : contrôler le port `DBState+12`, puis appeler **une seule fois** `Exec/GetMsg(SafePort)`, sans blocage.
3. Si aucun message n'est disponible : **ne dessiner aucun pixel**, restaurer registres/pile et retourner `0`. Aucun `WaitPort`, `Wait` ni `ReplyMsg`.
4. Si le message arrive : vider **seulement** le bit0, conserver le bit1 `Disp`, restaurer `GfxBase` et tous les registres vivants, puis effectuer l'opération graphique existante et `WaitBlit` normalement.
5. `D6` doit absolument être conservé : **Fill l'utilise comme limite `1<<depth`** après la validation de la couleur. Les arguments AMOS et le pointeur `A3` sont conservés exactement dans le contrat existant.

**Sémantique `0` :** refus de dessin (zone/couleur/état invalide **ou** buffer non `Safe`), sans distinction nouvelle. L'appelant peut réessayer **avec une limite** et `Aga Wait Vbl` ; une boucle illimitée sur un `0` est interdite. `Aga Wait Vbl` n'est pas lui-même un accusé Safe. Le `SafePort` et le suivi `Disp` restent ceux de `Aga Swap`, sans second consommateur indépendant.

## Compatibilité binaire et périmètre exact

La candidate est reconstruite **en mémoire** depuis [l'archive R26](../dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib), SHA256 `0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287`. Le format reste **AP20, 37 segments, 31 commandes nommées**, et **la table des tokens est strictement identique à R26**. Seuls trois segments peuvent changer :

- 19 `Aga Blit Copy` : garde Safe avant son unique DMA, `GetP` terminal conservé ;
- 20 `Aga Blit Fill` : même garde avant sa boucle de plans, `GetP` terminal conservé ;
- 21 `Aga Blit Clear` : wrapper historique inchangé dans ses opérations, **seul le déplacement BSR vers le nouvel Fill** peut varier.

Les segments **0–18 et 22–36** sont conservés octet pour octet : écran, `Aga Swap`, `Aga Wait Vbl`, `Aga Back Fill` historique, `Aga Text` R26 et les fonctions souris/collision ne sont pas modifiés. **`Aga Back Fill` (ancienne commande autonome, segment 12) n'est pas incluse dans la protection R27** et reste à distinguer des trois `Aga Blit ...` couvertes. Ce périmètre évite une modification implicite d'une fonction WinUAE-validée sans contrat complémentaire.

## Validation exigée

**Gate A 68000/CI avant tout binaire publié :**

- [Émetteur des fonctions Copy/Fill](../tools/m12_blit_safe_r27_emit.py), [builder HUNK en mémoire](../tools/build_m12_blit_safe_r27.py) et [tests CPU Unicorn](../tools/test_m12_blit_safe_r27.py).
- Vérifier l'identité de la table de tokens, la différence limitée aux trois segments, le `BSR.W` exact de Clear, les instructions 68000 (Capstone), ABI `D2/D3/A3/SP` et les registres non volatils.
- Pour Copy/Fill/Clear et les deux valeurs de `frontIndex` : bit Safe nul, bit Safe en attente avec message absent/présent, bit Disp seul ou combiné, port Safe nul, géométrie invalide, préservation du buffer en cas de refus, `GetMsg` au plus une fois par appel.
- Vérifier que des appels répétés après consommation du message ne le consomment pas une deuxième fois ; simuler des alternances de 40 images. Ne pas écrire de `R27.Lib` avant un Gate A **PASS**.

**Gate B (à venir, WinUAE) :** créer un unique `.asc` après Gate A et l'installation d'une **candidate R27**, sans sonde `Aga Text` avant les anciens Blitters : **40 images vert/rouge** en sonde par `Aga Blit Clear`, puis Fill/Copy, Swap et VBL bornés. Contrôler une alternance visuelle, les compteurs de refus/reprises, absence d'écriture avant Safe, fermeture correcte à AMOS. **Ne pas demander d'essai WinUAE de R27 tant que la candidate n'a pas été vérifiée en CPU.**

**Gates C/D :** AMOS Compiler et Amiga AGA physique restent NON TESTÉS. Aucune mesure 50 FPS ni validation exhaustive de course mémoire ne découle automatiquement de 40 alternances.

**Règles de projet :** travailler uniquement sur `main` ; ne pas ouvrir de branche, ne pas remplacer R26/R25/R24, ne pas promouvoir `LAST_GOOD` R10, ne pas modifier les tests déjà archivés.
