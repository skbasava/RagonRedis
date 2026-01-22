"""
Redis Schema – QGenie / TAG MPU Policy System
=============================================

This file defines the canonical Redis key schema used by the system.
It acts as:
- Documentation (single source of truth)
- A helper for generating consistent keys
- A guard against schema drift

DO NOT change keys casually. Treat this as a frozen contract.
"""

# ============================================================
# BLOOM FILTER
# ============================================================

"""
Bloom filter for fast existence checks of project+version.

Purpose:
- Avoid unnecessary API calls
- Fail fast if project/version does not exist anywhere

Key:
    bloom:project_version

Stored values:
    "{project}:{version}"
"""

BLOOM_PROJECT_VERSION = "bloom:project_version"


# ============================================================
# PROJECT / VERSION METADATA
# ============================================================

"""
Metadata for a parsed project+version.

Key:
    meta:{project}:{version}

Type:
    HASH

TTL:
    12h or 24h (configurable)

Fields:
    project     -> project name
    version     -> version string
    mpu_count   -> number of MPUs in this project/version
    parsed_at   -> ISO timestamp when parsing completed
"""

def meta_key(project: str, version: str) -> str:
    return f"meta:{project}:{version}"


# ============================================================
# MPU INDEX
# ============================================================

"""
Index of all MPUs available for a project+version.

Key:
    mpu_index:{project}:{version}

Type:
    SET

Members:
    MPU names (e.g. AOSS_PERIPH_MPU_XPU4)
"""

def mpu_index_key(project: str, version: str) -> str:
    return f"mpu_index:{project}:{version}"


# ============================================================
# REGION / POLICY CHUNKS (PRIMARY DATA)
# ============================================================

"""
Each MPU region is stored as a standalone chunk.

Key:
    chunk:{project}:{version}:{mpu}:{region_id}

Type:
    HASH

TTL:
    12h or 24h (LRU eligible)

Fields:
    mpu         -> MPU name
    region      -> region index/id
    addr_start  -> hex string (e.g. 0x0EF01000)
    addr_end    -> hex string (e.g. 0x0EF01FFF)
    profile     -> profile type (TZ_STATIC, NON_STATIC, etc.)
    is_dynamic  -> "true" | "false"
    raw_text    -> raw XML text for this region
"""

def chunk_key(
    project: str,
    version: str,
    mpu: str,
    region_id: str
) -> str:
    return f"chunk:{project}:{version}:{mpu}:{region_id}"


# ============================================================
# ADDRESS INDEX (FAST LOOKUP)
# ============================================================

"""
Sorted index for fast address-based lookup within an MPU.

Key:
    addr_index:{project}:{version}:{mpu}

Type:
    SORTED SET

Score:
    addr_start (integer value of hex address)

Member:
    region_id

Usage:
- Given an address, find candidate regions quickly
- Then load full chunk via chunk key
"""

def addr_index_key(project: str, version: str, mpu: str) -> str:
    return f"addr_index:{project}:{version}:{mpu}"


# ============================================================
# METRICS
# ============================================================

"""
Operational metrics for cache behavior.

Key:
    metrics:cache

Type:
    HASH

Fields:
    hits           -> number of cache hits
    misses         -> number of cache misses
    parse_time_ms  -> cumulative XML parse time in ms
"""

METRICS_CACHE = "metrics:cache"


# ============================================================
# SUMMARY (HUMAN READABLE)
# ============================================================

"""
KEY SUMMARY
-----------

Bloom:
    bloom:project_version

Metadata:
    meta:{project}:{version}

Indexes:
    mpu_index:{project}:{version}
    addr_index:{project}:{version}:{mpu}

Data:
    chunk:{project}:{version}:{mpu}:{region}

Metrics:
    metrics:cache

TTL POLICY
----------
- meta:*          -> 12h / 24h
- chunk:*         -> 12h / 24h (LRU eviction)
- addr_index:*    -> same TTL as chunks
- mpu_index:*     -> same TTL as chunks
- bloom:*         -> no TTL (rebuilt on ingestion)

DESIGN PRINCIPLES
-----------------
✔ Raw text is the source of truth
✔ Other fields are metadata for fast filtering
✔ No SQL joins
✔ Redis-only, horizontally scalable
✔ Safe for 1000+ concurrent users
"""