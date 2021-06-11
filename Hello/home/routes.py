import smtplib
from email.message import EmailMessage
from flask import render_template,redirect,url_for,request,flash
from wtforms.fields.html5 import EmailField
from .forms import Register_Indi,Login_Indi,Register_org,Login_org,Message_Send,ForgotPassword,ResetPassword
from home import app,db,bcrypt,mongo
from .data import User_indi,Message_user,User_org
import psycopg2

app.config['FILE_ALLOWED']=["PNG","JPG","JPEG","TXT","GIF"]

#---------------------------------------------------------------------------------------------------------------------------HOME PAGE-------------
@app.route("/")
def home():
    return render_template('home.html',title="HOME")

#-------------------------------------------------------------------------------------------------------------REGISTER AS AN INDIVIDUAL------------
@app.route('/register_indi',methods=['GET','POST'])
def register_indi():
    formo=Register_Indi()
    if formo.validate_on_submit():
        hashed_pw=bcrypt.generate_password_hash(formo.password.data).decode('utf-8')
        user=User_indi(fname=formo.fname.data,lname=formo.lname.data,email=formo.email.data,password=hashed_pw,aadhar=formo.aadhar.data)

        exist_user=User_indi.query.filter_by(email=formo.email.data).first()
        if exist_user==None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login_indi'))
        else:
            return redirect(url_for('login_indi'))

    return render_template("register_indi.html",form=formo,title="SIGNUP AS INDIVIDUAL")

#-----------------------------------------------------------------------------------------------------REGISTER AS ORGANISATION--------------------
@app.route("/register_org",methods=['GET','POST'])
def register_org():
    formor=Register_org()
    if request.method=='POST':
        hashed_pw = bcrypt.generate_password_hash(formor.passw.data).decode('utf-8')
        org = request.form['orgname']
        hod = request.form['hod']
        address = request.form['address']
        branch = request.form['branch']
        contact = request.form['contact']
        officialemail = request.form['official_email']
        passw = hashed_pw
        filetoupload = request.files['filetoupload']
        filen = filetoupload.filename

        mongo.save_file(filetoupload.filename,filetoupload)
        mongo.db.file_send.insert({'Organisation':org,'Head of the Organisation':hod,'Address':address,'Branch Area':branch, 
        'Contact':contact,'Official Email':officialemail,'Password':passw,'file_name':filen})

        user=User_org(orgname=formor.orgname.data,hod=formor.hod.data,oemail=formor.official_email.data,
                    contact=formor.contact.data,branch=formor.branch.data,passw=hashed_pw,address=formor.address.data)

        existingUser = User_org.query.filter_by(contact=formor.contact.data).first()
        if existingUser==None:
            db.session.add(user)
            db.session.commit()
            flash('You have successfully registered!!')
            return render_template('home.html',title="HOME")

        else:
            flash("You are already a registered organisation!!")
            return redirect(url_for('login_org'))
    return render_template('register_org.html',form=formor)

#------------------------------------------------------------------------------------------------------------LOGIN AS INDIVIDUAL------------------
@app.route('/login_indi',methods=['GET','POST'])
def login_indi():
    forml=Login_Indi()
    if forml.validate_on_submit():
        existingUser=User_indi.query.filter_by(email=forml.email.data).first()
        if existingUser and bcrypt.check_password_hash(existingUser.password,forml.password.data):
            flash("Welcome back !!","success")
            return render_template("message.html",title="HOME")
        else:
            flash("Email does not exist!!")
            return render_template('register_indi.html',title="REGISTER AS INDIVIDUAL")
    return render_template("login_indi.html",title="LOGIN AS INDIVIDUAL",form=forml)

#-------------------------------------------------------------------------------------------------------------LOGIN AS ORGANISATION---------------
@app.route('/login_org',methods=['GET','POST'])
def login_org():
    forml=Login_org()
    if forml.validate_on_submit():
        existingUser=User_org.query.filter_by(contact=forml.contact.data).first()
        if existingUser and bcrypt.check_password_hash(existingUser.passw,forml.passw.data):
            flash("Welcome back !!","success")
            return redirect(url_for("home"))
        else:
            flash("You are not registered!!")
            return render_template("home.html",title="HOME")
    return render_template("login_org.html",title="LOGIN AS ORGANISATION",form=forml)

@app.route('/message',methods=['GET','POST'])
def message():
    form=Message_Send()
    if request.method=='POST':
        user=Message_user(no_of_bodies=form.no_of_bodies.data,street_name=form.street_name.data,area=form.area.data,landmark=form.landmark.data,
        city=form.city.data,pincode=form.pincode.data)
        db.session.add(user)
        db.session.commit()

        number=request.form['no_of_bodies']
        street=request.form['street_name']
        area=request.form['area']
        landmark=request.form['landmark']
        city=request.form['city']
        pincode=request.form['pincode']

        #email sending
        msg=EmailMessage()
        msg['Subject']='Information about the corpses'
        msg['From']='The team of Dignity to the Dead'

        conn = psycopg2.connect(host="localhost",database="register",user="postgres",password="postpass")
        cur=conn.cursor()
        sql="SELECT oemail FROM user_organ"
        cur.execute(sql)
        recipients = cur.fetchall()
        r=len(recipients)
        l=[]
        for i in range(0,r):
            l.append(recipients[i][0])
        print(l)
        msg['To']=','.join(l)
        msg.set_content(f"Number of bodies : {number},\nStreet Name : {street},\nArea : {area},\nLandmark : {landmark},\nCity: {city},\npicode: {pincode}")

        s = smtplib.SMTP_SSL('smtp.gmail.com',465)
        s.login("dignitytothedead@gmail.com","dhasubgopbha")
        s.send_message(msg)
        s.quit()
        print("sent mail")
        return render_template('congrats.html')
    return render_template('message.html',form=form,title='ADD ON')

#to view the content in the file
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

#------------------------------------------------------------------------------------------------------------------RESET PASSWORD----------------
@app.route('/reset',methods=['GET','POST'])
def reset():
    form=ResetPassword()
    if request.method=='POST':
        return redirect(url_for('login_indi'))
    return render_template('reset.html',form=form)
#-------------------------------------------------------------------------------------------------------------------FORGOT PASSWORD---------------
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    form=ForgotPassword()
    if request.method=="POST":
        user=User_indi.query.filter_by(email=form.email.data).first()
        if user:
            msg=EmailMessage()
            msg['Subject']="Reset Password"
            msg['From']="The team of Dignity to the Dead"

            conn=psycopg2.connect(host="localhost",database="register",user="postgres",password="postpass")
            cur=conn.cursor()
            sql="SELECT email FROM user_individual"
            cur.execute(sql)
            recipients=cur.fetchall()

            r=len(recipients)
            l=[]
            for i in range(0,r):
                l.append(recipients[i][0])
            
            find = form.email.data
            for j in l:
                if j==find:
                    msg['To']=find
                    msg.set_content("It is time to reset password")

            s = smtplib.SMTP_SSL('smtp.gmail.com',465)
            s.login("dignitytothedead@gmail.com","dhasubgopbha")
            s.send_message(msg)
            s.quit()
            print("sent_mail")
            return redirect(url_for('reset'))
    return render_template('forgot.html',form=form)





