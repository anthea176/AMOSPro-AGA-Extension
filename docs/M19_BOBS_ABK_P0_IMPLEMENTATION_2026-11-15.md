# M19 — Prototype P0 banque Bob AGA multi-images

Référence obligatoire : docs/M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md, commit d00298d. Branche main exclusivement.

## Statut réel

Modèle hôte IMPLEMENTE : format ABK DATA multi-images, image planaire non compressée de 1 à 8 plans, masques 1-bit indépendants, capture à bornes inclusives sur tampons simulés, remplacement transactionnel, sérialisation et relecture. 8 tests Python locaux PASS.

NON IMPLEMENTE : tokens AP20 natifs Aga Bob Bank et Get AGA Bob, gestion réelle des banques AMOS dans la bibliothèque, allocation et préparation automatique en Chip RAM, TypeOfMem/MEMF_CHIP DMA, écrans AGA Safe, masques natifs, animation.

PREPARE seulement : tools/m19_bobs_ap20_feasibility.py, sondage structurel des deux entrées AP20 sur l'archive R88 SHA-vérifiée. Ce script crée en mémoire des stubs 68k factices NON INSTALLABLES ; aucune Gate A/B/C ne peut en découler directement. Pas encore exécuté avec les binaires du dépôt.

## Format binaire P0 provisoire

- Une seule banque AMOS DATA, enveloppe AmBk traditionnelle de 20 octets, nom AGABOB suivi de 2 espaces, numéro de banque AMOS 5..65535.
- Payload de 131072 octets, capacité fixe provisoire pour éviter les Bnk.Reserve destructifs lors de changements d'image. Capacité réelle mémoire à réévaluer avant API native.
- En-tête 40 octets big-endian : magic AGABOB01 (8), version WORD=1, slots WORD=128, count WORD, flags WORD=0, capacity LONG=131072, used LONG, dir_offset LONG=40, entry_size LONG=24, data_offset LONG=3112, reserved LONG=0.
- Répertoire de 128 entrées (ID 1..128), 24 octets chacune : ID, width, height, depth, stride, flags (tous WORD), pixel_offset, mask_offset, extent (tous LONG).
- Les pixels sont planaires, jamais RLE, depth 1..8, stride = 2*ceil(width/16) par ligne, bourrage zéro ; plans concaténés.
- Le masque indépendant facultatif suit les pixels, un seul plan, bit 1 visible ; un pixel index 0 sans masque demeure opaque.
- Les données commencent à l'offset 3112 ; aucune mutation n'est publiée si la capacité est dépassée. Les images non modifiées sont conservées.

## Fichiers

- tools/m19_agabob_abk.py : codec hôte et capture planaire sur buffers simulés.
- tools/test_m19_agabob_abk.py : lancer python -B tools/test_m19_agabob_abk.py.
- tools/m19_agabob_fixture.py : lancer python -B tools/m19_agabob_fixture.py pour créer M19_BOBS_HERO_BANK10.abk.
- tools/m19_bobs_ap20_feasibility.py : lancer python -B tools/m19_bobs_ap20_feasibility.py à la racine du dépôt avec les archives R84/R88 ; test de structure uniquement.
- tests/fixtures/m19_bobs/M19_BOBS_HERO_BANK10.abk : **asset ABK réel archivé dans le dépôt**, indépendant du ZIP et de GitHub Actions.
- tests/design/M19_BOBS_ABK_P0_LOAD_SAVE_01.asc : programme AMOS à exécuter via Project -> Merge ASCII, qui vérifie Load, Save, Erase, Load du fixture ; NE FAIT PAS appel aux nouveaux tokens absents.

## Fixture canonique — asset GitHub présent

**Fichier ABK versionné :** [tests/fixtures/m19_bobs/M19_BOBS_HERO_BANK10.abk](../tests/fixtures/m19_bobs/M19_BOBS_HERO_BANK10.abk). Voir [le README des assets](../tests/fixtures/m19_bobs/README.md) pour la copie **conjointe** de l'ABK et du test ASC dans le répertoire courant AMOS.

Banque 10 : image 1 31x19x4 masque index 0, image 2 37x20x8 masque index 27, image 3 1x1x1 non masquée. 131092 octets (enveloppe comprise), SHA256 b98aff949c0d2d28797c1a72dca66b466ffdbc2fffeb851669971b430e8a1ca6.

## Gates séparées

| Controle | Etat |
| --- | --- |
| Tests hôte P0 | 8 PASS localement |
| AP20 structural | PREPARE, non exécuté |
| Gate A native M19 | NON TESTE |
| Gate B WinUAE Runtime M19 | NON TESTE |
| Gate C Compiler M19 | NON TESTE |
| Gate D matériel | NON TESTE |

Étape suivante : exécuter la faisabilité AP20 et le roundtrip AMOS ; implanter en natif Aga Bob Bank avec Bnk.GetAdr/Reserve/Change sans écraser une banque existante et registre de mémoire propre ; puis Get AGA Bob depuis le back-buffer Safe avec capture planaire et staging automatique Chip vérifié par TypeOfMem/MEMF_CHIP. Tester WinUAE Runtime et Compiler sur les binaires exacts.

Interdits : modifier R84 LAST_GOOD, R88 candidate active, AGAPIC, tests historiques, ASC actif P2.8 ; créer une branche ; promouvoir un binaire sans demande.