from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션을 위한 시크릿 키 설정

# SQLite 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

option = ["가위", "바위", "보"]

# 데이터베이스 정의
class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_choice = db.Column(db.String(20), nullable=False)
    computer_choice = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<GameHistory {self.id} - {self.player_choice} vs {self.computer_choice}: {self.result}>'

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

def get_computer_choice():
    return random.choice(option)

def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        session['draw'] += 1
        result = "무승부!"
    elif (
        (player_choice == "바위" and computer_choice == "가위")
        or (player_choice == "가위" and computer_choice == "보")
        or (player_choice == "보" and computer_choice == "바위")
    ):
        session['win'] += 1
        result = "이겼습니다!"
    else:
        session['lose'] += 1
        result = "졌습니다.."
    return result

# 세션 초기화
def initialize_session():
    if 'win' not in session:
        session['win'] = 0
    if 'lose' not in session:
        session['lose'] = 0
    if 'draw' not in session:
        session['draw'] = 0

# 웹페이지 보여줌
@app.route('/')
def index():
    initialize_session()
    history = GameHistory.query.all()
    return render_template('index.html', history=history, win=session['win'], lose=session['lose'], draw=session['draw'])


@app.route('/play', methods=['POST'])
def play():
    initialize_session()
    player_choice = request.json.get('choice')
    computer_choice = get_computer_choice()
    result = determine_winner(player_choice, computer_choice)

    # 데이터베이스에 결과 저장
    new_game = GameHistory(player_choice=player_choice, computer_choice=computer_choice, result=result)
    db.session.add(new_game)
    db.session.commit()

    # 결과와 승, 패, 무승부 횟수 반환
    return jsonify({
        'player_choice': player_choice,
        'computer_choice': computer_choice,
        'result': result,
        'win': session['win'],
        'lose': session['lose'],
        'draw': session['draw']
    })

# 기록 초기화
@app.route('/reset', methods=['POST'])
def reset():
    session['win'] = 0
    session['lose'] = 0
    session['draw'] = 0
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)
