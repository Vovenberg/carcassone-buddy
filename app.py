import datetime
import time
from zoneinfo import ZoneInfo

from flask import Flask, render_template, request
from tinydb import TinyDB

app = Flask(__name__)

BASE_URL = "/carcassone-buddy"

def create_game_state():
    return {
        'start_date': time.time(),
        'end_date': None,
        'players': {},
        'active_player': '',
        'current_formula': '',
        'current_operation': '',
        'history': []
    }

game_state = {}
db = TinyDB('db.json')


@app.route(f'{BASE_URL}', methods=['GET'])
def index():
    empty_state = create_game_state()
    return render_template('index.html',
                         players=empty_state['players'],
                         active_player=empty_state['active_player'],
                         current_formula=empty_state['current_formula'],
                         history=empty_state['history'],
                         game_history=get_all()
                         )

@app.route(f'{BASE_URL}/start', methods=['POST'])
def start():
    players_str = request.form.get('players')
    if players_str is None:
        return 'Players not provided', 400
    players = [player.strip() for player in players_str.split(sep=',')]

    global game_state
    game_state = create_game_state()
    game_state['active_player'] = players[0]
    for player in players:
        game_state['players'][player] = {'score': 0 }
    print(game_state)
    return render_template('index.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history'])

@app.route(f'{BASE_URL}/toggle_player', methods=['POST'])
def toggle_player():
    # \"\"\"Переключение активного игрока\"\"\"
    player = request.form.get('player')
    if player in game_state['players']:
        game_state['active_player'] = player
        game_state['current_formula'] = ''
        game_state['current_operation'] = ''

    # Возвращаем обновленную панель счетчика
    return render_template('partials/score_display.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history'])

@app.route(f'{BASE_URL}/input_number', methods=['POST'])
def input_number():
    # \"\"\"Обработка ввода числа\"\"\"
    number = request.form.get('number')
    if number:
        if game_state['current_formula'] == '':
            game_state['current_formula'] = "+" + number
        else:
            game_state['current_formula'] += number

    return render_template('partials/score_display.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history'])

@app.route(f'{BASE_URL}/input_operator', methods=['POST'])
def input_operator():
    # \"\"\"Обработка ввода операции (+/-)\"\"\"
    operator = request.form.get('operator')
    if operator: ##and game_state['current_formula']:
        game_state['current_formula'] += operator

    return render_template('partials/score_display.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history'])

@app.route(f'{BASE_URL}/calculate', methods=['POST'])
def calculate():
    # \"\"\"Вычисление результата и обновление счета\"\"\"
    if game_state['current_formula'] and game_state['active_player']:
        try:
            # Безопасное вычисление только для простых математических операций
            formula = game_state['current_formula']

            # Проверяем, что формула содержит только числа и операторы +/-
            allowed_chars = set('0123456789+-')
            if all(c in allowed_chars for c in formula):
                result = eval(formula)  # В реальном приложении лучше использовать более безопасный способ

                player = game_state['active_player']
                old_score = game_state['players'][player]['score']
                new_score = old_score + result

                if new_score < 0:
                    raise Exception('Новое значение меньше 0')

                # Обновляем счет
                game_state['players'][player]['score'] = new_score

                # Сохраняем историю
                history = { "player": player,
                           "old_score": old_score,
                           "formula": formula,
                           "new_score": new_score
                        }
                game_state['history'].append(history)

                # Очищаем текущую операцию
                game_state['current_formula'] = ''
                game_state['current_operation'] = ''

                # Убираем current_operation если был
                if 'current_operation' in game_state['players'][player]:
                    del game_state['players'][player]['current_operation']

                print(game_state)

        except:
            # В случае ошибки просто очищаем формулу
            game_state['current_formula'] = ''

    return render_template('index.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history'])

game_state = {}

@app.route(f'{BASE_URL}/end', methods=['POST'])
def end():
    game_state['end_date'] = time.time()
    persist()
    game_state.clear()
    empty_state = create_game_state()
    return render_template('index.html',
                         players=empty_state['players'],
                         active_player=empty_state['active_player'],
                         current_formula=empty_state['current_formula'],
                         history=empty_state['history'],
                         game_history=get_all()
                         )

def persist():
    db.insert(game_state)

def get_all():
    items = db.all()
    print(f'items = {items}')
    return map(lambda x: {
        'date': f'{format_date(x['start_date']).strftime('%Y-%m-%d %H:%M')} - {format_date(x['end_date']).strftime('%H:%M')}',
        'players': ', '.join(format_players(index, data) for index, 
            data in enumerate(sorted(x['players'].items(), key=lambda item: item[1]['score'], reverse=True)))
    }, items)

def format_players(index, player_data):
    print(f'player_data = {player_data}')
    print(f'index = {index}')
    return f"{index == 0 and '🏆 ' or ''}{player_data[0]} - {player_data[1]['score']}"

def format_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).astimezone(ZoneInfo("Europe/Samara"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
