import json
from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from werkzeug.utils import redirect
from data import db_session
from data.dialog import Dialog
from data.forms import RegisterForm, LoginForm
from data.db_session import create_session, global_init
from data.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/messanger.sqlite")
session = create_session()
current_contact = 3


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(

                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
    return render_template('register.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='EmojiMS'
                           )


@app.route('/contacts')
def contacts():
    users = session.query(User).filter(User.id != current_user.id)
    return render_template('contacts.html', title='Домашняя страница', users=users
                           )


@app.route('/contact/<int:id>', methods=['GET', 'POST'])
def contact(id):
    dialog = session.query(Dialog).filter(Dialog.second_user == id).first()
    user = session.query(User).filter(User.id == id).first()

    global current_contact
    current_contact = id

    return render_template('chat.html', title='Dialog ', dialog=dialog, friend=user)


a = []


@app.route('/uploud', methods=['POST'])
def uploud():
    dialog = session.query(Dialog).filter(Dialog.first_user == current_user.id,
                                          Dialog.second_user == current_contact).first()
    if dialog is None:
        dialog = session.query(Dialog).filter(Dialog.first_user == current_contact,
                                              Dialog.second_user == current_user.id).first()
    messages = dialog.messages.split(',')
    history = []
    for i in messages:
        if len(i) != 0:
            history.append(i.split(':'))
    # print(history)
    return json.dumps({'status': 'OK', 'history': history, 'id': str(current_user.id)})


@app.route('/sendMessage', methods=['POST'])
def messages():
    dialog = session.query(Dialog).filter(Dialog.first_user == current_user.id,
                                          Dialog.second_user == current_contact).first()
    if dialog is None:
        dialog = session.query(Dialog).filter(Dialog.first_user == current_contact,
                                              Dialog.second_user == current_user.id).first()

    message = request.form['message']
    dialog.messages += f',{current_user.id}:{message},'

    session.commit()
    return json.dumps({'status': 'OK', 'message': message})


@app.route('/translateMessage', methods=['POST'])
def translateMessage():
    dialog = session.query(Dialog).filter(Dialog.first_user == current_user.id,
                                          Dialog.second_user == current_contact).first()
    if dialog is None:
        dialog = session.query(Dialog).filter(Dialog.first_user == current_contact,
                                              Dialog.second_user == current_user.id).first()

    messages_list = dialog.messages.split(',')

    translated_messages = []
    for i in messages_list:
        if len(i) != 0:
            print(i)
            number, text = i.split(':')
            text = convet_emoji(text)
            translated_messages.append(':'.join([number, text]))
    dialog.messages = ','.join(translated_messages)

    session.commit()
    return json.dumps({'status': 'OK'})
@app.route('/translateEmoji', methods=['POST'])
def translateEmoji():
    dialog = session.query(Dialog).filter(Dialog.first_user == current_user.id,
                                          Dialog.second_user == current_contact).first()
    if dialog is None:
        dialog = session.query(Dialog).filter(Dialog.first_user == current_contact,
                                              Dialog.second_user == current_user.id).first()

    messages_list = dialog.messages.split(',')

    translated_messages = []
    for i in messages_list:
        if len(i) != 0:
            print(i)
            number, text = i.split(':')
            text = convet_text(text)
            translated_messages.append(':'.join([number, text]))
    dialog.messages = ','.join(translated_messages)

    session.commit()
    return json.dumps({'status': 'OK'})

def convet_emoji(message):
    text_to_emoji = {'смешно': '\U0001F602', 'болею': '\U0001F912', 'грустно': '\U0001F622', 'окей': '\U0001F44C',
                     'не знаю': '\U0001F937'}
    text = message.split(' ')
    for i in range(len(text)):
        if text[i] in text_to_emoji.keys():
            text[i] = text_to_emoji[text[i]]
    text = ' '.join(text)
    return text

def convet_text(message):
    emoji_to_text = {'\U0001F602': 'смешно', '\U0001F912': 'болею', '\U0001F622' : 'грустно', '\U0001F44C': 'окей',
                     '\U0001F937': 'не знаю'}
    text = message.split(' ')
    for i in range(len(text)):
        if text[i] in emoji_to_text.keys():
            text[i] = emoji_to_text[text[i]]
    text = ' '.join(text)
    return text


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
