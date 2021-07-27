import configparser
import os
import random
import re
import requests
import smtplib
# import ssl

from datetime import datetime
from email.mime.text import MIMEText

from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, request, session, escape
from flask.helpers import send_file
from flask.json import jsonify
from werkzeug.utils import secure_filename

from dao.buy import DaoBuy
from dao.category import DaoCategory
from dao.event import DaoEvent
from dao.menu import DaoMenu
from dao.notice import DaoNotice
from dao.owner import DaoOwner
from dao.sys_ans import DaoSysAns
from dao.sys_ques import DaoSysQues
from dao.voc import DaoVoc

daoBuy = DaoBuy()
daoCategory = DaoCategory()
daoEvent = DaoEvent()
daoMenu = DaoMenu()
daoNotice = DaoNotice()
daoOwner = DaoOwner()
daoSysAns = DaoSysAns()
daoSysQues = DaoSysQues()
daoVoc = DaoVoc()

config = configparser.ConfigParser()
config.read("config.ini")

DIR_UPLOAD, KakaoAK, HOST, PORT, MAIL_ID, MAIL_PW = config['DIR_UPLOAD']['DIR_UPLOAD'], config['Kakao']['KakaoAK'], config['network']['HOST'], config['network']['PORT'], config['mail']['ID'], config['mail']['PW']

app = Flask(__name__, static_url_path="", static_folder="static/")
app.secret_key = os.urandom(24)


@app.route('/login')
def main():
    return redirect('login.html')


##################   register ######################

@app.route('/register', methods=['POST'])
def register():
    owner_name = request.form["owner_name"]
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]
    owner_str_name = request.form["owner_str_name"]
    owner_str_num = request.form["owner_str_num"].replace("-", "")
    owner_str_tel = request.form["owner_str_tel"]

    owner_add1 = request.form["owner_add1"]
    owner_add2 = request.form["owner_add2"]

    owner_seq = daoOwner.owner_seq_gen()

    logo = request.files["logo"]
    attach_path, attach_file = saveFile(logo, owner_seq)

    try:
        if daoOwner.insert(owner_seq, owner_name, owner_id, owner_pwd, owner_str_name, owner_str_num, owner_str_tel, owner_add1, owner_add2, attach_path, attach_file):
            return redirect("login.html")
    except Exception as e:
        print(e)
    return '<script>alert("회원가입에 실패하였습니다.");history.back()</script>'


@app.route('/id_check.ajax', methods=['POST'])
def id_check_ajax():
    owner_id = request.form['owner_id']
    return jsonify({'cnt': daoOwner.id_check(owner_id)})


@app.route('/owner_str_num_check.ajax', methods=['POST'])
def owner_str_num_check_ajax():
    owner_str_num = request.form['owner_str_num'].replace('-', '')
    return jsonify({'cnt': daoOwner.owner_str_num_check(owner_str_num)})


@app.route('/login_form', methods=['POST'])
def login():
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]
    owner = daoOwner.select_login(owner_id, owner_pwd)

    if owner:
        del (owner['owner_pwd'])
        session['owner'] = owner
        return redirect('dashboard')
    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login.html')


