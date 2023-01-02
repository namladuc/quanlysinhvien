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
import math

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

def login_required(func): # need for all router
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
                    JOIN image_data img ON img.id_image = sv.id_image
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
                    WHERE `user`.`id_user` = %s
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
        
        cur.execute("SHOW PROCESSLIST")
        data = cur.fetchall()
        check = True
        for elm in data:
            if ('event_scheduler' in elm):
                check = False
                
        if (check):
            mysql.connection.cursor().execute("SET GLOBAL event_scheduler = ON;")
            mysql.connection.commit()
        
        cur.close()
        return redirect(url_for("home"))
    return render_template('general/login.html',
                           truong = session['truong'])

@login_required
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@login_required
@app.route("/home")
def home():
    return render_template(session['role'] + 'index.html',
                    my_user = session['username'],
                    truong = session['truong'])

@app.route("/forgot")
def forgot():
    return render_template("general/forgot.html",
                           truong = session['truong'])

# -------------------------- Khoa -------------------------

@login_required
@app.route("/view_all_khoa")
def view_all_khoa():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT k.*, COUNT(n.ma_nganh)
                FROM nganh n
                RIGHT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE n.is_delete IS NULL OR n.is_delete != 1
                GROUP BY k.ma_khoa
                """)
    cac_khoa = cur.fetchall()
    
    return render_template(session['role'] + 'khoa/view_all_khoa.html',
                           cac_khoa = cac_khoa,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/view_all_khoa/view_khoa/<string:ma_khoa>")
def view_khoa(ma_khoa):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT k.*, COUNT(n.ma_nganh)
                FROM nganh n
                RIGHT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE (n.is_delete IS NULL OR n.is_delete != 1) AND k.ma_khoa = %s
                GROUP BY k.ma_khoa
                """, (ma_khoa, ))
    khoa = cur.fetchall()
    
    if (len(khoa) == 0):
        return "Error"
    
    khoa = khoa[0]
    
    cur.execute("""
                SELECT n.ma_nganh, n.ten_nganh, n.hinh_thuc_dao_tao, lh.ten_he, lh.hoc_phi_tin_chi
                FROM nganh n 
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                WHERE n.is_delete = 0 AND n.ma_khoa = %s
                """, (ma_khoa, ))
    cac_nganh = cur.fetchall()
    
    return render_template(session['role'] + 'khoa/view_khoa.html',
                           khoa = khoa,
                           cac_nganh = cac_nganh,
                           my_user = session['username'],
                           truong = session['truong'])
    
@login_required
@app.route("/view_all_khoa/form_add_khoa", methods=['GET','POST'])
def form_add_khoa():
    if request.method == 'POST':
        details = request.form
        ma_khoa= details['ma_khoa']
        ten_khoa = details['ten_khoa']
        
        cur = mysql.connection.cursor()
        cur.execute("""
                    SELECT * FROM khoa WHERE ma_khoa = %s
                    """, (ma_khoa, ))
        kiem_tra_ma_khoa = cur.fetchall()
        if (len(kiem_tra_ma_khoa) != 0):
            return render_template(session['role'] + 'khoa/form_add_khoa.html',
                                   ma_err = "Mã khoa đã tồn tại",
                                   my_user = session['username'],
                                   truong = session['truong'])
            
        cur.execute("""
                    INSERT INTO khoa(ma_khoa, ten_khoa) 
                    VALUES (%s, %s)
                    """, (ma_khoa, ten_khoa))
        mysql.connection.commit()
        return redirect(url_for('view_all_khoa'))
        
    return render_template(session['role'] +'khoa/form_add_khoa.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/view_all_khoa/form_update_khoa/<string:ma_khoa>", methods=['GET','POST'])
def form_update_khoa(ma_khoa):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT * 
                FROM khoa 
                WHERE ma_khoa = %s
                """, (ma_khoa, ))
    khoa = cur.fetchall()
    
    if (len(khoa) != 1):
        return "Error"
    
    khoa = khoa[0]
    
    if (request.method == 'POST'):
        details = request.form
        ten_khoa = details['ten_khoa']
        
        cur.execute("""
                    UPDATE khoa
                    SET ten_khoa = %s
                    WHERE ma_khoa = %s
                    """, (ten_khoa, ma_khoa))
        mysql.connection.commit()
        return redirect(url_for('view_khoa', ma_khoa = ma_khoa))
    
    return render_template(session['role'] +'khoa/form_update_khoa.html',
                           khoa = khoa,
                           my_user = session['username'],
                           truong = session['truong'])
    
@login_required
@app.route("/delete_khoa/<string:ma_khoa>")
def delete_khoa(ma_khoa):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT COUNT(n.ma_nganh)
                FROM nganh n
                RIGHT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE (n.is_delete IS NULL OR n.is_delete != 1) AND k.ma_khoa = %s
                GROUP BY k.ma_khoa
                """, (ma_khoa, ))
    data = cur.fetchall()[0][0]
    if (data != 0):
        return "Error"
    
    cur.execute("""
                DELETE FROM khoa
                WHERE ma_khoa = %s 
                """, (ma_khoa, ))
    
    mysql.connection.commit()
    return redirect(url_for('view_all_khoa'))

# -------------------------- Khoa -------------------------


# -------------------------- Nganh -------------------------

@app.route("/table_nganh")
def table_nganh():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT n.ma_nganh, n.ten_nganh, n.hinh_thuc_dao_tao, k.ten_khoa, lh.ten_he, COUNT(l.ma_lop)
                FROM nganh n
                LEFT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                LEFT JOIN loai_he lh ON lh.ma_he = n.ma_he
                LEFT JOIN lop l ON l.ma_nganh = n.ma_nganh
                WHERE n.is_delete = 0 AND (l.is_delete = 0 OR l.is_delete IS NULL)
                GROUP BY n.ma_nganh
                ORDER BY k.ten_khoa ASC, n.ten_nganh ASC
                """)
    cac_nganh = cur.fetchall()
    
    return render_template(session['role'] + 'nganh/table_nganh.html',
                           cac_nganh = cac_nganh,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/get_table_nganh_excel")
def get_table_nganh_excel():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT n.ma_nganh, n.ten_nganh, n.hinh_thuc_dao_tao, k.ten_khoa, lh.ten_he, COUNT(l.ma_lop)
                FROM nganh n
                LEFT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                LEFT JOIN loai_he lh ON lh.ma_he = n.ma_he
                LEFT JOIN lop l ON l.ma_nganh = n.ma_nganh
                WHERE n.is_delete = 0 AND (l.is_delete = 0 OR l.is_delete IS NULL)
                GROUP BY n.ma_nganh
                ORDER BY k.ten_khoa ASC, n.ten_nganh ASC
                """)
    cac_nganh = cur.fetchall()
    columnName = ['MaNganh','TenNganh','HinhThucDaoTao','TenKhoa','TenHe','SoLuongLop']
    data = pd.DataFrame.from_records(cac_nganh, columns=columnName)
    data = data.set_index('MaNganh')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Nganh.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_print_nganh")
def table_print_nganh():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT n.ma_nganh, n.ten_nganh, n.hinh_thuc_dao_tao, k.ten_khoa, lh.ten_he, COUNT(l.ma_lop)
                FROM nganh n
                LEFT JOIN khoa k ON k.ma_khoa = n.ma_khoa
                LEFT JOIN loai_he lh ON lh.ma_he = n.ma_he
                LEFT JOIN lop l ON l.ma_nganh = n.ma_nganh
                WHERE n.is_delete = 0 AND (l.is_delete = 0 OR l.is_delete IS NULL)
                GROUP BY n.ma_nganh
                ORDER BY k.ten_khoa ASC, n.ten_nganh ASC
                """)
    cac_nganh = cur.fetchall()
    return render_template("nganh/table_print_nganh.html",
                           cac_nganh = cac_nganh)

@login_required
@app.route("/get_table_nganh_pdf")
def get_table_nganh_pdf():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Nganh.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_nganh',pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_nganh/form_add_nganh_upload_file", methods=['GET','POST'])
def form_add_nganh_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_nganh_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_nganh_upload_process", filename=filename))
        return redirect(url_for("form_add_nganh_upload_file"))
    return render_template(session['role'] + 'nganh/form_add_nganh_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_nganh/form_add_nganh_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_nganh_upload_process(filename):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_nganh','ten_nganh','hinh_thuc_dao_tao','ma_khoa','ma_he']
    
    default_name_column = ['Mã ngành', 'Tên ngành', 'Hình thức đào tạo', 'Mã khoa', 'Mã hệ']
    
    data_mon_hoc = pd.read_excel(pathToFile)
    data_column = list(data_mon_hoc.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column) < 3:
        return "Error"
        
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 5):
            return "Error"
        
        # Kiểm tra xem mã ngành có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != 0):
            return "Error"
        
        # Kiểm tra xem mã khoa có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(3)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_khoa FROM khoa WHERE ma_khoa = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_khoa FROM khoa WHERE ma_khoa IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        # Kiểm tra xem mã hệ có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(4)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_he FROM loai_he WHERE ma_he = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_he FROM loai_he WHERE ma_he IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        sql = "INSERT INTO `nganh` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql = sql[:-1:]
        sql += ") VALUES "
        for index_row in range(data_mon_hoc.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_mon_hoc[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]  
        
        cur.execute(sql)
        mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for("table_nganh"))        
    
    return render_template(session['role'] + 'nganh/form_add_nganh_upload_process.html',
                           filename = filename,
                           truong = session['truong'],
                           my_user = session['username'],
                           name_column = default_name_column,
                           index_column = data_column)

@login_required
@app.route("/table_nganh/view_nganh_lop/<string:ma_nganh>")
def view_nganh_lop(ma_nganh):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT ma_nganh, ten_nganh FROM nganh WHERE ma_nganh = %s", (ma_nganh, ))
    nganh = cur.fetchall()
    
    if (len(nganh) != 1):
        return "Error"
    
    nganh = nganh[0]
    
    cur.execute("""
                SELECT l.*
                FROM lop l 
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE n.ma_nganh = %s AND l.is_delete = 0
                """, (ma_nganh, ))
    cac_lop = cur.fetchall()
    
    return render_template(session['role'] + 'nganh/view_nganh_lop.html',
                           nganh = nganh,
                           cac_lop = cac_lop,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_nganh/form_add_nganh", methods=['GET','POST'])
def form_add_nganh():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM khoa")
    cac_khoa = cur.fetchall()
    
    cur.execute("SELECT * FROM loai_he")
    cac_he = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_nganh = details['ma_nganh'].strip()
        ma_khoa = details['ma_khoa'].strip().split("_")[0].strip()
        ten_nganh = details['ten_nganh'].strip()
        hinh_thuc_dao_tao = details['hinh_thuc_dao_tao'].strip()
        ma_he = details['ma_he'].split("_")[0].strip()
        
        cur.execute("""
                    SELECT * 
                    FROM nganh
                    WHERE ma_nganh = %s
                    """, (ma_nganh, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'nganh/form_add_nganh.html',
                                   ma_err = "Mã ngành đã tồn tại",
                                   cac_he = cac_he,
                                   cac_khoa = cac_khoa,
                                   my_user = session['username'],
                                   truong = session['truong'])
        
        cur.execute("""
                    INSERT INTO nganh(ma_nganh, ma_khoa, ten_nganh, hinh_thuc_dao_tao, ma_he) VALUES
                    (%s, %s, %s, %s, %s)
                    """, (ma_nganh, ma_khoa, ten_nganh, hinh_thuc_dao_tao, ma_he))
        mysql.connection.commit()
        return redirect(url_for('table_nganh'))
        
    return render_template(session['role'] + 'nganh/form_add_nganh.html',
                           cac_khoa = cac_khoa,
                           cac_he = cac_he,
                           my_user = session['username'],
                           truong = session['truong']) 

@login_required
@app.route("/table_nganh/form_update_nganh/<string:ma_nganh>", methods = ['GET','POST'])
def form_update_nganh(ma_nganh):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT *
                FROM nganh n
                WHERE n.is_delete = 0 AND n.ma_nganh = %s
                """, (ma_nganh, ))
    nganh = cur.fetchall()
    
    if (len(nganh) != 1):
        return "Error"
    
    nganh = nganh[0]
    
    cur.execute("SELECT * FROM loai_he")
    cac_he = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_nganh = nganh[0]
        ma_khoa = nganh[1]
        ten_nganh = details['ten_nganh'].strip()
        hinh_thuc_dao_tao = details['hinh_thuc_dao_tao'].strip()
        ma_he = details['ma_he'].strip()
        
        cur.execute("""
                    UPDATE nganh
                    SET ten_nganh = %s, hinh_thuc_dao_tao = %s,
                    ma_he = %s WHERE ma_nganh = %s
                    """, (ten_nganh, hinh_thuc_dao_tao, ma_he, ma_nganh))
        mysql.connection.commit()
        return redirect(url_for('table_nganh'))
    
    return render_template(session['role'] + 'nganh/form_update_nganh.html',
                           cac_he = cac_he,
                           nganh = nganh,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_nganh/view_nganh_he")
def view_nganh_he():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM loai_he")
    cac_he = cur.fetchall()
    
    return render_template(session['role'] + 'nganh/view_nganh_he.html',
                           cac_he = cac_he,
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_nganh/form_add_he", methods=['GET','POST'])
def form_add_he():
    if request.method == 'POST':
        details = request.form
        ma_he = details['ma_he'].strip()
        ten_he = details['ten_he'].strip()
        hoc_phi_tin_chi = details['hoc_phi_tin_chi'].strip()
        
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT * FROM loai_he WHERE ma_he = %s", (ma_he, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'nganh/form_add_he.html',
                                   ma_err = "Mã hệ đã tồn tại",
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        cur.execute("""INSERT INTO loai_he(ma_he, ten_he, hoc_phi_tin_chi)
                    VALUES (%s, %s, %s)
                    """, (ma_he, ten_he, hoc_phi_tin_chi))
        mysql.connection.commit()
        return redirect(url_for('view_nganh_he'))
            
    return render_template(session['role'] + 'nganh/form_add_he.html',
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_nganh/form_update_he/<string:ma_he>", methods=['GET','POST'])
def form_update_he(ma_he):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM loai_he WHERE ma_he = %s", (ma_he, ))
    he = cur.fetchall()
    
    if (len(he) != 1):
        return "Error"
    
    he = he[0]
    
    if request.method == 'POST':
        details = request.form
        ten_he = details['ten_he'].strip()
        hoc_phi_tin_chi = details['hoc_phi_tin_chi'].strip()
        
        cur.execute("""
                    UPDATE loai_he
                    SET ten_he = %s, hoc_phi_tin_chi = %s
                    WHERE ma_he = %s
                    """, (ten_he, hoc_phi_tin_chi, ma_he))
        mysql.connection.commit()
        return redirect(url_for("view_nganh_he"))        
        
    return render_template(session['role'] + 'nganh/form_update_he.html',
                           he = he,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/delete_he/<string:ma_he>")
def delete_he(ma_he):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT COUNT(*) FROM nganh WHERE ma_he = %s", (ma_he, ))
    if (cur.fetchall()[0][0] != 0):
        return "Error"
    
    cur.execute("DELETE FROM loai_he WHERE ma_he = %s", (ma_he, ))
    mysql.connection.commit()
    return redirect(url_for('view_nganh_he'))

@login_required
@app.route("/delete_nganh/<string:ma_nganh>")
def delete_nganh(ma_nganh):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                UPDATE nganh
                SET is_delete = 1
                WHERE ma_nganh = %s
                """, (ma_nganh, ))
    mysql.connection.commit()
    
    return redirect(request.url)
# -------------------------- Nganh -------------------------


# -------------------------- Lop -------------------------

@login_required
@app.route("/table_lop")
def table_lop():
    cur = mysql.connection.cursor()
    
    cur.execute("""
               SELECT l.*, n.ten_nganh, COUNT(svl.ma_sinh_vien)
                FROM lop l 
                LEFT JOIN sinh_vien_lop svl ON svl.ma_lop = l.ma_lop
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE l.is_delete = 0
                GROUP BY l.ma_lop
                """)
    cac_lop = cur.fetchall()
    
    return render_template(session['role'] + 'lop/table_lop.html', 
                           cac_lop = cac_lop,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_lop/form_add_lop", methods=['GET','POST'])
def form_add_lop():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM nganh WHERE is_delete = 0")
    cac_nganh = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_lop = details['ma_lop'].strip()
        ma_nganh = details['ma_nganh'].split("_")[0].strip()
        nam = details['nam'].strip()
        ten_lop = details['ten_lop'].strip()
        ma_nguoi_quan_ly = details['ma_nguoi_quan_ly'].strip()
        
        cur.execute("SELECT * FROM lop WHERE ma_lop = %s", (ma_lop, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'lop/form_add_lop.html',
                           ma_err = "Mã lớp đã tồn tại",        
                            cac_nganh = cac_nganh,
                            my_user = session['username'],
                            truong = session['truong'])
            
        cur.execute("SELECT * FROM lop WHERE ma_nguoi_quan_ly = %s AND is_delete = 0", (ma_nguoi_quan_ly, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'lop/form_add_lop.html',
                           ma_err = "Người quản lý đang quản lý lớp khác",        
                            cac_nganh = cac_nganh,
                            my_user = session['username'],
                            truong = session['truong'])
        if ma_nguoi_quan_ly == '':
            cur.execute("""
                    INSERT INTO lop(ma_lop, ma_nganh, nam, ten_lop, ma_nguoi_quan_ly) VALUES
                    (%s, %s, %s, %s, NULL)
                    """, (ma_lop, ma_nganh, nam, ten_lop))
        else:
            cur.execute("""
                        INSERT INTO lop(ma_lop, ma_nganh, nam, ten_lop, ma_nguoi_quan_ly) VALUES
                        (%s, %s, %s, %s, %s)
                        """, (ma_lop, ma_nganh, nam, ten_lop, ma_nguoi_quan_ly))
        mysql.connection.commit()
        return redirect(url_for('table_lop'))
        
    return render_template(session['role'] + 'lop/form_add_lop.html',
                           cac_nganh = cac_nganh,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_lop/form_update_lop/<string:ma_lop>", methods=['GET','POST'])
def form_update_lop(ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM lop WHERE ma_lop = %s", (ma_lop, ))
    lop = cur.fetchall()
    
    if (len(lop) != 1):
        return "Error"
    
    lop = lop[0]
    
    if request.method == 'POST':
        details = request.form
        nam = details['nam'].strip()
        ten_lop = details['ten_lop'].strip()
        ma_nguoi_quan_ly = details['ma_nguoi_quan_ly'].strip()
        
        if (ma_nguoi_quan_ly == 'None' or ma_nguoi_quan_ly == ""):
            cur.execute("""
                UPDATE lop
                SET nam = %s, ten_lop = %s, ma_nguoi_quan_ly = NULL
                WHERE ma_lop = %s
                """, (nam, ten_lop, ma_lop))
        else:
            cur.execute("""
                    UPDATE lop
                    SET nam = %s, ten_lop = %s, ma_nguoi_quan_ly = %s
                    WHERE ma_lop = %s
                    """, (nam, ten_lop, ma_nguoi_quan_ly, ma_lop))
        
        mysql.connection.commit()
        return redirect(url_for('table_lop'))
    
    return render_template(session['role'] + 'lop/form_update_lop.html',
                           lop = lop,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_lop/form_add_lop_upload_file", methods=['GET','POST'])
def form_add_lop_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_nganh_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_lop_upload_process", filename=filename))
        return redirect(url_for("form_add_lop_upload_file"))
    return render_template(session['role'] + 'lop/form_add_lop_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_lop/form_add_lop_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_lop_upload_process(filename):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_lop','ma_nganh','nam','ten_lop','ma_nguoi_quan_ly']
    
    default_name_column = ['Mã Lớp', 'Mã Ngành', 'Năm', 'Tên Lớp', 'Mã Người Quản Lý']
    
    data_mon_hoc = pd.read_excel(pathToFile)
    data_column = list(data_mon_hoc.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column) < 3:
        return "Error"
        
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 5):
            return "Error"
        
        if (len(tuple(set(data_mon_hoc[data_column[column_match.index(4)]]))) 
            != len(tuple(data_mon_hoc[data_column[column_match.index(4)]]))):
            return "Error"
        
        # Kiểm tra xem mã nganh có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(1)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        # Kiểm tra xem mã lớp có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_lop FROM lop WHERE ma_lop = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_lop FROM lop WHERE ma_lop IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != 0):
            return "Error"
        
        sql = "INSERT INTO `lop` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql = sql[:-1:]
        sql += ") VALUES "
        for index_row in range(data_mon_hoc.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_mon_hoc[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]  
        
        cur.execute(sql)
        mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for("table_lop"))        
    
    return render_template(session['role'] + 'lop/form_add_lop_upload_process.html',
                           filename = filename,
                           truong = session['truong'],
                           my_user = session['username'],
                           name_column = default_name_column,
                           index_column = data_column)
    
@login_required
@app.route("/table_print_lop")
def table_print_lop():
    cur = mysql.connection.cursor()
    
    cur.execute("""
               SELECT l.*, n.ten_nganh, COUNT(svl.ma_sinh_vien)
                FROM lop l 
                LEFT JOIN sinh_vien_lop svl ON svl.ma_lop = l.ma_lop
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE l.is_delete = 0
                GROUP BY l.ma_lop
                """)
    cac_lop = cur.fetchall()
    
    return render_template('lop/table_print_lop.html', 
                           cac_lop = cac_lop)
    
@login_required
@app.route("/get_table_lop_pdf")
def get_table_lop_pdf():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Lop.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_lop',pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_lop_excel")
def get_table_lop_excel():
    cur = mysql.connection.cursor()
    
    cur.execute("""
               SELECT l.ma_lop, l.ma_nganh, l.nam, l.ten_lop, l.ma_nguoi_quan_ly, n.ten_nganh, COUNT(svl.ma_sinh_vien)
                FROM lop l 
                LEFT JOIN sinh_vien_lop svl ON svl.ma_lop = l.ma_lop
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE l.is_delete = 0
                GROUP BY l.ma_lop
                """)
    cac_lop = cur.fetchall()
    columnName = ['MaLop','MaNganh','Nam','TenLop','MaNguoiQuanLy', 'TenNganh','SoLuongSinhVien']
    data = pd.DataFrame.from_records(cac_lop, columns=columnName)
    data = data.set_index('MaLop')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_mon_hoc.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_lop/view_lop_sinh_vien/<string:ma_lop>")
def view_lop_sinh_vien(ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT l.*, n.ten_nganh
                FROM lop l
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE ma_lop = %s AND l.is_delete = 0""", (ma_lop, ))
    lop = cur.fetchall()
    if (len(lop) != 1):
        return "Error"
    lop = lop[0]
    
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.ngay_sinh,
                sv.dia_chi, sv.email, sv.so_dien_thoai
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                WHERE svl.ma_lop = %s AND sv.is_delete = 0
                """, (ma_lop, ))
    cac_sv = cur.fetchall()
    
    return render_template(session['role'] + 'lop/view_lop_sinh_vien.html',
                           lop = lop,
                           cac_sv = cac_sv,
                           my_user = session['username'],
                           truong =session['truong'])

@login_required
@app.route("/table_print_lop_sinh_vien/<string:ma_lop>")
def table_print_lop_sinh_vien(ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT l.*, n.ten_nganh
                FROM lop l
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE ma_lop = %s AND l.is_delete = 0""", (ma_lop, ))
    lop = cur.fetchall()
    if (len(lop) != 1):
        return "Error"
    lop = lop[0]
    
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.ngay_sinh,
                sv.dia_chi, sv.email, sv.so_dien_thoai
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                WHERE svl.ma_lop = %s AND sv.is_delete = 0
                """, (ma_lop, ))
    cac_sv = cur.fetchall()
    
    return render_template('lop/table_print_lop_sinh_vien.html',
                           lop = lop,
                           cac_sv = cac_sv)

@login_required
@app.route("/get_table_lop_sinh_vien_pdf/<string:ma_lop>")
def get_table_lop_sinh_vien_pdf(ma_lop):
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Lop_' + ma_lop + '.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-2:]) + '/table_print_lop_sinh_vien/' + ma_lop,pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_lop_sinh_vien_excel/<string:ma_lop>")
def get_table_lop_sinh_vien_excel(ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT l.*, n.ten_nganh
                FROM lop l
                LEFT JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE ma_lop = %s AND l.is_delete = 0""", (ma_lop, ))
    lop = cur.fetchall()
    if (len(lop) != 1):
        return "Error"
    lop = lop[0]
    
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.ngay_sinh,
                sv.dia_chi, sv.email, sv.so_dien_thoai
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                WHERE svl.ma_lop = %s AND sv.is_delete = 0
                """, (ma_lop, ))
    cac_sv = cur.fetchall()
    columnName = ['MaSinhVien','HoTen','GioiTinh','NgaySinh','DiaChi', 'Email','SoDienThoai']
    data = pd.DataFrame.from_records(cac_sv, columns=columnName)
    data = data.set_index('MaSinhVien')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Sinh_Vien_Lop_" + ma_lop + ".xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/delete_lop/<string:ma_lop>")
def delete_lop(ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                UPDATE lop
                SET is_delete = 1
                WHERE ma_lop = %s
                """, (ma_lop, ))
    mysql.connection.commit()
    return redirect(request.url)

