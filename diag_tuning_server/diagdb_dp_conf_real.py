#!/usr/bin/env python3
"""
Proyecto: Herramienta de Diagnóstico del Rendimiento de BDs PostgreSQL
Módulo:   1. Diagnóstico preliminar de la BD
Script:   1.3. Script para recopilar parámetros del rendimiento "reales" con la instancia arriba.
Nombre:   pardb_dp_conf_real.py
Versión:  1.0

Autor:    Jose Luis Pérez R.
Creación: 02-agosto-2022
Ult.Mod.: 04-agosto-2022
"""

import sys
import getopt
import psycopg2
from conf.constants import *

pfile_list = (
'max_connections',
'effective_cache_size',
'shared_buffers',
'work_mem',
'maintenance_work_mem',
'wal_buffers',
'checkpoint_completion_target',
'effective_io_concurrency',
'default_statistics_target',
'random_page_cost',
'min_wal_size',
'max_wal_size',
'synchronous_commit',
'fsync',
'max_worker_processes',
'max_parallel_workers_per_gather',
'max_parallel_workers',
'max_parallel_maintenance_workers',
'listen_addresses',
'port',
'ssl',
'track_io_timing',
'shared_preload_libraries',
'logging_collector',
'log_filename',
'log_line_prefix',
'log_rotation_age',
'log_checkpoints',
'log_temp_files',
'log_autovacuum_min_duration',
'log_error_verbosity',
'lc_messages',
'log_connections',
'log_disconnections',
'log_lock_waits',
'log_min_duration_statement',
'log_rotation_size',
'log_statement')

def usage_and_exit():
    print("")
    print("Diagnóstico del Rendimiento de BDs PostgreSQL (default %s)" % DEFAULT_PG_VERSION)
    print("[1.3] Script para recopilar parámetros del rendimiento 'reales' con la instancia arriba.")
    print("")
    print("Uso: %s [-a <dirección_ip>] [-p <puerto>] [-d] <basedatos> [-u] <usuario> [-w] <contraseña> [-o] [-h]")
    print("")
    print("donde:")
    print("  -a <addr>   : nombre del servidor o dirección IP")
    print("  -p <port>   : puerto del servidor, por omisión 5432")
    print("  -d <dbname> : nombre de base de datos a conectarse, por omisión postgres")
    print("  -u <user>   : nombre de usuario, por omisión postgres")
    print("  -w <passwd> : password de usuario (contraseña)")
    print("  -o          : print the configuration of the read parameters, default activated")
    print("  -h          : print this help message")

    sys.exit(1)

def conf_real_main(read_params, argums):
    if 'host' in argums:
        v_host = argums['host']
    else:
        v_host = None
    if 'port' in argums:
        v_port = argums['port']
    else:
        v_port = '5432'
    if 'database' in argums:
        v_database = argums['database']
    else:
        v_database = 'postgres'
    if 'user' in argums:
        v_user = argums['user']
    else:
        v_user = 'postgres'
    if 'password' in argums:
        v_passwd = argums['password']
    else:
        v_passwd = None

    v_host = '192.168.21.9'
    v_passwd = 'manager'

    if v_host and v_passwd:
        conn = psycopg2.connect(
            database = v_database, user = v_user, password = v_passwd, host = v_host, port = v_port
        )
        pfile_dic = dict.fromkeys(pfile_list)
        cursor = conn.cursor()
        for key in pfile_list:
            sql = "select name, setting, unit from pg_settings where name = '%s'" % key
            cursor.execute(sql)
            data = cursor.fetchone()
            if data[2] == '8kB':
                if int(data[1]) == 0:
                    pfile_dic[key] = data[1]
                else:
                    value_8kb = round((int(data[1])*8)/K)
                    if value_8kb < K:
                        pfile_dic[key] = str(value_8kb)+'MB'
                    else:
                        pfile_dic[key] = str(round(value_8kb/K))+'GB'
            elif data[2] == 'kB':
                if int(data[1]) == 0:
                    pfile_dic[key] = data[1]
                else:
                    value_kb = round(int(data[1])/K)
                    if value_kb < K:
                        pfile_dic[key] = str(value_kb)+'MB'
                    else:
                        pfile_dic[key] = str(round(value_kb/K))+'GB'
            elif data[2] == 'MB':
                if int(data[1]) == 0:
                    pfile_dic[key] = data[1]
                else:
                    value_mb = int(data[1])
                    if value_mb < K:
                        pfile_dic[key] = str(value_mb)+'MB'
                    else:
                        pfile_dic[key] = str(round(value_mb/K))+'GB'
            elif data[2] == 'min':
                value_min = int(data[1])
                if value_min == DAY:
                    pfile_dic[key] = '1d'
                else:
                    pfile_dic[key] = data[1]
            else:
                pfile_dic[key] = data[1]
    
        cursor.close()
        conn.close()

        if read_params:    
            for x, y in pfile_dic.items():
                print("%s = '%s'" % (x, y))
            
        return pfile_dic
    else:
        print("")
        print("ERROR: En lectura de parámetros del servidor.")
        print("ERROR: Los nombres de 'host' y 'password' son obligatorios...!!!")
        print("")
        return 0

#        conn = psycopg2.connect(
#            database='moni', user='postgres', password='manager', host='192.168.21.9', port='5432'
#        )

def main():
    argums = {}
    read_params = True

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'a:p:d:u:w:oh')

        for opt, arg in opts:
            if opt == '-a':
                value = str(arg)
                argums['host'] = value
            elif opt == '-p':
                value = str(arg)
                argums['port'] = value
            elif opt == '-d':
                value = str(arg)
                argums['database'] = value
            elif opt == '-u':
                value = str(arg)
                argums['user'] =  value
            elif opt == '-w':
                value = str(arg)
                argums['password'] = value
            elif opt == '-o':
                read_params = True
            elif opt == '-h':
                usage_and_exit()
            else:
                print('invalid option: %s' % opt)
                usage_and_exit()
    except getopt.GetoptError as err:
        print(err)
        usage_and_exit()

    conf_real_main(read_params, argums)

if __name__ == '__main__':
    main()