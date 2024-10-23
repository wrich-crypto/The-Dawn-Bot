import os
from loguru import logger
from tortoise import Tortoise
from tortoise.exceptions import OperationalError

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
        logger.info(f"正在初始化数据库：{db_url}")

        await Tortoise.init(
            db_url=db_url,
            modules={"models": ["database.models.accounts"]},
            timezone="UTC",
        )

        # 检查并更新数据库架构
        await check_and_update_schema()

        logger.info("数据库初始化成功")

    except Exception as error:
        logger.error(f"初始化数据库时出错：{error}")
        raise  # 抛出异常，让调用者处理

async def check_and_update_schema():
    try:
        # 尝试生成架构，如果表已存在则不会进行更改
        await Tortoise.generate_schemas(safe=True)
        
        logger.info("数据库架构检查和更新完成")
    except OperationalError as e:
        logger.warning(f"更新数据库架构时出现问题：{e}")
        logger.info("正在尝试重新创建数据库架构...")
        await Tortoise.generate_schemas(safe=False)
        logger.info("数据库架构重新创建完成")

# 可选：添加一个关闭数据库连接的函数
async def close_database():
    await Tortoise.close_connections()
