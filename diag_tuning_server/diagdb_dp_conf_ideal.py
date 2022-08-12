#!/usr/bin/env python3
"""
Proyecto: Herramienta de Diagnóstico del Rendimiento de BDs PostgreSQL
Módulo:   1. Diagnóstico preliminar de la BD
Script:   1.2. Script para generar parámetros estándar "ideales" basado en recursos disponibles.
Nombre:   pardb_dp_conf_ideal.py
Versión:  1.0

Autor:    Jose Luis Pérez R.
Creación: 28-julio-2022
Ult.Mod.: 28-julio-2022
"""

import sys
import getopt
from datetime import datetime
from diagdb_dp_recursos import recursos_main
from conf.constants import *

params = {}

def usage_and_exit():
    print("")
    print("Diagnóstico del Rendimiento de BDs PostgreSQL (default %s)" % DEFAULT_PG_VERSION)
    print("[1.2] Script para generar parámetros 'ideales' basado en los recursos disponibles.")
    print("")
    print("Uso: %s [-c <conn>] [-l <listen_addresses>] [-p <port>] [-s] [-m] [-g] [-o] [-h]")
    print("")
    print("donde:")
    print("  -c <conn> : max number of concurrent client connections, default 100")
    print("  -l <addr> : address(es) on which the server is to listen for incomming connections, default localhost")
    print("  -p <port> : number of port for connections, default 5432")
    print("  -s        : enable ssl security mode for connections")
    print("  -m        : enable performance monitoring parameters, requires pg_stat_statements extension created")
    print("  -g        : enable audit logs")
    print("  -o        : print the parameters settings (postgresql.auto.conf_suffix_ file), default activated")
    print("  -h        : print this help message")

    sys.exit(1)

def gbytes(mbytes):
    return round(mbytes / K)

def gbytes_suffix(mbytes):
    return str(round(mbytes / K)) + SIZE_SUFFIX[3]

def mbytes(cadena):
    size_suffix = cadena[-2:]
    entero = int(cadena.rstrip(size_suffix))

    if size_suffix == SIZE_SUFFIX[3]:
        return (entero * K)
    elif size_suffix == SIZE_SUFFIX[2]:
        return (entero * B)

def mbytes_suffix(mbytes):
    return str(round(mbytes)) + SIZE_SUFFIX[2]

def conf_memory(arch, mach, memt, argums):
    if arch == '64bit' or mach == 'x86_64':
        if 'max_connections' in argums:
            if argums['max_connections'] > (DEFAULT_MAX_CONN * 3):
                params['max_connections'] = DEFAULT_MAX_CONN * 3
            elif argums['max_connections'] < DEFAULT_MIN_CONN:
                params['max_connections'] = DEFAULT_MIN_CONN
            else:
                params['max_connections'] = argums['max_connections']
        else:
            params['max_connections'] = DEFAULT_MAX_CONN
    else:
        if 'max_connections' in argums:
            if argums['max_connections'] > DEFAULT_MAX_CONN:
                params['max_connections'] = DEFAULT_MAX_CONN
            elif argums['max_connections'] < DEFAULT_MIN_CONN:
                params['max_connections'] = DEFAULT_MIN_CONN
            else:
                params['max_connections'] = argums['max_connections']
        else:
            params['max_connections'] = round(DEFAULT_MAX_CONN / 2)

    ramM = mbytes(memt)

    if round(ramM * FACT_EFFEC_CACHE,1) < K*2:
        params['effective_cache_size'] = mbytes_suffix(ramM * FACT_EFFEC_CACHE)
    else:
        params['effective_cache_size'] = gbytes_suffix(ramM * FACT_EFFEC_CACHE)

    if round(ramM * FACT_SHARED_BUFFERS,1) < K:
        params['shared_buffers'] = mbytes_suffix(ramM * FACT_SHARED_BUFFERS)
    else:
        params['shared_buffers'] = gbytes_suffix(ramM * FACT_SHARED_BUFFERS)

    max_conn = params['max_connections']
    if max_conn > DEFAULT_MAX_CONN:
        params['work_mem'] = mbytes_suffix((ramM * FACT_WORK_MEM) - ((max_conn - DEFAULT_MAX_CONN) * 0.05))
    elif max_conn < DEFAULT_MAX_CONN:
        params['work_mem'] = mbytes_suffix((ramM * FACT_WORK_MEM) + ((DEFAULT_MAX_CONN - max_conn) * 0.5))
    else:
        params['work_mem'] = mbytes_suffix(ramM * FACT_WORK_MEM)

    if ramM < K*2:
        params['maintenance_work_mem'] = mbytes_suffix(BYTE*4)
    elif ramM >= K*2 and ramM < K*4:
        params['maintenance_work_mem'] = mbytes_suffix(BYTE*BYTE)
    elif ramM >= K*4 and ramM < K*BYTE:
        params['maintenance_work_mem'] = mbytes_suffix(K/4)
    elif ramM >= K*BYTE:
        params['maintenance_work_mem'] = mbytes_suffix(K/2)

    params['wal_buffers'] = '32MB'
    
