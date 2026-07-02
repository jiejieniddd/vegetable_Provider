import os
import traceback
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, session, redirect, g, send_from_directory
from flask_mail import Message

import commands
from decorators import login_required
from dlmodel import predict
from exts import db, migrate, mail

from models import User, EmailCode, Vegetable, VegetableCategory
import config
import random
import string
import uuid

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# 创建命令
app.cli.command("init_category")(commands.init_vegetable_category)


@app.before_request
def before_request():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        g.user = user
    else:
        g.user = None


@app.context_processor
def context_processor():
    categories = db.session.scalars(db.select(VegetableCategory)).all()
    return {
        'user': g.user,
        'categories': categories
    }


@app.route('/')
def index():
    # 规定好:前端传递category参数,通过query string的形式
    category_id = request.args.get('category', type=int)
    if category_id:
        stmt = db.select(Vegetable).where(Vegetable.category_id == category_id)
    else:
        stmt = db.select(Vegetable)
    vegetables=db.session.scalars(stmt.order_by(Vegetable.pub_time.desc())).all()
    return render_template('index.html', vegetables=vegetables)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        try:
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            code = request.form.get('code')
            code_model = db.session.scalar(db.select(EmailCode).where(EmailCode.email == email, EmailCode.code == code))
            if not code_model or (datetime.now() - code_model.create_time) > timedelta(minutes=10):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"result": False, "message": "请输入正确的验证码!"})
                else:
                    return render_template('register.html', error="请输入正确的验证码!")

            # 检查邮箱是否已注册
            existing_user = db.session.scalar(db.select(User).where(User.email == email))
            if existing_user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({"result": False, "message": "该邮箱已被注册!"})
                else:
                    return render_template('register.html', error="该邮箱已被注册!")

            user = User(username=username, password=password, email=email)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"result": False, "message": f"注册失败: {e}"})
            else:
                return render_template('register.html', error=f"注册失败: {e}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"result": True, "message": None})
        else:
            return redirect('/login')


@app.get("/email/code")
def get_email_code():
    # /email/code?eail=abc@qq.com
    email = request.args.get('email')
    if not email:
        return jsonify({"result": False, "message": "邮箱不能为空"})

    # 生成验证码
    source = string.digits * 4
    code = "".join(random.sample(source, k=4))
    message = Message(
        subject="【小蟹鲜生】注册验证码",
        recipients=[email],
        body=f"【小蟹鲜生供应商】注册验证码:{code}"
    )
    try:
        mail.send(message)
    except Exception as e:
        return jsonify({"result": False, "message": f"发送邮件失败:{e}"})
    # memcached/redis
    code_model = EmailCode(email=email, code=code)
    db.session.add(code_model)
    db.session.commit()
    return jsonify({"result": True, "message": None})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user and user.check_password(password):
            session['user_id'] = user.id
            # permanent设置为True,用户登录数据能够保存31天
            session.permanent = True if remember else False
            return redirect('/')
        else:
            print("邮箱或密码错误")
            return redirect('login')


@app.post("/logout")
def logout():
    session.clear()
    return redirect('/')


@app.route('/pub', methods=['GET', 'POST'])
@login_required
def pub():
    if request.method == 'GET':
        categories = db.session.scalars(db.select(VegetableCategory)).all()
        return render_template('pub.html', categories=categories)
    else:
        picture = request.form.get('picture')
        category_id = request.form.get('category')
        name = request.form.get('name')
        content = request.form.get('content')
        price = request.form.get('price')
        provider = request.form.get('provider')
        mobile = request.form.get('mobile')
        place = request.form.get('place')

        vegetable = Vegetable(
            name=name,
            content=content,
            picture=picture,
            category_id=category_id,
            price=price,
            provider=provider,
            mobile=mobile,
            place=place,
            publisher_id=g.user.id,
        )
        db.session.add(vegetable)
        db.session.commit()
        return redirect("/")


@app.post("/upload/picture")
def upload_picture():
    # 当用户上传图片时,图片的name为picture
    picture = request.files['picture']
    # 重新给图片命名
    picture.filename.split(".")
    ext = picture.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    picture_path = os.path.join(app.config['MEDIA_DIR'], filename)
    picture.save(picture_path)

    # 预测蔬菜分类
    category_name = predict(picture_path)
    category = db.session.scalar(db.select(VegetableCategory).where(VegetableCategory.name == category_name))
    return jsonify({"result": True, "filename": filename, "category": {"id": category.id, "name": category_name}})


@app.route("/detail/<int:vegetable_id>")
def detail(vegetable_id):
    vegetable = db.session.get(Vegetable, vegetable_id)
    return render_template('detail.html', vegetable=vegetable)


@app.route("/media/<filename>")
def media(filename):
    return send_from_directory(config.MEDIA_DIR, filename)


if __name__ == '__main__':
    app.run()
