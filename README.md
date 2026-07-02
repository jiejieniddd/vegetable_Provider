# 🥬 小蟹鲜生 — 蔬菜供应商平台

基于 Flask 的蔬菜供应信息发布与展示平台，集成 PyTorch 深度学习模型，实现蔬菜图片的 AI 智能分类。

## ✨ 功能特性

- **用户系统** — 邮箱验证码注册、密码哈希登录、登录状态持久化
- **蔬菜发布** — 供应商登录后可发布蔬菜信息，包括名称、价格、产地、联系方式、图片等
- **分类浏览** — 首页支持按 15 种蔬菜分类筛选，按发布时间倒序展示
- **详情查看** — 点击卡片查看完整的供应信息
- **AI 智能分类** — 上传图片时自动调用 CNN 模型识别蔬菜种类并填充分类

## 🛠️ 技术栈

| 层面 | 技术 |
|---|---|
| 后端框架 | Flask |
| 数据库 | MySQL + SQLAlchemy ORM |
| 数据库迁移 | Flask-Migrate (Alembic) |
| 邮件服务 | Flask-Mail (QQ 邮箱 SMTP) |
| AI 模型 | PyTorch CNN 图像分类 |
| 前端样式 | Tailwind CSS |
| 前端交互 | jQuery |

## 📁 项目结构

```
vegetable-provider/
├── app.py              # Flask 应用主入口
├── config.py           # 配置文件（数据库、邮件、密钥等）
├── models.py           # 数据模型（User、Vegetable、VegetableCategory、EmailCode）
├── exts.py             # Flask 扩展初始化
├── commands.py         # CLI 命令（初始化蔬菜分类）
├── decorators.py       # 装饰器（登录验证）
├── dlmodel/
│   ├── __init__.py     # CNN 模型定义与预测函数
│   └── model.pth       # 预训练模型权重
├── migrations/         # 数据库迁移文件
├── templates/          # Jinja2 模板
│   ├── base.html       # 基础布局（导航、分类栏、页脚）
│   ├── index.html      # 首页（蔬菜列表）
│   ├── detail.html     # 详情页
│   ├── login.html      # 登录页
│   ├── register.html   # 注册页
│   └── pub.html        # 发布页
├── static/             # 静态资源
│   ├── base.css        # 自定义样式
│   ├── tailwind.js     # Tailwind CSS
│   ├── jquery-3.7.1.min.js
│   ├── register.js     # 注册页逻辑
│   └── pub.js          # 发布页逻辑
└── media/              # 上传的图片存储目录
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- MySQL 5.7+
- pip

### 安装步骤

```bash
# 1. 克隆项目
git clone git@github.com:jiejieniddd/vegetable_Provider.git
cd vegetable_Provider

# 2. 创建虚拟环境并安装依赖
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install flask flask-sqlalchemy flask-migrate flask-mail pymysql torch torchvision pillow

# 3. 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE vegetable_provider CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. 修改配置
# 编辑 config.py，填入你的数据库密码和邮箱配置

# 5. 初始化数据库
flask db upgrade

# 6. 初始化蔬菜分类数据
flask init_category

# 7. 启动项目
flask run
```

访问 http://127.0.0.1:5000 即可使用。

## 📊 数据模型

| 表名 | 说明 | 主要字段 |
|---|---|---|
| `user` | 用户表 | id, email, username, password |
| `vegetable_category` | 蔬菜分类表 | id, name |
| `vegetable` | 蔬菜商品表 | id, name, content, price, picture, mobile, place, provider, pub_time, category_id, publisher_id |
| `email_code` | 验证码表 | id, email, code, create_time |

## 🤖 AI 模型说明

项目内置一个自训练的 CNN 图像分类模型，支持识别以下 15 类蔬菜：

> 豌豆、苦瓜、蒲瓜、茄子、西兰花、卷心菜、灯笼椒、胡萝卜、花菜、黄瓜、木瓜、土豆、南瓜、萝卜、西红柿

模型接收 40×40 的 RGB 图片，经多层卷积和全连接层输出分类结果。

## 📄 License

MIT
