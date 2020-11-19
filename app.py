import io
import csv
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost/lo_lf_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='lo_lf_tracker',
                                         user='root',
                                         password='')
except:
    print("Error Connection")

db = SQLAlchemy(app)


# Creating model table for our CRUD database
class associates(db.Model):
    __tablename__ = 'associates'
    badge_barcode_id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    employee_name = db.Column(db.String(100))


class data(db.Model):
    sn = db.Column(db.Integer)
    badge_barcode_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    amazon_id = db.Column(db.String(100))
    date = db.Column(db.String(100))
    lolf = db.Column(db.String(100))

    def __init__(self, badge_barcode_id, employee_name, amazon_id, date, lolf):
        self.badge_barcode_id = badge_barcode_id
        self.employee_name = employee_name
        self.amazon_id = amazon_id
        self.date = date
        self.lolf = lolf


@app.route('/')
def Index():
    return render_template("index.html")


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    badge_barcode_id = request.form['badge_barcode_id']
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    lolf = request.form['lolf']

    try:

        sql_select_Query1 = "SELECT employee_name, user_id FROM associates WHERE badge_barcode_id = {};".format(
            badge_barcode_id)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query1)
        records = cursor.fetchall()

        sql = "INSERT INTO data(badge_barcode_id, employee_name, amazon_id, date, lolf) VALUES (%s, %s, %s, %s, %s)"
        value = (badge_barcode_id, records[0][0], records[0][1], date, lolf)
        print(value)
        cursor.execute(sql, value)
        #connection.commit()

        flash(lolf + " Driver \"" + records[0][1] + "\" Checked In Succcessful")

        return redirect(url_for('Index'))
    except:
        flash(badge_barcode_id + " Associate Not Found")
        return redirect(url_for('Index'))


@app.route('/fetch', methods=['POST'])
def fetch():
    start = request.form['start']
    end = request.form['end']
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")

    if (start == '') and (end != ''):
        print("1st")
        date_end = datetime.strptime(end, '%Y-%m-%d').date()
        formatted_end = datetime.strftime(date_end, '%d/%m/%Y')
        sql_select_Query = "select * from data where date <= '{} 23:59:59.999'".format(formatted_end)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        return render_template("display.html", data=records)


    elif (end == '') and (start != ''):
        print("2st")
        date_start = datetime.strptime(start, '%Y-%m-%d').date()
        formatted_start = datetime.strftime(date_start, '%d/%m/%Y')
        sql_select_Query = "select * from data where date between {} and '{} 23:59:59.999'".format(formatted_start,
                                                                                                   date)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        return render_template("display.html", data=records)

    elif (start == '' and end == ''):
        print("3st")

        sql_select_Query = "select * from data"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        return render_template("display.html", data=records)

    else:
        print("4st")
        date_start = datetime.strptime(start, '%Y-%m-%d').date()
        formatted_start = datetime.strftime(date_start, '%d/%m/%Y')
        date_end = datetime.strptime(end, '%Y-%m-%d').date()
        formatted_end = datetime.strftime(date_end, '%d/%m/%Y')
        sql_select_Query = "select * from data where date between {} and '{} 23:59:59.999'".format(formatted_start,
                                                                                                   formatted_end)
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        return render_template("display.html", data=records)

    return redirect(url_for('Index'))


@app.route('/add_user', methods=['POST'])
def add_user():
    add_badge_barcode_id = request.form['add_badge_barcode_id']
    employee_id = request.form['employee_id']
    amazon_id = request.form['amazon_id']
    employee_name = request.form['employee_name']

    try:
        cursor = connection.cursor()
        sql = "INSERT INTO associates(badge_barcode_id, employee_id, user_id, employee_name) VALUES (%s, %s, %s, %s)"
        value = (add_badge_barcode_id, employee_id, amazon_id, employee_name);
        print(value)
        cursor.execute(sql, value)

        flash(" Associate \"" + employee_name + "\" added Succcessful")

        return redirect(url_for('Index'))

    except:
        flash("Something went wrong, Please try again")
        return redirect(url_for('Index'))


@app.route('/download')
def download():

        output = io.StringIO()
        writer = csv.writer(output)

        sql_select_Query = "select * from data"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        line = ['S/N', 'BADGE ID' , 'EMPLOYEE NAME' , 'USER ID', 'DATE', 'FUNCTION']
        writer.writerow(line)
        for row in records:
            line = [str(row[0]), str(row[1]), str(row[2]), str(row[
                3]), str(row[4]), str(row[5])]
            writer.writerow(line)

        output.seek(0)
        return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=Lo_LF_Report.csv"})




if __name__ == '__main__':
    app.run(debug=True)