@app.route('/temp_pwd_send.ajax', methods=['POST'])
def temp_pwd_send_ajax():
    owner_str_num = request.form["owner_str_num"].replace("-", "")
    owner_id = request.form["owner_id"]

    try:
        owner = daoOwner.id_check_list(owner_id, owner_str_num)
        pwd_list = ['!', '@', '#', '$', '%', '^', '&', '+', '=', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                    'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                    'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        regPwd = '.*(?=^.{8,15}$)(?=.*\d)(?=.*[a-zA-Z])(?=.*[!@#$%^&+=]).*'
        match = None

        while True:
            temp = ""
            for _ in range(15):
                match = re.match(regPwd, temp)
                if match:
                    break
                temp += pwd_list[random.randint(0, 70)]
            if match:
                break

        s = smtplib.SMTP('smtp.gmail.com', 587)  # 세션 생성
        s.starttls()  # TLS 보안 시작
        s.login(MAIL_ID, MAIL_PW)  # 로그인 인증

        # 보낼 메시지 설정
        title = "죠기요 임시 비밀번호 발급"  # 메일 제목
        content = owner["owner_name"] + "님의 임시 비밀번호는 " + temp + " 입니다. \n로그인 후에 비밀번호를 변경하여 사용하시기 바랍니다."  # 메일 내용

        msg = MIMEText(content)
        msg['Subject'] = title

        s.sendmail(MAIL_ID,  # 메일 보내기
                   owner_id,
                   msg.as_string())

        s.quit()  # 세션 종료

        cnt = daoOwner.update_pwd(temp, owner_id)
        return str(cnt)

    except Exception as e:
        print(e)
        return '0'


##################   dashboard   ######################

@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])

    if escape(session['owner']['admin_yn']) == 'Y' or escape(session['owner']['admin_yn']) == 'y':
        return render_template('web/dashboard/admin_dashboard.html',
                               dayschart=daoOwner.daysChart(30),
                               monthschart=daoOwner.monthsChart(6),
                               yearschart=daoOwner.monthsChart(12),
                               title="JYOGIYO")

    thismonth = datetime.now().strftime("%Y-%m")
    lastmonth = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m")

    return render_template('web/dashboard/owner_dashboard.html',
                           menuCntChart_this=daoMenu.menuCntChart(owner_seq, thismonth),
                           menuCntChart_last=daoMenu.menuCntChart(owner_seq, lastmonth),
                           menuSalesChart_this=daoMenu.menuSalesChart(owner_seq, thismonth),
                           menuSalesChart_last=daoMenu.menuSalesChart(owner_seq, lastmonth),
                           salesChart=daoMenu.salesChart(owner_seq, 12),
                           title=f"{escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/account_manage')
def account_manage():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']["owner_seq"])
    owner = daoOwner.select(owner_seq)
    if owner and owner['owner_str_num']:
        owner_str_num = list(owner['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        owner['owner_str_num'] = ''.join(owner_str_num)
    return render_template('web/account/account_manage.html', owner=owner, title=f"정보 수정 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/account_show')
def account_show():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']["owner_seq"])
    owner = daoOwner.select(owner_seq)
    if owner and owner['owner_str_num']:
        owner_str_num = list(owner['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        owner['owner_str_num'] = ''.join(owner_str_num)
    return render_template('web/account/account_show.html', owner=owner, title=f"마이페이지 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/account_mod_form', methods=["POST"])
def account_mod_form():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']["owner_seq"])
    owner_name = request.form["owner_name"]
    owner_pwd = request.form["owner_pwd"]
    owner_str_name = request.form["owner_str_name"]
    owner_str_tel = request.form["owner_str_tel"]
    owner_add1 = request.form["owner_add1"]
    owner_add2 = request.form["owner_add2"]
    logo_path = request.form["logo_path"]
    logo_file = request.form["logo_file"]

    logo = request.files["logo"]
    if logo:
        logo_path, logo_file = saveFile(logo)

    try:
        if daoOwner.update(owner_name, owner_pwd, owner_str_name, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file, owner_seq):
            owner = daoOwner.select(owner_seq)
            del (owner['owner_pwd'])
            session['owner'] = owner
            return "<script>alert('정보가 수정되었습니다.');location.href='account_show'</script>"
    except Exception as e:
        print(e)
    return "<script>alert('정보가 수정되었습니다.');history.back()</script>"


##################   notice   ######################

@app.route('/noti_list')
def noti_list():
    if 'owner' not in session:
        return redirect('login.html')
    list = daoNotice.selectlist()
    len_list = len(list)
    return render_template('web/notice/noti_list.html', list=list,len_list=len_list,
                           title=f"공지사항 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/noti_detail')
def noti_detail():
    if 'owner' not in session:
        return redirect('login.html')

    noti_seq = request.args.get('noti_seq')
    obj = daoNotice.select(noti_seq)
    return render_template('web/notice/noti_detail.html', noti=obj,
                           title=f"공지사항 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/noti_add', methods=['POST'])
def noti_add():
    if 'owner' not in session:
        return redirect('login.html')

    owner_seq = escape(session['owner']['owner_seq'])
    noti_title = request.form['noti_title']
    noti_content = request.form['noti_content']

    attach_path = ""
    attach_file = ""

    noti_file = request.files['noti_file']
    if noti_file:
        attach_path, attach_file = saveFile(noti_file)

    try:
        cnt = daoNotice.insert(noti_title, noti_content, attach_path, attach_file, owner_seq)
        if cnt:
            return redirect('noti_list')
    except Exception as e:
        print(e)

    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route('/noti_mod', methods=['POST'])
def noti_mod():
    if 'owner' not in session:
        return redirect('login.html')
    noti_seq = request.form['noti_seq']
    noti_title = request.form['noti_title']
    noti_content = request.form['noti_content']
    owner_seq = escape(session['owner']["owner_seq"])

    noti_file = request.files['noti_file']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']

    if noti_file:
        attach_path, attach_file = saveFile(noti_file)

    cnt = daoNotice.update(noti_seq, noti_title, noti_content, attach_path, attach_file, owner_seq)

    if cnt:
        return redirect("noti_detail?noti_seq=" + noti_seq)
    return '<script>alert("공지사항 수정에 실패하였습니다.");history.back()</script>'


@app.route('/noti_del')
def noti_del():
    if 'owner' not in session:
        return redirect('login.html')
    admin_yn = escape(session['owner']['admin_yn'])
    noti_seq = request.args.get('noti_seq')

    
    if admin_yn == "y" or admin_yn=="Y" :
        try:
            cnt = daoNotice.delete(noti_seq)
            if cnt:
                return redirect('noti_list')
        except Exception as e:
            print(e)
        return '<script>alert("공지사항 삭제에 실패하였습니다.");history.back()</script>'
    else :
        return '<script>alert("권한이 없습니다.");history.back()</script>'
        


@app.route("/noti_del_img.ajax", methods=['POST'])
def noti_del_img():
    noti_seq = request.form['noti_seq']
    cnt = daoNotice.del_img(noti_seq)
    print('cnt', cnt)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


##################   category   ######################

@app.route('/cate_list')
def cate_list():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    list = daoCategory.selectAll(owner_seq)

    return render_template('web/category/cate_list.html', list=list, title=f"카테고리 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/cate_detail')
def cate_detail():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    cate_seq = request.args.get('cate_seq')
    obj = daoCategory.select(owner_seq, cate_seq)
    return render_template('web/category/cate_detail.html', cate=obj, title=f"카테고리 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/cate_add', methods=['POST'])
def cate_add():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    cate_name = request.form['cate_name']
    cate_content = request.form['cate_content']
    cate_display_yn = request.form['cate_display_yn']
    attach_path, attach_file = '', ''

    cate_file = request.files['cate_file']
    if cate_file:
        attach_path, attach_file = saveFile(cate_file)

    try:
        cnt = daoCategory.myinsert(owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file)
        if cnt:
            return redirect('cate_list')
    except Exception as e:
        print(e)
    return '<script>alert("카테고리 작성에 실패하였습니다.");history.back()</script>'


@app.route('/cate_mod', methods=['POST'])
def cate_mod():
    if 'owner' not in session:
        return redirect('login.html')
    cate_seq = request.form['cate_seq']
    owner_seq = escape(session['owner']['owner_seq'])
    cate_name = request.form['cate_name']
    cate_content = request.form['cate_content']
    cate_display_yn = request.form['cate_display_yn']

    cate_file = request.files['cate_file']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']
    print(cate_seq)

    if attach_file == 'None':
        attach_file = ""
        attach_path = ""

    if cate_file:
        attach_path, attach_file = saveFile(cate_file)

    cnt = daoCategory.myupdate(cate_seq, owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file, None, owner_seq, None, owner_seq)

    if cnt:
        return redirect("cate_detail?cate_seq=" + cate_seq)
    return '<script>alert("수정에 실패하였습니다.");history.back()</script>'


@app.route("/cate_del_img.ajax", methods=['POST'])
def cate_del_img():
    cate_seq = request.form['cate_seq']
    cnt = daoCategory.del_img(cate_seq)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


##################     menu     ######################
@app.route('/menu_list')
def menu_list():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    menu_list = daoMenu.selectAll(owner_seq)
    categoryList = daoCategory.selectYList(owner_seq)
    return render_template('web/menu/menu_list.html', menu_list=menu_list, categoryList=categoryList, title=f"메뉴 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/multi_menu_add')
def multi_menu_add():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    categoryList = daoCategory.selectYList(owner_seq)
    return render_template('web/menu/multi_menu_add.html', categoryList=categoryList, title=f"여러 메뉴 추가 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/multi_menu_add_form', methods=['POST'])
def multi_menu_add_form():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    req = dict(request.form)

    insertList = list()
    insertDictList = list()

    for key in req:
        num = key.split('_')[-1]
        if num not in insertList:
            insertList.append(num)
            temp = dict()
            temp['cate_seq'] = req['cateseq_' + num]
            temp['menu_name'] = req['menuname_' + num]
            temp['menu_price'] = req['menu_price_' + num]
            temp['menu_content'] = req['menu_content_' + num]
            temp['attach_path'], temp['attach_file'] = saveFile(request.files['file_' + num])
            temp['menu_display_yn'] = req['menu_display_yn_' + num]
            insertDictList.append(temp)

    try:
        cnt = daoMenu.multiInsert(owner_seq, insertDictList)
        return f"<script>alert('{cnt}개 자료가 추가되었습니다.');location.href='menu_list'</script>"
    except Exception as e:
        print(e)

    return "<script>alert('추가에 실패하였습니다.');history.back()</script>"


@app.route('/menu_detail')
def menu_detail():
    if 'owner' not in session:
        return redirect('login.html')
    menu_seq = request.args.get('menu_seq')
    owner_seq = escape(session['owner']['owner_seq'])
    menu = daoMenu.select(menu_seq, owner_seq)
    if menu:
        categoryList = daoCategory.selectYList(owner_seq)
        return render_template('web/menu/menu_detail.html', menu=menu, categoryList=categoryList, title=f"메뉴 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")
    return '<script>alert("권한이 없습니다.");history.back()</script>'


@app.route('/menu_add_form', methods=['POST'])
def menu_add_form():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    cate_seq = request.form['cate_seq']
    menu_name = request.form['menu_name']
    menu_price = request.form['menu_price']
    menu_content = request.form['menu_content']
    menu_display_yn = request.form['menu_display_yn']
    attach_path = ''
    attach_file = ''

    file = request.files['file']
    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if daoMenu.insert(owner_seq, cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file):
            return "<script>alert('성공적으로 추가되었습니다.');location.href='menu_list'</script>"
    except Exception as e:
        print(e)

    return "<script>alert('추가에 실패하였습니다.');history.back()</script>"


@app.route('/menu_mod_form', methods=['POST'])
def menu_mod_form():
    if 'owner' not in session:
        return redirect('login.html')
    menu_seq = request.form['menu_seq']
    owner_seq = escape(session['owner']['owner_seq'])
    cate_seq = request.form['cate_seq']
    menu_name = request.form['menu_name']
    menu_price = request.form['menu_price']
    menu_content = request.form['menu_content']
    menu_display_yn = request.form['menu_display_yn']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']

    file = request.files['file']
    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if daoMenu.update(cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file, owner_seq, menu_seq):
            return f"<script>alert('성공적으로 수정되었습니다.');location.href='menu_detail?menu_seq={menu_seq}'</script>"
    except Exception as e:
        print(e)

    return "<script>alert('수정에 실패하였습니다.');history.back()</script>"


##################    event     ######################  
@app.route('/event_list')
def event_list():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    list = daoEvent.selectAll(owner_seq)
    return render_template('web/event/event_list.html', list=list, title=f"이벤트 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/event_detail')
def event_detail():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    event_seq = request.args.get('event_seq')
    obj = daoEvent.select(owner_seq, event_seq)
    return render_template('web/event/event_detail.html', event=obj, title=f"이벤트 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/event_addact', methods=['POST'])
def event_addact():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    event_seq = request.form["event_seq"]
    event_title = request.form["event_title"]
    event_content = request.form["event_content"]
    event_start = request.form["event_start"]
    event_end = request.form["event_end"]
    attach_path = ""
    attach_file = ""

    event_file = request.files['event_file']
    if event_file:
        attach_path, attach_file = saveFile(event_file)
    try:
        cnt = daoEvent.insert(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, owner_seq, None, owner_seq)
        if cnt:
            return redirect('event_list')
    except Exception as e:
        print(e)
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route('/event_modact', methods=['POST'])
def event_modact():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    event_seq = request.form["event_seq"]
    event_title = request.form["event_title"]
    event_content = request.form["event_content"]
    event_start = request.form["event_start"]
    event_end = request.form["event_end"]
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']
    event_file = request.files['event_file']

    if attach_file == 'None':
        attach_path = ""
        attach_file = ""

    if event_file:
        attach_path, attach_file = saveFile(event_file)

    try:
        cnt = daoEvent.update(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, owner_seq, None, owner_seq)
        if cnt:
            return f'<script>location.href="event_detail?owner_seq={owner_seq}&event_seq={event_seq}"</script>'
    except Exception as e:
        print(e)
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route("/event_delact")
def event_delact():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = request.args.get("owner_seq")
    event_seq = request.args.get("event_seq")
    try:
        cnt = daoEvent.delete(owner_seq, event_seq)
        if cnt:
            return redirect('event_list')
    except Exception as e:
        print(e)
    return '<script>alert("진행중인 이벤트입니다.");history.back()</script>'


@app.route("/event_del.ajax", methods=['POST'])
def event_del_img():
    owner_seq = request.form['owner_seq']
    event_seq = request.form['event_seq']
    cnt = daoEvent.del_img(owner_seq, event_seq)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


##################    sys_qna     ######################

@app.route('/sys_ques_list')
def sys_ques_list():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])
    list = daoSysQues.selectAll(owner_seq)
    return render_template('web/sys_ques/sys_ques_list.html', list=list, enumerate=enumerate, title=f"시스템 문의사항 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO", len=len)


@app.route('/sys_ques_detail')
def sys_ques_detail():
    if 'owner' not in session:
        return redirect('login.html')

    sys_ques_seq = request.args.get('sys_ques_seq')
    ques = daoSysQues.select(sys_ques_seq)
    reply = daoSysAns.select(sys_ques_seq)
    return render_template('web/sys_ques/sys_ques_detail.html', ques=ques, reply=reply, title=f"시스템 문의사항 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/sys_ques_add', methods=['POST'])
def sys_ques_add():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])

    sys_ques_title = request.form["title"]
    sys_ques_content = request.form["content"]
    sys_ques_display_yn = request.form["display_yn"]
    file = request.files['file']

    attach_path = ""
    attach_file = ""

    if file:
        attach_path, attach_file = saveFile(file)
        print("file O")
    else:
        print("file X")

    print(attach_path)
    print(attach_file)
    try:
        if daoSysQues.insert(owner_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, "", owner_seq, "", owner_seq):
            return "<script>alert('성공적으로 추가되었습니다.');location.href='sys_ques_list'</script>"
    except Exception as e:
        print(e)

    return "<script>alert('추가에 실패하였습니다.');history.back()</script>"


@app.route('/sys_ques_mod', methods=['POST'])
def sys_ques_mod():
    if 'owner' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner']['owner_seq'])

    sys_ques_seq = request.form["sys_ques_seq"]
    sys_ques_title = request.form["title"]
    sys_ques_content = request.form["content"]
    sys_ques_display_yn = request.form["display_yn"]
    file = request.files["file"]
    attach_path = request.form["attach_path"]
    attach_file = request.form["attach_file"]

    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if daoSysQues.update(sys_ques_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, "", owner_seq, "", owner_seq):
            return f"<script>alert('성공적으로 수정되었습니다.');location.href='sys_ques_detail?sys_ques_seq={sys_ques_seq}'</script>"
    except Exception as e:
        print(e)


#     return redirect(url_for('sys_ques_detail', sys_ques_seq=sys_ques_seq))

@app.route('/sys_ques_del.ajax', methods=['POST'])
def sys_ques_del():
    if 'owner' not in session:
        return redirect('login.html')
    sys_ques_seq = request.form['sys_ques_seq']

    daoSysAns.delete(sys_ques_seq)
    cnt = daoSysQues.delete(sys_ques_seq)

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


@app.route('/reply_add.ajax', methods=['POST'])
def sys_ans_add():
    owner_seq = escape(session['owner']['owner_seq'])

    sys_ques_seq = request.form['sys_ques_seq']
    sys_ans_reply = request.form['sys_ans_reply']

    try:
        cnt = daoSysAns.insert(sys_ques_seq, sys_ans_reply, "", owner_seq, "", owner_seq)
        print(cnt)
    except Exception as e:
        print(e)
        cnt = 0

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


@app.route('/sys_reply_del.ajax', methods=['POST'])
def sys_reply_del():
    sys_ques_seq = request.form['sys_ques_seq']
    cnt = daoSysAns.delete(sys_ques_seq)
    print(cnt)

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


##################    store     ######################

@app.route('/store_list')
def store_list():
    if 'owner' not in session:
        return redirect('login.html')

    store_sales = daoBuy.store_sales()
    saleList = daoBuy.sixMonthStoreSales()
    return render_template('web/store/store_list.html', storeschart=store_sales, saleList=saleList, title=f"가맹점 관리 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


#########################################################

@app.route('/password_change_successful')
def password_change_successful():
    return render_template('web/account/password_change_successful.html')


@app.route('/password_change_failed')
def password_change_failed():
    return render_template('web/account/password_change_failed.html')


@app.route('/kiosk_main')
def k_main():
    if 'owner' not in session:
        return redirect('kiosk_main')
    return render_template('kiosk/main.html', title=escape(session['owner']['owner_str_name']))


@app.route('/kiosk_login', methods=['POST'])
def kiosk_login():
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]

    owner = daoOwner.select_login(owner_id, owner_pwd)

    if owner:
        del (owner['owner_pwd'])
        session['owner'] = owner
        return redirect('kiosk_home')

    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/kiosk_home')
def k_home():
    if 'owner' not in session:
        return redirect('kiosk_main')
    logo_path = escape(session['owner']["logo_path"])
    logo_file = escape(session['owner']["logo_file"])
    owner_seq = escape(session['owner']["owner_seq"])
    list = daoEvent.selectAll(owner_seq)
    return render_template('kiosk/home.html', logo_path=logo_path, logo_file=logo_file, list=list, title=escape(session['owner']['owner_str_name']))


@app.route('/kiosk_menu')
def k_menu():
    if 'owner' not in session:
        return redirect('kiosk_main')
    owner_seq = escape(session['owner']["owner_seq"])
    logo_path = escape(session['owner']["logo_path"])
    logo_file = escape(session['owner']["logo_file"])
    cate_list = daoCategory.selectKiosk(owner_seq)
    return render_template('kiosk/menu.html', cate_list=cate_list, logo_path=logo_path, logo_file=logo_file, title=escape(session['owner']['owner_str_name']))


@app.route('/select_menu.ajax', methods=["POST"])
def select_menu():
    cate_seq = request.form["cate_seq"]
    try:
        owner_seq = escape(session['owner']["owner_seq"])

        menu_list = daoMenu.selectKiosk(owner_seq, cate_seq)
        return jsonify(menu_list=menu_list)
    except Exception as e:
        print(e)
    return None


@app.route('/select_menu_by_name.ajax', methods=['POST'])
def owner_seq():
    try:
        owner_seq = escape(session['owner']["owner_seq"])
        menu_name = request.form["menu_name"]
        menu_list = daoMenu.selectByName(owner_seq, menu_name)
        return jsonify(menu_list=menu_list)
    except Exception as e:
        print(e)
    return None


@app.route('/kiosk_pay_form', methods=["POST"])
def kiosk_pay_form():
    if 'owner' not in session:
        return redirect('kiosk_main')
    owner_seq = escape(session['owner']['owner_seq'])
    goods = dict(request.form)
    print(goods)

    buyList = {'menu': [],
               'buy_seq': daoBuy.genBuySeq(),
               'total_price': 0,
               'url': goods.pop('url')}

    menuList = daoMenu.selectKakao(owner_seq)
    count = 0
    for key, value in goods.items():
        buyList['menu'].append({'menu_seq': int(key.split("_")[1]),
                                'menu_name': menuList[int(key.split("_")[-1])]['menu_name'],
                                'count': int(value),
                                'menu_price': menuList[int(key.split("_")[1])]['menu_price']})
        buyList['total_price'] += menuList[int(key.split("_")[1])]['menu_price'] * int(value)
        count += int(value)
    buy_name = buyList['menu'][0]['menu_name']
    if count - 1:
        buy_name += ' 외 ' + str(count - 1) + '개'

    URL = 'https://kapi.kakao.com/v1/payment/ready'
    headers = {
        'Authorization': "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",
        "partner_order_id": buyList['buy_seq'],
        "partner_user_id": "Kiosk",
        "item_name": buy_name,
        "quantity": 1,
        "total_amount": buyList['total_price'],
        "tax_free_amount": 0,
        "approval_url": f"{buyList['url']}/pay_success",
        "cancel_url": f"{buyList['url']}/kiosk_home",
        "fail_url": f"{buyList['url']}/pay_fail",
    }

    res = requests.post(URL, headers=headers, params=params)
    buyList['tid'] = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장
    session['buy'] = buyList
    return redirect(res.json()['next_redirect_pc_url'])


@app.route('/pay_success')
def pay_success():
    if 'owner' not in session:
        return redirect('kiosk_main')
    buyList = session['buy']
    owner_seq = escape(session['owner']['owner_seq'])

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 테스트용 코드
        "tid": buyList['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": buyList['buy_seq'],  # 주문번호
        "partner_user_id": "Kiosk",  # 유저 아이디
        "pg_token": request.args.get("pg_token"),  # 쿼리 스트링으로 받은 pg토큰
    }
    res = requests.post(URL, headers=headers, params=params).json()

    owner = daoOwner.select(escape(session['owner']['owner_seq']))

    if owner and owner['owner_str_num']:
        owner_str_num = list(owner['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        owner['owner_str_num'] = ''.join(owner_str_num)

    daoBuy.insert(buyList['buy_seq'], buyList['menu'], owner_seq)

    return render_template('kiosk/success.html', owner=owner, res=res, buyList=buyList, title=escape(session['owner']['owner_seq']))


@app.route("/kakaopay/fail", methods=['POST', 'GET'])
def fail():
    if 'owner' not in session:
        return redirect('kiosk_main')
    return render_template('kiosk/fail.html', title=escape(session['owner']['owner_seq']), buyList=session['buy'])


@app.route('/kakaopay/retry')
def kakaopay_retry():
    if 'owner' not in session:
        return redirect('kiosk_main')

    buyList = session['buy']
    count = 0

    for menu in buyList['menu']:
        count += menu['count']

    buy_name = buyList['menu'][0]['menu_name']
    if count - 1:
        buy_name += ' 외 ' + str(count - 1) + '개'

    URL = 'https://kapi.kakao.com/v1/payment/ready'
    headers = {
        'Authorization': "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",
        "partner_order_id": buyList['buy_seq'],
        "partner_user_id": "Kiosk",
        "item_name": buy_name,
        "quantity": 1,
        "total_amount": buyList['total_price'],
        "tax_free_amount": 0,
        "approval_url": f"{buyList['url']}/pay_success",
        "cancel_url": f"{buyList['url']}/kiosk_home",
        "fail_url": f"{buyList['url']}/pay_fail",
    }

    res = requests.post(URL, headers=headers, params=params)
    buyList['tid'] = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장
    session['buy'] = buyList
    return redirect(res.json()['next_redirect_pc_url'])


@app.route('/downloads')
def downloads():
    path = request.args.get('path')
    file = request.args.get('file')
    return send_file(DIR_UPLOAD + path + '/' + file)


def saveFile(file, owner_seq=None):
    if owner_seq:
        attach_path = 'uploads/' + str(owner_seq)
    else:
        attach_path = f"uploads/{escape(session['owner']['owner_seq'])}"
    attach_file = str(datetime.today().strftime("%Y%m%d%H%M%S")) + str(random.random()) + '.' + secure_filename(file.filename).split('.')[-1]
    os.makedirs(DIR_UPLOAD + attach_path, exist_ok=True)
    file.save(os.path.join(DIR_UPLOAD + attach_path, attach_file))
    return attach_path, attach_file


##########################    voc   ##################################

@app.route('/voc_list')
def voc_list():
    if 'owner' not in session:
        return redirect('login.html')

    owner_seq = escape(session['owner']['owner_seq'])
    list = daoVoc.select(owner_seq)
    return render_template('web/voc/voc_list.html', list=list, len=len,
                           title=f"고객소리함 - {escape(session['owner']['owner_str_name'])} :: JYOGIYO")


@app.route('/voc_addact', methods=['POST'])
def voc_addact():
    if 'owner' not in session:
        return redirect('kiosk_main')
    owner_seq = escape(session['owner']['owner_seq'])
    content = request.form['content']
    try:
        cnt = daoVoc.insert(owner_seq, content, '', '')
        if cnt:
            return redirect(f"kiosk_menu?owner_seq={owner_seq}")
    except Exception as e:
        print(e)
    return '<script>alert("소리함 작성에 실패하였습니다.");history.back()</script>'


@app.route('/search_menu.ajax', methods=['POST'])
def search_menu_ajax():
    owner_seq = escape(session['owner']['owner_seq'])
    msg = request.form['msg']
    menu_list = daoMenu.selectByName(owner_seq, msg)
    return jsonify(menu_list=menu_list)


if __name__ == '__main__':
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # ssl_context.load_cert_chain(certfile='ssl/rootCA.pem', keyfile='ssl/rootCA.key', password='java')
    # app.run(host=HOST, port=PORT, debug=True, ssl_context=ssl_context)
    app.run(host=HOST, port=PORT, debug=True)
