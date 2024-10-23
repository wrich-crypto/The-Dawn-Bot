import pytz

from datetime import datetime, timedelta
from tortoise import Model, fields
from loguru import logger


class Accounts(Model):
    email = fields.CharField(max_length=255, unique=True)
    headers = fields.JSONField(null=True)
    sleep_until = fields.DatetimeField(null=True)
    session_blocked_until = fields.DatetimeField(null=True)
    registered = fields.BooleanField(default=True)
    login_attempts = fields.IntField(default=0)

    class Meta:
        table = "dawn_accounts_v1.4"

    @classmethod
    async def get_account(cls, email: str):
        return await cls.get_or_none(email=email)

    @classmethod
    async def get_accounts(cls):
        return await cls.all()

    @classmethod
    async def create_account(cls, email: str, headers: dict = None):
        account = await cls.get_account(email=email)
        if account is None:
            account = await cls.create(email=email, headers=headers)
            return account
        else:
            account.headers = headers
            await account.save()
            return account

    @classmethod
    async def delete_account(cls, email: str):
        account = await cls.get_account(email=email)
        if account is None:
            return False

        await account.delete()
        return True

    @classmethod
    async def set_sleep_until(cls, email: str, sleep_until: datetime):
        account = await cls.get_account(email=email)
        if account is None:
            return False

        if sleep_until.tzinfo is None:
            sleep_until = pytz.UTC.localize(sleep_until)
        else:
            sleep_until = sleep_until.astimezone(pytz.UTC)

        account.sleep_until = sleep_until
        await account.save()
        logger.info(f"账户: {email} | 设置新的sleep_until: {sleep_until}")
        return True

    @classmethod
    async def set_session_blocked_until(
        cls, email: str, session_blocked_until: datetime
    ):
        account = await cls.get_account(email=email)
        if account is None:
            account = await cls.create_account(email=email)
            account.session_blocked_until = session_blocked_until
            await account.save()
            logger.info(
                f"账户: {email} | 设置新的session_blocked_until: {session_blocked_until}"
            )
            return

        if session_blocked_until.tzinfo is None:
            session_blocked_until = pytz.UTC.localize(session_blocked_until)
        else:
            session_blocked_until = session_blocked_until.astimezone(pytz.UTC)

        account.session_blocked_until = session_blocked_until
        await account.save()
        logger.info(
            f"账户: {email} | 设置新的session_blocked_until: {session_blocked_until}"
        )

    @classmethod
    async def get_registered_status(cls, email: str):
        account = await cls.get_account(email=email)
        if account is None:
            return True
        return account.registered

    @classmethod
    async def set_registered_status(cls, email: str, status: bool):
        account = await cls.get_account(email=email)
        if account is None:
            return False
        account.registered = status
        await account.save()
        logger.info(f"账户: {email} | 设置注册状态为: {status}")
        return True

    @classmethod
    async def get_login_attempts(cls, email: str):
        account = await cls.get_account(email=email)
        if account is None:
            return 0
        return account.login_attempts

    @classmethod
    async def set_login_attempts(cls, email: str, attempts: int):
        account = await cls.get_account(email=email)
        if account is None:
            return False
        account.login_attempts = attempts
        await account.save()
        logger.info(f"账户: {email} | 设置登录尝试次数为: {attempts}")
        return True

    @classmethod
    async def get_wait_time_by_login_attempts(cls, email: str):
        attempts = await cls.get_login_attempts(email)
        if attempts == 0:
            return 0
        wait_time = 10 * attempts  # 10秒，逐次递增
        return wait_time

    @classmethod
    async def increment_login_attempts(cls, email: str):
        account = await cls.get_account(email=email)
        if account is None:
            return False
        account.login_attempts += 1
        await account.save()
        logger.info(f"账户: {email} | 登录尝试次数增加1，现为: {account.login_attempts}")
        return True

    @classmethod
    async def reset_login_attempts(cls, email: str):
        account = await cls.get_account(email=email)
        if account is None:
            return False
        account.login_attempts = 0
        await account.save()
        logger.info(f"账户: {email} | 登录尝试次数已重置为0")
        return True
