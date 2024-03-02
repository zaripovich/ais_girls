import asyncio
from service import run, init_models


if __name__ == "__main__":
    asyncio.run(init_models())
    run()
