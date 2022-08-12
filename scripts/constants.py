# -*- coding: utf-8 -*-
"""
Proyecto: Herramienta de Diagnóstico del Rendimiento de BDs PostgreSQL

Autor:    Jose Luis Pérez R.
Creación: 27-julio-2022
Ult.Mod.: 27-julio-2022
"""

B = 1
K = 1024
M = K * K
G = K * M

BYTE = 8
DEC = 10
DAY = 60*24

DATA_SIZES = {'b': B, 'k': K, 'm': M, 'g': G}
SIZE_SUFFIX = ["", "KB", "MB", "GB", "TB"]

DEFAULT_PG_VERSION = 12
DEFAULT_MAX_CONN = 100
DEFAULT_MIN_CONN = 10
DEFAULT_LISTENER = '*'
DEFAULT_PORT = 5432
DEFAULT_SSL = 'off'
DEFAULT_MONITORING = False
DEFAULT_LOGGING = False
DEFAULT_OUTPUT = True

FACT_EFFEC_CACHE = 0.8
FACT_SHARED_BUFFERS = round(FACT_EFFEC_CACHE * 0.6,1)
FACT_WORK_MEM = 0.00097
FACT_MAINT_WORK_MEM = 1
