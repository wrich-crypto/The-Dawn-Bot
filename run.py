import asyncio
import random
import sys
from typing import Callable, Coroutine, Any, List, Set

from loguru import logger
from loader import config, semaphore, file_operations
from core.bot import Bot
from models import Account
from utils import setup
from console import Console
import asyncio
from loguru import logger
from database.settings import initialize_database, close_database


accounts_with_initial_delay: Set[str] = set()


async def run_module_safe(
        account: Account, process_func: Callable[[Bot], Coroutine[Any, Any, Any]]
) -> Any:
    global accounts_with_initial_delay

    async with semaphore:
        bot = Bot(account)
        try:
            # 检查是否需要延迟启动
            if config.delay_before_start.min > 0:
                # 对于farming操作且账户未进行过初始延迟的情况
                if process_func == process_farming and account.email not in accounts_with_initial_delay:
                    # 生成随机延迟时间
                    random_delay = random.randint(config.delay_before_start.min, config.delay_before_start.max)
                    logger.info(f"账户: {account.email} | 初始farming延迟: {random_delay} 秒")
                    await asyncio.sleep(random_delay)
                    # 将账户添加到已进行初始延迟的集合中
                    accounts_with_initial_delay.add(account.email)

                # 对于非farming操作的情况
                elif process_func != process_farming:
                    # 生成随机延迟时间
                    random_delay = random.randint(config.delay_before_start.min, config.delay_before_start.max)
                    logger.info(f"账户: {account.email} | 休眠 {random_delay} 秒")
                    await asyncio.sleep(random_delay)

            # 执行指定的处理函数
            result = await process_func(bot)
            return result
        finally:
            # 确保在函数结束时关闭bot会话
            await bot.close_session()


async def process_registration(bot: Bot) -> None:
    operation_result = await bot.process_registration()
    await file_operations.export_result(operation_result, "register")


async def process_farming(bot: Bot) -> None:
    await bot.process_farming()


async def process_export_stats(bot: Bot) -> None:
    data = await bot.process_get_user_info()
    await file_operations.export_stats(data)


async def process_complete_tasks(bot: Bot) -> None:
    operation_result = await bot.process_complete_tasks()
    await file_operations.export_result(operation_result, "tasks")


async def run_module(
        accounts: List[Account], process_func: Callable[[Bot], Coroutine[Any, Any, Any]]
) -> tuple[Any]:
    # 创建一个任务列表,每个任务对应一个账户的处理
    tasks = [run_module_safe(account, process_func) for account in accounts]
    # 并发执行所有任务并等待结果
    return await asyncio.gather(*tasks)


async def farm_continuously(accounts: List[Account]) -> None:
    while True:
        # 随机打乱账户列表顺序
        random.shuffle(accounts)
        # 对所有账户执行farming操作
        await run_module(accounts, process_farming)
        # 等待10秒后继续下一轮
        await asyncio.sleep(10)


def reset_initial_delays():
    global accounts_with_initial_delay
    accounts_with_initial_delay.clear()


async def run() -> None:
    try:
        await initialize_database()
        await file_operations.setup_files()
        reset_initial_delays()

        module_map = {
            "register": (config.accounts_to_register, process_registration),
            "farm": (config.accounts_to_farm, farm_continuously),
            "complete_tasks": (config.accounts_to_farm, process_complete_tasks),
            "export_stats": (config.accounts_to_farm, process_export_stats),
        }

        while True:
            Console().build()

            if config.module not in module_map:
                logger.error(f"Unknown module: {config.module}")
                break

            accounts, process_func = module_map[config.module]

            if not accounts:
                logger.error(f"No accounts for {config.module}")
                break

            if config.module == "farm":
                await process_func(accounts)
            else:
                await run_module(accounts, process_func)
                input("\n\nPress Enter to continue...")
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
    finally:
        await close_database()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    setup()
    asyncio.run(run())