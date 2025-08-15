from flask import Flask,redirect,render_template,request,url_for,flash,session
from flask_login import LoginManager,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from models import db,User 

app = Flask(__name__)
app.secret_key = 'secrect'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)

with app.app_context():
    db.create_all()


# what is the use of this 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', user=current_user)
    return render_template('home.html', user=None)


@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method="pbkdf2:sha256")
        new_user = User(username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        session['new_user'] = True
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash('login successfully','success')
            return redirect(url_for('dashboard'))
        else:
             flash('Invalid credentioals','danger')
             return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():  
      new_user = session.pop('new_user',False)
      return render_template('dashboard.html',username=current_user.username,new_user=new_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)



