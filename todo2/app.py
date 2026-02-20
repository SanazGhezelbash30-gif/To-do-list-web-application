from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key-2026'

USERS = {'admin': '1234'}

def get_user_data(username):
    filename = f'data_{username}.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {'lists': {}, 'list_names': []}

def save_user_data(username, data):
    filename = f'data_{username}.json'
    with open(filename, 'w') as f:
        json.dump(data, f)

def user_exists(username):
    filename = f'data_{username}.json'
    return os.path.exists(filename)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    data = get_user_data(session['username'])
    return render_template('index.html', lists=data['lists'], list_names=data['list_names'], username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form['username']
        password = request.form['password']
        
        if action == 'signup':
            # ثبت‌نام جدید
            if username in USERS:
                return render_template('login.html', error='this user already exists')
            USERS[username] = password
            session['username'] = username
            save_user_data(username, {'lists': {}, 'list_names': []})
            return redirect(url_for('index'))
        else:
            # لاگین
            if username in USERS and USERS[username] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='username or password is wrong')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_list', methods=['POST'])
def add_list():
    data = get_user_data(session['username'])
    name = request.json['name']
    if name not in data['lists']:
        data['lists'][name] = []
        data['list_names'].append(name)
        save_user_data(session['username'], data)
    return jsonify({'success': True})

@app.route('/delete_list', methods=['POST'])
def delete_list():
    data = get_user_data(session['username'])
    name = request.json['name']
    if name in data['lists']:
        del data['lists'][name]
        data['list_names'].remove(name)
        save_user_data(session['username'], data)
    return jsonify({'success': True})

@app.route('/add_note', methods=['POST'])
def add_note():
    data = get_user_data(session['username'])
    listname = request.json['listname']
    note = request.json['note']
    if listname in data['lists']:
        data['lists'][listname].append(note)
        save_user_data(session['username'], data)
    return jsonify({'success': True})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True)
