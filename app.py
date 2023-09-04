import sqlite3
from pandas.core.reshape.concat import concat
from pandas.io import json
import cx_Oracle 
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect,jsonify
from werkzeug.exceptions import abort
from flasgger import Swagger
from flasgger import swag_from
from flask_cors import CORS


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_Oracle_db_connection():
    conn = cx_Oracle.connect("erz", "erz", "db14")
    #con.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

# Connect as user "hr" with password "welcome" to the "orclpdb1" service running on this computer.
#connection = cx_Oracle.connect("erz", "erz", "db14")




def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your secret key'

app.config['SWAGGER'] = {
    'title': 'WK-Dashboard API'
}
swagger = Swagger(app)

@app.route('/')
@swag_from('Dashboard_api.yml')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

@app.route('/test')
def test():
    conn = get_db_connection()
    conn.row_factory = dict_factory
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()

    return jsonify(posts)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))


@app.route('/statistic')
def statistic():
    con = get_Oracle_db_connection()
    #con = cx_Oracle.connect("erz", "erz", "db14")
    #cursor = connection.cursor()
    #cursor.execute("""select to_char(Anfang,'YYYY-MM') as DATUM, sum(sum_Kosten ) as Kosten from(select Anfang,sum(KAPAZITAET) over(order by Anfang,Ende asc)as Sum_Kosten from lfp_Termine where Vorhaben_ID = 6358)group by  to_char(Anfang,'YYYY-MM')order by Datum """) 
    #cursor.execute(""" select Ressource, sum(KAPAZITAET) as Kapa from lfp_termine where Vorhaben_id = 6358  and Ressource <> 'FL' group by Ressource  """)
    #rows = cursor.fetchall()
    
    #labels = []
    #values = []
    

    #for row in rows:
    #    labels.append(row[0])
    #    values.append(row[1])
    
    df = pd.read_sql("""select to_char(Anfang,'YYYY-MM') as DATUM, sum(sum_Kosten ) as Kosten from(select Anfang,sum(KAPAZITAET) over(order by Anfang,Ende asc)as Sum_Kosten from lfp_Termine where Vorhaben_ID = 6358)group by  to_char(Anfang,'YYYY-MM')order by Datum """,con)
    labels = df['DATUM'].values.tolist()
    values = df['KOSTEN'].values.tolist()

    x = pd.read_sql("""Select Beschreibung, Ressource, Kapazitaet, Anfang, Ende From LFP_Termine where Vorhaben_ID = 6358""",con)
   #print (df2)
    #con = sqlite3.cnnect('database.db')
    #df = pd.read_sql_query("SELECT * from posts", con) 
    #con = sqlite3.connect('database.db')
    #df = pd.read_sql_query("select date(created) as Datum ,count(*) as Anzahl, sum(count(*))over(order by date(created) asc)as Sum_Anzahl  from posts group by date(created)",con)
    #labels = df['Datum'].values.tolist()
    #values = df['Sum_Anzahl'].values.tolist()

    legend = 'Monthly Data'
    #abels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    #values = [5, 9, 8, 11, 6, 4, 7, 8]

    #labels2 = df['Datum'].values.tolist()
    #values21 = df['Anzahl'].values.tolist()
    #values22 = df['Sum_Anzahl'].values.tolist()
    legend2 = 'Monthly Data'
    labels2 = ["S", "M", "T", "W", "T", "F", "S"]
    values21 =  [589, 445, 483, 503, 689, 692, 634]
    values22 = [639, 465, 493, 478, 589, 632, 674]

     
     

    con.close()
    return render_template('statistic.html', values=values, labels=labels, legend=legend,values21=values21, values22=values22, labels2=labels2,legend2=legend2, data = x)


@app.route('/WK_Dashboard', methods=['GET'])
def WK_Dashboard():
   return "<h1>WK Dashboard API</h1><p><h2>API CALL's</h2></p><p><a href='/WK_Dashboard/all'>WK_Dashboard/all -- Alle Daten</a></p>"



@app.route('/WK_Dashboard/all', methods=['GET'])
@swag_from('Dashboard_api.yml')
def WK_Dashboard_all():

    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    WK_all = cur.execute('SELECT * FROM WK_Dashboard;').fetchall()

    return jsonify(WK_all)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
