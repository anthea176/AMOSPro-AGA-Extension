# Prompt de reprise — Démo RPG AGA / AMOS Professional

> À utiliser **uniquement après correction et validation des anomalies natives** de l'extension AGA (SafePort/B8, accès IFF aux pages, interactions avec les snapshots et régressions des commandes graphiques).
>
> Ce document est un **prompt pour une future conversation**, pas une demande de correction immédiate.

## PROMPT À COPIER DANS LA NOUVELLE CONVERSATION

Nous reprenons **le chantier de démonstration RPG AGA sous AMOS Professional**, laissé en attente à cause de problèmes natifs de `AMOSPro_AGA.Lib`. L'objectif est de faire fonctionner une **vraie scène RPG avec un décor IFF et un personnage mobile géré par Bob AGA persistant**, sans revenir à des artifices BASIC pour contourner les défauts de la bibliothèque.

### 1. Vérifier les prérequis AVANT de reprendre

- Dépôt : `anthea176/AMOSPro-AGA-Extension`, **branche `main` uniquement**. Ne jamais créer ou utiliser une autre branche sans mon autorisation explicite.
- Lire sur le **dernier `main`** : `EXTENSION_SOURCE_RULES.md`, `docs/NEXT_SESSION.md`, `tests/current/README.md`, les API et les sources natives correspondant à la bibliothèque réellement installée.
- Vérifier la **version, le builder, les SHA et le statut des Gates** de la bibliothèque corrigée. **Ne pas supposer que P2d est encore la bibliothèque courante** : le chantier Sprite S1 a continué après P2d.
- Confirmer que les anomalies identifiées dans l'audit transversal sont corrigées ou, si ce n'est pas le cas, que le test RPG concerné est explicitement autorisé et sûr. En particulier :
  - premier `Aga Bob Update` / `Aga Bob Auto Update(1)` après `Aga Swap`, avec Safe pending ;
  - `Aga Iff Load` sur le back buffer après Swap ;
  - cohérence des sauvegardes de fond B8 après écriture du décor ;
  - conservation du comportement Bob et Sprite, absence de refus persistant, nettoyage à `Aga Screen Close`.
- **Si les corrections ou leurs preuves manquent, ne pas inventer une nouvelle V10.** Faire d'abord le constat précis des prérequis manquants.
- Ne modifier ni `dist/AMOSPro_AGA_LAST_GOOD.Lib`, ni les exemples distribués, ni le banc actif, et ne pas remplacer la Lib sans demande explicite.

### 2. Point de départ : ce qui existait

Cible du POC : AMOS Professional + extension AGA native, CPU **MC68020+**, PAL **320 × 256 × 8 bitplanes / 256 couleurs**, mode `$00021000`, double buffering AGA.

Ressources réelles :

- `RPG_BG.iff` : décor IFF ILBM 320×256×8, palette 256 couleurs.
- `RPG_HERO_SOURCE.iff` : source IFF ILBM 320×256×8, personnage **20×18 pixels à l'origine (0,0)** ; index 0 transparent, capture et masque natifs AGBO.
- Environnement précédent : `DH6:examples/demo/RPG_BG.iff` et `DH6:examples/demo/RPG_HERO_SOURCE.iff` ; sous Windows le dossier a été signalé comme `F:\[Github] AMOSPro-AGA-Extension\examples\demo\`. **Vérifier les chemins existants au moment de la reprise** et ne pas déplacer les ressources sans nécessité.

Dernier programme : `RPG_MOVE_AGA_BOB_SAFE_FIRST.asc` (**V9**), à reprendre comme **témoin d'échec, non comme version validée**. Le programme vérifie l'IFF, crée la banque AGBO **24** via `Aga Bob Bank`, capture l'image **1** avec `Get AGA Bob 1,0,0,19,17`, crée le masque `Make AGA Bob Mask 1,0`, puis charge le décor sur les deux pages et active `Aga Bob Auto Update(1)`.

Contrôles du prototype : **flèches pour déplacer** le personnage (pas 3 pixels), **miroir horizontal** via `Aga Bob Flip`, **Échap pour sortir**, déplacement borné dans la zone **192×192** du décor. Bob initial à **(84,84)**. Fermeture AGA et retour à AMOS obligatoires.

### 3. Échec historique à ne pas oublier

Le journal réel de V9 `RPG_P2D_V9_RUNTIME.TXT` contient :

```text
TEST RPG_MOVE_AGA_BOB_V9_SAFE_FIRST
PRG_STATE 1
RESULT 0
ERR 14
STAGE FIRST BOB AUTO SWAP
BG0 1
BG1 1
AUTO 1
BG_SWAP 1
BOB_SWAP 0
GET_X 84
GET_Y 84
GET_IMAGE 1
SHEET_IFF_LOAD 1
BANKLEN 720
BANKMASK 1
FRAMES 0
PRE_SWAP_VBLS 2
EXPLICIT_BOB_UPDATE 0
SWAP_RETRIES 4
CLOSE_RETURNED 1
```

La V8 échouait au premier `Aga Bob Update` explicite ; la V9 échouait au premier Swap avec Auto Update, **même avec plusieurs attentes VBL**. La bibliothèque P2d testée avait SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`. Ne pas en déduire que la bibliothèque réparée a le même comportement sans l'essayer.

