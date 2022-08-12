#!/usr/bin/env python3
"""
Proyecto: Herramienta de Diagnóstico del Rendimiento de BDs PostgreSQL
Módulo:   1. Diagnóstico preliminar de la BD
Script:   1.4. Script para realizar un análisis comparativo de parámetros, basado en sistemas OLTP.
Nombre:   pardb_dp_ajusta.py
Versión:  1.0

Autor:    Jose Luis Pérez R.
Creación: 03-agosto-2022
Ult.Mod.: 05-agosto-2022
"""

import sys
import json
import getopt
from diagdb_dp_conf_ideal import conf_ideal_main
from diagdb_dp_conf_real import conf_real_main
from conf.constants import *

pfileBoth = {}

def usage_and_exit():
    print("")
    print("Diagnóstico del Rendimiento de BDs PostgreSQL (default %s)" % DEFAULT_PG_VERSION)
    print("[1.4] Script para realizar un análisis comparativo de parámetros, basado en sistemas OLTP.")
    print("")
    print("Uso: %s [-a <dirección_ip>] [-p <puerto>] [-d] <basedatos> [-u] <usuario> [-w] <contraseña> [-o] [-h]")
    print("")
    print("donde:")
    print("  -a <addr>   : nombre del servidor o dirección IP, obligatorio")
    print("  -p <port>   : puerto del servidor, por omisión 5432")
    print("  -d <dbname> : nombre de base de datos a conectarse, por omisión postgres")
    print("  -u <user>   : nombre de usuario, por omisión postgres")
    print("  -w <passwd> : contraseña de usuario, obligatorio")
    print("  -c <conn>   : máximo número de conexiones de cliente concurrentes, por omisión 100")
    print("  -l <addr>   : address(es) on which the server is to listen for incomming connections, default localhost")
    print("  -P <port>   : número del puerto para conexiones, por omisión 5432")
    print("  -s          : habilitar modo de seguridad ssl para conexiones")
    print("  -m          : habilitar parámetros de monitoreo del rendimiento, requiere que la extensión PG_STAT_STATEMENTS esté creada")
    print("  -g          : habilitar trazabilidad (logs) de auditoría")
    print("  -o          : imprime en formato json la comparación de valores a los parámetros, por omisión desactivado")
    print("  -h          : imprime este mensaje de ayuda")

    sys.exit(1)

def compara_main(gen_both, argumsReal, argumsIdeal):
#    argumsIdeal = {}
#    argumsReal = {'host': '192.168.21.9', 'password': 'manager'}

    pfileIdeal = conf_ideal_main(False,argumsIdeal)
    pfileReal = conf_real_main(False,argumsReal)

    if isinstance(pfileReal, dict):
        for key in pfileIdeal:
            if key == 'shared_preload_libraries' and pfileReal[key] != None:
                if str(pfileReal[key]).find('pg_stat_statements') == -1:
                    pfileIdeal[key] = pfileReal[key] + ', ' + pfileIdeal[key]
                    pfileBoth[key] = {
                        'actual': str(pfileReal[key]),
                        'sugerido': pfileIdeal[key]
                    }
            else:
                pfileBoth[key] = {
                    'actual': str(pfileReal[key]),
                    'sugerido': str(pfileIdeal[key])
                }
    else:
        for key in pfileIdeal:
            pfileBoth[key] = {
                'actual': None,
                'sugerido': str(pfileIdeal[key])
            }

    if gen_both:
        data = json.dumps(pfileBoth, indent=4)
        print(data)

    for key in pfileBoth:
        if pfileBoth[key]['actual'] != pfileBoth[key]['sugerido']:
            if key == 'shared_preload_libraries' and pfileReal[key] != None:
                print("alter system set %s to %s;" % (key,pfileBoth[key]['sugerido']))
            else:
                print("alter system set %s to '%s';" % (key,pfileBoth[key]['sugerido']))

    return pfileBoth

def main():
    gen_both = False
    argumsReal = {}
    argumsIdeal = {"monitoring": True}

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'a:p:d:u:w:c:l:P:smgoh')

        for opt, arg in opts:
            if opt == '-a':
                value = str(arg)
                argumsReal['host'] = value
            elif opt == '-p':
                value = str(arg)
                argumsReal['port'] = value
            elif opt == '-d':
                value = str(arg)
                argumsReal['database'] = value
            elif opt == '-u':
                value = str(arg)
                argumsReal['user'] =  value
            elif opt == '-w':
                value = str(arg)
                argumsReal['password'] = value
            elif opt == '-c':
                value = int(arg)
                argumsIdeal['max_connections'] = value
            elif opt == '-l':
                value = str(arg)
                argumsIdeal['listen_addresses'] = value
            elif opt == '-P':
                value = int(arg)
                argumsIdeal['port'] = value
            elif opt == '-s':
                argumsIdeal['ssl'] = True
            elif opt == '-m':
                argumsIdeal['monitoring'] = True
            elif opt == '-g':
                argumsIdeal['logging'] = True
            elif opt == '-o':
                gen_both = True
            elif opt == '-h':
                usage_and_exit()
            else:
                print('invalid option: %s' % opt)
                usage_and_exit()
    except getopt.GetoptError as err:
        print(err)
        usage_and_exit()

    compara_main(gen_both, argumsReal, argumsIdeal)

if __name__ == '__main__':
    main()