from redis_client import redis_client

def bloom_key(project, version):
    return f"{project.lower()}:{version.lower()}"

def bloom_exists(project, version) -> bool:
    return redis_client.execute_command(
        "BF.EXISTS",
        "bf:project_versions",
        bloom_key(project, version)
    ) == 1

def bloom_add(project, version):
    redis_client.execute_command(
        "BF.ADD",
        "bf:project_versions",
        bloom_key(project, version)
    )