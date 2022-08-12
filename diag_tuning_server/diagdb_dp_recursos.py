#!/usr/bin/env python3
"""
Proyecto: Herramienta de Diagnóstico del Rendimiento de BDs PostgreSQL
Módulo:   1. Diagnóstico preliminar de la BD
Script:   1.1. Script para obtener recursos disponibles del servidor.
Nombre:   pardb_dp_recursos.py
Versión:  1.0

Autor:    Jose Luis Pérez R.
Creación: 27-julio-2022
Ult.Mod.: 27-julio-2022
"""

import sys
import json
import psutil
import getopt
import platform
from math import floor, log
from conf.constants import *

resource = {}

def to_size_string(n):
    f = int(floor(log(n, K)))
    return "%d%s" % (int(n/K**f), SIZE_SUFFIX[f])

def beautify(n):
    if type(n) is int and n > K:
        return to_size_string(n)
    return str(n)

def arquitectura():
    resource['server'] = {
        'architec': platform.architecture()[0],
        'machine': platform.machine(),
        'systemName': platform.system(),
    	'osVersion': platform.version(),
    	'osRelease': platform.release(),
    	'node': platform.node()}
    
def cantidad_cpus():
    resource['cpu'] = {
    	'logicalCPUs': '16',
    	'physicalCPUs': '8'}

def memoria():
    resource['memory'] = {
    	'total': beautify(psutil.virtual_memory()[0]),
    	'available': beautify(psutil.virtual_memory()[1]),
    	'percent': psutil.virtual_memory()[2],
    	'used': beautify(psutil.virtual_memory()[3]),
    	'free': beautify(psutil.virtual_memory()[4]),
    	'shared': beautify(psutil.virtual_memory()[9])}

def disco():
#    part = psutil.disk_partitions()
#    for x in range(len(part)):
#        unit = part[x][1]
    unit = '/'
    disp = psutil.disk_usage(unit)
    resource['disco'] = {
    	'total': beautify(disp[0]),
    	'used': beautify(disp[1]),
        'free': beautify(disp[2]),
    	'percent': disp[3]}

def usage_and_exit():
    print("")
    print("Diagnóstico del Rendimiento de BDs PostgreSQL")
    print("[1.1] Script para obtener recursos disponibles del servidor.")
    print("")
    print("Uso: %s [-o] [-h]")
    print("")
    print("donde:")
    print("  -o        : print the available resources in json format")
    print("  -h        : print this help message")

    sys.exit(1)

def json_and_exit():
    recursos_main(True)

    sys.exit(1)

def recursos_main(output):
    arquitectura()
    cantidad_cpus()
    memoria()
    disco()

    if output:
        data = json.dumps(resource, indent=4)
        print(data)
        with open('server_resources.json', 'w') as file:
            json.dump(resource, file, indent=4)

    return resource

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'oh')

        for opt, arg in opts:
            if opt == '-o':
                json_and_exit()
            elif opt == '-h':
                usage_and_exit()
            else:
                print('invalid option: %s' % opt)
                usage_and_exit()
    except getopt.GetoptError as err:
        print(err)
        usage_and_exit()

    recursos_main(True)

if __name__ == '__main__':
    main()