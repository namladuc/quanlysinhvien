import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask import Response, json, jsonify, send_file, render_template_string
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib.pyplot as plt
import os
import io
import MySQLdb.cursors
import datetime
import calendar
from calendar import monthrange
import pandas as pd
import numpy as np
import functools
import pdfkit
import re

app = Flask(__name__)
app.secret_key = 'La Nam'

UPLOAD_FOLDER = 'static/web'
UPLOAD_FOLDER_IMG = 'static/web/img'
SAVE_FOLDER_PDF = 'static/web/pdf'
SAVE_FOLDER_EXCEL = 'static/web/excel'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'qlsv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_IMG'] = UPLOAD_FOLDER_IMG
app.config['SAVE_FOLDER_PDF'] = SAVE_FOLDER_PDF
app.config['SAVE_FOLDER_EXCEL'] = SAVE_FOLDER_EXCEL

mysql = MySQL(app)

def login_required(func): # need for some router
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)

    return secure_function

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def login():
    if 'username' in session.keys():
        return redirect(url_for("home"))
    
    cur = mysql.connection.cursor()
    
    if 'truong' not in session.keys():
        cur.execute("SELECT * FROM truong")
        truong = cur.fetchall()[0]
        session['truong'] = truong
    
    if request.method == 'POST':
        details = request.form
        user_name = details['username'].strip()
        password = hashlib.md5(details['current-password'].encode()).hexdigest()
        
        if user_name[:6:] == "151056":
            cur.execute("""SELECT us.*, nql.ho_ten, img.path_to_image
                FROM user us
                JOIN nguoi_quan_li nql ON nql.ma_nguoi_quan_li = us.ma_nguoi_dung 
                JOIN image_data img ON img.id_image = nql.id_image
                WHERE username=%s""",(user_name,))
            user_data = cur.fetchall()
        else:        
            cur.execute("""SELECT us.*, sv.ho_ten, img.path_to_image
                    FROM user us
                    JOIN sinh_vien sv ON sv.ma_sinh_vien = us.ma_nguoi_dung 
                    JOIN image_data img ON img.id_image = nql.id_image
                    WHERE username=%s""",(user_name,))
            user_data = cur.fetchall()
        
        if len(user_data)==0:
            return render_template('general/login.html',
                                   truong = session['truong'],
                                   user_exits='False',
                                   pass_check='False')
        
        if password != user_data[0][2]:
            return render_template('general/login.html', 
                                   truong = session['truong'],
                                   user_exits='True', 
                                   pass_check='False')
    
        my_user = user_data[0]
        
        cur.execute("""
                    UPDATE `user` 
                    SET `last_login` = CURRENT_TIMESTAMP()
                    WHERE `user`.`ma_nguoi_dung` = %s
                    """, (my_user[0],))
        session['username'] = my_user
        mysql.connection.commit()
        
        cur.execute("""
                SELECT r.role_path
                FROM role r
                JOIN role_user ru ON ru.role_id = r.role_id
                WHERE ru.id_user = %s
            """, (my_user[0], ))
        role = cur.fetchall()[0][0]
        session['role'] = role
        
        cur.execute("""
                SELECT r.role_id
                FROM role r
                JOIN role_user ru ON ru.role_id = r.role_id
                WHERE ru.id_user = %s
            """, (my_user[0], ))
        role_id = cur.fetchall()[0][0]
        session['role_id'] = role_id
        
        cur.close()
        return redirect(url_for("home"))
    return render_template('general/login.html',
                           truong = session['truong'])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/home")
def home():
    return render_template(session['role'] + 'index.html',
                    my_user = session['username'],
                    truong = session['truong'])

# -------------------------- Khoa -------------------------

@app.route('/form_add_khoa')
def form_add_khoa():
    return "Error"

@app.route("/view_all_khoa")
def view_all_khoa():
    return render_template(session['role'] + 'khoa/view_all_khoa.html',
                           my_user = session['username'],
                           truong = session['truong'])

# -------------------------- Khoa -------------------------

# -------------------------- Sinh vien -------------------------

@app.route("/bang_sinh_vien")
def bang_sinh_vien():
    return render_template('sinhvien/bang_sinh_vien.html')  

"""
    - View table sinh vien:
        SELECT sv.ma_sinh_vien, img.path_to_img, sv.ho_ten, sv.gioi_tinh, 
        FROM sinh_vien sv
        JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
        JOIN lop l ON svl.ma_lop = l.ma_lop
        JOIN khoa k ON l.ma_khoa = k.ma_khoa
        JOIN nganh n ON l.ma_nganh = n.ma_nganh
        JOIN loai_he h ON n.ma_he = h.ma_he
        JOIN image_data img ON sv.id_image = img.id_image
        WHERE sv.is_delete == 0
        
"""
# -------------------------- Sinh vien -------------------------