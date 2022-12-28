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
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                JOIN lop l ON l.ma_nganh = n.ma_nganh
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
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                JOIN lop l ON l.ma_nganh = n.ma_nganh
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
                JOIN khoa k ON k.ma_khoa = n.ma_khoa
                JOIN loai_he lh ON lh.ma_he = n.ma_he
                JOIN lop l ON l.ma_nganh = n.ma_nganh
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
@app.route("/table_nganh/view_nganh/<string:ma_nganh>")
def view_nganh(ma_nganh):
    return "Error"

@app.route("/table_nganh/form_add_nganh")
def form_add_nganh():
    return render_template(session['role'] + 'nganh/form_add_nganh.html',
                           my_user = session['username'],
                           truong = session['truong']) 

@app.route("/table_nganh/form_update_nganh/<string:ma_nganh>")
def form_update_nganh(ma_nganh):
    cur = mysql.connection.cursor()
    
    cur.execute("""
                SELECT *
                FROM nganh n
                WHERE n.is_delete = 0 AND n.ma_nganh = %s
                """, (ma_nganh, ))
    nganh = cur.fetchall()
    
    return render_template(session['role'] + 'nganh/form_update_nganh.html',
                           nganh = nganh,
                           my_user = session['username'],
                           truong = session['truong'])

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
            if data_file.filename.split(".")[-1] not in ['txt', 'xlsx', 'csv', 'xls', 'xlsm']:
                return redirect(url_for("form_add_data_employees_upload_file"))
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
    
    data_sv = pd.read_excel(pathToFile)
    data_column = list(data_sv.columns)
    
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
        tmp = tuple(set(data_sv[data_column[column_match.index(13)]]))
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
        msv_ma_lop = data_sv[[data_column[column_match.index(0)], data_column[column_match.index(13)]]]
        col_ma_lop = [data_column[column_match.index(0)], data_column[column_match.index(13)]]
        data_sv = data_sv.drop(data_column[column_match.index(13)], axis=1)
        data_column.remove(data_column[column_match.index(13)])
        column_match.remove(13)
        
        sql = "INSERT INTO `sinh_vien` ("
        for index in column_match:
            sql += default_tag_column[index] + ","
        sql += 'created_by'
        sql += ") VALUES "
        for index_row in range(data_sv.shape[0]):
            sql += "("
            for col in data_column:
                sql +=  "\"" + str(data_sv[col][index_row]) + "\"" + ","
            sql += "\"" + session['username'][6] + "\""
            sql += "),"
        sql = sql[:-1:]    
        cur.execute(sql)
        
        sql = "INSERT INTO `sinh_vien_lop` ( ma_sinh_vien, ma_lop ) VALUES "
        for index_row in range(msv_ma_lop.shape[0]):
            sql += "("
            for col in col_ma_lop:
                sql += "\"" + str(msv_ma_lop[col][index_row]) + "\"" + ","
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
    