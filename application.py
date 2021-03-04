from flask import Flask,render_template,url_for,request,flash,redirect,request,session, send_file
import psycopg2
import configparser
import config
import sqlite3
import time
import openpyxl
from datetime import timedelta

class inital(object):
    def __init__(self):
        self.test = False
        con = sqlite3.connect("visits.db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS table_of_visits (ip text,url text,agent text,date text)""")
        con.commit()
        con.close()
        self.admin = False
        self.decrypt_url()

    def decrypt_url(self):
        self.conf = config.Configurate()
        self.suite = self.conf.cipher_suite
        self.encry_host = self.conf.host
        self.encry_database = self.conf.database
        self.encry_user = self.conf.user
        self.encry_port = self.conf.port
        self.encry_password = self.conf.password
        self.encry_admin = self.conf.adminpass
        self.test = True

testing = inital()
app = Flask(__name__)
app.secret_key = "Moicestmartin7687"
app.permanent_session_lifetime = timedelta(minutes=10)

e = "No Error"

@app.route("/noconnection")
def noco():
    return render_template("noco.html",error = e)

@app.route('/info')
def info():
    return render_template("info.html")

@app.route('/clear')
def clear():
    if "admin" in session:
        con = sqlite3.connect("visits.db")
        cur = con.cursor()
        cur.execute("DELETE FROM table_of_visits")
        con.commit()
        con.close()
        return redirect(url_for('admin'))
    else:
        return redirect(url_for("index"))

