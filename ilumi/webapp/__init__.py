import os
import sys
import asyncio
import uvloop

sys.path.append(os.getcwd())
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
