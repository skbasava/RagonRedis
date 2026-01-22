import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Bloom setup (run once)
redis_client.execute_command(
    "BF.RESERVE", "bf:project_versions", 0.01, 10000
)