@app.route("/logout")
def logout():
    if "admin" in session:
        session.pop('admin',None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

@app.route('/login',methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        password = request.form["passw"]
        passwencry = str(testing.suite.decrypt(testing.encry_admin))
        if password == passwencry[2:len(passwencry) - 1]:
            session["admin"] = "ademo"
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("login"))

@app.route('/requestsite',methods = ["GET","POST"])
def requete():
    if request.method == "GET":
        return render_template("requete.html")
    elif request.method == "POST":
        print("reqestzkjrhgjz",request.form)
        titre = request.form["name"]
        descri = request.form["descr"]
        type_site = request.form["type"]
        username = request.form["user"]
        try:
            resp = request.form["resp"]
            resp = "True"
        except:
            resp = "False"
        try:
            tel = request.form["telephone"]
        except:
            tel = "None"

        try:
            email = request.form["email"]
        except:
            email = "None"
        title = titre.replace("'","''")
        descr = descri.replace("'","''")
        dicto = {
            "title":title,
            "descri":descr,
            "tel":tel,
            "email":email
        }
        if email != "None" or tel != "None":
            database = str(testing.suite.decrypt(testing.encry_database))
            host = str(testing.suite.decrypt(testing.encry_host))
            user = str(testing.suite.decrypt(testing.encry_user))
            port = int(testing.suite.decrypt(testing.encry_port))
            password = str(testing.suite.decrypt(testing.encry_password))
            try:
                conadd = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
            except Exception as e:
                return redirect(url_for("noco",error = e))

            curadd = conadd.cursor()
            curadd.execute(f"""INSERT INTO requests (name,descr,phone,email,type,responive,username) VALUES('{title}','{descr}','{tel}','{email}','{type_site}','{resp}','{username}');""")
            conadd.commit()
            conadd.close()
            flash("Requête envoyée avec succès. Nous vous répondrons au plus vite.")
            return redirect(url_for('index'))
        else:
            flash("Vous n'avez pas entré de moyen de contact.")
            return redirect(url_for("requete"))

@app.route('/admin',methods = ["GET","POST"])
def admin():
    if "admin" in session:
        if request.method == "GET":
            return render_template("admin.html")

        elif request.method == "POST":
            return redirect(url_for("admin"))
    else:
        return redirect(url_for("index"))

@app.route('/admin/tab=<tab>',methods = ["GET","POST"])
def admin_tab(tab):
    if "admin" in session:
        if request.method == "GET":
            if tab == "visits":
                con = sqlite3.connect('visits.db')
                cur = con.cursor()
                cur.execute("SELECT * FROM table_of_visits")
                rows = cur.fetchall()
                ip = []
                url = []
                agent = []
                dates = []
                for r in rows:
                    ip.append(str(r[0]))
                    url.append(str(r[1]))
                    agent.append(str(r[2]))
                    dates.append(str(r[3]))

                return render_template("visits.html",longv= len(ip),ips = ip,urls = url, agents = agent,dates = dates)
            elif tab == "addsite":
                return render_template("add_site.html")
            
            elif tab == "requests":
                database = str(testing.suite.decrypt(testing.encry_database))
                host = str(testing.suite.decrypt(testing.encry_host))
                user = str(testing.suite.decrypt(testing.encry_user))
                port = int(testing.suite.decrypt(testing.encry_port))
                password = str(testing.suite.decrypt(testing.encry_password))
                conadd = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
                curadd = conadd.cursor()
                curadd.execute("""SELECT * FROM requests""")
                rows = curadd.fetchall()
                titles = []
                descr = []
                tel = []
                email = []
                types = []
                responive = []
                username = []

                for r in rows:
                    titles.append(str(r[0]))
                    descr.append(str(r[1]))
                    tel.append(str(r[2]))
                    email.append(str(r[3]))
                    types.append(str(r[4]))
                    responive.append(str(r[5]))
                    username.append(str(r[6]))

                conadd.close()
                return render_template('requests.html',long = len(titles),titles = titles,descr = descr,tel = tel,email = email,types = types,responsive = responive,username = username)
                
            elif tab == 'devis':
                return render_template("add_devis.html")
            else:
                return redirect(url_for("admin"))
        else:

            if tab == "addsite":
                title = request.form["titre"]
                descr = request.form["descr"]
                link = request.form["link"]
                titre = title.replace("'","''")
                descr = descr.replace("'","''")
                database = str(testing.suite.decrypt(testing.encry_database))
                host = str(testing.suite.decrypt(testing.encry_host))
                user = str(testing.suite.decrypt(testing.encry_user))
                port = int(testing.suite.decrypt(testing.encry_port))
                password = str(testing.suite.decrypt(testing.encry_password))
                try:
                    conadd = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
                except Exception as e:
                    return redirect(url_for("noco",error = e))                
                
                curadd = conadd.cursor()
                curadd.execute(f"""INSERT INTO site (titre,descr,lien) VALUES('{titre}','{descr}','{link}');""")
                conadd.commit()
                conadd.close()
                flash("C'est tout bon")
                return redirect(url_for("admin_tab",tab = "addsite"))

            elif tab == "devis":
                descriptions = []
                prix = []
                progress = []
                for x in range(1,11):
                    if request.form["descr"+str(x)] != '' and request.form["prix"+str(x)] != '':
                        descriptions.append(request.form["descr"+str(x)])
                        prix.append(int(request.form["prix"+str(x)]))
                        progress.append('F')

                liste_devis = [descriptions,prix,progress]
                email = request.form["titre"]
                code = request.form["link"]

                total = 0
                for y in liste_devis[1]:
                    total = total + y

                database = str(testing.suite.decrypt(testing.encry_database))
                host = str(testing.suite.decrypt(testing.encry_host))
                user = str(testing.suite.decrypt(testing.encry_user))
                port = int(testing.suite.decrypt(testing.encry_port))
                password = str(testing.suite.decrypt(testing.encry_password))
                conadd = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
                curadd = conadd.cursor()
                print(liste_devis)
                curadd.execute(f"""INSERT INTO devis (code,email,prix,detail,detail_prix,progress) VALUES('{code}','{email}','{total}',ARRAY{liste_devis[0]},ARRAY{liste_devis[1]},ARRAY{liste_devis[2]});""")
                conadd.commit()
                conadd.close()
                print(liste_devis)
                return render_template("to_send.html",email = email,code = code)
            else:
                return redirect(url_for("admin"))
    else:
        return redirect(url_for("index"))
                


def add_visit():
    con = sqlite3.connect("visits.db")
    cur = con.cursor()
    cur.execute(f"""INSERT INTO table_of_visits (ip,url,agent,date) VALUES('{request.remote_addr}','{request.url}','{request.user_agent}','{time.strftime('%d/%m/%y')}')""")
    con.commit()
    con.close()
    return True

@app.route("/deconnect")
def deconnect():
    session.pop('email',None)
    session.pop('password',None)
    flash("Vous êtes bien déconnecté.")
    return redirect(url_for('index'))

@app.route('/client/create',methods = ["GET","POST"])
def create():
    if request.method == "GET":
        return redirect(url_for("client"))
    else:
        new_passw = request.form["passw"]
        url = inital()
        database = str(url.suite.decrypt(url.encry_database))
        host = str(url.suite.decrypt(url.encry_host))
        user = str(url.suite.decrypt(url.encry_user))
        port = int(url.suite.decrypt(url.encry_port))
        password = str(url.suite.decrypt(url.encry_password))
        try:
            con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
        except Exception as err:
            e = err
            return redirect(url_for("noco"))

        cur = con.cursor()
        cur.execute(f"""SELECT password FROM devis WHERE email = '{session["email"]}'""")
        cur.execute(f"""UPDATE devis SET password = '{new_passw}' WHERE email = '{session["email"]}'""")
        con.commit()
        session["password"] = new_passw
        con.close()
        return redirect(url_for('client'))



@app.route('/client',methods = ["GET","POST"])
def client():
    if request.method == "GET":
        if "email" in session:
            if "password" in session:
                url = inital()
                database = str(url.suite.decrypt(url.encry_database))
                host = str(url.suite.decrypt(url.encry_host))
                user = str(url.suite.decrypt(url.encry_user))
                port = int(url.suite.decrypt(url.encry_port))
                password = str(url.suite.decrypt(url.encry_password))
                try:
                    con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
                except Exception as err:
                    e = err
                    return redirect(url_for("noco"))

                cur = con.cursor()
                cur.execute(f"""SELECT * FROM devis WHERE email = '{session["email"]}' AND password = '{session["password"]}'""")
                rows = cur.fetchall()
                con.close()
                result_devis = [[],[]]
                for r in rows:
                    code = str(r[0]) + str(r[1])
                    for x in range(len(r[4])):
                        (result_devis[0]).append(r[4][x])
                        (result_devis[1]).append(r[6][x])
                return render_template("client.html",name = session["email"],details = result_devis,long = len(result_devis[1]),code = code)
            else:
                return render_template('connection.html',email = session["email"])
        else:
            return render_template('connectemail.html')

    else:
        url = inital()
        database = str(url.suite.decrypt(url.encry_database))
        host = str(url.suite.decrypt(url.encry_host))
        user = str(url.suite.decrypt(url.encry_user))
        port = int(url.suite.decrypt(url.encry_port))
        password = str(url.suite.decrypt(url.encry_password))
        try:
            con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
        except Exception as err:
            e = err
            return redirect(url_for("noco"))

        cur = con.cursor()
        try:
            email = request.form["email"]
            print("Email")
            cur.execute(f"SELECT password,code FROM devis WHERE email = '{email}'")
            rows = cur.fetchall()
            if rows[0][1] != None:
                if rows[0][0] != None:
                    session["email"] = email
                    return redirect(url_for('client'))
                else:
                    session["email"] = email
                    return render_template("client_connect.html",email = email)
            else:
                flash('Mauvais email')
                return redirect(url_for('client'))
        except:
            try:
                password = request.form["passw"]
                cur.execute(f"""SELECT * FROM devis WHERE email = '{session["email"]}'""")
                rows = cur.fetchall()
                for r in rows:
                    if r[7] == password:
                        session["password"] = password
                        return redirect(url_for('client'))
                    else:
                        flash('Mauvais mot de passe')
                        return redirect(url_for('client'))
            except:
                print("error")
                return 'error'


@app.route("/devis&code=<code>/download")
def download_devis(code):
    if "email" in session:
        xlsx = openpyxl.Workbook()
        sheet = xlsx.active
        sheet.append(["Devis Weberama",time.strftime("%d/%m/%y")])
        sheet.append([email,code])
        for x in range(len(result_devis[0])):
            sheet.append([result_devis[0][x],result_devis[1][x]])

        sheet.append(["Total:",total_devis])
        xlsx.save(f'devis{code}.xlsx')
        filename = 'devis' + code + '.xlsx'
        return send_file(filename, as_attachment=True)
    

@app.route("/devis&code=<code>", methods = ["GET","POST"])
def devis(code):
    global e
    if request.method == "GET":
        if "email" in session:
            email = session["email"]
            url = inital()
            database = str(url.suite.decrypt(url.encry_database))
            host = str(url.suite.decrypt(url.encry_host))
            user = str(url.suite.decrypt(url.encry_user))
            port = int(url.suite.decrypt(url.encry_port))
            password = str(url.suite.decrypt(url.encry_password))
            try:
                con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
            except Exception as err:
                e = err
                return redirect(url_for("noco"))

            cur = con.cursor()
            to = len(str(code)) - 7
            id = int(str(code)[:to])
            coding = code[len(str(id)):]
            cur.execute(f"""SELECT * FROM devis WHERE id = {id} AND code = '{coding}' AND email = '{email}'""")
            rows = cur.fetchall()
            result_devis = [[],[]]
            if len(rows) > 0:
                for r in rows:
                    title_devis = r[2]
                    total_devis = r[3]
                    for x in range(len(r[4])):
                        result_devis[0].append(r[4][x])
                        result_devis[1].append(r[5][x])

                return render_template("devis.html",titre = title_devis,total = total_devis,details = result_devis,long = len(result_devis[0]),code = code)
            else:
                flash("Code invalide")
                session.pop('email',None)
                return redirect(url_for("devis",code = code))

        else:
            return render_template("login_devis.html")
    else:
        email = request.form["email"]
        url = inital()
        database = str(url.suite.decrypt(url.encry_database))
        host = str(url.suite.decrypt(url.encry_host))
        user = str(url.suite.decrypt(url.encry_user))
        port = int(url.suite.decrypt(url.encry_port))
        password = str(url.suite.decrypt(url.encry_password))
        try:
            con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
        except Exception as err:
            return render_template("noco",error = err)

        cur = con.cursor()
        cur.execute(f"""SELECT id, code FROM devis WHERE email = '{email}'""")
        rows = cur.fetchall()
        print(rows)
        if len(rows) > 0:
            session["email"] = email
            return redirect(url_for("devis",code = code))
        else:
            flash("Il n'y a pas d'email associé.")
            return redirect(url_for("devis",code = code))

@app.route('/')
def index():
    global e
    url = inital()
    database = str(url.suite.decrypt(url.encry_database))
    host = str(url.suite.decrypt(url.encry_host))
    user = str(url.suite.decrypt(url.encry_user))
    port = int(url.suite.decrypt(url.encry_port))
    password = str(url.suite.decrypt(url.encry_password))
    try:
        con = psycopg2.connect(host = host[2:len(host) - 1],user = user[2:len(user) - 1], database = database[2:len(database) - 1],password = password[2:len(password) - 1],port = port)
        print('\033[93m',"----------\n##### -CONNECTION ESTABLISHED- #####\n----------",'\033[0m')
    except Exception as err:
        print('\033[93m',f"----------\n##### -{err}- #####\n----------",'\033[0m')
        return render_template("noco.html",error = err)

    cur = con.cursor()
    cur.execute("SELECT * FROM site")
    rows = cur.fetchall()
    titles = []
    links = []
    descr = []
    adminonwer = []
    for r in rows:
        titles.append(str(r[0]).replace("''","'"))
        links.append(str(r[2]))
        descr.append(str(r[1]).replace("''","'"))

    add_visit()
    return render_template('index.html',titles = titles,links = links,descr = descr,long = len(titles))

if __name__ == "__main__":
    if testing.test == True:
        app.run(debug=True)