# -------------------------- Lop -------------------------


# -------------------------- Sinh vien -------------------------

@login_required
@app.route("/bang_sinh_vien")
def bang_sinh_vien():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                 SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.noi_sinh, l.ten_lop,
                 n.ten_nganh, sv.email, sv.so_dien_thoai, sv.chung_minh_thu
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE sv.is_delete = 0
                """)
    sinh_vien = cur.fetchall()
    
    return render_template(session['role'] +'sinhvien/bang_sinh_vien.html',
                           sinh_vien = sinh_vien,
                           my_user = session['username'],
                           truong = session['truong'])  

@login_required
@app.route("/delete_sinh_vien/<string:ma_sinh_vien>")
def delete_sinh_vien(ma_sinh_vien):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                UPDATE sinh_vien
                SET is_delete = 1
                WHERE ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    
    mysql.connection.commit()
    return redirect(url_for('bang_sinh_vien'))

@login_required
@app.route("/bang_sinh_vien/form_view_update_sinh_vien/<string:ma_sinh_vien>_<string:can_edit>", methods=['GET','POST'])
def form_view_update_sinh_vien(ma_sinh_vien, can_edit):
    mode = "disabled"
    if (can_edit == "Y"):
        mode = ""
    cur = mysql.connection.cursor()
    
    cur.execute("""
                 SELECT sv.*, img.path_to_image, CONCAT(l.ten_lop, " _ ", n.ten_nganh, " _ ", k.ten_khoa), l.ma_lop
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN image_data img ON img.id_image = sv.id_image
                WHERE sv.is_delete = 0 AND sv.ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    data_default = cur.fetchall()
    
    if (len(data_default) == 0):
        return "Error"
    
    data_default = data_default[0]
    
    cur.execute("SELECT * FROM gia_dinh WHERE ma_sinh_vien = %s", (ma_sinh_vien, ))
    gia_dinh = cur.fetchall()[0]
    
    cur.execute("""
                SELECT l.ma_lop, 
                CONCAT(l.ten_lop, " _ ", n.ten_nganh, " _ ", k.ten_khoa)
                FROM lop l 
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE l.ma_lop != %s
                """, (data_default[-1],))
    cac_lop = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_sinh_vien = data_default[0]
        ho_ten = details['ho_ten'].strip()
        ngay_sinh = details['ngay_sinh'].strip()
        gioi_tinh = details['gioi_tinh'].strip()
        dan_toc = details['dan_toc'].strip()
        quoc_tich = details['quoc_tich'].strip()
        noi_sinh = details['noi_sinh'].strip()
        email = details['email'].strip()
        dia_chi = details['dia_chi'].strip()
        so_dien_thoai = details['so_dien_thoai'].strip()
        chung_minh_thu = details['chung_minh_thu'].strip()
        ngay_cmt = details['ngay_cmt'].strip()
        noi_cmt = details['noi_cmt'].strip()
        id_image = data_default[13]
        
        ma_lop = details['ma_lop'].strip()
        image_profile = request.files['ImageProfileUpload']
        
        if image_profile.filename != '':
            ID_image = "Image_Profile_" + str(ma_sinh_vien) 
            id_image = ID_image
            filename = ID_image + "." + secure_filename(image_profile.filename).split(".")[1]
            pathToImage = app.config['UPLOAD_FOLDER_IMG'] + "/" + filename
            image_profile.save(pathToImage)
            take_image_to_save(ID_image, pathToImage)
            

        if ma_lop != data_default[-2]:
            for elm in cac_lop:
                if elm[1] == ma_lop:
                    ma_lop = elm[0]
                    break
            cur.execute("""
                        UPDATE sinh_vien_lop
                        SET ma_lop = %s
                        WHERE ma_sinh_vien = %s AND ma_lop = %s
                        """, (ma_lop, ma_sinh_vien, data_default[-1]))
            mysql.connection.commit()
            
        #  Thông tin gia đình
        ten_cha = details['ten_cha']
        nam_sinh_cha = details['nam_sinh_cha']
        email_cha = details['email_cha']
        sdt_cha = details['sdt_cha']
        nghe_cha = details['nghe_cha']
        dia_chi_cha = details['dia_chi_cha']
        noi_cha = details['noi_cha']
        
        ten_me = details['ten_me']
        nam_sinh_me = details['nam_sinh_me']
        email_me = details['email_me']
        sdt_me = details['sdt_me']
        nghe_me = details['nghe_me']
        dia_chi_me = details['dia_chi_me']
        noi_me = details['noi_me']
        
        ten_vo_chong = details['ten_vo_chong']
        ngay_sinh_vo_chong = details['ngay_sinh_vo_chong']
        nghe_vo_chong = details['nghe_vo_chong']
        dia_chi_vo_chong = details['dia_chi_vo_chong']
        
        thong_tin_anh_chi_em = details['thong_tin_anh_chi_em']
        thong_tin_cac_con = details['thong_tin_cac_con']
        
        cur.execute("""
                    UPDATE gia_dinh
                    SET ten_cha = %s, nam_sinh_cha = %s, email_cha = %s, sdt_cha = %s, nghe_cha = %s,
                    dia_chi_cha = %s, noi_cha = %s, ten_me = %s, nam_sinh_me = %s, email_me = %s, 
                    sdt_me = %s, nghe_me = %s, dia_chi_me = %s, noi_me = %s, ten_vo_chong = %s, ngay_sinh_vo_chong = %s,
                    nghe_vo_chong = %s, dia_chi_vo_chong = %s, thong_tin_anh_chi_em = %s, thong_tin_cac_con = %s
                    WHERE ma_sinh_vien = %s
                    """, (ten_cha, nam_sinh_cha, email_cha, sdt_cha, nghe_cha, dia_chi_cha, noi_cha, ten_me, nam_sinh_me,
                          email_me, sdt_me, nghe_me, dia_chi_me, noi_me, ten_vo_chong, ngay_sinh_vo_chong,
                          nghe_vo_chong, dia_chi_vo_chong, thong_tin_anh_chi_em, thong_tin_cac_con, ma_sinh_vien))
        mysql.connection.commit()
        
        cur.execute("""
                    UPDATE sinh_vien
                    SET ho_ten = %s, gioi_tinh = %s, ngay_sinh = %s, quoc_tich = %s,
                    dan_toc = %s, chung_minh_thu = %s, ngay_cmt = %s, noi_cmt = %s,
                    dia_chi = %s, noi_sinh = %s, email = %s, so_dien_thoai = %s, id_image = %s, update_at = current_timestamp(), 
                    update_by = %s
                    WHERE ma_sinh_vien = %s
                    """, (ho_ten, gioi_tinh, ngay_sinh, quoc_tich, dan_toc, chung_minh_thu, ngay_cmt, noi_cmt, dia_chi,
                          noi_sinh, email, so_dien_thoai, id_image, session['username'][6], ma_sinh_vien))
        mysql.connection.commit()
        if (ma_sinh_vien == session['username'][3]):
                cur.execute("""SELECT us.*, sv.ho_ten, img.path_to_image
                    FROM user us
                    JOIN sinh_vien sv ON sv.ma_sinh_vien = us.ma_nguoi_dung 
                    JOIN image_data img ON img.id_image = nql.id_image
                    WHERE username=%s""",(ma_sinh_vien,))
                user_data = cur.fetchall()
                
                my_user = user_data[0]
        
                session['username'] = my_user
        
        mysql.connection.commit()
        return redirect(url_for("bang_sinh_vien"))
    
    return render_template(session['role'] +'sinhvien/form_view_update_sinh_vien.html',
                           mode = mode,
                           gia_dinh = gia_dinh,
                           sinh_vien = data_default,
                           cac_lop = cac_lop,
                           my_user = session['username'],
                           truong = session['truong']) 

@login_required
@app.route("/bang_sinh_vien/form_add_sinh_vien_upload_file", methods=['GET','POST'])
def form_add_sinh_vien_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_sinh_vien_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_sinh_vien_upload_process", filename=filename))
        return redirect(url_for("form_add_sinh_vien_upload_file"))
    return render_template(session['role'] +'sinhvien/form_add_sinh_vien_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong']) 

@login_required
@app.route("/bang_sinh_vien/form_add_sinh_vien_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_sinh_vien_upload_process(filename):
    
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_sinh_vien', 'ho_ten', 'gioi_tinh', 'ngay_sinh', 'noi_sinh',
                    'email', 'dan_toc', 'dia_chi', 'so_dien_thoai', 'quoc_tich',
                    'chung_minh_thu', 'ngay_cmt', 'noi_cmt', 'ma_lop']
    
    default_name_column = ['Mã Sinh Viên', 'Họ tên', 'Giới tính', 'Ngày sinh', 'Nơi sinh',
                           'Email', 'Dân tộc', 'Địa chỉ', 'Số điện thoại', 'Quốc tịch',
                           'CMT / Thẻ căn cước', 'Nơi cấp CMT', 'Ngày cấp CMT', 'Mã Lớp']
    
    data_mon_hoc = pd.read_excel(pathToFile)
    data_column = list(data_mon_hoc.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column) < 3:
        return "Error"
        
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if 0 not in column_match or 1 not in column_match or 2 not in column_match:
            return "Error"
        if 3 not in column_match or 4 not in column_match or 13 not in column_match:
            return "Error"
        
        # Kiểm tra xem mã lớp có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(13)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_lop FROM lop WHERE ma_lop = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_lop FROM lop WHERE ma_lop IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        # Tách cột mã lớp ra so với các cột còn lại để import vào bảng khác
        ma_mon_ma_nganh = data_mon_hoc[[data_column[column_match.index(0)], data_column[column_match.index(13)]]]
        col_ma_lop = [data_column[column_match.index(0)], data_column[column_match.index(13)]]
        data_mon_hoc = data_mon_hoc.drop(data_column[column_match.index(13)], axis=1)
        data_column.remove(data_column[column_match.index(13)])
        column_match.remove(13)
        
        sql = "INSERT INTO `sinh_vien` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql += 'created_by'
        sql += ") VALUES "
        for index_row in range(data_mon_hoc.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_mon_hoc[col][index_row]) + "\"" + ","
            sql += "\"" + session['username'][6] + "\""
            sql += "),"
        sql = sql[:-1:]    
        cur.execute(sql)
        
        sql = "INSERT INTO `sinh_vien_lop` ( ma_sinh_vien, ma_lop ) VALUES "
        for index_row in range(ma_mon_ma_nganh.shape[0]):
            sql += "("
            for col in col_ma_lop:
                sql += "\"" + str(ma_mon_ma_nganh[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]
        
        cur.execute(sql)
        mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for("bang_sinh_vien"))        
        
    return render_template(session['role'] +"sinhvien/form_add_data_sinh_vien_upload_process.html",
                           filename = filename,
                           truong = session['truong'],
                           my_user = session['username'],
                           name_column = default_name_column,
                           index_column = data_column)
    
