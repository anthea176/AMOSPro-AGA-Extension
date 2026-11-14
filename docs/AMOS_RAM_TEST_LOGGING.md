# Protocole permanent des tests AMOS : journal texte RAM:

Établi le 14/11/2026 à partir du fichier fourni par l'auteur M0_R73_MENU_02_RAM_LOG.asc. Le fichier source fourni est un **exemple non qualifié sous AMOS/WinUAE** ; la procédure est appliquée au seul test actif C2P_R76_CONVERT_01.asc, sans annoncer une Gate B ou C de cet ASC modifié.

## Règles

- Un seul tests/current/*.asc à la fois. Pour les nouveaux tests, journal texte RAM:<ID_TEST>_<RUN_MODE>.TXT sur PASS et FAIL si l'épilogue est atteint.
- Prg State vaut **0** en interprété, **-1** en compilé, **1** en runtime. Toujours écrire PRG_STATE et RUN_MODE.
- Pour le CPU sans nouvelle dépendance : lire ExecBase à Leek(4) puis son WORD AttnFlags à Deek(_SYSBASE+296), seulement si le pointeur est non nul. Bits 0/1/2/3/7 = 68010/68020/68030/68040/68060, du moins au plus capable. CPU et CPU_ATTNFLAGS sont des **valeurs signalées par l'OS**, pas un diagnostic matériel absolu. Le code de détection lui-même est à vérifier sur WinUAE et dans une Gate C autorisée.
- Le résultat inclut ID de test, version candidate, RUN_MODE, PRG_STATE, CPU, CPU_ATTNFLAGS, RESULT, VERDICT, erreurs, compteurs, état de fermeture, Chip Free/Fast Free avant-après. Lire les mesures mémoire **avant** Open Out.
- Trap Open Out, Errtrap immédiat, Print #, Trap Close, Errtrap immédiat. Afficher le chemin et les deux erreurs I/O en console. Un log non créé n'est pas une preuve de PASS.
- Finir par End après le compte rendu. Ne jamais maintenir un test sur un Do / Wait Vbl / Loop terminal uniquement pour garder les résultats à l'écran. Les attentes Échap utiles pour regarder une mire ou les attentes VBL bornées de synchronisation restent autorisées.
- RAM: est **volatile**, et Open Out **écrase** les données du même test/mode à chaque exécution. Copier le fichier hors de RAM: avant reset ou nouvel essai pour conserver une archive.
- Un crash/Guru ne permet pas de garantir la création du log final. Regrouper les chemins FAIL contrôlés vers l'épilogue lorsque possible, sans changer le test natif ni masquer les fautes.

## Exemple à adapter au test

~~~amos
' A l'initialisation
_PSTATE=Prg State
_MODE$="UNKNOWN"
_LOGFILE$="RAM:TEST_UNKNOWN.TXT"
If _PSTATE=0
   _MODE$="INTERPRETED"
   _LOGFILE$="RAM:TEST_INTERPRETED.TXT"
End If
If _PSTATE=-1
   _MODE$="COMPILED"
   _LOGFILE$="RAM:TEST_COMPILED.TXT"
End If
If _PSTATE=1
   _MODE$="RUNTIME"
   _LOGFILE$="RAM:TEST_RUNTIME.TXT"
End If
_CPU$="UNKNOWN"
_FLAGS=0
_SYSBASE=Leek(4)
If _SYSBASE<>0
   _FLAGS=Deek(_SYSBASE+296)
   _CPU$="68000"
   If (_FLAGS And 1)<>0
      _CPU$="68010"
   End If
   If (_FLAGS And 2)<>0
      _CPU$="68020"
   End If
   If (_FLAGS And 4)<>0
      _CPU$="68030"
   End If
   If (_FLAGS And 8)<>0
      _CPU$="68040"
   End If
   If (_FLAGS And 128)<>0
      _CPU$="68060"
   End If
End If

' ... apres les operations du test, fermer les ecrans et relever
' _RESULT, _ERR, _CHIP0, _CHIP1 avant ouverture du fichier RAM ...
_VERDICT$="FAIL"
If _RESULT=1
   _VERDICT$="PASS"
End If
_LOGERR=0
_CLOSEERR=0
Trap Open Out 1,_LOGFILE$
_LOGERR=Errtrap
If _LOGERR=0
   Print #1,"TEST IDENTIFIANT"
   Print #1,"RUN_MODE ";_MODE$
   Print #1,"PRG_STATE ";_PSTATE
   Print #1,"CPU ";_CPU$
   Print #1,"CPU_ATTNFLAGS ";_FLAGS
   Print #1,"RESULT ";_RESULT
   Print #1,"VERDICT ";_VERDICT$
   Print #1,"ERR ";_ERR
   Print #1,"CHIP_BEFORE ";_CHIP0
   Print #1,"CHIP_AFTER ";_CHIP1
   Print #1,"CLOSE_RETURNED 1"
   Trap Close 1
   _CLOSEERR=Errtrap
End If
Print "LOG FILE ";_LOGFILE$
Print "LOG OPEN ERR ";_LOGERR;" CLOSE ERR ";_CLOSEERR
End
~~~

Les variables de test doivent avoir été initialisées, et CLOSE_RETURNED ne doit être écrit à 1 que si cette fermeture a réellement été exécutée. Un Open Out sur un fichier du même nom détruit le journal précédent.

## Sources techniques vérifiées

- Manuel AMOS Pro : [Prg State](https://amospromanual.dev/11-04-multitasking.html), [fichiers et Print #](https://amospromanual.dev/10-02-disc-access.html), [Trap/Errtrap](https://amospromanual.dev/12-02-error-handling.html).
- [NDK Amiga ExecBase / AttnFlags](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node009E.html), décalage $128 / 296.
- Contrôle statique de CI : tools/test_current_ram_log.py. Cela ne remplace jamais un essai AMOS/WinUAE réel.
