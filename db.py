import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# pylint: disable=E0213,C0115,C0116,W0718
class DbResult:
    error_desc: str = ""
    value = None
    is_error = False

    def error(error_desc: str = "", value=None):
        response = DbResult()
        response.is_error = True
        response.error_desc = error_desc
        response.value = value
        return response

    def result(value=None):
        response = DbResult()
        response.is_error = False
        response.value = value
        response.error_desc = ""
        return response


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

engine = create_async_engine(
    os.environ.get("DATABASE_URL"), echo=os.environ.get("DEBUG") == "1"
)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