@login_required
@app.route("/get_table_sinh_vien_excel")
def get_table_sinh_vien_excel():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.ngay_sinh, sv.noi_sinh, svl.ma_lop
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                WHERE sv.is_delete = 0
                """)
    sinh_vien = cur.fetchall()
    columnName = ['MaSinhVien','HoTen','GioiTinh','NgaySinh','NoiSinh','MaLop']
    data = pd.DataFrame.from_records(sinh_vien, columns=columnName)
    data = data.set_index('MaSinhVien')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Sinh_Vien.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)
    
@login_required
@app.route('/get_table_sinh_vien_pdf')
def get_table_sinh_vien_pdf():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Sinh Vien.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_sinh_vien',pathFile)
    return send_file(pathFile, as_attachment=True)
    
@login_required
@app.route("/bang_sinh_vien/form_add_sinh_vien", methods=['GET','POST'])
def form_add_sinh_vien():
    
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT l.ma_lop, 
                CONCAT(l.ten_lop, " _ ", n.ten_nganh, " _ ", k.ten_khoa)
                FROM lop l 
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                """)
    cac_lop = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_sinh_vien = details['ma_sinh_vien'].strip()
        ho_ten = details['ho_ten'].strip()
        ngay_sinh = details['ngay_sinh'].strip()
        gioi_tinh = details['gioi_tinh'].strip()
        dan_toc = details['dan_toc'].strip()
        quoc_tich = details['quoc_tich'].strip()
        noi_sinh = details['noi_sinh'].strip()
        email = details['email'].strip()
        dia_chi = details['dia_chi'].strip()
        so_dien_thoai = details['so_dien_thoai'].strip()
        chung_minh_thu = details['chung_minh_thu'].strip()
        ngay_cmt = details['ngay_cmt'].strip()
        noi_cmt = details['noi_cmt'].strip()
        id_image = "none_image_profile"
        
        ma_lop = details['ma_lop'].strip()
        
        for elm in cac_lop:
            if elm[1] == ma_lop:
                ma_lop = elm[0]
                break
        
        cur.execute("""SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien=%s""", (ma_sinh_vien, ))
        kiem_tra_ma_sinh_vien = cur.fetchall()
        
        if len(kiem_tra_ma_sinh_vien) != 0:
            return render_template(session['role'] +'employees/form_add_data_employees.html',
                        ma_err="True",
                        my_user = session['username'],
                        truong = session['truong']) 
            
        image_profile = request.files['ImageProfileUpload']
        
        if image_profile.filename != '':
            ID_image = "Image_Profile_" + ma_sinh_vien 
            filename = ID_image + "." + secure_filename(image_profile.filename).split(".")[1]
            pathToImage = app.config['UPLOAD_FOLDER_IMG'] + "/" + filename
            image_profile.save(pathToImage)
            take_image_to_save(ID_image, pathToImage)
            
        cur.execute("""
                    INSERT INTO `sinh_vien` 
                    (`ma_sinh_vien`, `ho_ten`, `gioi_tinh`, `ngay_sinh`, `noi_sinh`,
                    `email`, `dan_toc`, `dia_chi`, `so_dien_thoai`, `quoc_tich`,
                    `chung_minh_thu`, `ngay_cmt`, `noi_cmt`, `id_image`, `is_delete`,
                    `created_at`, `created_by`, `update_at`, `update_by`) 
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, 
                    '0', current_timestamp(), %s, current_timestamp(), NULL);
                    """, (ma_sinh_vien, ho_ten, gioi_tinh, ngay_sinh, noi_sinh, email,
                          dan_toc, dia_chi, so_dien_thoai, quoc_tich, chung_minh_thu, 
                          ngay_cmt, noi_cmt, id_image, session['username'][6]))
        
        cur.execute("""
                    INSERT INTO sinh_vien_lop (ma_sinh_vien, ma_lop)
                    VALUES (%s, %s)
                    """, (ma_sinh_vien, ma_lop))
        
        mysql.connection.commit()
        return redirect(url_for("bang_sinh_vien"))
        
    return render_template(session['role'] +'sinhvien/form_add_sinh_vien.html',
                           cac_lop = cac_lop,
                           my_user = session['username'],
                           truong = session['truong']) 

@login_required
@app.route("/form_infomation_one_sinh_vien/<string:ma_sinh_vien>")
def form_infomation_one_sinh_vien(ma_sinh_vien):
    
    cur = mysql.connection.cursor()
    
    cur.execute("""
                 SELECT sv.*, img.path_to_image, CONCAT(l.ten_lop, " _ ", n.ten_nganh, " _ ", k.ten_khoa), l.ma_lop
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN image_data img ON img.id_image = sv.id_image
                WHERE sv.is_delete = 0 AND sv.ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    data_default = cur.fetchall()
    
    if (len(data_default) == 0):
        return "Error"
    
    data_default = data_default[0]
    
    cur.execute("SELECT * FROM gia_dinh WHERE ma_sinh_vien = %s", (ma_sinh_vien, ))
    gia_dinh = cur.fetchall()[0]
    
    cur.execute("SELECT * FROM truong")
    truong = cur.fetchall()
    truong = truong[0]
    
    return render_template("sinhvien/form_infomation_one_sinh_vien.html",
                           gia_dinh = gia_dinh,
                           sinh_vien = data_default,
                           truong = truong)

@login_required
@app.route("/get_pdf_one_sinh_vien/<string:ma_sinh_vien>")
def get_pdf_one_sinh_vien(ma_sinh_vien):
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Sinh Vien_' + ma_sinh_vien + '.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-2:]) + '/form_infomation_one_sinh_vien/' + ma_sinh_vien,pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_print_sinh_vien")
def table_print_sinh_vien():
    
    cur = mysql.connection.cursor()
    
    cur.execute("""
                 SELECT sv.ma_sinh_vien, sv.ho_ten, sv.gioi_tinh, sv.noi_sinh, l.ten_lop,
                 n.ten_nganh, sv.email, sv.so_dien_thoai, sv.chung_minh_thu
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE sv.is_delete = 0
                """)
    sinh_vien = cur.fetchall()
    
    return render_template('sinhvien/table_print_sinh_vien.html', 
                           sinh_vien =  sinh_vien) 

# -------------------------- Sinh vien -------------------------

# -------------------------- Mon hoc -------------------------

@app.route("/table_mon_hoc")
def table_mon_hoc():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT * 
                FROM mon_hoc
                WHERE is_delete = 0
                """)
    cac_mon = cur.fetchall()
    
    return render_template(session['role'] + 'monhoc/table_mon_hoc.html',
                           cac_mon = cac_mon,
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_mon_hoc/form_add_mon_hoc", methods = ['GET','POST'])
def form_add_mon_hoc():
    
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT n.*, lh.ten_he
                FROM nganh n
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                WHERE is_delete = 0""")
    cac_nganh = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_mon = details['ma_mon'].strip()
        ten_mon = details['ten_mon'].strip()
        so_tin_chi = details['so_tin_chi'].strip()
        
        lst_nganh = list(details.keys())
        lst_nganh.remove('ma_mon')
        lst_nganh.remove('ten_mon')
        lst_nganh.remove('so_tin_chi')
        
        cur.execute("SELECT * FROM mon_hoc WHERE ma_mon = %s", (ma_mon, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'monhoc/form_add_mon_hoc.html',
                                   ma_err = "Mã môn đã tồn tại",
                                    cac_nganh = cac_nganh,
                                    my_user = session['username'],
                                    truong = session['truong'])
        
        cur.execute("""
                    INSERT INTO mon_hoc(ma_mon, ten_mon, so_tin_chi)
                    VALUES (%s, %s, %s)
                    """, (ma_mon, ten_mon, so_tin_chi))
        mysql.connection.commit()
        
        sql = "INSERT INTO mon_hoc_nganh(ma_mon, ma_nganh) VALUES " 
        for ma_nganh in lst_nganh:
            sql += " (\"" + ma_mon + "\","  
            sql += "\"" + ma_nganh + "\"),"
        sql = sql[:-1:]
        cur.execute(sql)
        mysql.connection.commit()
        return redirect(url_for("table_mon_hoc"))
    
    return render_template(session['role'] + 'monhoc/form_add_mon_hoc.html',
                           cac_nganh = cac_nganh,
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_mon_hoc/form_update_mon_hoc/<string:ma_mon>", methods = ['GET','POST'])
def form_update_mon_hoc(ma_mon):
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT n.*, lh.ten_he
                FROM nganh n
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                WHERE is_delete = 0 AND ma_nganh IN (
                    SELECT ma_nganh 
                    FROM mon_hoc_nganh
                    WHERE ma_mon = %s
                    )""", (ma_mon, ))
    cac_nganh_thuoc = cur.fetchall()
    
    cur.execute("""SELECT n.*, lh.ten_he
                FROM nganh n
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                WHERE is_delete = 0 AND ma_nganh NOT IN (
                    SELECT ma_nganh 
                    FROM mon_hoc_nganh
                    WHERE ma_mon = %s
                    )""", (ma_mon, ))
    cac_nganh = cur.fetchall()
    
    cur.execute("SELECT * FROM mon_hoc WHERE is_delete = 0 AND ma_mon = %s", (ma_mon, ))
    mon_hoc = cur.fetchall()
    
    if (len(mon_hoc) != 1):
        return "Error"
    
    mon_hoc = mon_hoc[0]
    
    if (request.method == 'POST'):
        details = request.form
        so_tin_chi = details['so_tin_chi']
        ten_mon = details['ten_mon']
        
        lst_nganh = list(details.keys())
        lst_nganh.remove('ten_mon')
        lst_nganh.remove('so_tin_chi')
        
        cur.execute("""
                    UPDATE mon_hoc
                    SET ten_mon = %s, so_tin_chi = %s
                    WHERE ma_mon = %s
                    """, (ten_mon, so_tin_chi, ma_mon))
        mysql.connection.commit()
        
        cur.execute("DELETE FROM mon_hoc_nganh WHERE ma_mon = %s", (ma_mon, ))
        mysql.connection.commit()
        
        if len(lst_nganh) == 0:
            return redirect(url_for("table_mon_hoc"))
        sql = "INSERT INTO mon_hoc_nganh(ma_mon, ma_nganh) VALUES " 
        for ma_nganh in lst_nganh:
            sql += " (\"" + ma_mon + "\","  
            sql += "\"" + ma_nganh + "\"),"
        sql = sql[:-1:]
        cur.execute(sql)
        mysql.connection.commit()
        return redirect(url_for("table_mon_hoc"))
    
    return render_template(session['role'] + 'monhoc/form_update_mon_hoc.html',
                           mon_hoc = mon_hoc,
                           cac_nganh = cac_nganh,
                           cac_nganh_thuoc = cac_nganh_thuoc,
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_mon_hoc/form_add_mon_hoc_upload_file", methods=['GET','POST'])
def form_add_mon_hoc_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_mon_hoc_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_mon_hoc_upload_process", filename=filename))
        return redirect(url_for("form_add_mon_hoc_upload_file"))
    return render_template(session['role'] + 'monhoc/form_add_mon_hoc_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong'])

