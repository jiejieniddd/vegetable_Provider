import os

Mysql_host = "localhost"
Mysql_port = 3306
Mysql_user = "root"
Mysql_password = "123456"
Mysql_database = "vegetable_provider"

SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://{Mysql_user}:{Mysql_password}@{Mysql_host}:{Mysql_port}/{Mysql_database}?charset=utf8mb4"

# 邮箱配置
MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = "2796412183@qq.com"
MAIL_PASSWORD = "jfncvpxdizrkdeac"
MAIL_DEFAULT_SENDER = "2796412183@qq.com"

SECRET_KEY = "kfalfkda2344"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
