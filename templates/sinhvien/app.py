from flask import Flask, render_template, request, redirect, url_for, session, json, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'duongnam'
@app.route("/login")
def login():
    return render_template('general/login.html')  

@app.route("/forgot")
def forgot():
    return render_template('general/forgot.html')  

@app.route("/base")
def base():
    return render_template('base.html')  
@app.route("/")
@app.route("/bang_sinh_vien")
def bang_sinh_vien():
    return render_template('sinhvien/bang_sinh_vien.html')  
@app.route("/form_view_update_sinh_vien")
def form_view_update_sinh_vien():
    return render_template('sinhvien/form_view_update_sinh_vien.html')
@app.route("/form_add_sinh_vien_upload_file")
def form_add_sinh_vien_upload_file():
    return render_template('sinhvien/form_add_sinh_vien_upload_file.html')
@app.route("/form_add_sinh_vien")
def form_add_sinh_vien():
    return render_template('sinhvien/form_add_sinh_vien.html') 
@app.route("/form_infomation_one_sinh_vien")
def form_infomation_one_sinh_vien():
    return render_template('sinhvien/form_infomation_one_sinh_vien.html')

@app.route("/table_print_sinh_vien")
def table_print_sinh_vien():
    return render_template('sinhvien/table_print_sinh_vien.html')

@app.route("/view_all_khoa")
def view_all_khoa():
    return render_template('khoa/view_all_khoa.html')  

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'quan_ly_nhan_vien'