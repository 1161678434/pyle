"""
配置分离 — 环境切换
====================
核心原则：代码里不写死 URL、账号、密码，全部从配置读取。

切换环境方式（优先级从高到低）：
  1. 命令行：pytest --env=staging
  2. 环境变量：set TEST_ENV=staging
  3. 默认值：dev
"""

import os


class Config:
    """基础配置 — 所有环境共享的值"""
    TIMEOUT = 10
    RETRY_COUNT = 3
    HEADERS = {"User-Agent": "QATest/1.0"}


class DevConfig(Config):
    """开发环境"""
    BASE_URL = "http://127.0.0.1:5000"
    DB_HOST = "localhost"


class StagingConfig(Config):
    """预发布环境"""
    BASE_URL = "http://staging-api.example.com"
    DB_HOST = "staging-db.example.com"


class ProdConfig(Config):
    """生产环境 — 只读！"""
    BASE_URL = "http://api.example.com"
    DB_HOST = "prod-db.example.com"


# ---- 环境名 → 配置类的映射 ----
ENV_MAP = {
    "dev": DevConfig,
    "staging": StagingConfig,
    "prod": ProdConfig,
}


def get_config(env=None):
    """
    根据环境名返回对应的配置对象。

    用法：
      config = get_config()           # 默认 dev
      config = get_config("staging")  # 指定环境
      config.BASE_URL                 # 访问配置项
    """
    if env is None:
        env = os.getenv("TEST_ENV", "dev")
    config_class = ENV_MAP.get(env, DevConfig)
    return config_class()


# ---- 全局默认配置 ----
config = get_config()