L'audit Codex a identifié dans l'ancienne P2d un défaut d'amorçage : un sélecteur B8 refusait le premier Bind avec Safe pending avant que la notification SafePort puisse être consommée. Il a aussi signalé l'écriture IFF sans acquisition Safe appropriée. Ces conclusions sont étayées par la lecture des sources et du binaire ; leur correction et la validation dynamique **doivent être vérifiées sur le nouveau code**.

À l'inverse, les tests natifs P2d avec décor généré par Blit Fill ont démontré qu'un Bob **20×18** et son pixel opaque (19,17) étaient dessinables ; la taille du Bob n'est donc pas, à elle seule, une cause démontrée.

### 4. Objectif de reprise — limité à la démo RPG

Réaliser un programme AMOS `.asc` **simple, robuste, autonome hors ses deux IFF** :

1. Charger le personnage depuis son IFF, capturer son image en AGBO avec masque, et afficher un vrai décor IFF sur les deux pages.
2. Réussir le **premier affichage d'un Bob persistant**, sans `Aga Blit Fill` artificiel juste pour amorcer SafePort et sans double appel contradictoire `Aga Bob Update` / Auto Update.
3. Permettre le déplacement aux flèches dans la zone prévue et le flip gauche/droite, sans fantômes, corruption du décor, flicker anormal ni décalage de coordonnées.
4. Vérifier les retours de toutes les commandes sensibles, arrêter proprement en cas d'échec, journaliser l'étape fautive, fermer l'écran et libérer la banque créée.
5. Garder l'application **exclusivement une démo technique de déplacement** : pas de combat, scrolling, collisions, tiles ou autres nouvelles fonctionnalités dans cette reprise.

### 5. Méthode de travail imposée

- **D'abord** comparer la séquence V9 à l'API corrigée et au banc natif valide sur la même version. Identifier si un changement AMOS est réellement nécessaire ; ne pas refaire le programme intégralement.
- **Ensuite** produire une seule révision ciblée, avec un `SOURCE_TAG` unique, un journal Runtime distinct et une liste précise des différences par rapport à V9.
- Vérifier chaque commande AGA contre le dépôt sur le même commit ; appliquer les règles de syntaxe AMOS Professional, sans constructions BASIC inventées.
- Exécuter le préflight statique de l'ASC exact et les tests associés ; annoncer clairement que le préflight **n'est pas** une compilation ou un test WinUAE.
- Préparer une validation **Gate B Runtime WinUAE** : premier Bob visible, déplacement dans les quatre sens, flip, persistance du décor, fermeture, puis **deux lancements consécutifs** pour traquer les états résiduels.
- Si une validation **Gate C AMOS Compiler** est demandée, compiler ce même programme avec la même Lib et fournir un journal distinct ; ne jamais transférer un PASS Runtime au Compiler.
- Si le programme échoue, analyser **le premier refus natif** à partir des sources et du journal. **Pas de génération en chaîne de V10/V11/V12** sans nouvelle hypothèse discriminante et résultat de test.

### 6. Critères d'acceptation

- Le premier Bob apparaît sur le décor IFF, sans erreur de Swap.
- Le personnage reste visible pendant le déplacement ; le flip ne déforme pas sa position.
- Aucune trace du Bob sur les anciennes positions ; fond intact et pages cohérentes.
- Retours de commandes contrôlés ; aucun refus de Swap persistant, aucun freeze/Guru.
- Sortie Échap : `Aga Screen Close`, `Amos To Front`, banque 24 libérée si créée par le programme.
- Journal complet `RESULT 1`, `ERR 0`, `CLOSE_RETURNED 1` et observations visuelles Runtime correspondantes.
- Deux lancements Runtime consécutifs réussis. Gate C notée **NON TESTÉE** tant qu'aucune compilation et exécution réelles ne sont réalisées.

### 7. Livraison et protections GitHub

- Tant que l'exemple n'est pas officiellement distribuable, **le ranger dans `tests/proto/` et jamais dans `examples/`**.
- Ne pas toucher aux fichiers `tests/current/`, `tests/passed/`, au chantier Sprite, au code natif, aux bibliothèques `dist/` ni à `LAST_GOOD` dans le cadre de cette démo sans demande explicite.
- Pour toute modification GitHub **expressément autorisée**, travailler **uniquement sur `main`**, relire le HEAD juste avant l'écriture et vérifier le fichier après commit. Ne créer aucune branche, aucun autre dépôt.
- Préserver les sources V8/V9 et les journaux d'échec comme témoins, ne jamais les réécrire pour afficher un PASS artificiel.

**Première réponse attendue :** identifier la bibliothèque actuelle et les prérequis validés, confirmer les deux IFF et l'ASC V9 disponibles, puis proposer **le plus petit ensemble de changements** pour rendre la démo fonctionnelle avec la bibliothèque corrigée. Ne pas commencer par modifier la Lib.

---

## Fichiers à joindre si la nouvelle conversation n'y a pas accès

- `RPG_MOVE_AGA_BOB_SAFE_FIRST.asc` (V9)
- `RPG_P2D_V9_RUNTIME.TXT` (échec historique)
- `RPG_BG.iff`
- `RPG_HERO_SOURCE.iff`
- Compte rendu final de l'audit transversal et SHA de la bibliothèque corrigée, si disponibles

**État lors de la rédaction (23/11/2026) :** chantier démo RPG suspendu ; aucune correction native ou Gate B de la nouvelle bibliothèque présumée acquise.
