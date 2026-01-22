import asyncio
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
from aiolimiter import AsyncLimiter
from redis_client import redis_client

MAX_IO = 10
MAX_CPU = 4

io_limiter = AsyncLimiter(MAX_IO, 1)

def parse_mpu(mpu_node, project, version):
    mpu_name = mpu_node.get("name")
    chunks = []

    for region in mpu_node.findall(".//Region"):
        region_id = int(region.get("id"))
        addr_start = int(region.get("start"), 16)
        addr_end = int(region.get("end"), 16)
        profile = region.get("profile", "UNKNOWN")

        raw_text = etree.tostring(region, encoding="unicode")

        chunks.append({
            "project": project,
            "version": version,
            "mpu": mpu_name,
            "region": region_id,
            "profile": profile,
            "addr_start": addr_start,
            "addr_end": addr_end,
            "raw_text": raw_text
        })

    return chunks

async def store_chunks(chunks):
    for c in chunks:
        key = f"mpu:{c['project']}:{c['version']}:{c['mpu']}:{c['region']}"
        redis_client.hset(key, mapping=c)
        redis_client.expire(key, 3600)

async def parse_and_cache(xml, project, version):
    root = etree.XML(xml.encode())
    mpus = root.findall(".//MPU")

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=MAX_CPU)

    tasks = []
    for mpu in mpus:
        tasks.append(
            loop.run_in_executor(
                executor,
                parse_mpu,
                mpu,
                project,
                version
            )
        )

    for future in asyncio.as_completed(tasks):
        chunks = await future
        async with io_limiter:
            await store_chunks(chunks)