@app.route("/table_mon_hoc/form_add_mon_hoc_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_mon_hoc_upload_process(filename):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_mon', 'ten_mon', 'so_tin_chi', 'ma_nganh']
    
    default_name_column = ['Mã môn', 'Tên môn', 'Số tín chỉ', 'Mã ngành']
    
    data_mon_hoc = pd.read_excel(pathToFile)
    data_column = list(data_mon_hoc.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column) < 3:
        return "Error"
        
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 4):
            return "Error"
        
        # Kiểm tra xem mã môn có tồn tại không
        tmp = tuple(set(data_mon_hoc[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != 0):
            return "Error"
        
        # Tách cột mã nganh ra so với các cột còn lại để import vào bảng khác
        ma_mon_ma_nganh = data_mon_hoc[[data_column[column_match.index(0)], data_column[column_match.index(3)]]]
        col_ma_nganh = [data_column[column_match.index(0)], data_column[column_match.index(3)]]
        data_mon_hoc = data_mon_hoc.drop(data_column[column_match.index(3)], axis=1)
        data_column.remove(data_column[column_match.index(3)])
        column_match.remove(3)
        
        sql = "INSERT INTO `mon_hoc` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql = sql[:-1:]
        sql += ") VALUES "
        for index_row in range(data_mon_hoc.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_mon_hoc[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]  
        cur.execute(sql)
        mysql.connection.commit()
        
        ma_mon_ma_nganh[col_ma_nganh[1]] = ma_mon_ma_nganh[col_ma_nganh[1]].str.split(",")
        ma_mon_ma_nganh = ma_mon_ma_nganh.explode(col_ma_nganh[1])
        ma_mon_ma_nganh = ma_mon_ma_nganh.reset_index()
        
        # Kiểm tra xem mã ngành có tồn tại không
        tmp = tuple(set(ma_mon_ma_nganh[col_ma_nganh[1]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_nganh FROM nganh WHERE ma_nganh IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        
        sql = "INSERT INTO `mon_hoc_nganh` ( ma_mon, ma_nganh ) VALUES "
        for index_row in range(ma_mon_ma_nganh.shape[0]):
            sql += "("
            for col in col_ma_nganh:
                sql += "\"" + str(ma_mon_ma_nganh[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]
        
        cur.execute(sql)
        mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for("table_mon_hoc"))         
     
    return render_template(session['role'] + 'monhoc/form_add_mon_hoc_upload_process.html',
                           filename = filename,
                           truong = session['truong'],
                           my_user = session['username'],
                           name_column = default_name_column,
                           index_column = data_column)

@login_required
@app.route("/table_print_mon_hoc")
def table_print_mon_hoc():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT * 
                FROM mon_hoc
                WHERE is_delete = 0
                """)
    cac_mon = cur.fetchall()
    return render_template('monhoc/table_print_mon_hoc.html',
                           cac_mon = cac_mon)

@login_required
@app.route("/get_table_mon_hoc_pdf")
def get_table_mon_hoc():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Mon Hoc.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_mon_hoc',pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_mon_hoc_excel")
def get_table_mon_hoc_excel():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT ma_mon, ten_mon, so_tin_chi
                FROM mon_hoc
                WHERE is_delete = 0
                """)
    cac_mon = cur.fetchall()
    columnName = ['MaMon','TenMon','SoTC']
    data = pd.DataFrame.from_records(cac_mon, columns=columnName)
    data = data.set_index('MaMon')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Mon_Hoc.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/delete_mon_hoc/<string:ma_mon>")
def delete_mon_hoc(ma_mon):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                UPDATE mon_hoc
                SET is_delete = 1
                WHERE ma_mon = %s
                """, (ma_mon, ))
    mysql.connection.commit()
    return redirect(url_for('table_mon_hoc'))
# -------------------------- Mon hoc -------------------------

# -------------------------- Ket Qua Hoc Tap -------------------------

@login_required
@app.route("/table_kqht_sv")
def table_kqht_sv():
    cur = mysql.connection.cursor()

    cur.execute("""
                SELECT d.ma_sinh_vien, sv.ho_ten, sv.ngay_sinh, l.ten_lop, n.ten_nganh,
                k.ten_khoa, ROUND(SUM(d.thang_4 * mh.so_tin_chi)/SUM(mh.so_tin_chi),2)
                FROM diem d
                JOIN sinh_vien sv ON d.ma_sinh_vien = sv.ma_sinh_vien
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_mon IN (
                    SELECT DISTINCT mhn.ma_mon 
                    FROM mon_hoc_nganh mhn
                    WHERE mhn.ma_nganh = n.ma_nganh
                ) AND d.thang_10 >= 4
                GROUP BY d.ma_sinh_vien
                """)
    diem_sinh_vien = cur.fetchall()
    
    return render_template(session['role'] + 'ketquahoctap/table_kqht_sv.html',
                           diem_sinh_vien = diem_sinh_vien,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_print_kqht_sv")
def table_print_kqht_sv():
    cur = mysql.connection.cursor()

    cur.execute("""
                SELECT d.ma_sinh_vien, sv.ho_ten, sv.ngay_sinh, l.ten_lop, n.ten_nganh,
                k.ten_khoa, ROUND(SUM(d.thang_4 * mh.so_tin_chi)/SUM(mh.so_tin_chi),2)
                FROM diem d
                JOIN sinh_vien sv ON d.ma_sinh_vien = sv.ma_sinh_vien
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_mon IN (
                    SELECT DISTINCT mhn.ma_mon 
                    FROM mon_hoc_nganh mhn
                    WHERE mhn.ma_nganh = n.ma_nganh
                ) AND d.thang_10 >= 4
                GROUP BY d.ma_sinh_vien
                """)
    diem_sinh_vien = cur.fetchall()
    return render_template('ketquahoctap/table_print_kqht_sv.html',
                           diem_sinh_vien = diem_sinh_vien)

@login_required
@app.route("/get_table_kqht_sv_excel")
def get_table_kqht_sv_excel():
    cur = mysql.connection.cursor()

    cur.execute("""
                SELECT d.ma_sinh_vien, sv.ho_ten, sv.ngay_sinh, l.ten_lop, n.ten_nganh,
                k.ten_khoa, ROUND(SUM(d.thang_4 * mh.so_tin_chi)/SUM(mh.so_tin_chi),2)
                FROM diem d
                JOIN sinh_vien sv ON d.ma_sinh_vien = sv.ma_sinh_vien
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_mon IN (
                    SELECT DISTINCT mhn.ma_mon 
                    FROM mon_hoc_nganh mhn
                    WHERE mhn.ma_nganh = n.ma_nganh
                ) AND d.thang_10 >= 4
                GROUP BY d.ma_sinh_vien
                """)
    diem_sinh_vien = cur.fetchall()
    columnName = ['MSV','HoTen','NgaySinh','TenLop','TenNganh','TenKhoa','GPA']
    data = pd.DataFrame.from_records(diem_sinh_vien, columns=columnName)
    data = data.set_index('MSV')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_KQHT_SV.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_kqht_sv_pdf")
def get_table_kqht_sv_pdf():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Kqht SV.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_kqht_sv',pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_kqht_sv/table_kqht/<string:ma_sinh_vien>")
def table_kqht(ma_sinh_vien):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh, k.ten_khoa
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE sv.ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    sinh_vien = cur.fetchall()
    
    if (len(sinh_vien) != 1):
        return "Error"
    
    sinh_vien = sinh_vien[0]
    
    cur.execute("""
                SELECT hk.ma_hoc_ky, hk.ten_hoc_ky
                FROM diem d
                JOIN hoc_ky hk ON d.ma_hoc_ky = hk.ma_hoc_ky
                WHERE d.ma_sinh_vien = %s
                GROUP BY hk.ma_hoc_ky
                ORDER BY hk.ma_hoc_ky DESC
                """, (ma_sinh_vien, ))
    tmp_hoc_ky = cur.fetchall()
    
    index_hk = []
    hk = []
    index = 0
    for elm in tmp_hoc_ky:
        index_hk.append(index)
        hk.append(elm[0])
        index += 1
    
    index_diem_hk = []
    data_diem_hk = []
    for elm in hk:
        cur.execute("""
                    SELECT d.id_diem, d.ma_mon, mh.ten_mon, mh.so_tin_chi, d.thang_10, d.thang_chu, d.thang_4
                    FROM diem d
                    JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                    WHERE d.ma_hoc_ky = %s AND d.ma_sinh_vien = %s 
                    ORDER BY mh.ma_mon
                    """, (elm, ma_sinh_vien))
        data_diem_hk.append(cur.fetchall())
        index_diem_hk.append([i for i in range(len(data_diem_hk[-1]))])
    
    cur.execute("""
                SELECT d.ma_sinh_vien, ROUND(SUM(d.thang_4 * mh.so_tin_chi)/SUM(mh.so_tin_chi),2), sum(mh.so_tin_chi)
                FROM diem d
                JOIN sinh_vien sv ON d.ma_sinh_vien = sv.ma_sinh_vien
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_mon IN (
                    SELECT DISTINCT mhn.ma_mon 
                    FROM mon_hoc_nganh mhn
                    WHERE mhn.ma_nganh = n.ma_nganh
                ) AND d.thang_10 >= 4 AND d.ma_sinh_vien = %s
                GROUP BY d.ma_sinh_vien
                """, (ma_sinh_vien, ))
    tk_diem_sinh_vien = cur.fetchall()
    
    if (len(tk_diem_sinh_vien) != 1):
        return "Error"
    
    tk_diem_sinh_vien = tk_diem_sinh_vien[0]
    
    hk = []
    for elm in tmp_hoc_ky:
        hk.append(elm[1])
    
    return render_template(session['role'] + 'ketquahoctap/table_kqht.html',
                           sinh_vien = sinh_vien,
                           index_hk = index_hk,
                           tk_diem_sinh_vien = tk_diem_sinh_vien,
                           hk = hk,
                           index_diem_hk = index_diem_hk,
                           data_diem_hk = data_diem_hk,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_kqht_sv/table_kqht_chi_tiet/<string:ma_sinh_vien>_<string:id_diem>")
def table_kqht_chi_tiet(ma_sinh_vien, id_diem):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh, k.ten_khoa
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE sv.ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    sinh_vien = cur.fetchall()
    
    if (len(sinh_vien) != 1):
        return "Error"
    
    sinh_vien = sinh_vien[0]
    
    cur.execute("""
                SELECT d.*, hk.*, mh.ten_mon
                FROM diem d 
                JOIN hoc_ky hk ON d.ma_hoc_ky = hk.ma_hoc_ky
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE id_diem = %s AND ma_sinh_vien = %s
                """, (id_diem, ma_sinh_vien))
    diem_mon = cur.fetchall()
    if (len(diem_mon) != 1):
        return "Error"
    diem_mon = diem_mon[0]
    
    return render_template(session['role'] + 'ketquahoctap/table_kqht_chi_tiet.html',
                           diem_mon = diem_mon,
                           sinh_vien = sinh_vien,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_print_kqht/<string:ma_sinh_vien>")
def table_print_kqht(ma_sinh_vien):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh, k.ten_khoa
                FROM sinh_vien sv
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                WHERE sv.ma_sinh_vien = %s
                """, (ma_sinh_vien, ))
    sinh_vien = cur.fetchall()
    
    if (len(sinh_vien) != 1):
        return "Error"
    
    sinh_vien = sinh_vien[0]
    
    cur.execute("""
                SELECT hk.ma_hoc_ky, hk.ten_hoc_ky
                FROM diem d
                JOIN hoc_ky hk ON d.ma_hoc_ky = hk.ma_hoc_ky
                WHERE d.ma_sinh_vien = %s
                GROUP BY hk.ma_hoc_ky
                ORDER BY hk.ma_hoc_ky DESC
                """, (ma_sinh_vien, ))
    tmp_hoc_ky = cur.fetchall()
    
    index_hk = []
    hk = []
    index = 0
    for elm in tmp_hoc_ky:
        index_hk.append(index)
        hk.append(elm[0])
        index += 1
    
    index_diem_hk = []
    data_diem_hk = []
    for elm in hk:
        cur.execute("""
                    SELECT d.id_diem, d.ma_mon, mh.ten_mon, mh.so_tin_chi, d.thang_10, d.thang_chu, d.thang_4
                    FROM diem d
                    JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                    WHERE d.ma_hoc_ky = %s AND d.ma_sinh_vien = %s 
                    ORDER BY mh.ma_mon
                    """, (elm, ma_sinh_vien))
        data_diem_hk.append(cur.fetchall())
        index_diem_hk.append([i for i in range(len(data_diem_hk[-1]))])
    
    cur.execute("""
                SELECT d.ma_sinh_vien, SUM(d.thang_4 * mh.so_tin_chi)/SUM(mh.so_tin_chi), sum(mh.so_tin_chi)
                FROM diem d
                JOIN sinh_vien sv ON d.ma_sinh_vien = sv.ma_sinh_vien
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN mon_hoc mh ON mh.ma_mon = d.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_mon IN (
                    SELECT DISTINCT mhn.ma_mon 
                    FROM mon_hoc_nganh mhn
                    WHERE mhn.ma_nganh = n.ma_nganh
                ) AND d.thang_10 >= 4 AND d.ma_sinh_vien = %s
                GROUP BY d.ma_sinh_vien
                """, (ma_sinh_vien, ))
    tk_diem_sinh_vien = cur.fetchall()
    
    if (len(tk_diem_sinh_vien) != 1):
        return "Error"
    
    tk_diem_sinh_vien = tk_diem_sinh_vien[0]
    
    hk = []
    for elm in tmp_hoc_ky:
        hk.append(elm[1])
    
    return render_template('ketquahoctap/table_print_kqht.html',
                           sinh_vien = sinh_vien,
                           index_hk = index_hk,
                           tk_diem_sinh_vien = tk_diem_sinh_vien,
                           hk = hk,
                           index_diem_hk = index_diem_hk,
                           data_diem_hk = data_diem_hk)

@login_required
@app.route("/get_table_kqht_pdf/<string:ma_sinh_vien>")
def get_table_kqht_pdf(ma_sinh_vien):
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Bang Diem ' + ma_sinh_vien + '.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-2:]) + '/table_print_kqht/' + ma_sinh_vien,pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_kqht_excel/<string:ma_sinh_vien>")
def get_table_kqht_excel(ma_sinh_vien):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT d.ma_sinh_vien, d.ma_hoc_ky, d.ma_mon, mh.ten_mon,
                d.thang_10, d.thang_4, d.thang_chu 
                FROM diem d
                JOIN mon_hoc mh ON d.ma_mon = mh.ma_mon
                WHERE d.diem_he_3 != -1 AND d.ma_sinh_vien = %s
                ORDER BY d.ma_hoc_ky DESC
                """, (ma_sinh_vien, ))
    cac_diem = cur.fetchall()
    columnName = ['MSV','MaHocKy','MaMon','TenMon','ThangDiem10','ThangDiem4','ThangDiemChu']
    data = pd.DataFrame.from_records(cac_diem, columns=columnName)
    data = data.set_index('MaMon')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Diem_" + ma_sinh_vien + ".xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)
    
@login_required
@app.route("/delete_diem/<string:id_diem>")
def delete_diem(id_diem):
    cur = mysql.connection.cursor()
    
    cur.execute("""DELETE FROM diem
                WHERE id_diem = %s""", (id_diem, ))
    mysql.connection.commit()
    return redirect(url_for('table_kqht_sv'))

@login_required
@app.route("/table_kqht_sv/form_add_kqht", methods = ['GET','POST'])
def form_add_kqht():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT ma_hoc_ky, ten_hoc_ky
                FROM hoc_ky
                """)
    cac_hk = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_sinh_vien = details['ma_sinh_vien'].strip()
        ma_mon = details['ma_mon'].strip()
        ma_hoc_ky = details['ma_hoc_ky'].split("_")[0].strip()
        he_so_1 = details['he_so_1']
        diem_he_1 = details['diem_he_1']
        he_so_2 = details['he_so_2']
        diem_he_2 = details['diem_he_2']
        he_so_3 = details['he_so_3']
        diem_he_3 = details['diem_he_3']
        
        if diem_he_3 == "":
            diem_he_3 = -1
        
        cur.execute("SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien = %s",
                    (ma_sinh_vien, ))
        if (len(cur.fetchall()) != 1):
            return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                                   ma_err = "Mã sinh viên không tồn tại",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        cur.execute("""
                    SELECT ma_mon
                    FROM mon_hoc_nganh
                    WHERE ma_mon = %s
                    AND ma_nganh IN (SELECT ma_nganh
                                    FROM lop 
                                    WHERE ma_lop IN (
                                        SELECT ma_lop
                                        FROM sinh_vien_lop
                                        WHERE ma_sinh_vien = %s
                                    ))
                    """,  (ma_mon, ma_sinh_vien))
        if (len(cur.fetchall()) == 0):
            return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                                   ma_err = "Môn học không tồn tại, môn học không đúng với ngành của sinh viên",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
        
        if (int(float(he_so_1) + float(he_so_2) + float(he_so_3)) != 1):
            return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                                   ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        if float(he_so_3) != 0.6 or float(diem_he_1) < 0 or float(diem_he_1) > 10:
            return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                                   ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        if float(diem_he_2) < 0 or float(diem_he_2) > 10 or float(diem_he_3) > 10 or float(diem_he_3) < -1:
            return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                                   ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
        cur.execute("""
                    INSERT INTO diem(ma_sinh_vien, ma_mon, ma_hoc_ky, he_so_1, he_so_2, he_so_3,
                    diem_he_1, diem_he_2, diem_he_3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    """, (ma_sinh_vien, ma_mon, ma_hoc_ky, he_so_1, he_so_2, he_so_3, diem_he_1,
                          diem_he_2, diem_he_3))
        mysql.connection.commit()
        return redirect(url_for('table_kqht_sv'))
    
    return render_template(session['role'] + 'ketquahoctap/form_add_kqht.html',
                           cac_hk = cac_hk,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_kqht_sv/form_add_kqht_upload_file", methods = ['GET','POST'])
def form_add_kqht_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_kqht_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_kqht_upload_process", filename=filename))
        return redirect(url_for("form_add_kqht_upload_file"))
    return render_template(session['role'] + 'ketquahoctap/form_add_kqht_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong'])
    
@login_required
@app.route("/table_kqht_sv/form_add_kqht_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_kqht_upload_process(filename):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_sinh_vien', 'ma_mon', 'ma_hoc_ky', 'he_so_1', 'he_so_2',
                          'he_so_3', 'diem_he_1', 'diem_he_2', 'diem_he_3']
    
    default_name_column = ['Mã sinh viên', 'Mã môn', 'Mã học kỳ', 'Hệ số 1', 'Hệ số 2', 'Hệ số 3',
                           'Điểm hệ 1', 'Điểm hệ 2', 'Điểm hệ 3']
    
    data_kqht = pd.read_excel(pathToFile)
    data_column = list(data_kqht.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column)  < 9:
        return "Error"
    
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 9):
            return "Error"
        
        # Kiểm tra xem mã sinh viên có tồn tại không
        tmp = tuple(set(data_kqht[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien = %s", tmp)
        else:
            new_tmp = ["\"" + str(text) +"\"" for text in tmp]
            cur.execute("SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        # Kiểm tra xem mã môn có tồn tại không
        tmp = tuple(set(data_kqht[data_column[column_match.index(1)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        # Kiểm tra xem mã HK có tồn tại không
        tmp = tuple(set(data_kqht[data_column[column_match.index(2)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_hoc_ky FROM hoc_ky WHERE ma_hoc_ky = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_hoc_ky FROM hoc_ky WHERE ma_hoc_ky IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        
        # Kiểm tra các môn mà các sinh viên được học
        # nếu ko sẽ tự xóa bản ghi đó
        msv_lst = list(set(data_kqht[data_column[column_match.index(0)]]))
        for elm in msv_lst:
            cur.execute("""
                        SELECT mhn.ma_mon
                        FROM mon_hoc_nganh mhn
                        JOIN lop l ON mhn.ma_nganh = l.ma_nganh
                        JOIN sinh_vien_lop svl ON svl.ma_lop = l.ma_lop
                        WHERE svl.ma_sinh_vien = %s;
                        """, (elm, ))
            data_mon = cur.fetchall()
            cac_mon_duoc_hoc = []
            for data in data_mon:
                cac_mon_duoc_hoc.append(data[0])
            
            cac_mon =  data_kqht[data_kqht[data_column[column_match.index(0)]] == elm][data_column[column_match.index(1)]]
            index_mon = list(cac_mon.index)
            cac_mon = list(cac_mon)
            for i in range(len(index_mon)):
                if (cac_mon[i] not in cac_mon_duoc_hoc):
                    print("Check")
                    data_kqht = data_kqht.drop(index_mon[i])
                    
        data_kqht = data_kqht.reset_index()
        
        
        # Kiểm tra xem sinh viên này đã có điểm môn đó chưa
        # Nếu có rồi thì update
        for index_row in range(data_kqht.shape[0]):
            sql = "SELECT id_diem FROM diem WHERE ma_sinh_vien = %s AND ma_mon = %s"
            val = (data_kqht[data_column[column_match.index(0)]][index_row],
                   data_kqht[data_column[column_match.index(1)]][index_row])
            cur.execute(sql,val)
            diem_sv = cur.fetchall()
            if (len(diem_sv) >= 2):
                return "Error"
            if (len(diem_sv) == 1):
                sql = """
                    UPDATE diem
                    SET he_so_1 = %s, he_so_2 = %s, he_so_3 = %s,
                    diem_he_1 = %s, diem_he_2 = %s, diem_he_3 = %s,
                    ma_hoc_ky = %s
                    WHERE id_diem = %s
                """
                val = (
                    data_kqht[data_column[column_match.index(3)]][index_row],
                    data_kqht[data_column[column_match.index(4)]][index_row],
                    data_kqht[data_column[column_match.index(5)]][index_row],
                    data_kqht[data_column[column_match.index(6)]][index_row],
                    data_kqht[data_column[column_match.index(7)]][index_row],
                    data_kqht[data_column[column_match.index(8)]][index_row],
                    data_kqht[data_column[column_match.index(2)]][index_row],
                    diem_sv[0][0]
                )
                cur.execute(sql,val)
                mysql.connection.commit()
                data_kqht = data_kqht.drop(index_row)
        
        data_kqht = data_kqht.reset_index()
    
        sql = "INSERT INTO `diem` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql = sql[:-1:]
        sql += ") VALUES "
        for index_row in range(data_kqht.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_kqht[col][index_row]) + "\"" + ","
            sql = sql[:-1:]
            sql += "),"
        sql = sql[:-1:]  
        cur.execute(sql)
        mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for('table_kqht_sv'))         
     
    return render_template(session['role'] + 'ketquahoctap/form_add_kqht_upload_process.html',
                           filename = filename,
                           truong = session['truong'],
                           my_user = session['username'],
                           name_column = default_name_column,
                           index_column = data_column)

@app.route("/table_kqht_sv/form_update_kqht/<string:id_diem>", methods = ['GET','POST'])
def form_update_kqht(id_diem):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT * 
                FROM diem
                WHERE id_diem = %s
                """, (id_diem, ))
    diem = cur.fetchall()
    
    if (len(diem) != 1):
        return "Error"
    
    diem = diem[0]
    
    cur.execute("""
                SELECT ma_sinh_vien, ho_ten
                FROM sinh_vien sv
                WHERE sv.ma_sinh_vien = %s
                """, (diem[1], ))
    ten_sv = cur.fetchall()[0]
    
    if request.method == 'POST':
        details = request.form
        he_so_1 = details['he_so_1']
        diem_he_1 = details['diem_he_1']
        he_so_2 = details['he_so_2']
        diem_he_2 = details['diem_he_2']
        he_so_3 = details['he_so_3']
        diem_he_3 = details['diem_he_3']
        
        if diem_he_3 == "":
            diem_he_3 = -1
        
        if (int(float(he_so_1) + float(he_so_2) + float(he_so_3)) != 1):
            return render_template(session['role'] + 'ketquahoctap/form_update_kqht.html',
                    ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        if float(he_so_3) != 0.6 or float(diem_he_1) < 0 or float(diem_he_1) > 10:
            return render_template(session['role'] + 'ketquahoctap/form_update_kqht.html',
                    ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        if float(diem_he_2) < 0 or float(diem_he_2) > 10 or float(diem_he_3) > 10 or float(diem_he_3) < -1:
            return render_template(session['role'] + 'ketquahoctap/form_update_kqht.html',
                    ma_err = "Tổng các hệ số không bằng 1, hoặc các giá trị điểm và hệ số vượt quá giá trị quy định",
                                    my_user = session['username'],
                                    truong = session['truong'])
        cur.execute("""
                    UPDATE diem
                    SET he_so_1 = %s, he_so_2 = %s, he_so_3 = %s,
                    diem_he_1 = %s, diem_he_2 = %s, diem_he_3 = %s
                    WHERE id_diem = %s
                    """, (he_so_1, he_so_2, he_so_3, diem_he_1, diem_he_2, diem_he_3, id_diem))
        mysql.connection.commit()
        return redirect(url_for('table_kqht_sv'))
    return render_template(session['role'] + 'ketquahoctap/form_update_kqht.html',
                           ten_sv = ten_sv,
                           diem = diem,
                           my_user = session['username'],
                           truong = session['truong'])

# -- HK
@login_required
@app.route("/table_kqht_sv/table_hoc_ky")
def table_hoc_ky():
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT * 
            FROM hoc_ky
            ORDER BY nam_hoc DESC, ten_hoc_ky DESC
            """)
    
    cac_hk = cur.fetchall()
    
    return render_template(session['role'] + 'ketquahoctap/table_hoc_ky.html',
                           cac_hk = cac_hk,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_print_hoc_ky")
def table_print_hoc_ky():
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT * 
            FROM hoc_ky
            ORDER BY nam_hoc DESC, ten_hoc_ky DESC
            """)
    
    cac_hk = cur.fetchall()
    
    return render_template('ketquahoctap/table_print_hoc_ky.html',
                           cac_hk = cac_hk)

@login_required
@app.route("/get_table_hoc_ky_excel")
def get_table_hoc_ky_excel():
    cur = mysql.connection.cursor()
    
    cur.execute("""SELECT * 
            FROM hoc_ky
            ORDER BY nam_hoc DESC, ten_hoc_ky DESC
            """)
    
    cac_hk = cur.fetchall()
    columnName = ['MaHK','TenHocKy','Nam']
    data = pd.DataFrame.from_records(cac_hk, columns=columnName)
    data = data.set_index('MaHK')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Data_Hoc_Ky.xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_hoc_ky_pdf")
def get_table_hoc_ky_pdf():
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table Hoc Ky.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-1:]) + '/table_print_hoc_ky',pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_kqht_sv/form_add_hoc_ky", methods = ['GET','POST'])
def form_add_hoc_ky():
    if request.method == 'POST':
        details = request.form
        ma_hoc_ky = details['ma_hoc_ky'].strip()
        ten_hoc_ky = details['ten_hoc_ky'].strip()
        nam_hoc = details['nam_hoc'].strip()
        
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT * FROM hoc_ky WHERE ma_hoc_ky = %s", (ma_hoc_ky, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'ketquahoctap/form_add_hoc_ky.html',
                                   ma_err = "Mã học kỳ đã tồn tại",
                           my_user = session['username'],
                           truong = session['truong'])
            
        cur.execute("INSERT INTO hoc_ky(ma_hoc_ky,ten_hoc_ky,nam_hoc) VALUES (%s,%s,%s)",
                    (ma_hoc_ky,ten_hoc_ky,nam_hoc))
        mysql.connection.commit()
        return redirect(url_for('table_hoc_ky'))
    
    return render_template(session['role'] + 'ketquahoctap/form_add_hoc_ky.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_kqht_sv/form_update_hoc_ky/<string:ma_hoc_ky>", methods = ['GET','POST'])
def form_update_hoc_ky(ma_hoc_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT * 
                FROM hoc_ky
                WHERE ma_hoc_ky = %s
                """, (ma_hoc_ky, ))
    hoc_ky = cur.fetchall()
    if (len(hoc_ky) != 1):
        return "Error"
    
    hoc_ky = hoc_ky[0]
    
    if request.method == 'POST':
        details = request.form
        ten_hoc_ky = details['ten_hoc_ky'].strip()
        nam_hoc = details['nam_hoc'].strip()
        
        cur.execute("""
                    UPDATE hoc_ky
                    SET ten_hoc_ky = %s, nam_hoc = %s
                    WHERE ma_hoc_ky = %s
                    """, (ten_hoc_ky, nam_hoc, ma_hoc_ky))
        mysql.connection.commit()
        return redirect(url_for('table_hoc_ky'))
    
    return render_template(session['role'] + 'ketquahoctap/form_update_hoc_ky.html',
                           hoc_ky = hoc_ky,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/delete_hoc_ky/<string:ma_hoc_ky>")
def delete_hoc_ky(ma_hoc_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT COUNT(*) 
                FROM diem
                WHERE ma_hoc_ky = %s
                """, (ma_hoc_ky, ))
    if (cur.fetchall()[0][0] != 0):
        return redirect(url_for('table_hoc_ky'))
    
    cur.execute("""
                SELECT COUNT(*)
                FROM dot_dang_ky
                WHERE ma_hoc_ky = %s
                """, (ma_hoc_ky, ))
    if (cur.fetchall()[0][0] != 0):
        return redirect(url_for('table_hoc_ky'))
    
    cur.execute("""
                DELETE FROM hoc_ky
                WHERE ma_hoc_ky = %s
                """, (ma_hoc_ky, ))
    mysql.connection.commit()
    return redirect(url_for('table_hoc_ky'))

# -------------------------- Ket Qua Hoc Tap -------------------------

# -------------------------- Dang Ky Hoc -------------------------
@login_required
@app.route("/table_dang_ky_hoc", methods=['GET','POST'])
def table_dang_ky_hoc():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT ddk.ma_dot, ddk.ma_hoc_ky, hk.ten_hoc_ky
                FROM dot_dang_ky ddk
                JOIN hoc_ky hk ON ddk.ma_hoc_ky = hk.ma_hoc_ky
                ORDER BY ddk.ngay_bat_dau DESC
                """)
    cac_ddk = cur.fetchall()
    
    if (len(cac_ddk) != 0):
        ma_dot = str(cac_ddk[0][0]) + " _ " + str(cac_ddk[0][1]) + " _ " + str(cac_ddk[0][2])
        ma_dot_dang_ky = str(cac_ddk[0][0])
    else:
        ma_dot = ''
        ma_dot_dang_ky = ''
        
    if request.method == 'POST':
        details = request.form
        ma_dot = details['ma_dot_dang_ky'].strip()
        ma_dot_dang_ky = details['ma_dot_dang_ky'].split("_")[0].strip()
    
    cur.execute("""
                SELECT mhdk.id_dang_ky, mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky, 
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mh.ma_mon = mhdk.ma_mon
                WHERE mhdk.ma_dot = %s
                """, (ma_dot, ))
    cac_lop = cur.fetchall()
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    data = pd.DataFrame.from_records(cac_lop, columns=column_name)
    
    data = data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.values.tolist()
    
    return render_template(session['role'] + 'dangkyhoc/table_dang_ky_hoc.html',
                           ma_dot_dang_ky = ma_dot_dang_ky,
                           ma_dot = ma_dot,
                           cac_lop = data,
                           cac_ddk = cac_ddk,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/get_print_dang_ky_hoc/<string:ma_dot>")
def get_print_dang_ky_hoc(ma_dot):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT ddk.ma_dot, ddk.ma_hoc_ky, hk.ten_hoc_ky
                FROM dot_dang_ky ddk
                JOIN hoc_ky hk ON ddk.ma_hoc_ky = hk.ma_hoc_ky
                WHERE ddk.ma_dot = %s
                """, (ma_dot, ))
    cac_ddk = cur.fetchall()
    
    if (len(cac_ddk) != 0):
        ma_dot_dang_ky = str(cac_ddk[0][0]) + " _ " + str(cac_ddk[0][1]) + " _ " + str(cac_ddk[0][2])
    else:
        return "Error"
    
    cur.execute("""
                SELECT mhdk.id_dang_ky, mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky, 
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mh.ma_mon = mhdk.ma_mon
                WHERE mhdk.ma_dot = %s
                """, (ma_dot, ))
    cac_lop = cur.fetchall()
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    data = pd.DataFrame.from_records(cac_lop, columns=column_name)
    
    data = data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.values.tolist()
    
    return render_template('dangkyhoc/table_print_dang_ky_hoc.html',
                           ma_dot_dang_ky = ma_dot_dang_ky,
                           ma_dot = ma_dot,
                           cac_lop = data)

@login_required
@app.route("/get_table_dang_ky_hoc_pdf/<string:ma_dot>")
def get_table_dang_ky_hoc_pdf(ma_dot):
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table_Lop_Dot_' + ma_dot + '.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-2:]) + '/get_print_dang_ky_hoc/' + str(ma_dot),pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_dang_ky_hoc_excel/<string:ma_dot>")
def get_table_dang_ky_hoc_excel(ma_dot):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT ddk.ma_dot, ddk.ma_hoc_ky, hk.ten_hoc_ky
                FROM dot_dang_ky ddk
                JOIN hoc_ky hk ON ddk.ma_hoc_ky = hk.ma_hoc_ky
                WHERE ddk.ma_dot = %s
                """, (ma_dot, ))
    cac_ddk = cur.fetchall()
    
    if (len(cac_ddk) != 0):
        ma_dot_dang_ky = str(cac_ddk[0][0]) + " _ " + str(cac_ddk[0][1]) + " _ " + str(cac_ddk[0][2])
    else:
        return "Error"
    
    cur.execute("""
                SELECT mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky, 
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mh.ma_mon = mhdk.ma_mon
                WHERE mhdk.ma_dot = %s
                """, (ma_dot, ))
    cac_lop = cur.fetchall()
    column_name = ['ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    data = pd.DataFrame.from_records(cac_lop, columns=column_name)
    
    data = data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.set_index('ma_so_lop')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Danh_Sach_lop_Dot_" + ma_dot + ".xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/table_dang_ky_hoc/form_add_dot_dk", methods = ['GET','POST'])
def form_add_dot_dk():
    cur = mysql.connection.cursor()
    # DROP EVENT IF EXISTS `dk_hoc_end_202001`
    cur.execute("""
                SELECT ma_hoc_ky, ten_hoc_ky
                FROM hoc_ky
                ORDER BY ma_hoc_ky DESC, ten_hoc_ky DESC
                """)
    cac_hk = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        ma_dot = details['ma_dot'].strip()
        ma_hoc_ky = details['ma_hoc_ky'].split("_")[0].strip()
        ngay_bat_dau = datetime.datetime.strptime(details['ngay_bat_dau'].strip(), '%Y-%m-%dT%H:%M')
        ngay_ket_thuc = datetime.datetime.strptime(details['ngay_ket_thuc'].strip(), '%Y-%m-%dT%H:%M')
        # datetime.datetime.strptime(detail['Ngay'].strip(), '%Y-%m-%d')
        # datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if (ngay_bat_dau - datetime.datetime.now() < datetime.timedelta(hours=6)):
            return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày bắt đầu không được từ quá khứ",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
        
        if (ngay_ket_thuc - ngay_bat_dau < datetime.timedelta(days=1)):
            return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày kết thúc phải sau ngày bắt đầu ít nhất 1 ngày",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        cur.execute("SELECT * FROM dot_dang_ky WHERE ma_dot = %s", (ma_dot, ))
        if (len(cur.fetchall()) != 0):
            return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Mã đợt đăng ký đã tồn tại",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])

        cur.execute("""
                    SELECT COUNT(*)
                    FROM dot_dang_ky ddk
                    LEFT JOIN dot_yeu_cau_dang_ky ks ON ddk.ma_dot = ks.ma_dot_dang_ky
                    WHERE 
                    (STR_TO_DATE('""" +
                    ngay_bat_dau.strftime("%Y-%m-%d %H:%M:%S")
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ks.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    OR
                    (STR_TO_DATE('""" + 
                    ngay_bat_dau.strftime("%Y-%m-%d %H:%M:%S") 
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ddk.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    """)
        if cur.fetchall()[0][0] != 0:
            return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Bị trùng với các đợt đăng ký đã có trước đó",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
        cur.execute("""
                    SELECT COUNT(*)
                    FROM dot_dang_ky ddk
                    LEFT JOIN dot_yeu_cau_dang_ky ks ON ddk.ma_dot = ks.ma_dot_dang_ky
                    WHERE 
                    (STR_TO_DATE('""" +
                    ngay_ket_thuc.strftime("%Y-%m-%d %H:%M:%S")
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ks.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    OR
                    (STR_TO_DATE('""" + 
                    ngay_ket_thuc.strftime("%Y-%m-%d %H:%M:%S") 
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ddk.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    """)
        if cur.fetchall()[0][0] != 0:
            return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Bị trùng với các đợt đăng ký đã có trước đó",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
        
        if details['co_ks'] == 'yes':
            ma_dot_khao_sat = details['ma_dot_khao_sat']
            ngay_bat_dau_ks = datetime.datetime.strptime(details['ngay_bat_dau_ks'].strip(), '%Y-%m-%dT%H:%M')
            ngay_ket_thuc_ks = datetime.datetime.strptime(details['ngay_ket_thuc_ks'].strip(), '%Y-%m-%dT%H:%M')
            
            if (ngay_bat_dau - datetime.datetime.now() < datetime.timedelta(days=5) ):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                    ma_err = "Ngày bắt đầu không được từ quá khứ, khi có đợt khảo sát phải mở đợt khảo sát ít nhất 5 ngày",
                                        cac_hk = cac_hk,
                                        my_user = session['username'],
                                        truong = session['truong'])
 
            if (ngay_bat_dau_ks - datetime.datetime.now() < datetime.timedelta(hours=6)):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày bắt đầu khảo sát không được từ quá khứ",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
 
            if (ngay_bat_dau < ngay_bat_dau_ks):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày bắt đầu khảo sát phải trước ngày bắt đầu chính thức",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
                
            if (ngay_ket_thuc_ks > ngay_bat_dau_ks and ngay_bat_dau - ngay_ket_thuc_ks < datetime.timedelta(days=1)):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày kết thúc khảo sát phải kết thúc trước ngày bắt đầu ít nhất 1 ngày",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
                
            if (ngay_ket_thuc_ks - ngay_bat_dau_ks < datetime.timedelta(days=5)):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Ngày kết thúc khảo sát phải kết thúc sau ngày bắt đầu khảo sát ít nhất 5 ngày",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
            
            cur.execute("SELECT * FROM dot_yeu_cau_dang_ky WHERE ma_dot_yeu_cau = %s", (ma_dot_khao_sat, ))
            if (len(cur.fetchall()) != 0):
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                   ma_err = "Mã đợt khảo sát đã tồn tại",
                                    cac_hk = cac_hk,
                                    my_user = session['username'],
                                    truong = session['truong'])
                
            cur.execute("""
                    SELECT COUNT(*)
                    FROM dot_dang_ky ddk
                    LEFT JOIN dot_yeu_cau_dang_ky ks ON ddk.ma_dot = ks.ma_dot_dang_ky
                    WHERE 
                    (STR_TO_DATE('""" +
                    ngay_bat_dau_ks.strftime("%Y-%m-%d %H:%M:%S")
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ks.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    OR
                    (STR_TO_DATE('""" + 
                    ngay_bat_dau_ks.strftime("%Y-%m-%d %H:%M:%S") 
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ddk.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    """)
            if cur.fetchall()[0][0] != 0:
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                    ma_err = "Đợt khảo sát bị trùng với các đợt đăng ký đã có trước đó",
                                        cac_hk = cac_hk,
                                        my_user = session['username'],
                                        truong = session['truong'])
                
            cur.execute("""
                    SELECT COUNT(*)
                    FROM dot_dang_ky ddk
                    LEFT JOIN dot_yeu_cau_dang_ky ks ON ddk.ma_dot = ks.ma_dot_dang_ky
                    WHERE 
                    (STR_TO_DATE('""" +
                    ngay_ket_thuc_ks.strftime("%Y-%m-%d %H:%M:%S")
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ks.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    OR
                    (STR_TO_DATE('""" + 
                    ngay_ket_thuc_ks.strftime("%Y-%m-%d %H:%M:%S") 
                    + """', '%Y-%m-%d %H:%i:%s') BETWEEN ddk.ngay_bat_dau AND ddk.ngay_ket_thuc)
                    """)
            if cur.fetchall()[0][0] != 0:
                return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                                    ma_err = "Đợt khảo sát bị trùng với các đợt đăng ký đã có trước đó",
                                        cac_hk = cac_hk,
                                        my_user = session['username'],
                                        truong = session['truong'])
                
            cur.execute("""
                        INSERT INTO dot_yeu_cau_dang_ky(ma_dot_yeu_cau,ma_dot_dang_ky,ma_hoc_ky,ngay_bat_dau,ngay_ket_thuc)
                        VALUES (%s, %s, %s, %s, %s)
                        """, (
                            ma_dot_khao_sat,
                            ma_dot,
                            ma_hoc_ky,
                            ngay_bat_dau_ks.strftime("%Y-%m-%d %H:%M:%S"),
                            ngay_ket_thuc_ks.strftime("%Y-%m-%d %H:%M:%S")
                        ))
            mysql.connection.commit()
            
            sql = "CREATE EVENT IF NOT EXISTS "
            sql += "ks_hoc_start_" + ma_dot + " "
            sql += "ON SCHEDULE AT \'" + ngay_bat_dau_ks.strftime("%Y-%m-%d %H:%M:%S") + "\' "
            sql += "DO "
            sql += """
                UPDATE dot_yeu_cau_dang_ky
                SET trang_thai = "Đang mở"
                WHERE ma_dot_dang_ky = \'""" + ma_dot + "\' AND ma_dot_yeu_cau = '" + ma_dot_khao_sat + "' ;"
            cur.execute(sql)
            mysql.connection.commit()
            
            sql = "CREATE EVENT IF NOT EXISTS "
            sql += "ks_hoc_end_" + ma_dot + " "
            sql += "ON SCHEDULE AT \'" + ngay_ket_thuc_ks.strftime("%Y-%m-%d %H:%M:%S") + "\' "
            sql += "DO "
            sql += """
                UPDATE dot_yeu_cau_dang_ky
                SET trang_thai = "Đã đóng"
                WHERE ma_dot_dang_ky = \'""" + ma_dot + "\' AND ma_dot_yeu_cau = '" + ma_dot_khao_sat + "' ;"
            cur.execute(sql)
            mysql.connection.commit()
            
        cur.execute("""INSERT INTO dot_dang_ky(ma_dot, ma_hoc_ky, ngay_bat_dau, ngay_ket_thuc)
                    VALUES (%s, %s, %s, %s)
                    """, (
                        ma_dot,
                        ma_hoc_ky,
                        ngay_bat_dau.strftime("%Y-%m-%d %H:%M:%S"),
                        ngay_ket_thuc.strftime("%Y-%m-%d %H:%M:%S")
                    ))
        mysql.connection.commit()
        
        
        sql = "CREATE EVENT IF NOT EXISTS "
        sql += "dk_hoc_start_" + ma_dot + " "
        sql += "ON SCHEDULE AT \'" + ngay_bat_dau.strftime("%Y-%m-%d %H:%M:%S") + "\' "
        sql += "DO "
        sql += """
            UPDATE dot_dang_ky
            SET trang_thai = "Đang mở"
            WHERE ma_dot = \'""" + ma_dot + "\' ;"
        cur.execute(sql)
        mysql.connection.commit()
        
        sql = "CREATE EVENT IF NOT EXISTS "
        sql += "dk_hoc_end_" + ma_dot + " "
        sql += "ON SCHEDULE AT \'" + ngay_ket_thuc.strftime("%Y-%m-%d %H:%M:%S") + "\' "
        sql += "DO "
        sql += """
            UPDATE dot_dang_ky
            SET trang_thai = "Đã đóng"
            WHERE ma_dot = \'""" + ma_dot + "\' ;"
        cur.execute(sql)
        mysql.connection.commit()
        return redirect(url_for('table_dang_ky_hoc'))
    return render_template(session['role'] + 'dangkyhoc/form_add_dot_dk.html',
                           cac_hk = cac_hk,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_dang_ky_hoc/table_dkh_sv/<string:id_dang_ky>")
def table_dkh_sv(id_dang_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT mhdk.ma_dot, hk.ten_hoc_ky, mh.ten_mon, mhdk.ma_so_lop
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                JOIN dot_dang_ky ddk ON ddk.ma_dot = mhdk.ma_dot
                JOIN hoc_ky hk ON hk.ma_hoc_ky = ddk.ma_hoc_ky
                WHERE mhdk.id_dang_ky = %s
                GROUP BY mhdk.id_dang_ky
                """, (id_dang_ky, ))
    thong_tin = cur.fetchall()
    if (len(thong_tin) == 0):
        return "Error"
    thong_tin = thong_tin[0]

    cur.execute("""
                SELECT dkm.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh
                FROM dang_ky_mon dkm
                JOIN sinh_vien sv ON sv.ma_sinh_vien = dkm.ma_sinh_vien
                JOIN sinh_vien_lop svl ON dkm.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE dkm.id_dang_ky = %s
                """, (id_dang_ky, ))
    cac_sv = cur.fetchall()
    
    return render_template(session['role'] + 'dangkyhoc/table_dkh_sv.html',
                           id_dang_ky = id_dang_ky,
                           thong_tin = thong_tin,
                           cac_sv = cac_sv,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/get_print_table_dkh_sv/<string:id_dang_ky>")
def get_print_table_dk_sv(id_dang_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT mhdk.ma_dot, hk.ten_hoc_ky, mh.ten_mon, mhdk.ma_so_lop
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                JOIN dot_dang_ky ddk ON ddk.ma_dot = mhdk.ma_dot
                JOIN hoc_ky hk ON hk.ma_hoc_ky = ddk.ma_hoc_ky
                WHERE mhdk.id_dang_ky = %s
                """, (id_dang_ky, ))
    thong_tin = cur.fetchall()
    if (len(thong_tin) == 0):
        return "Error"
    thong_tin = thong_tin[0]

    cur.execute("""
                SELECT dkm.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh
                FROM dang_ky_mon dkm
                JOIN sinh_vien sv ON sv.ma_sinh_vien = dkm.ma_sinh_vien
                JOIN sinh_vien_lop svl ON dkm.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE dkm.id_dang_ky = %s
                """, (id_dang_ky, ))
    cac_sv = cur.fetchall()
    
    return render_template('dangkyhoc/table_print_dkh_sv.html',
                           id_dang_ky = id_dang_ky,
                           thong_tin = thong_tin,
                           cac_sv = cac_sv)

@login_required
@app.route("/get_table_dkh_sv_pdf/<string:id_dang_ky>_<string:ma_lop>")
def get_table_dkh_sv_pdf(id_dang_ky, ma_lop):
    pathFile = app.config['SAVE_FOLDER_PDF']  + '/Table_Lop_' + ma_lop + '.pdf'
    pdfkit.from_url("/".join(request.url.split("/")[:-2:]) + '/get_print_table_dkh_sv/' + str(id_dang_ky),pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/get_table_dkh_sv_excel/<string:id_dang_ky>_<string:ma_lop>")
def get_table_dkh_sv_excel(id_dang_ky, ma_lop):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT mhdk.ma_dot, hk.ten_hoc_ky, mh.ten_mon, mhdk.ma_so_lop
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                JOIN dot_dang_ky ddk ON ddk.ma_dot = mhdk.ma_dot
                JOIN hoc_ky hk ON hk.ma_hoc_ky = ddk.ma_hoc_ky
                WHERE mhdk.id_dang_ky = %s
                """, (id_dang_ky, ))
    thong_tin = cur.fetchall()
    if (len(thong_tin) == 0):
        return "Error"
    thong_tin = thong_tin[0]
    del ma_lop
    cur.execute("""
                SELECT dkm.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh
                FROM dang_ky_mon dkm
                JOIN sinh_vien sv ON sv.ma_sinh_vien = dkm.ma_sinh_vien
                JOIN sinh_vien_lop svl ON dkm.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE dkm.id_dang_ky = %s
                """, (id_dang_ky, ))
    cac_sv = cur.fetchall()
    columnName = ['ma_sinh_vien','ho_ten','ten_lop','ten_nganh']
    data = pd.DataFrame.from_records(cac_sv, columns=columnName)
    data = data.set_index('ma_sinh_vien')
    pathFile = app.config['SAVE_FOLDER_EXCEL'] + "/" + "Danh_Sach_lop_" + thong_tin[3] + ".xlsx"
    data.to_excel(pathFile)
    return send_file(pathFile, as_attachment=True)

@login_required
@app.route("/huy_dang_ky_sv/<string:id_dang_ky>_<string:ma_sinh_vien>")
def huy_dang_ky_sv(id_dang_ky, ma_sinh_vien):
    if (session['role_id'] != 1):
        return "Error"
    
    cur = mysql.connection.cursor()
    cur.execute("""
                DELETE FROM dang_ky_mon
                WHERE id_dang_ky = %s AND ma_sinh_vien = %s
                """, (id_dang_ky, ma_sinh_vien))
    mysql.connection.commit()
    return redirect(url_for('table_dkh_sv', id_dang_ky = id_dang_ky))

@login_required
@app.route("/table_dang_ky_hoc/table_dkh_lop_hoc/<string:ma_dot>")
def table_dkh_lop_hoc(ma_dot):
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT ddk.ma_dot, ddk.ma_hoc_ky, hk.ten_hoc_ky
                FROM dot_dang_ky ddk
                JOIN hoc_ky hk ON ddk.ma_hoc_ky = hk.ma_hoc_ky
                WHERE ddk.ma_dot = %s
                """, (ma_dot, ))
    thong_tin_dot = cur.fetchall()
    if (len(thong_tin_dot) == 0):
        return "Error"
    thong_tin_dot = thong_tin_dot[0]
    
    cur.execute("""
                SELECT mhdk.id_dang_ky, mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky,
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                WHERE mhdk.ma_dot = %s
                ORDER BY mhdk.ma_so_lop ASC;
                """, (ma_dot, ))
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop', 'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    cac_mon_dk = cur.fetchall()
    data = pd.DataFrame.from_records(cac_mon_dk, columns=column_name)
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi',
                                'ma_so_lop', 'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.values.tolist()
    return render_template(session['role'] + 'dangkyhoc/table_dkh_lop_hoc.html',
                           tt_dot = thong_tin_dot,
                           cac_mon_dk = data,
                           ma_dot = ma_dot,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_dang_ky_hoc/form_add_dkh_lop_hoc_upload_file/<string:ma_dot>", methods = ['GET','POST'])
def form_add_dkh_lop_hoc_upload_file(ma_dot):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT *
                FROM dot_dang_ky
                WHERE ma_dot = %s
                """, (ma_dot, ))
    if (len(cur.fetchall()) == 0):
        return "Error"
    
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_dkh_lop_hoc_upload_file", ma_dot = ma_dot))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_dkh_lop_hoc_upload_process", filename=filename, ma_dot = ma_dot))
        return redirect(url_for("form_add_dkh_lop_hoc_upload_file", ma_dot = ma_dot))
    return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc_upload_file.html',
                           ma_dot = ma_dot,
                           my_user = session['username'],
                           truong = session['truong'])
    
@login_required
@app.route("/table_dang_ky_hoc/form_add_dkh_lop_hoc_upload_process/<string:filename>_<string:ma_dot>", methods = ['GET','POST'])
def form_add_dkh_lop_hoc_upload_process(filename, ma_dot):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['ma_mon', 'ma_so_lop', 'thu', 'phong_hoc', 'th_lt',
                          'tiet_bat_dau', 'tiet_ket_thuc', 'so_luong']
    
    default_name_column = ['Mã môn học', 'Mã số lớp', 'Ngày học (thứ mấy)', 'Phòng học', 'Hình thức học (LT hay TH)',
                           'Tiết bắt đầu', 'Tiết kết thúc', 'Số lượng sinh viên']
    
    data_lop_dk = pd.read_excel(pathToFile)
    data_column = list(data_lop_dk.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column)  < 8:
        return "Error"
    
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 8):
            return "Error"
        
        cur.execute("""
                    SELECT ma_dot_yeu_cau
                    FROM dot_yeu_cau_dang_ky
                    WHERE ma_dot_dang_ky = %s
                    """, (ma_dot, ))
        ma_dot_ks = cur.fetchall()
        if (len(ma_dot_ks) != 0):
            ma_dot_ks = ma_dot_ks[0][0]
        else:
            ma_dot_ks = -1
        
        # Kiểm tra xem mã môn có tồn tại không
        tmp = tuple(set(data_lop_dk[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_mon FROM mon_hoc WHERE ma_mon IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        
        if (len(data_tmp_take) != len(tmp)):
            return "Error"
        
        data_lop_dk = data_lop_dk.fillna(' ')
        
        # Kiểm tra xem có mã số lớp đó chưa
        # Nếu có đủ rồi thì drop
        # nếu là loại khác thì sẽ thêm vào 
        for index_row in range(data_lop_dk.shape[0]):
            sql = "SELECT id_dang_ky FROM mon_hoc_dot_dang_ky WHERE ma_so_lop = %s AND th_lt = %s"
            val = (data_lop_dk[data_column[column_match.index(1)]][index_row],
                   data_lop_dk[data_column[column_match.index(4)]][index_row])
            cur.execute(sql,val)
            ktra_lop = cur.fetchall()
            if (len(ktra_lop) != 0):
                data_lop_dk = data_lop_dk.drop(index_row)
            else:
                sql = "SELECT id_dang_ky FROM mon_hoc_dot_dang_ky WHERE ma_so_lop = %s"
                val = (data_lop_dk[data_column[column_match.index(1)]][index_row], )
                cur.execute(sql,val)
                id_dk = cur.fetchall()
                if (len(id_dk) != 0):
                    sql = """
                        INSERT INTO mon_hoc_dot_dang_ky(`id_dang_ky`, `ma_mon`,
                        `ma_so_lop`, `ma_dot_yeu_cau`, `ma_dot`, `th_lt`, `thu`,
                        `phong_hoc`, `tiet_bat_dau`, `tiet_ket_thuc`, `so_luong`,
                        `so_luong_con_lai`)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        id_dk[0][0],
                        data_lop_dk[data_column[column_match.index(0)]][index_row],
                        data_lop_dk[data_column[column_match.index(1)]][index_row],
                        ma_dot_ks,
                        ma_dot,
                        data_lop_dk[data_column[column_match.index(2)]][index_row],
                        data_lop_dk[data_column[column_match.index(3)]][index_row],
                        data_lop_dk[data_column[column_match.index(4)]][index_row],
                        data_lop_dk[data_column[column_match.index(5)]][index_row],
                        data_lop_dk[data_column[column_match.index(6)]][index_row],
                        data_lop_dk[data_column[column_match.index(7)]][index_row],
                        data_lop_dk[data_column[column_match.index(7)]][index_row]
                    )
                    cur.execute(sql,val)
                    mysql.connection.commit()
                    data_lop_dk = data_lop_dk.drop(index_row)
        
        data_lop_dk = data_lop_dk.reset_index()
    
        data_lop_dk = data_lop_dk.drop('index', axis=1)
    
        sql = "INSERT INTO `mon_hoc_dot_dang_ky` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql += "ma_dot_yeu_cau,ma_dot"
        sql += ") VALUES "
        for index_row in range(data_lop_dk.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_lop_dk[col][index_row]) + "\"" + ","
            sql += "\"" + str(ma_dot_ks) + "\",\"" + str(ma_dot) + "\""
            sql += "),"
        sql = sql[:-1:]  
        cur.execute(sql)
        mysql.connection.commit()
        
        ma_so_lst = list(set(data_lop_dk[data_column[column_match.index(1)]].values.tolist()))
        
        for elm in ma_so_lst:
            cur.execute("""
                        SELECT id_dang_ky
                        FROM mon_hoc_dot_dang_ky 
                        WHERE ma_so_lop = %s
                        LIMIT 1
                        """, (elm, ))
            id_dk = cur.fetchall()[0][0]
            
            cur.execute("""
                        UPDATE mon_hoc_dot_dang_ky
                        SET id_dang_ky = %s
                        WHERE ma_so_lop = %s AND ma_dot = %s;
                        """, (id_dk, elm, ma_dot))
            mysql.connection.commit()
        os.remove(pathToFile)
        return redirect(url_for('table_dkh_lop_hoc', ma_dot = ma_dot))         
    return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc_upload_process.html',
                           my_user = session['username'],
                           truong = session['truong'],
                           filename = filename,
                           ma_dot = ma_dot,
                           name_column = default_name_column,
                           index_column = data_column)

@login_required
@app.route("/table_dang_ky_hoc/form_add_dkh_lop_hoc/<string:ma_dot>", methods=['GET','POST'])
def form_add_dkh_lop_hoc(ma_dot):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        ma_mon = details['ma_mon'].strip()
        ma_so_lop = details['ma_so_lop'].strip()
        thu = details['thu'].split()[0].strip()
        phong_hoc = details['phong_hoc'].strip()
        th_lt = details['th_lt'].split()[0].strip()
        tiet_bat_dau = details['tiet_bat_dau'].strip()
        tiet_ket_thuc = details['tiet_ket_thuc'].strip()
        so_luong = details['so_luong']
        
        # kiem tra ma mon
        cur.execute("""
                    SELECT ma_mon
                    FROM mon_hoc
                    WHERE ma_mon = %s
                    """, (ma_mon, ))
        if len(cur.fetchall()) == 0:
            return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc.html',
                                   ma_err = "Mã môn không tồn tại",
                           my_user = session['username'],
                           truong = session['truong'])

        cur.execute("SELECT ma_dot_yeu_cau FROM dot_yeu_cau_dang_ky WHERE ma_dot_dang_ky = %s", (ma_dot, ))
        ma_dot_yeu_cau = cur.fetchall()
        if len(ma_dot_yeu_cau) == 0:
            ma_dot_yeu_cau = '-1'
        else:
            ma_dot_yeu_cau = ma_dot_yeu_cau[0][0]

        cur.execute("""
                    SELECT id_dang_ky
                    FROM mon_hoc_dot_dang_ky
                    WHERE ma_so_lop = %s
                    """, (ma_so_lop, ))
        lop = cur.fetchall()
        if len(lop) != 0:
            cur.execute("""
                        SELECT th_lt
                        FROM mon_hoc_dot_dang_ky
                        WHERE id_dang_ky = %s AND th_lt = %s
                        """, (lop[0][0], th_lt))
            if (len(cur.fetchall()) != 0):
                return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc.html',
                                    ma_err = "Mã số lớp đã tồn tại",
                            my_user = session['username'],
                            truong = session['truong'])
            else:
                cur.execute("""
                    INSERT INTO mon_hoc_dot_dang_ky(id_dang_ky,ma_mon, ma_so_lop, ma_dot_yeu_cau, ma_dot, th_lt,
                    thu, phong_hoc, tiet_bat_dau, tiet_ket_thuc, so_luong, so_luong_con_lai) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        lop[0][0],
                        ma_mon,
                        ma_so_lop,
                        ma_dot_yeu_cau,
                        ma_dot,
                        th_lt,
                        thu,
                        phong_hoc,
                        tiet_bat_dau,
                        tiet_ket_thuc,
                        so_luong,
                        so_luong
                    ))
                mysql.connection.commit()
                return redirect(url_for('table_dkh_lop_hoc', ma_dot = ma_dot))
        
        if int(tiet_bat_dau) >= int(tiet_ket_thuc):
            return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc.html',
                                   ma_err = "Phải bắt đầu trước tiết kết thúc",
                           my_user = session['username'],
                           truong = session['truong'])
            
    
            
        cur.execute("""
                    INSERT INTO mon_hoc_dot_dang_ky(ma_mon, ma_so_lop, ma_dot_yeu_cau, ma_dot, th_lt,
                    thu, phong_hoc, tiet_bat_dau, tiet_ket_thuc, so_luong, so_luong_con_lai) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ma_mon,
                        ma_so_lop,
                        ma_dot_yeu_cau,
                        ma_dot,
                        th_lt,
                        thu,
                        phong_hoc,
                        tiet_bat_dau,
                        tiet_ket_thuc,
                        so_luong,
                        so_luong
                    ))
        mysql.connection.commit()
        return redirect(url_for('table_dkh_lop_hoc', ma_dot = ma_dot))
    return render_template(session['role'] + 'dangkyhoc/form_add_dkh_lop_hoc.html',
                           ma_dot = ma_dot,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/delete_lop_hoc/<ma_dot>_<id_dang_ky>")
def delete_lop_hoc(ma_dot,id_dang_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                DELETE FROM dang_ky_mon
                WHERE id_dang_ky = %s
                """, (id_dang_ky, ))
    mysql.connection.commit()
    
    cur.execute("""
                DELETE FROM mon_hoc_dot_dang_ky
                WHERE id_dang_ky = %s
                """, (id_dang_ky, ))
    mysql.connection.commit()
    return redirect(url_for('table_dkh_lop_hoc', ma_dot = ma_dot))

@login_required
@app.route("/delete_dot_dang_ky/<string:ma_dot>")
def delete_dot_dang_ky(ma_dot):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT DISTINCT mhdk.id_dang_ky
                FROM mon_hoc_dot_dang_ky mhdk
                WHERE mhdk.ma_dot = %s
                """, (ma_dot, ))
    cac_id_dk = cur.fetchall()
    
    cac_id = "("
    for elm in cac_id_dk:
        cac_id += "\"" + elm[0] + "\","
    cac_id = cac_id[:-1:]
    cac_id += ")"

    if (len(cac_id_dk) != 0):
        cur.execute("""
                    DELETE FROM dang_ky_mon
                    WHERE id_dang_ky IN """ + cac_id)
        mysql.connection.commit()
        
        cur.execute("""
                    DELETE FROM mon_hoc_dot_dang_ky
                    WHERE id_dang_ky IN """ + cac_id)
        mysql.connection.commit()
    
    cur.execute("""
                DROP EVENT IF EXISTS dk_hoc_start_""" + ma_dot + """
                """)
    mysql.connection.commit()
    
    cur.execute("""
                DROP EVENT IF EXISTS dk_hoc_end_""" + ma_dot + """
                """)
    mysql.connection.commit()
    
    #ks_hoc_start_
    cur.execute("""
                DROP EVENT IF EXISTS ks_hoc_start_""" + ma_dot + """
                """)
    mysql.connection.commit()
    
    cur.execute("""
                DROP EVENT IF EXISTS ks_hoc_end_""" + ma_dot + """
                """)
    mysql.connection.commit()
    
    cur.execute("""
                DELETE FROM dot_yeu_cau_dang_ky
                WHERE ma_dot_dang_ky = %s
                """, (ma_dot, ))
    mysql.connection.commit()
    
    cur.execute("""
                DELETE FROM dot_dang_ky
                WHERE ma_dot = %s
                """, (ma_dot, ))
    mysql.connection.commit()
    return redirect(url_for('table_dang_ky_hoc'))
    
@login_required
@app.route("/table_khao_sat", methods = ['GET','POST'])
def table_khao_sat():
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT dks.ma_dot_yeu_cau, ddk.ma_hoc_ky, hk.ten_hoc_ky, ddk.ma_dot
                FROM dot_dang_ky ddk
                JOIN hoc_ky hk ON ddk.ma_hoc_ky = hk.ma_hoc_ky
                JOIN dot_yeu_cau_dang_ky dks ON dks.ma_dot_dang_ky = ddk.ma_dot
                ORDER BY ddk.ngay_bat_dau DESC
                """)
    cac_ks = cur.fetchall()
    
    if (len(cac_ks) != 0):
        ma_ks = str(cac_ks[0][0]) + " _ " + str(cac_ks[0][1]) + " _ " + str(cac_ks[0][2]) + " _ " + str(cac_ks[0][3])
        ma_dot_dang_ky = str(cac_ks[0][3])
    else:
        ma_ks = ''
        ma_dot_dang_ky = ''
        
    if request.method == 'POST':
        details = request.form
        ma_ks = details['ma_dot_khao_sat'].strip()
        ma_dot_dang_ky = details['ma_dot_khao_sat'].split("_")[-1].strip()
    
    cur.execute("""
                SELECT mhdk.id_dang_ky, mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky, 
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mh.ma_mon = mhdk.ma_mon
                WHERE mhdk.ma_dot = %s
                """, (ma_dot_dang_ky, ))
    cac_lop = cur.fetchall()
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    data = pd.DataFrame.from_records(cac_lop, columns=column_name)
    
    data = data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.values.tolist()
    
    return render_template(session['role'] + 'khaosat/table_khao_sat.html',
                           ma_dot_dang_ky = ma_dot_dang_ky,
                           ma_dot = ma_ks,
                           cac_lop = data,
                           cac_ks = cac_ks,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/table_khao_sat/table_khao_sat_sv/<string:id_dang_ky>")
def table_khao_sat_sv(id_dang_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT mhdk.ma_dot, hk.ten_hoc_ky, mh.ten_mon, mhdk.ma_so_lop
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                JOIN dot_dang_ky ddk ON ddk.ma_dot = mhdk.ma_dot
                JOIN hoc_ky hk ON hk.ma_hoc_ky = ddk.ma_hoc_ky
                WHERE mhdk.id_dang_ky = %s
                GROUP BY mhdk.id_dang_ky
                """, (id_dang_ky, ))
    thong_tin = cur.fetchall()
    if (len(thong_tin) == 0):
        return "Error"
    thong_tin = thong_tin[0]

    cur.execute("""
                SELECT dkm.ma_sinh_vien, sv.ho_ten, l.ten_lop, n.ten_nganh
                FROM dang_ky_mon dkm
                JOIN sinh_vien sv ON sv.ma_sinh_vien = dkm.ma_sinh_vien
                JOIN sinh_vien_lop svl ON dkm.ma_sinh_vien = svl.ma_sinh_vien
                JOIN lop l ON svl.ma_lop = l.ma_lop
                JOIN nganh n ON l.ma_nganh = n.ma_nganh
                WHERE dkm.id_dang_ky = %s
                """, (id_dang_ky, ))
    cac_sv = cur.fetchall()
    
    return render_template(session['role'] + 'khaosat/table_khao_sat_sv.html',
                           id_dang_ky = id_dang_ky,
                           thong_tin = thong_tin,
                           cac_sv = cac_sv,
                           my_user = session['username'],
                           truong = session['truong'])

# student
@login_required
@app.route("/view_dang_ky_hoc", methods = ['GET','POST'])
def view_dang_ky_hoc():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT ma_dot
                FROM dot_dang_ky dk
                WHERE CURRENT_TIMESTAMP() BETWEEN dk.ngay_bat_dau AND dk.ngay_ket_thuc
                """)
    ma_dot = cur.fetchall()
    ma_dot = (('202001',),)
    ma_sinh_vien = '20002077'
    if (len(ma_dot) == 0):
        return render_template('student/dangkyhoc/view_dang_ky_hoc.html',
                           my_user = session['username'],
                           truong = session['truong'])

    ma_dot = ma_dot[0][0]
    cur.execute("""
                SELECT mhn.ma_mon
                FROM mon_hoc_nganh mhn
                WHERE mhn.ma_nganh IN (SELECT DISTINCT n.ma_nganh
                                    FROM sinh_vien_lop svl
                                    JOIN lop l ON l.ma_lop = svl.ma_lop
                                    JOIN nganh n ON n.ma_nganh = l.ma_nganh
                                    WHERE svl.ma_sinh_vien = %s);
                """, (ma_sinh_vien, ))
    ma_mon = cur.fetchall()
    ma_mon_dh = "("
    for elm in ma_mon:
        ma_mon_dh += "'" + elm[0] + "',"
    ma_mon_dh = ma_mon_dh[:-1:]
    ma_mon_dh += ")"
    
     # lay thong tin hoc ky
    cur.execute("""
                SELECT * 
                FROM hoc_ky hk
                WHERE hk.ma_hoc_ky = (SELECT ddk.ma_hoc_ky
                                    FROM dot_dang_ky ddk
                                    WHERE ddk.ma_dot = %s)
                """, (ma_dot, ))
    thong_tin_hk = cur.fetchall()
    if (len(thong_tin_hk) == 0):
        return "Error"
    thong_tin_hk = thong_tin_hk[0]
    
    cur.execute("""
            SELECT mhdk.id_dang_ky, mh.ten_mon, mh.so_tin_chi, d.thang_4, mhdk.ma_so_lop, mhdk.so_luong, mhdk.so_luong_da_dang_ky,
            CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
            FROM mon_hoc_dot_dang_ky mhdk
            LEFT JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
            LEFT JOIN (SELECT * FROM diem d WHERE d.ma_sinh_vien = '""" + ma_sinh_vien + """' ) d ON d.ma_mon = mh.ma_mon
            WHERE mhdk.ma_dot = '""" + ma_dot + """' AND mhdk.ma_mon IN """ + ma_mon_dh + """
            ORDER BY mhdk.ma_so_lop ASC;
            """)
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'thang_4', 'ma_so_lop',
                    'so_luong', 'so_luong_da_dang_ky', 'lich_hoc']
    cac_mon_dk = cur.fetchall()
    data = pd.DataFrame.from_records(cac_mon_dk, columns=column_name)
    
    data = data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if data.shape[0] == 0:
        data = ()
    else:
        data = data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi', 'thang_4',
                                'ma_so_lop', 'so_luong', 'so_luong_da_dang_ky'], group_keys=False).apply(f).reset_index()
        data = data.values.tolist()
        
    
    if request.method == 'POST':
        details = request.form
        cac_ma_dk = details['mon_hoc_dang_ky'].strip()
        
        cac_ma_dk = list(set(cac_ma_dk.split(",")))
        
        if (len(cac_ma_dk) == 0):
            return "Error"
        
        cur.execute("SELECT id_dang_ky FROM dang_ky_mon WHERE ma_sinh_vien = %s", (ma_sinh_vien, ))
        check_exits = cur.fetchall()
        id_tmp = []
        for elm in check_exits:
            id_tmp.append(elm[0])
            
        for elm in cac_ma_dk:
            if elm in id_tmp:
                cac_ma_dk.remove(elm)
        
        sql = "INSERT INTO dang_ky_mon(id_dang_ky, ma_sinh_vien) VALUES "
        for elm in cac_ma_dk:
            sql += "('" + elm + "','" + ma_sinh_vien + "'),"
        sql = sql[:-1:]
        cur.execute(sql)
        mysql.connection.commit()
        return redirect(url_for('view_dang_ky_hoc'))
        
    # cac mon da dang ky duoc
    cur.execute("""
                SELECT dkm.id_dang_ky, mh.ten_mon, mh.so_tin_chi, mhdk.ma_so_lop,
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM dang_ky_mon dkm
                JOIN mon_hoc_dot_dang_ky mhdk ON dkm.id_dang_ky = mhdk.id_dang_ky
                LEFT JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                WHERE mhdk.ma_dot = '""" + ma_dot + """' 
                AND dkm.ma_sinh_vien = '""" + ma_sinh_vien + """' 
                AND mhdk.ma_mon IN """ + ma_mon_dh + """
                ORDER BY mhdk.ma_so_lop ASC;
                """)
    column_name = ['id_dang_ky', 'ten_mon','so_tin_chi', 'ma_so_lop', 'lich_hoc']
    cac_mon_da_dk = cur.fetchall()
    sub_data = pd.DataFrame.from_records(cac_mon_da_dk, columns=column_name)
    
    sub_data = sub_data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    if sub_data.shape[0] == 0:
        sub_data = ()
    else:
        sub_data = sub_data.groupby(by=['id_dang_ky', 'ten_mon','so_tin_chi','ma_so_lop'],
                                    group_keys=False).apply(f).reset_index()
        sub_data = sub_data.values.tolist()
    
    return render_template('student/dangkyhoc/view_dang_ky_hoc.html',
                           thong_tin_hk = thong_tin_hk,
                           ma_sinh_vien = ma_sinh_vien,
                            cac_mon = data,
                            cac_mon_da_dk = sub_data,
                        ma_dot = ma_dot,
                    my_user = session['username'],
                    truong = session['truong'])

@login_required
@app.route("/form_print_dkh/<string:ma_dot>_<string:ma_sinh_vien>")
def form_print_dkh(ma_dot,ma_sinh_vien):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT ma_dot
                FROM dot_dang_ky dk
                WHERE ma_dot = %s
                """, (ma_dot, ))
    if (len(cur.fetchall()) == 0):
        return "Error"

    ma_sinh_vien = '20002077'
    
    cur.execute("""
                SELECT mhn.ma_mon
                FROM mon_hoc_nganh mhn
                WHERE mhn.ma_nganh IN (SELECT DISTINCT n.ma_nganh
                                    FROM sinh_vien_lop svl
                                    JOIN lop l ON l.ma_lop = svl.ma_lop
                                    JOIN nganh n ON n.ma_nganh = l.ma_nganh
                                    WHERE svl.ma_sinh_vien = %s);
                """, (ma_sinh_vien, ))
    ma_mon = cur.fetchall()
    ma_mon_dh = "("
    for elm in ma_mon:
        ma_mon_dh += "'" + elm[0] + "',"
    ma_mon_dh = ma_mon_dh[:-1:]
    ma_mon_dh += ")"
    
    # lay thong tin hoc ky
    cur.execute("""
                SELECT * 
                FROM hoc_ky hk
                WHERE hk.ma_hoc_ky = (SELECT ddk.ma_hoc_ky
                                    FROM dot_dang_ky ddk
                                    WHERE ddk.ma_dot = %s)
                """, (ma_dot, ))
    thong_tin_hk = cur.fetchall()
    if (len(thong_tin_hk) == 0):
        return "Error"
    thong_tin_hk = thong_tin_hk[0]
    
    # lay thong tin sinh vien
    cur.execute("""
                SELECT sv.ma_sinh_vien, sv.ho_ten, DATE_FORMAT(sv.ngay_sinh, "%d/%m/%Y"),
                CONCAT(l.ten_lop, " ", n.ten_nganh), l.nam
                FROM sinh_vien sv 
                JOIN sinh_vien_lop svl ON sv.ma_sinh_vien = sv.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                WHERE sv.ma_sinh_vien = """ + ma_sinh_vien + """
                GROUP BY sv.ma_sinh_vien
                LIMIT 1
                """)
    sinh_vien = cur.fetchall()
    if (len(sinh_vien) == 0):
        return "Error"
    sinh_vien = sinh_vien[0]
    
    # ngay thang
    cur.execute("""
                SELECT DAY(CURRENT_DATE()), MONTH(CURRENT_DATE()), YEAR(CURRENT_DATE())
                """)
    date = cur.fetchall()[0]
    
    
    # cac mon da dang ky duoc
    cur.execute("""
                SELECT dkm.id_dang_ky, mh.ma_mon, mh.ten_mon, mh.so_tin_chi, mh.so_tin_chi * lh.hoc_phi_tin_chi, 
                mhdk.ma_so_lop,
                CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                FROM dang_ky_mon dkm
                JOIN mon_hoc_dot_dang_ky mhdk ON dkm.id_dang_ky = mhdk.id_dang_ky
                JOIN mon_hoc mh ON mhdk.ma_mon = mh.ma_mon
                JOIN mon_hoc_nganh mhn ON mhn.ma_mon = mhdk.ma_mon
                JOIN sinh_vien_lop svl ON svl.ma_sinh_vien = dkm.ma_sinh_vien
                JOIN lop l ON l.ma_lop = svl.ma_lop
                JOIN nganh n ON n.ma_nganh = l.ma_nganh
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                WHERE mhdk.ma_dot = '""" + ma_dot + """' 
                AND dkm.ma_sinh_vien = '""" + ma_sinh_vien + """' 
                AND mhdk.ma_mon IN """ + ma_mon_dh + """
                GROUP BY mhdk.ma_so_lop, CONCAT("T",mhdk.thu,"(",mhdk.tiet_bat_dau,"-",mhdk.tiet_ket_thuc,")",mhdk.phong_hoc)
                ORDER BY mhdk.ma_so_lop ASC;
                """)
    column_name = ['id_dang_ky', 'ma_mon', 'ten_mon','so_tin_chi','hoc_phi', 'ma_so_lop', 'lich_hoc']
    cac_mon_da_dk = cur.fetchall()
    sub_data = pd.DataFrame.from_records(cac_mon_da_dk, columns=column_name)
    
    sub_data = sub_data.fillna(' ')
    
    def f(x):
        return pd.Series(dict(lich_hoc = "%s" % ','.join(x['lich_hoc'])))
    
    tong_tc = 0
    tong_hp = 0
    index_arr = []
    if sub_data.shape[0] == 0:
        sub_data = ()
    else:
        sub_data = sub_data.groupby(by=['id_dang_ky', 'ma_mon', 'ten_mon','so_tin_chi','hoc_phi', 'ma_so_lop'],
                                    group_keys=False).apply(f).reset_index()
        tong_tc = sub_data['so_tin_chi'].sum()
        tong_hp = sub_data['hoc_phi'].sum()
        tong_hp = round(tong_hp, -3)
        index_arr = [i for i in range(sub_data.shape[0])]
        sub_data = sub_data.values.tolist()
        
    
    
    return render_template('student/dangkyhoc/form_print_dkh.html',
                           sinh_vien = sinh_vien,
                           date = date,
                           thong_tin_hk = thong_tin_hk,
                           tong_tc = tong_tc,
                           tong_hp = tong_hp,
                           index_arr = index_arr,
                        ma_sinh_vien = ma_sinh_vien,   
                        cac_mon_da_dk = sub_data,
                        ma_dot = ma_dot,)

@login_required
@app.route("/huy_dang_ky_mon/<string:id_dang_ky>")
def huy_dang_ky_mon(id_dang_ky):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT ma_dot
                FROM dot_dang_ky dk
                WHERE CURRENT_TIMESTAMP() BETWEEN dk.ngay_bat_dau AND dk.ngay_ket_thuc
                """)
    ma_dot = cur.fetchall()
    ma_dot = (('202001',),)
    ma_sinh_vien = '20002077'
    if (len(ma_dot) == 0):
        return render_template('student/dangkyhoc/view_dang_ky_hoc.html',
                           my_user = session['username'],
                           truong = session['truong'])

    ma_dot = ma_dot[0][0]
    
    cur.execute("""
                SELECT DISTINCT mhdk.id_dang_ky
                FROM mon_hoc_dot_dang_ky mhdk
                JOIN dang_ky_mon dkm ON dkm.id_dang_ky = mhdk.id_dang_ky
                WHERE mhdk.ma_dot = %s AND mhdk.id_dang_ky = %s AND ma_sinh_vien = %s
                """, (ma_dot, id_dang_ky, ma_sinh_vien))
    id_tmp = cur.fetchall()
    if (len(id_tmp) == 0):
        return "Error"
    
    cur.execute("""
                DELETE FROM dang_ky_mon
                WHERE ma_sinh_vien = %s AND id_dang_ky = %s
                """, (ma_sinh_vien, id_dang_ky))
    mysql.connection.commit()
    return redirect(url_for('view_dang_ky_hoc'))

# -------------------------- Dang Ky Hoc -------------------------


# -------------------------- Cai dat -------------------------

@login_required
@app.route("/cai_dat")
def cai_dat():
    cur  = mysql.connection.cursor()

    cur.execute("""
                SELECT COUNT(*)
                FROM user
                """)
    so_acc = cur.fetchall()[0][0]
    
    return render_template(session['role'] + "caidat/cai_dat.html",
                           so_acc = so_acc,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/view_tk")
def view_tk():
    cur = mysql.connection.cursor()
    
    cur.execute("""
               SELECT us.id_user, us.ma_nguoi_dung, nql.ho_ten, r.role_name, us.last_login, us.register
                FROM user us
                JOIN role_user ru ON ru.id_user = us.id_user
                JOIN role r ON ru.role_id = r.role_id
                JOIN nguoi_quan_li nql ON nql.ma_nguoi_quan_li = us.ma_nguoi_dung
                WHERE us.ma_nguoi_dung LIKE '151056%'
                UNION
                SELECT us.id_user, us.ma_nguoi_dung, sv.ho_ten, r.role_name, us.last_login, us.register
                FROM user us
                JOIN role_user ru ON ru.id_user = us.id_user
                JOIN role r ON ru.role_id = r.role_id
                JOIN sinh_vien sv ON sv.ma_sinh_vien = us.ma_nguoi_dung
                WHERE us.ma_nguoi_dung NOT LIKE '151056%'
                """)
    cac_user = cur.fetchall()
    
    return render_template(session['role'] + 'caidat/view_tk.html',
                           cac_user = cac_user,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_add_tk", methods = ['GET','POST'])
def form_add_tk():
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT sv.ma_sinh_vien
                FROM sinh_vien sv
                WHERE sv.ma_sinh_vien NOT IN (
                    SELECT us.ma_nguoi_dung
                    FROM user us
                )
                """)
    cac_ma = cur.fetchall()
    
    if request.method == 'POST':
        details = request.form
        username = details['MND']
        password = hashlib.md5(details['password'].encode()).hexdigest()
        password_repeat = hashlib.md5(details['password_repeat'].encode()).hexdigest()  
        
        if password != password_repeat:
            return render_template(session['role'] + 'caidat/form_add_tk.html',
                                   my_err = 'Nhập lại mật khẩu bị sai',
                           cac_ma = cac_ma,
                           my_user = session['username'],
                           truong = session['truong'])
            
        cur.execute("""
                    INSERT INTO user(username,password,ma_nguoi_dung)
                    VALUES (%s, %s, %s)
                    """, (username, password, username))
        mysql.connection.commit()
        
        cur.execute("""
                    SELECT id_user
                    FROM user 
                    WHERE ma_nguoi_dung = %s
                    """, (username, ))
        id_user = cur.fetchall()[0][0]
        
        cur.execute("""
                    INSERT INTO role_user(id_user, role_id)
                    VALUES (%s,%s)
                    """, (id_user, 3))
        mysql.connection.commit()
        return redirect(url_for('view_tk'))
    
    return render_template(session['role'] + 'caidat/form_add_tk.html',
                           cac_ma = cac_ma,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_add_tk_qt", methods=['GET','POST'])
def form_add_tk_qt():
    cur = mysql.connection.cursor()
    cac_quyen = {
        'Admin':1,
        'Người quản lý':2
    }
    
    if request.method == 'POST':
        details = request.form
        username = details['taikhoan']
        ten_tk = details['ten_tk']
        loai = cac_quyen[details['TYPE'].strip()]
        password = hashlib.md5(details['password'].encode()).hexdigest()
        password_repeat = hashlib.md5(details['password_repeat'].encode()).hexdigest()  
        
        if not username.startswith("151056"):
            return render_template(session['role'] + "caidat/form_add_tk_qt.html",
                                   my_err = "Mã người quản lý phải bắt đầu bằng 151056 !",
                           my_user = session['username'],
                           truong = session['truong'])
        
        cur.execute("""
                    SELECT ma_nguoi_quan_li
                    FROM nguoi_quan_li
                    WHERE ma_nguoi_quan_li = %s
                    """, (username, ))
        if len(cur.fetchall()) != 0:
            return render_template(session['role'] + "caidat/form_add_tk_qt.html",
                                   my_err = "Mã người quản lý đã tồn tại !",
                           my_user = session['username'],
                           truong = session['truong'])
            
        if password != password_repeat:
            return render_template(session['role'] + "caidat/form_add_tk_qt.html",
                                   my_err = "Mật khẩu nhập lại không đúng",
                           my_user = session['username'],
                           truong = session['truong'])
            
        cur.execute("""
                    INSERT INTO nguoi_quan_li(ma_nguoi_quan_li, ho_ten)
                    VALUES (%s, %s)
                    """, (username, ten_tk))
        mysql.connection.commit()
        
        cur.execute("""
                    INSERT INTO user(username,password,ma_nguoi_dung)
                    VALUES (%s, %s, %s)
                    """, (username, password, username))
        mysql.connection.commit()
        
        cur.execute("""
                    SELECT id_user
                    FROM user 
                    WHERE ma_nguoi_dung = %s
                    """, (username, ))
        id_user = cur.fetchall()[0][0]
        
        cur.execute("""
                    INSERT INTO role_user(id_user, role_id)
                    VALUES (%s,%s)
                    """, (id_user, loai))
        mysql.connection.commit()
        return redirect(url_for('view_tk'))
        
    return render_template(session['role'] + "caidat/form_add_tk_qt.html",
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_chinh_sua_mk/<string:id_user>", methods=['GET','POST'])
def form_chinh_sua_mk(id_user):
    if request.method == 'POST':
        details = request.form
        password = hashlib.md5(details['password'].encode()).hexdigest()
        password_repeat = hashlib.md5(details['password_repeat'].encode()).hexdigest()  
        
        if password != password_repeat:
            return render_template(session['role'] + 'caidat/form_chinh_sua_mk.html',
                                   id_user = id_user,
                                   my_err = "Mật khẩu nhập lại không đúng",
                           my_user = session['username'],
                           truong = session['truong'])
        
        cur = mysql.connection.cursor()
        cur.execute("""
                    UPDATE user
                    SET password = %s
                    WHERE id_user = %s
                    """, (password, id_user))
        mysql.connection.commit()
        return redirect(url_for('view_tk'))    
        
    return render_template(session['role'] + 'caidat/form_chinh_sua_mk.html',
                           id_user = id_user,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_add_tk_upload_file", methods=['GET','POST'])
def form_add_tk_upload_file():
    if request.method == 'POST':
        data_file = request.files['FileDataUpload']
        if data_file.filename != '':
            if data_file.filename.split(".")[-1] not in ['xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_tk_upload_file"))
            filename = "TMP_" + data_file.filename 
            pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
            data_file.save(pathToFile)
            return redirect(url_for("form_add_tk_upload_process", filename=filename))
        return redirect(url_for("form_add_tk_upload_file"))
    return render_template(session['role'] +'caidat/form_add_tk_upload_file.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_add_tk_upload_process/<string:filename>", methods=['GET','POST'])
def form_add_tk_upload_process(filename):
    pathToFile = app.config['UPLOAD_FOLDER'] + "/" + filename
    
    default_tag_column = ['username', 'ten_nguoi_dung', 'password', 'role_id']
    
    default_name_column = ['Tài Khoản', 'Tên Người Dùng', 'Mật Khẩu', 'Loại quyền']
    
    data_acc = pd.read_excel(pathToFile)
    data_column = list(data_acc.columns)
    
    if (len(data_column) > len(default_tag_column)) or len(data_column)  < 4:
        return "Error"
    
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        details = request.form
        column_link = [details[col] for col in data_column]
        column_match = [default_name_column.index(elm) for elm in column_link]
        
        if (len(set(column_match)) != len(column_link)):
            return "Error"
        
        if (len(column_match) != 4):
            return "Error"
        
        # lọc các mã quản lý để xử lý
        data_acc = data_acc.fillna(" ")
        data_mng = data_acc.copy(True)
        data_mng[data_column[column_match.index(0)]] = data_mng[data_column[column_match.index(0)]].astype(str)
        data_mng = data_mng.loc[data_mng[data_column[column_match.index(0)]].str.startswith('151056')]
        # lấy index của những record là của người quản lý
        index_drop = list(data_mng.index)
        
        for elm in index_drop:
            data_acc = data_acc.drop(elm)
        data_acc = data_acc.drop(data_column[column_match.index(1)], axis=1)
        data_acc = data_acc.reset_index()
        
        # Kiểm tra xem mã nguoi quan ly có tồn tại không
        # nếu tồn tại thì ko cho nhập
        tmp = tuple(set(data_mng[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_nguoi_quan_li FROM nguoi_quan_li WHERE ma_nguoi_quan_li = %s", tmp)
        else:
            new_tmp = ["\"" + text +"\"" for text in tmp]
            cur.execute("SELECT ma_nguoi_quan_li FROM nguoi_quan_li WHERE ma_nguoi_quan_li IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != 0):
            return "Error"
        
        # kiểm tra mã quyền có trong khoảng quy định ko 1 - 3
        tmp = tuple(set(data_mng[data_column[column_match.index(3)]]))
        tmp = [int(elm) for elm in tmp]
        if max(tmp) > 3 or min(tmp) < 0:
            return "Error 1"
        
        # xử lý dữ liệu người quản lý
        # tách cột để cho vào bảng user
        for index in list(data_mng.index):
            cur.execute("""
                        INSERT INTO nguoi_quan_li(ma_nguoi_quan_li, ho_ten)
                        VALUES (%s, %s)
                        """, (
                            data_mng[data_column[column_match.index(0)]][index],
                            data_mng[data_column[column_match.index(1)]][index]
                        ))
            mysql.connection.commit()
            
            cur.execute("""
                        INSERT INTO user(username, password, ma_nguoi_dung)
                        VALUES (%s, %s, %s)
                        """, (
                            data_mng[data_column[column_match.index(0)]][index],
                            data_mng[data_column[column_match.index(2)]][index],
                            data_mng[data_column[column_match.index(0)]][index]
                        ))
            mysql.connection.commit()
            
            cur.execute("""
                        SELECT id_user
                        FROM user
                        WHERE username = %s
                        """, (
                            data_mng[data_column[column_match.index(0)]][index],
                        ))
            id_user = cur.fetchall()[0][0]
            
            cur.execute("""
                        INSERT INTO role_user(id_user, role_id)
                        VALUES (%s, %s)
                        """, (id_user,
                              data_mng[data_column[column_match.index(3)]][index]
                              ))
            mysql.connection.commit()
        
        
        # Kiểm tra xem mã sinh viên có tồn tại không
        # nếu tồn tại thì ko cho nhập
        tmp = tuple(set(data_acc[data_column[column_match.index(0)]]))
        if len(tmp) == 1:
            cur.execute("SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien = %s", tmp)
        else:
            new_tmp = ["\"" + str(text) +"\"" for text in tmp]
            cur.execute("SELECT ma_sinh_vien FROM sinh_vien WHERE ma_sinh_vien IN (" + ", ".join(new_tmp) + ")")
        data_tuple = cur.fetchall()
        data_tmp_take = []
        for elm in data_tuple:
            data_tmp_take.append(elm[0])
        if (len(data_tmp_take) != len(tmp)):
            return "Error 1"
        
        # Xử lý dữ liệu cho sinh viên
        for index_row in range(data_acc.shape[0]):
            cur.execute("""
                        INSERT INTO user(username, password, ma_nguoi_dung)
                        VALUES (%s, %s, %s)
                        """, (
                            data_acc[data_column[column_match.index(0)]][index_row],
                            data_acc[data_column[column_match.index(2)]][index_row],
                            data_acc[data_column[column_match.index(0)]][index_row]
                        ))
            mysql.connection.commit()
            
            cur.execute("""
                        SELECT id_user
                        FROM user
                        WHERE username = %s
                        """, (
                            data_acc[data_column[column_match.index(0)]][index_row],
                        ))
            id_user = cur.fetchall()[0][0]
            
            cur.execute("""
                        INSERT INTO role_user(id_user, role_id)
                        VALUES (%s, %s)
                        """, (id_user,
                              3
                              ))
            mysql.connection.commit()        
        os.remove(pathToFile)
        return redirect(url_for('view_tk'))
    
    return render_template(session['role'] + 'caidat/form_add_tk_upload_process.html',
                           my_user = session['username'],
                           truong = session['truong'],
                           filename = filename,
                           name_column = default_name_column,
                           index_column = data_column)

@login_required
@app.route("/cai_dat/form_view_truong/<string:can_edit>", methods=['GET','POST'])
def form_view_truong(can_edit):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT *
                FROM truong
                LIMIT 1
                """)
    data_truong = cur.fetchall()[0]
    
    if request.method == 'POST':
        details = request.form
        TenTH = details['TenTH']
        NgayThanhLap = details['NgayThanhLap']
        DIACHI = details['DIACHI']
        
        image_profile = request.files['ImageProfileUpload']
        pathToImage = data_truong[3]
        if image_profile.filename != "":
            ID_image = "logo_web"
            filename = 'favicon' + "." + secure_filename(image_profile.filename).split(".")[1]
            pathToImage = app.config['UPLOAD_FOLDER_IMG'] + "/" + filename
            image_profile.save(pathToImage)
            take_image_to_save(ID_image, pathToImage)
            pathToImage = "/".join(pathToImage.split("/")[1::])
        
        cur.execute("""
                    UPDATE truong
                    SET ten_truong = %s, dia_chi = %s, logo_path = %s, ngay_thanh_lap = %s
                    WHERE ID = %s
                    """,(TenTH, DIACHI, pathToImage, NgayThanhLap, 1))
        mysql.connection.commit()
        
        cur.execute("""
                    SELECT * 
                    FROM truong
                    """)
        session['truong'] = cur.fetchall()[0]
        return redirect(url_for('cai_dat'))
        
    if can_edit == 'E':
        return render_template(session['role'] +'caidat/form_view_truong.html', 
                           mode = '',
                           data_truong = data_truong,
                           my_user = session['username'],
                           truong = session['truong'])
        
    return render_template(session['role'] + 'caidat/form_view_truong.html',
                           mode = 'disabled',
                           data_truong = data_truong,
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/cai_dat/form_chinh_sua_mk_one", methods=['GET','POST'])
def form_chinh_sua_mk_one():
    if request.method == 'POST':
        details = request.form
        password = hashlib.md5(details['password'].encode()).hexdigest()
        password_repeat = hashlib.md5(details['password_repeat'].encode()).hexdigest()  
        
        if password != password_repeat:
            return render_template(session['role'] + 'caidat/form_chinh_sua_mk_one.html',
                                   my_err = "Mật khẩu nhập lại không đúng",
                           my_user = session['username'],
                           truong = session['truong'])
        
        cur = mysql.connection.cursor()
        cur.execute("""
                    UPDATE user
                    SET password = %s
                    WHERE id_user = %s
                    """, (password, session['username'][0]))
        mysql.connection.commit()
        return redirect(url_for('cai_dat'))  
        
    return render_template(session['role'] + 'caidat/form_chinh_sua_mk_one.html',
                           my_user = session['username'],
                           truong = session['truong'])

@login_required
@app.route("/delete_account/<string:id_user>")
def delete_account(id_user):
    if session['role_id'] != 1:
        return "Error"
    
    cur = mysql.connection.cursor()
    
    cur.execute("""
                DELETE FROM role_user
                WHERE id_user = %s
                """, (id_user, ))
    mysql.connection.commit()
    
    cur.execute("""
                DELETE FROM user
                WHERE id_user = %s
                """, (id_user, ))
    mysql.connection.commit()
    return redirect(url_for('view_tk'))

# -------------------------- Cai dat -------------------------
def take_image_to_save(id_image, path_to_img):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM image_data""")
    img_data = cur.fetchall()
    change_path = False
    
    path_to_img = "/".join(path_to_img.split("/")[1::])
    
    for data in img_data:
        if id_image in data:
            change_path = True
            if os.path.exists(data[1]):
                os.remove(data[1])
            break
    
    if change_path:
        sql = """
            UPDATE image_data
            SET path_to_image = %s
            WHERE id_image = %s"""
        val = (id_image, path_to_img)
        cur.execute(sql,val)
        mysql.connection.commit()
        return True
    
    sql = """
        INSERT INTO image_data (id_image, path_to_image) 
        VALUES (%s, %s)"""
    val = (id_image, path_to_img)
    cur.execute(sql,val)
    mysql.connection.commit()
    return True
    