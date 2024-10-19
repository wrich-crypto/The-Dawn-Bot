import os
from loguru import logger
from tortoise import Tortoise

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库文件路径
DB_PATH = os.path.join(BASE_DIR, "The-Dawn-Bot", "database", "database.sqlite3")

async def initialize_database() -> None:
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        # 使用绝对路径初始化数据库
        db_url = f"sqlite://{DB_PATH}"
        logger.info(f"Initializing database at: {db_url}")

        await Tortoise.init(
            db_url=db_url,
            modules={"models": ["database.models.accounts"]},
            timezone="UTC",
        )

        # 生成数据库架构
        await Tortoise.generate_schemas(safe=True)

        logger.info("Database initialized successfully")

    except Exception as error:
        logger.error(f"Error while initializing database: {error}")
        raise  # 抛出异常，让调用者处理

# 可选：添加一个关闭数据库连接的函数
async def close_database():
    await Tortoise.close_connections()