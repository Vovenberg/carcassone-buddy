
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_URL = "/carcassone-buddy"
DEFAULT_PLAYERS = ['Люба', 'Вова']

game_state = {
    'players': {},
    'active_player': '',
    'current_formula': '',
    'current_operation': '',
    'history': []
}


@app.route(f'{BASE_URL}/')
def index():
    # "\"Главная страница с калькулятором\"\"\"
    return render_template('index.html',
                         players=game_state['players'],
                         active_player=game_state['active_player'],
                         current_formula=game_state['current_formula'],
                         history=game_state['history']
                         )

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

@app.route(f'{BASE_URL}/clear', methods=['GET'])
def clear():
    game_state['active_player'] = next(iter(game_state['players']))
    game_state['history'] = []
    for player in game_state['players']:
        game_state['players'][player]['score'] = 0
    return render_template('index.html',
                        players=game_state['players'],
                        active_player=game_state['active_player'],
                        current_formula=game_state['current_formula'],
                        history=game_state['history']
                        )


def initPlayers(players):
    game_state['active_player'] = players[0]
    for player in players:
        game_state['players'][player] = {'score': 0 }
    print(game_state)


initPlayers(DEFAULT_PLAYERS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5151)