def conf_disco(disc):
    disco = mbytes(disc)
#    disco = 500000
#    print(disc)
#    print(disco)

    if disco < K*(DEC/2):
        params['checkpoint_completion_target'] = '0.7'
        params['effective_io_concurrency'] = '50'
    elif disco >= K*(DEC/2) and disco < K*(DEC*5):
        params['checkpoint_completion_target'] = '0.8'
        params['effective_io_concurrency'] = '100'
    elif disco >= K*(DEC*5):
        params['checkpoint_completion_target'] = '0.9'
        params['effective_io_concurrency'] = '300'

    params['default_statistics_target'] = '100'
    params['random_page_cost'] = '1.1'

def conf_wal(disc):
    disco = mbytes(disc)

    if disco < K*(DEC/2):
        params['min_wal_size'] = mbytes_suffix(K/4)
        params['max_wal_size'] = mbytes_suffix(K/2)
    elif disco >= K*(DEC/2) and disco < K*(DEC*4):
        params['min_wal_size'] = gbytes_suffix(K)
        params['max_wal_size'] = gbytes_suffix(K*2)
    elif disco >= K*(DEC*4) and disco < K*(DEC*DEC):
        params['min_wal_size'] = gbytes_suffix(K)
        params['max_wal_size'] = gbytes_suffix(K*4)
    elif disco >= K*(DEC*DEC) and disco < K*(DEC*DEC*3):
        params['min_wal_size'] = gbytes_suffix(K*4)
        params['max_wal_size'] = gbytes_suffix(K*BYTE)
    elif disco >= K*(DEC*DEC*3):
        params['min_wal_size'] = gbytes_suffix(K*4)
        params['max_wal_size'] = gbytes_suffix(K*(BYTE*2))
        
    params['synchronous_commit'] = 'off'
    params['fsync'] = 'on'
        
def conf_procs(cpul):
    cpus = int(cpul)
    params['max_worker_processes'] = cpus

    if cpus >= 4:
        cpuPer = round(cpus/4)
    else:
        cpuPer = 0

    params['max_parallel_workers_per_gather'] = cpuPer
    params['max_parallel_workers'] = cpus
    params['max_parallel_maintenance_workers'] = cpuPer

def conf_moni(stats):
    if stats:
        params['track_io_timing'] = 'on'
        params['shared_preload_libraries'] = 'pg_stat_statements'
    else:
        params['track_io_timing'] = 'off'

