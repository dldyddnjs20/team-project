from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, flash
import mariadb
import sys

app = Flask(__name__)
#session 사용을 위한 secret_key 정의
app.secret_key = b'_5#y2L"F4Q8z\\n\\xec]/'

#mariadb 에 연결
def mariadb_conn():
    try:
        db = mariadb.connect(
            user = 'lyw',
            password = 'lee',
            host = 'localhost',
            port = 13306,
            database = 'Users'
            )

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return db
    
#메인화면
@app.route('/')
def main():
    return render_template('main.html')

#로그인 페이지
@app.route('/login')
def login_page():
    if g.user:
        return redirect(url_for('calendar'))
    return render_template('login.html')

#회원가입 페이지 
@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

#회원가입
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        register_info = request.form
        
        #post로 넘어온 값을 변수로 저장
        name = register_info['name']
        username = register_info['username']
        hashed_password = register_info['password']
        phone = register_info['phone']
        degree = register_info['degree']
        
        #db에 데이터 저장
        print(name, username, hashed_password, phone, degree)
        conn = mariadb_conn()
        cur = conn.cursor()
        sql = "INSERT INTO UserInfo (name, username, hashed_password, phone, degree) VALUES (?, ?, ?, ?, ?)"
        cur.execute(sql, (name, username, hashed_password, phone, degree)) 
        conn.commit()
        conn.close()
        flash('회원가입이 완료되었습니다')
    
    #로그인페이지로 이동
    return redirect(url_for('login_page'))

#로그인
@app.route('/login', methods=['POST'])
def login_info():
    if request.method == 'POST':
        login_info = request.form
        #로그인 사이트에서 username, password 값이 post로 요청되면 아래와 같이 변수에 저장
        username = login_info['username']
        password = login_info['password']
        #쿼리문 실행해서 값을 가져오고 그값을 rows변수에 담는다
        conn = mariadb_conn()
        cur = conn.cursor()
        sql = "SELECT username, hashed_password, degree FROM UserInfo WHERE username=?"
        cur.execute(sql, (username,))
        rows = cur.fetchall() #cur.fetchall() -> 쿼리문으로 실행된 데이터베이스 정보를 list로 저장
        conn.close()
        print(rows)

        #post로 요청한 username에 값이 데이터 베이스에 있을경우 len(rows)=1, 없을경우 len(lows)=0
        if len(rows) > 0:
            print("user info: ", rows[0])
            #요청한 값이 있을경우 비밀번호 확인
            if password == rows[0][1]:
                password_check = True
                print("password check: ", password_check)
                #비밀번호가 일치할경우 session에 usernamer과 degree 저장 
                if password_check == True:
                    session.clear()
                    session['loginned_user'] = username
                    session['degree'] = rows[0][2]
                    print(session)
                    #예약페이지로 이동
                    return redirect(url_for('calendar'))
            #비밀번호가 틀리면 다시 로그인페이지로 이동
            else:
                flash("비밀번호가 틀립니다.")
                return render_template("login.html")
        #회원정보가 없을경우 다시 로그인페이지로 이동
        else:
            flash("회원정보가 없습니다.")
            return render_template("login.html")
    
#로그아웃
@app.route('/logout')
def logout():
    #session 값을 모두 제거하고 로그인페이지로 이동
    session.clear() 
    return redirect(url_for("login_page")) 

#로그인 상태 유무 확인 및 로그인 유지
#app.before_request -> 사이트가 요청될때마다 route가 실행되기전 항상 먼저 실행된다
@app.before_request
def load_logged_in_user():
    username = session.get('loginned_user')
    degree = session.get('degree')
    
    #로그인 상태 확인
    if username is None:
        g.user = None
    else:
        g.user = username, degree
        print(g.user[1])

