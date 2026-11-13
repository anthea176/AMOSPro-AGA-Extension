# M18/R60 v0.13.5 — AGAPIC Image Region (candidate)

**12 novembre 2026.** Développement directement sur `main`. **Unique binaire de travail** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **35 056 octets**, SHA256 `00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8`. **R59 v0.13.4 `LAST_GOOD` inchangée** (32 984 octets, SHA256 `00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d`). Aucune nouvelle branche, archive ou binaire alternatif.

## Fonctionnalité et API

```amos
_OK=Aga Image Region(Bank,SrcX,SrcY,Width,Height,X,Y,Mode)
```

Fonction entière additive n°54 ; **54 commandes / 61 entrées AP20**. Le bloc monolithique Compiler V2 atteint **32 798 octets**, donc dépasse 32 Kio sans bourrage artificiel. **Code nouveau : 2 012 octets 68000**, offset 30 752 dans le code natif. Les 53 signatures R59 antérieures sont préservées.

- `Bank` : numéro AMOS 5..65535 d'une banque DATA AGAPIC v1 vivante. Résolution par `Bnk.GetAdr` sur l'ABI AMOS365, pas par un pointeur conservé.
- `SrcX,SrcY,Width,Height` : rectangle **entièrement inclus** dans la source, X/Y positifs, dimensions non nulles ; tout débordement entraîne retour 0 sans écriture.
- `X,Y` : destination sur le **back buffer privé AGA inactif** ; clipping aux quatre bords, sans arrondi d'alignement ; dessin hors écran valide (retour 1).
- `Mode=0` : opaque, y compris index 0 ; `Mode=1` : masque AGAPIC indépendant (le bit 0 conserve le pixel destination).
- Vérification stricte du RLE et de la banque avant dessin, `Safe` non bloquant, aucun Swap/VBL/Blitter/palette implicite. CPU peut lire depuis la Fast RAM et dessiner en Chip RAM ; le placement réel de la banque doit être mesuré, pas déduit de ses flags.

Les images restent au format AGAPIC **v1**, aucune nouvelle compression ni gestion de frames automatique dans la Lib. Une animation est contrôlée par le programme, qui choisit le rectangle de frame voulu.

## Gate A et vérifications

**Gate A native CPU 68000 / CI : PASS** — [run 43318155860](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43318155860) : **86 scénarios réels Unicorn M68000**, validation pixels, masquage, modes, clipping, refus sans altérer le back buffer, bank lookup, pile A3/A7, registres, `Safe`, absence d'allocation/d'écriture front, stubs AP20 simulés en interprété **et** séparés comme Compiler. [Reconstruction reproductible et candidat 35 056 octets](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43318332456) ; module de test [`test_m18_r60_image_region.py`](../tools/test_m18_r60_image_region.py). **Un test CPU avec layout Compiler simulé n'est pas une Gate C WinUAE.**

**Gates A/B/C : PASS sur leurs scénarios respectifs.**

**Gate B AMOS interprété et Gate C nouvel exécutable Compiler V2 sous WinUAE : PASS (captures de l'auteur, 13/11/2026).** Même ASC R60 : `OPEN 1 DB 1 SW0 1 SAFE 1`, `FRAMES 1 1 1 1 SHIFT 1`, `CLIP 1 1 1 1 OUT 1`, `BAD BANK/X/Y/W/M 0 0 0 0 0`, `LEGACY 1 SWAP 1 NOS 0 CLOSE -1`, `RESULT 1`, `CLOSE RETURNED`. Les quatre sous-images et l'image complète héritée s'affichent, sans Guru visible. La mémoire Chip libre reste identique dans chaque test : **interprété 1 831 960 → 1 831 960, compilé 1 864 456 → 1 864 456**. L'interruption interprétée à la ligne 143 (`Wait Vbl`) est celle de la boucle finale volontaire et ne constitue pas un plantage. Ce PASS ne couvre pas tous les scénarios des 54 commandes.

**Gate D Amiga AGA physique : NON TESTÉE.** Aucun benchmark des performances R60 effectué.

**Seul ASC actif :** [`tests/current/M18_R60_IMAGE_REGION_01.asc`](../tests/current/M18_R60_IMAGE_REGION_01.asc), requiert [`M16_AGAPIC_SAMPLE_BANK10.abk`](../tests/current/M16_AGAPIC_SAMPLE_BANK10.abk) dans le répertoire AMOS. **Attention : `Load` remplace la banque 10** ; faire le test dans une configuration jetable. Le programme affiche quatre sous-images, un rectangle X décalé, les quatre clips, erreurs source, contrôle d'une commande R59 ancienne et fermeture.

**Attendu** : `FRAMES 1 1 1 1 SHIFT 1`, `CLIP 1 1 1 1 OUT 1`, `BAD BANK/X/Y/W/M 0 0 0 0 0`, `LEGACY 1`, `RESULT 1`, `CLOSE RETURNED`, sans Guru. La boucle finale `Do / Wait Vbl / Loop` s'arrête manuellement. Les retours numériques ne suffisent pas à qualifier un rendu incorrect : contrôler visuellement les sous-images.

**R60 non promue** : Gates B/C confirmées, régression complète sur le SHA exact de pré-release et accord explicite de l'auteur requis avant remplacement de `LAST_GOOD`. CBlock et `F 16 Icon` restent des lots séparés M18 ; pas de choix CPU/Blitter AUTO avant mesures.

## Sources

- [Émetteur 68000](../tools/m18_image_region_emit.py)
- [Builder SHA-pinné depuis R59](../tools/build_m18_r60_image_region.py)
- [Test natif CPU et ABI](../tools/test_m18_r60_image_region.py)
- [Contrat M18 / atlas P0](M18_AGAPIC_ATLAS_P0.md)