def conf_log(logging, disc):
    params['logging_collector'] = 'on'
    params['log_filename'] = 'postgresql-%Y-%m-%d_%H%M%S.log'
    params['log_line_prefix'] = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
    params['log_rotation_age'] = '1d'
    params['log_checkpoints'] = 'on'
    params['log_temp_files'] = '0'
    params['log_autovacuum_min_duration'] = '0'
    params['log_error_verbosity'] = 'default'

    if logging:
        params['lc_messages'] = 'en_US.UTF-8'
        params['log_connections'] = 'on'
        params['log_disconnections'] = 'off'
        params['log_lock_waits'] = 'on'
        disco = mbytes(disc)
        if disco < K*(DEC*2):
            params['log_min_duration_statement'] = '200'
            params['log_rotation_size'] = mbytes_suffix(DEC)
            params['log_statement'] = 'mod'
        elif disco >= K*(DEC*2) and disco < K*(DEC*5):
            params['log_min_duration_statement'] = '300'
            params['log_rotation_size'] = mbytes_suffix(DEC*2)
            params['log_statement'] = 'mod'
        elif disco >= K*(DEC*5) and disco < K*(DEC*DEC):
            params['log_min_duration_statement'] = '400'
            params['log_rotation_size'] = mbytes_suffix(DEC*5)
            params['log_statement'] = 'all'
        elif disco >= K*(DEC*DEC):
            params['log_min_duration_statement'] = '500'
            params['log_rotation_size'] = mbytes_suffix(DEC*DEC)
            params['log_statement'] = 'all'
    else:
        params['log_connections'] = 'off'
        params['log_disconnections'] = 'off'
        params['log_lock_waits'] = 'off'
        params['log_min_duration_statement'] = '-1'
        params['log_rotation_size'] = mbytes_suffix(DEC)
        params['log_statement'] = 'none'

def conf_ideal_main(gen_pfile, argums):
    res = recursos_main(False)
    arch = res['server']['architec']
    mach = res['server']['machine']
    memt = res['memory']['total']
    cpul = res['cpu']['logicalCPUs']
    disc = res['disco']['free']

    conf_memory(arch, mach, memt, argums)
    conf_disco(disc)
    conf_wal(disc)
    conf_procs(cpul)
    
    if 'listen_addresses' in argums:
        params['listen_addresses'] = argums['listen_addresses']
    else:
        params['listen_addresses'] = DEFAULT_LISTENER

    if 'port' in argums:
        params['port'] = argums['port']
    else:
        params['port'] = DEFAULT_PORT

    if 'ssl' in argums:
        params['ssl'] = 'on'
    else:
        params['ssl'] = DEFAULT_SSL

    if 'monitoring' in argums:
        conf_moni(True)
    else:
        conf_moni(DEFAULT_MONITORING)

    if 'logging' in argums:
        conf_log(True, disc)
    else:
        conf_log(DEFAULT_LOGGING, disc)

    if gen_pfile:
#        print('# Do not edit this file manually!')
#        print('# It will be overwritten by the ALTER SYSTEM command.')
        file = open('postgresql.auto.conf_suffix_', 'w')
        file.write('#\n')
        file.write("# Generated by the 'pardb_dp_conf_ideal.py' script.\n")
        file.write('# Date: %s\n' % datetime.today().strftime('%B %d, %Y'))
        file.write('#\n')
        for x, y in params.items():
            file.write("%s = '%s'\n" % (x, y))
        file.close()

        file = open('postgresql.auto.conf_suffix_', 'r')
        if file.mode == 'r':
            contenido = file.read()
            print(contenido)
        file.close()
        
    return params

def main():
    argums = {}
    gen_pfile = True

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:l:p:smgoh')

        for opt, arg in opts:
            if opt == '-c':
                value = int(arg)
                argums['max_connections'] = value
            elif opt == '-l':
                value = str(arg)
                argums['listen_addresses'] = value
            elif opt == '-p':
                value = int(arg)
                argums['port'] = value
            elif opt == '-s':
                argums['ssl'] = True
            elif opt == '-m':
                argums['monitoring'] = True
            elif opt == '-g':
                argums['logging'] = True
            elif opt == '-o':
                gen_pfile = True
            elif opt == '-h':
                usage_and_exit()
            else:
                print('invalid option: %s' % opt)
                usage_and_exit()
    except getopt.GetoptError as err:
        print(err)
        usage_and_exit()

    conf_ideal_main(gen_pfile, argums)

if __name__ == '__main__':
    main()