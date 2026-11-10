# M11 — première étude de compatibilité graphique AMOS/AGA

## Objectif et état

**M11 commence par un diagnostic, pas par une nouvelle bibliothèque R26.** Bibliothèque de référence : **R25 0.9.1** (30 commandes AP20), Gate A CPU/CI et Gate B AMOS interprété/WinUAE validées **sur le scénario R25 archivé**. `dist/AMOSPro_AGA.Lib`, son archive R25, R24 et `LAST_GOOD` R10 restent inchangés.

L'écran AGA de l'extension est ouvert via **Intuition/AmigaOS** et n'est pas nécessairement l'écran AMOS courant. Les commandes graphiques natives `Text`, `Screen Copy`, `Paste Bob` et les extensions AMCAF/Turbo peuvent donc utiliser des **RastPorts, bitplanes et écrans différents**. Il faut le vérifier avant d'inventer une API de dessin, des commandes de fonte ou des accès à `ScOnAd` / `Ec_RastPort`.

## Expérience M11-01 : texte graphique natif

**Programme unique en cours :** [`tests/current/M11_R25_AMOS_TEXT_01.asc`](../tests/current/M11_R25_AMOS_TEXT_01.asc), bandeau `M11-R25-AMOS-TEXT-01`. **Aucun binaire modifié. Gate B M11 non testée.**

Commande AMOS existante (syntaxe documentée) : `Text x,y,texte$`, par exemple :

```amos
Ink 2
Text 52,110,"AMOS TEXT VISIBLE?"
```

Référence syntaxique : [manuel AMOS Professional — Fonts / TEXT](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMOSProManual/11/1103.html). Cette commande appartient à AMOS, **pas** à l'extension AP20.

### Recette WinUAE

1. Utiliser la bibliothèque R25 déjà installée et **redémarrer AMOS** si nécessaire. Importer le seul `.asc` courant par **Project → Merge ASCII**.
2. Choisir `examples/demo.iff` (ou `iff-TEST/AGA_TESTCARD_320x256_256C.iff`), mire PAL 320×256×8. Ici l'IFF apporte mode/palette, pas une image à conserver.
3. Observer le **panneau bleu** affiché dans l'écran Intuition AGA pendant **300 VBL**. Le test dessine le panneau dans **les deux buffers**, les présente avec `Aga Swap`, puis appelle le **`Text` natif d'AMOS** après `Amos To Back`.
4. Noter si **`AMOS TEXT VISIBLE?` apparaît DANS le panneau bleu pendant que l'écran AGA est ouvert**. Si le texte apparaît uniquement après le retour à AMOS, il a probablement été écrit sur l'écran AMOS. Si aucun texte n'est visible, ce seul essai ne démontre pas une impossibilité de compatibilité via un RastPort/une passerelle.
5. Attendre la fermeture automatique et fournir la capture de la console. Les jalons attendus sont `DRAWERR 0` et `CLOSE RETURNED` ; **il n'y a pas encore de verdict automatique pour la visibilité du texte**.

**Interprétation prudente :** l'essai est destiné à distinguer l'effet visible d'une commande AMOS existante, pas à confirmer la compatibilité AMCAF, ni le bon rendu de toutes les polices, ni une prise en charge native de l'écran par AMOS. En cas d'erreur de syntaxe ou de fonctionnement, conserver le message exact sans modifier la Lib R25.

## Ordre d'étude après ce test

- **Fontes AMOS/AMCAF :** retrouver et vérifier les sources/contrats de `Change Bank Font`, `Scrn Rastport`, `Text` et `Text Length`. Ne pas attribuer à l'écran Intuition de l'extension un RastPort AMOS par hypothèse.
- **Palette :** étudier une solution explicite de définition de couleurs AGA, utile pour supprimer la dépendance à un IFF dans les démos dessinées au Blitter. Aucun nom de commande ni signature R26 n'est décidé.
- **Copies et objets :** distinguer `Aga Blit Copy` (copie dans le back buffer) de `Screen Copy` (autres écrans) et tester séparément Bob/Icon, transparence, masques et commandes Turbo.
- **Gates :** (A) contrats/syntaxe/CI ; (B) essai sous AMOS interprété/WinUAE ; (C) Compiler ; (D) vrai Amiga. Un résultat B ne valide pas C ou D.

**Précautions :** un seul `.asc` dans `tests/current/` ; ne pas archiver avant retour utilisateur ; ne pas générer de R26 ni de branche. Préserver R25/R24, `LAST_GOOD` et les tests exacts de `tests/passed/`.