#예약페이지
@app.route('/calendar')
def calendar():
    #로그인 상태확인
    if g.user is None:
        flash("로그인을 먼저 해주세요.")
        return redirect(url_for("login_page"))
    
    #db연결, id, title 값 호출
    conn = mariadb_conn()
    cur = conn.cursor()
    reservation_user = g.user[0]
    print(type(reservation_user))
    sql = "SELECT id, title FROM reservation WHERE username = '{}'".format(reservation_user)
    cur.execute(sql)

    
    #class list 목록 생성
    html = ""
    modal_data_dict = []
    for id, title in cur:
        html += "<button style='background-color: #272727; border: 0; display: block; line-height: 40px;'><a href='/calendar/status={id}'>- {title}</a></button>".format(id=id, title=title)
        print(id, title)

    conn.close()
    
    return render_template('calendar.html', data = html)

#모달에서 받은 데이터를 데이터베이스에 저장
@app.route('/modal_data', methods=['POST'])
def modal_data():
    data = request.get_json()

    #json 형태로 보내진 데이터(딕션어리형태)값을 각 변수에 저장 
    title = data.get('title')
    name = data.get('name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    room = data.get('room')
    message_text = data.get('message_text')
    start = data.get('start')
    end = data.get('end')
    
    sql = """
        INSERT INTO modalContent (title, recipient_name, email, phone_number, room, message_text, start, end) 
        VALUES (?, ?, ?, ?, ?, ?, ? ,?)
        """

    #데이터 전송 및 저장
    conn = mariadb_conn()
    cur = conn.cursor()
    cur.execute(sql, (title, name, email, phone_number, room, message_text, start, end))
    conn.commit()
    conn.close()
    return jsonify(result = "success", result2= data)
 

#모달에 입력한 데이터 달력에 띄우기
@app.route('/postdata', methods=['POST'])
def moadldata_load():
    conn = mariadb_conn()
    cur = conn.cursor()
    sql = "SELECT * FROM modalContent"
    cur.execute(sql)
    data_list = []
    
    for id, title, recipient_name, email, phone_number, room, message_text, start, end in cur:
        data = {
            'id': id,
            'title': title,
            'recipient_name': recipient_name,
            'email': email,
            'phone_number': phone_number,
            'room': room,
            'message_text': message_text,
            'start': start,
            'end': end
        }
        data_list.append(data)
        
    conn.close()
    return jsonify(data_list)

#class list 클릭시 이벤트
#url에 들어간 데이터의 id로 데이터 판단
@app.route('/calendar/status=<title_id>')
def status(title_id):

    conn = mariadb_conn()
    cur = conn.cursor()

    sql = "SELECT * FROM modalContent WHERE id={}".format(title_id)
    cur.execute(sql)
    data_list = []

    for id, title, recipient_name, email, phone_number, room, message_text, start, end in cur: 
        data_dict = {
        'id' : f'{id}',
        'title': f'{title}',
        'recipient_name': f'{recipient_name}',
        'email': f'{email}',
        'phone_number': f'{phone_number}',
        'room': f'{room}',
        'message_text': f'{message_text}',
        'start': f'{start}',
        'end': f'{end}'
        } 
    
    data_list.append(data_dict)
    print(data_list)
    conn.close
    return data_dict

@app.route('/reservation', methods=['POST'])
def reservation():
    reservation_data = request.get_json()

    title = reservation_data.get('title')
    name = reservation_data.get('name')
    email = reservation_data.get('email')
    phone_number = reservation_data.get('phone_number')
    room = reservation_data.get('room')
    message_text = reservation_data.get('message_text')
    start = reservation_data.get('start')
    end = reservation_data.get('end')
    username = g.user[0]
    print(title, name, email, phone_number, room, message_text, start, end, username)
    print(g.user[0])
    sql = """
        INSERT INTO reservation (title, name, email, phone_number, room, message_text, start, end, username) 
        VALUES (?, ?, ?, ?, ?, ?, ? ,?, ?)
        """

    #데이터 전송 및 저장
    conn = mariadb_conn()
    cur = conn.cursor()
    cur.execute(sql, (title, name, email, phone_number, room, message_text, start, end, username))
    conn.commit()
    conn.close()
    
    return jsonify(result = "success")

if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0")