from flask import Blueprint, render_template, url_for, redirect, request, flash
import flask_login, re
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Influencer, Campaign, Ad_request
from markupsafe import Markup 

auth=Blueprint("auth",__name__)

@auth.route("/", methods=["GET", "POST"])
@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        user_name=request.form['usrname']
        name=request.form['name']
        mailid=request.form['mail']
        pwd1=request.form['p1']
        pwd2=request.form['p2']
        role=request.form['role']

        email_already_exists=User.query.filter_by(mail=mailid).first()
        user_already_exists=User.query.filter_by(usr_name=user_name).first()

        gen_mail= r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        def isValid(mail):
            if re.fullmatch(gen_mail, mail):
                return "Valid Email"
            else:
                return "Invalid Email"
        
        if isValid(mailid)=='Invalid Email':
            flash('Invalid Email Adress', category='danger')
        elif email_already_exists:
            flash(Markup('Email already in use. <a href="/login" class="alert-link">Login</a> instead.'), category='warning')
        elif user_already_exists:
            flash('Username already exist. Choose a different username.', category='danger')
        elif pwd2!=pwd1:
            flash("Confirm password does not match. Renter the password", category='danger')
        else:
            usr=User(usr_name=user_name, name=name,mail=mailid,password=generate_password_hash(pwd1),role=role)
            db.session.add(usr)
            db.session.commit()
            if role=='Influencer':
                new_influencer = Influencer(
                    user_id=usr.usr_id,  # Reference to the user
                    name=name,
                    mail_id=mailid)
                db.session.add(new_influencer)
                db.session.commit()
            flash('User Created. Login to Proceed', 'success')
            return redirect(url_for("auth.login"))
    return render_template('signup.html', message=0)


# # ---------------------------------- Login --------------------------------------------

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method== 'POST':
        user_name = request.form['usrname']
        pwd = request.form['password']

        if not user_name:
            flash('Please enter username', category='warning')
        elif not pwd:
            flash('Enter the password', category='warning')
        else:
            user = User.query.filter_by(usr_name=user_name).first()
            if user and check_password_hash(user.password, pwd):
                login_user(user)
                if user.role=="Sponsor":
                    return redirect(url_for("views.sponsor_home"))
                elif user.role=="Influencer":
                    influ= Influencer.query.filter_by(user_id=user.usr_id).first()
                    if influ and influ.is_flag:
                        flash("You have been Flagged. Can't login", category="danger")
                        return redirect(url_for('auth.login'))
                    return redirect(url_for("views.influ_home"))
                else:
                    return redirect(url_for("views.admin_home"))
            elif user:
                flash('Invalid Password', category='danger')
            else:
                flash(Markup('You haven\'t registered yet. <a href="/signup" class="alert-link">Sign Up</a> instead'), category='warning')
    return render_template('login.html')


# # ------------------------ LOGOUT -----------------------------------------------------

@auth.route("/logout")
@flask_login.login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))