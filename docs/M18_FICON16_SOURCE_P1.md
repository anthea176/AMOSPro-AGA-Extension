# M18/P1 — Audit Fast Icons 16×16 et modèles CPU/Blitter

**13 novembre 2026 — main uniquement, P1 HÔTE, aucune Lib R61 produite.**
Référence protégée : R60 v0.13.5 LAST_GOOD, 35 056 octets, SHA256
00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8.

## 1. Source primaire retrouvée : AMOS Professional Unity SpecialFX

Fichier assembleur original :
[AmiDARK / AMOSProUnity_SpecialFX.s](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s).

| Emplacement source | Constat vérifié |
|---|---|
| [L53–63](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L53-L63) | En-tête : taille long, compte/largeur/hauteur/profondeur mots ; données à l'offset 12. |
| [L159–170](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L159-L170) | Noms exacts : Reserve F Icon, Set Current F Icon Bank, Get Current F Icon Bank, Get F Icon, **Paste F Icon**, avec surcharge 3 ou 4 arguments. |
| [L1155–1196](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L1155-L1196) | Banques dédiées DATA/Fast numéro **6 à 255**, au moins **4 icônes**, largeur/hauteur **16×16**, **8 plans AGA**, 6 ECS ; réservation de 9 mots par ligne. |
| [L1225–1229 et L1295–1304](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L1225-L1229) | Lignes dans l'ordre : masque 16 bits puis mots de plan ; numéro d'icône 1-based, offset fixe à partir du numéro. |
| [L1382–1398](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L1382-L1398) | Le masque est le complément de l'OR des plans de couleur : **index 0 transparent** en mode masqué. |
| [L1416–1587](https://github.com/AmiDARK/AmosProfessionalUnity-SourceCode/blob/main/src/APULib_SpecialFX/AMOSProUnity_SpecialFX.s#L1416-L1587) | **Paste F Icon IconID,X,Y[,Transparency]** copie les mots avec le CPU ; **X ET Y rabattus au multiple de 16** ; opaque ou masqué. |

**Ne pas confondre trois commandes historiques :**

1. **Paste Icon**, AMOS Professional standard : banque Icon 2, Blitter, coordonnées quelconques ([manuel](https://amospromanual.dev/07-07-icons-and-blocks.html)).
2. **F Paste Icon**, AMOS Turbo Plus : accélération citée dans la [discussion AMOS](https://www.amigaimpact.org/forums/topic/amos-professional-x-devient-unity/), syntaxe/implémentation Turbo non auditées à la source.
3. **Paste F Icon**, AMOS Professional Unity SpecialFX : **source primaire vérifiée**, banque Fast 16×16 et copie CPU.

Le nom **« F 16 Icon »** de notre objectif peut décrire la troisième, mais ce nom littéral n'a **pas** été retrouvé comme instruction. N'affirmer aucune identité binaire ou sémantique entre Turbo et Unity.

## 2. Contrat de banque 16×16 (prototype AGA)

Format de test : en-tête big-endian **12 octets** (long taille totale, mots compte, largeur=16, hauteur=16, profondeur=8). Par ligne, **1 masque + 8 mots de plan = 18 octets** ; par icône **16 × 18 = 288 octets** ; taille totale **12 + 288 × compte** ; ID **1..compte**. Pas de RLE.

Le prototype limite volontairement le compte à 4096, **ce n'est pas une limite prouvée du code historique**. Il refuse pour l'instant les banques ECS de profondeur 6 : le code d'affichage d'origine utilise un pas constant de 18 octets qui mérite une étude dédiée.

**Différences explicites à conserver :**
- Mode historique Unity : X/Y alignés vers le bas sur 16 ; couleur zéro transparente en mode masqué (complément de l'OR des plans).
- Mode AGA proposé : **rendu pixel exact**, clipping aux quatre côtés ; pas d'arrondi implicite de X/Y ; copie dans le seul back buffer privé.
- **AGAPIC v1 de R60** : compressé RLE par lignes et masque **indépendant** ; une couleur 0 peut y être opaque. **Une conversion en Fast Icon Unity perd donc une partie des possibilités de transparence** sans politique explicite.
- Ces banques Fast Icon ne sont ni la banque Icon 2 standard ni une banque AGAPIC v1 : **interdit de les charger avec Aga Image Region** sans conversion.

## 3. Travail réalisé sur les modèles Python

- [m18_ficon16_model.py](../tools/m18_ficon16_model.py) : génération/validation de la banque historique 8 plans, rendu **CPU au pixel**, et rendu indépendant **par mots planaires simulant le travail d'un Blitter** (décalage, masque, clipping).
- [test_m18_ficon16_model.py](../tools/test_m18_ficon16_model.py) : contrôle des octets, rendu comparé à un oracle indépendant, rejet des corruptions et paramètres invalides sans écriture, garde mémoire et second buffer inchangé.
- Le chemin arithmétique Blitter est un **modèle logiciel, pas une exécution DMA** ; une source Fast impose un staging explicite dans le modèle, compté à **288 octets par icône**.

**AUCUNE mesure de vitesse CPU/Blitter Amiga n'est revendiquée.** Les compteurs d'opérations ne sont pas comparables à des cycles. Le benchmark futur doit inclure les copies Fast→Chip, installation des registres Blitter, attente, contention et mémoire réellement placée, sur WinUAE et idéalement matériel.

## 4. Suite avant toute R61

À décider sur contrat, sans toucher R60 LAST_GOOD : commande 16×16 numérotée et banque sélectionnée explicitement ; si conversion AGAPIC, sort du masque indépendant ; mode historique 16 pixels **optionnel** versus pixel exact par défaut ; chemins CPU Fast→Chip et Blitter Chip→Chip identiques bit à bit ; Gateway AP20/Compiler V2 validée par Gate A native puis B et C WinUAE avec un seul ASC actif.

**Après les icônes, terminer CBlock AGA pixel-exact avant 68020+ puis c2p.library.** Pas de nouvelle bibliothèque native, ASC ni publication Aminet dans ce P1 hôte.
