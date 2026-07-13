import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client=redis.from_url(os.environ["REDIS_URL"],decode_responses=True)

#this file has defined the redis client variable 
#this can be defined in the required file also but this way it can be reused by all other files if needed