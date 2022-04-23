# ____________________________________ИМПОРТИРУЕМЫЕ БИБЛИОТЕКИ И ИХ НАСТРОЙКИ___________________________________________

import sqlite3 as sql
import random
import decimal
from collections import Counter
import winsound
duration = 1000  # millisecond
freq = 440  # Hz

# _______________________________________________КОНСОЛЬ УПРАВЛЕНИЯ_____________________________________________________

# Отсюда мы управляем программой, задавая разные параметры для сбора статистики.
samples = 0  # Считает количество раздач.
distributions_target = 30  # Задаём количество раздач, которое нас интересует.
samples_target = 1  # Задаём количество сэмплов на ситуацию, которое хотим увидеть на дистанции.
gain_target = 0  # Задаём показатель выигрыша, который хотим видеть для конкретной ситуации.

# Можем проверить конкретную ситуацию в БД, задав диапазоны игроков.
range1_target = 44
range2_target = 26
range3_target = 6
range4_target = 39
check_unique_situation = False

# Список и количество участвующих игроков.
plr1 = True
plr2 = True
plr3 = True
plr4 = True
plrs_list = [plr1, plr2, plr3, plr4]
plrs_num = len([plr for plr in plrs_list if plr])

# Рэйк и блайнды.
rake = decimal.Decimal(0.012).quantize(decimal.Decimal('1.000'))
sb = decimal.Decimal(0.05).quantize(decimal.Decimal('1.00'))
bb = decimal.Decimal(0.1).quantize(decimal.Decimal('1.0'))
bet = 1


# _______________________________________________СЛОВАРИ С ДАННЫМИ______________________________________________________

deck = {'Ad': (14, 'd'), 'Ah': (14, 'h'), 'As': (14, 's'), 'Ac': (14, 'c'),
        'Kd': (13, 'd'), 'Kh': (13, 'h'), 'Ks': (13, 's'), 'Kc': (13, 'c'),
        'Qd': (12, 'd'), 'Qh': (12, 'h'), 'Qs': (12, 's'), 'Qc': (12, 'c'),
        'Jd': (11, 'd'), 'Jh': (11, 'h'), 'Js': (11, 's'), 'Jc': (11, 'c'),
        'Td': (10, 'd'), 'Th': (10, 'h'), 'Ts': (10, 's'), 'Tc': (10, 'c'),
        '9d': (9, 'd'), '9h': (9, 'h'), '9s': (9, 's'), '9c': (9, 'c'),
        '8d': (8, 'd'), '8h': (8, 'h'), '8s': (8, 's'), '8c': (8, 'c'),
        '7d': (7, 'd'), '7h': (7, 'h'), '7s': (7, 's'), '7c': (7, 'c'),
        '6d': (6, 'd'), '6h': (6, 'h'), '6s': (6, 's'), '6c': (6, 'c'),
        '5d': (5, 'd'), '5h': (5, 'h'), '5s': (5, 's'), '5c': (5, 'c'),
        '4d': (4, 'd'), '4h': (4, 'h'), '4s': (4, 's'), '4c': (4, 'c'),
        '3d': (3, 'd'), '3h': (3, 'h'), '3s': (3, 's'), '3c': (3, 'c'),
        '2d': (2, 'd'), '2h': (2, 'h'), '2s': (2, 's'), '2c': (2, 'c')}

algorithm = {'AA': [0.45, 0.45, 0.45], 'KK': [0.9, 0.9, 0.9], 'QQ': [1.36, 1.36, 1.36], 'JJ': [1.81, 1.81, 1.81],
             'TT': [2.26, 2.26, 2.26], 'AKs': [2.56, 3.02, 3.47], '99': [3.02, 2.71, 2.71], 'AQs': [3.32, 3.32, 3.77],
             'AJs': [3.62, 4.07, 4.52], 'AKo': [4.52, 4.98, 5.43], 'KQs': [4.83, 5.58, 7.84], 'ATs': [5.13, 5.28, 5.73],
             'KJs': [5.43, 6.79, 9.8], 'AQo': [6.33, 6.49, 6.64], '88': [6.79, 3.77, 3.17], 'KTs': [7.09, 8.45, 10.41],
             'QJs': [7.39, 10.86, 14.33], 'AJo': [8.3, 8.14, 7.54], 'KQo': [9.2, 10.56, 11.61],
             'A9s': [9.5, 8.75, 8.14], 'QTs': [9.8, 11.46, 17.5], 'ATo': [10.71, 9.65, 9.5],
             'JTs': [11.01, 14.03, 23.83], 'A8s': [11.31, 11.16, 10.11], 'KJo': [12.22, 12.37, 13.73],
             '77': [12.67, 7.24, 4.22], 'K9s': [12.97, 12.97, 15.54], 'A7s': [13.27, 12.67, 10.71],
             'QJo': [14.18, 17.04, 21.72], 'A5s': [14.48, 13.73, 12.82], 'KTo': [15.38, 14.93, 16.89],
             'Q9s': [15.69, 18.55, 23.53], 'A6s': [15.99, 15.23, 14.03], 'A4s': [16.29, 17.35, 17.19],
             'A9o': [17.19, 16.14, 12.52], 'QTo': [18.1, 19.76, 25.64], 'J9s': [18.4, 21.57, 29.11],
             'T9s': [18.7, 25.34, 35.14], 'K8s': [19.0, 18.85, 19.0], 'A3s': [19.31, 20.06, 18.7],
             'JTo': [20.21, 24.13, 33.03], '66': [20.66, 13.42, 8.6], 'A8o': [21.57, 18.25, 15.23],
             'K7s': [21.87, 21.27, 22.93], 'A2s': [22.17, 22.78, 23.23], 'Q8s': [22.47, 25.94, 27.9],
             'K9o': [23.38, 22.47, 22.62], 'K6s': [23.68, 25.64, 25.94], 'A7o': [24.59, 20.97, 18.4],
             'J8s': [24.89, 28.36, 34.84], 'T8s': [25.19, 31.67, 40.72], 'A5o': [26.09, 25.04, 19.91],
             'K5s': [26.4, 27.15, 27.6], '98s': [26.7, 34.09, 46.15], 'Q9o': [27.6, 29.26, 32.13],
             'A6o': [28.51, 26.85, 20.81], 'K4s': [28.81, 30.47, 31.22], 'Q7s': [29.11, 31.98, 34.24],
             'J9o': [30.02, 32.88, 38.46], '55': [30.47, 23.23, 15.99], 'A4o': [31.37, 28.05, 24.74],
             'T9o': [32.28, 36.95, 43.74], 'K8o': [33.18, 30.17, 28.81], 'J7s': [33.48, 37.25, 40.42],
             'Q6s': [33.79, 34.69, 35.44], 'K3s': [34.09, 34.39, 34.54], 'T7s': [34.39, 39.97, 47.36],
             'A3o': [35.29, 31.37, 26.85], '97s': [35.6, 41.48, 52.94], '87s': [35.9, 42.68, 54.75],
             'Q5s': [36.2, 39.37, 38.76], 'K7o': [37.1, 33.79, 30.02], 'K2s': [37.41, 39.67, 37.56],
             'Q8o': [38.31, 38.16, 37.25], 'A2o': [39.22, 35.6, 30.92], 'Q4s': [39.52, 41.18, 41.03],
             'J8o': [40.42, 42.38, 44.65], 'K6o': [41.33, 39.06, 33.94], 'T8o': [42.23, 44.19, 50.08],
             'J6s': [42.53, 42.99, 47.66], '44': [42.99, 36.05, 27.3], 'Q3s': [43.29, 43.29, 44.95],
             'T6s': [43.59, 46.61, 53.24], '76s': [43.89, 50.98, 64.4], '98o': [44.8, 47.51, 55.66],
             '86s': [45.1, 52.19, 60.78], '96s': [45.4, 50.38, 57.77], 'J5s': [45.7, 46.3, 49.17],
             'K5o': [46.61, 40.87, 36.35], 'Q2s': [46.91, 47.81, 48.87], 'J4s': [47.21, 50.68, 52.64],
             'Q7o': [48.11, 46.0, 41.93], 'K4o': [49.02, 45.1, 40.12], '65s': [49.32, 58.82, 70.44],
             'J7o': [50.23, 51.89, 50.98], '75s': [50.53, 59.73, 69.83], 'J3s': [50.83, 55.2, 54.45],
             'Q6o': [51.73, 49.17, 45.85], 'T5s': [52.04, 55.51, 58.37], 'T7o': [52.94, 54.9, 56.56],
             '85s': [53.24, 60.03, 66.82], 'K3o': [54.15, 50.08, 42.84], '95s': [54.45, 59.13, 63.8],
             '87o': [55.35, 58.22, 66.21], '97o': [56.26, 56.41, 61.69], 'T4s': [56.56, 59.43, 60.48],
             '33': [57.01, 48.27, 39.22], 'J2s': [57.32, 58.52, 58.07], '54s': [57.62, 64.71, 76.47],
             'Q5o': [58.52, 53.09, 48.57], 'K2o': [59.43, 54.0, 47.06], 'T3s': [59.73, 62.14, 64.1],
             '64s': [60.03, 67.12, 76.77], 'Q4o': [60.94, 57.32, 52.34], '74s': [61.24, 70.44, 76.17],
             'J6o': [62.14, 60.94, 57.47], 'T2s': [62.44, 66.82, 66.52], '76o': [63.35, 68.93, 75.57],
             '84s': [63.65, 70.74, 72.85], 'T6o': [64.56, 64.4, 63.5], '94s': [64.86, 69.23, 70.14],
             '86o': [65.76, 68.02, 72.55], '96o': [66.67, 66.52, 67.72], '53s': [66.97, 72.25, 82.5],
             'Q3o': [67.87, 61.84, 54.15], 'J5o': [68.78, 63.5, 59.28], '93s': [69.08, 71.04, 71.64],
             '22': [69.53, 62.59, 51.43], '63s': [69.83, 77.38, 83.71], 'Q2o': [70.74, 65.61, 60.18],
             '43s': [71.04, 79.79, 85.82], 'J4o': [71.95, 70.14, 62.59], '92s': [72.25, 73.45, 75.87],
             '65o': [73.15, 74.36, 81.9], '73s': [73.45, 79.49, 82.2], '83s': [73.76, 80.09, 78.88],
             '75o': [74.66, 78.28, 79.79], 'T5o': [75.57, 73.15, 69.53], 'J3o': [76.47, 71.95, 65.31],
             '85o': [77.38, 79.19, 78.58], '82s': [77.68, 80.39, 81.0], '52s': [77.98, 82.5, 89.14],
             '95o': [78.88, 75.26, 73.76], 'T4o': [79.79, 76.17, 71.34], '54o': [80.69, 82.2, 87.63],
             'J2o': [81.6, 77.07, 68.63], '62s': [81.9, 84.62, 89.44], '42s': [82.2, 86.73, 90.65],
             '72s': [82.5, 87.03, 88.84], '64o': [83.41, 83.41, 88.54], 'T3o': [84.31, 81.3, 74.66],
             '74o': [85.22, 86.43, 86.73], '32s': [85.52, 89.14, 94.57], '84o': [86.43, 87.93, 84.62],
             '94o': [87.33, 85.52, 80.69], 'T2o': [88.24, 84.31, 77.68], '53o': [89.14, 90.05, 93.36],
             '93o': [90.05, 88.84, 83.41], '63o': [90.95, 91.86, 94.27], '43o': [91.86, 92.76, 95.48],
             '92o': [92.76, 90.95, 85.52], '73o': [93.67, 93.67, 92.46], '83o': [94.57, 94.57, 90.35],
             '52o': [95.48, 96.38, 97.29], '82o': [96.38, 95.48, 91.55], '42o': [97.29, 98.19, 99.1],
             '62o': [98.19, 97.29, 98.19], '72o': [99.1, 99.1, 96.38], '32o': [100, 100, 100]}


# _________________________________________________ФУНКЦИИ И МЕТОДЫ_____________________________________________________

def get_label(pocket_hand):
    hand_label = [[pocket_hand[0], deck.get(pocket_hand[0])[0], deck.get(pocket_hand[0])[1]],
                  [pocket_hand[1], deck.get(pocket_hand[1])[0], deck.get(pocket_hand[1])[1]]]
    hand_label.sort(key=lambda x: x[1], reverse=True)
    if hand_label[0][1] == hand_label[1][1]:
        hand_label = hand_label[0][0][0] + hand_label[1][0][0]
    else:
        if hand_label[0][2] == hand_label[1][2]:
            hand_label = hand_label[0][0][0] + hand_label[1][0][0] + 's'
        else:
            hand_label = hand_label[0][0][0] + hand_label[1][0][0] + 'o'
    return hand_label


def suit_combination_builder(draft_hand):
    suited_group = False
    diamonds_group = []
    hearts_group = []
    spades_group = []
    clubs_group = []

    for suit in draft_hand:
        if suit[1] == 'd':
            diamonds_group.append(suit)
            continue
        if suit[1] == 'h':
            hearts_group.append(suit)
            continue
        if suit[1] == 's':
            spades_group.append(suit)
            continue
        if suit[1] == 'c':
            clubs_group.append(suit)

    suited_container = [diamonds_group, hearts_group, spades_group, clubs_group]

    for box in suited_container:
        if len(box) >= 5:
            suited_group = list(map(lambda x: x[0], box))

    if suited_group:
        straight_flush = progression_selector(suited_group)
        if straight_flush:
            straight_flush_rank = straight_flush[0]
            return 8, straight_flush_rank
        else:
            return 5, suited_group[0], suited_group[1], suited_group[2], suited_group[3], suited_group[4]


def progression_selector(input_hand):
    normal_progression_group = progression_builder(input_hand)
    if normal_progression_group:
        return normal_progression_group
    elif 14 in input_hand:
        draft_wheel_progression_group = list(map(lambda x: 1 if (x == 14) else x, input_hand))
        draft_wheel_progression_group = sorted(draft_wheel_progression_group, reverse=True)
        wheel_progression_group = progression_builder(draft_wheel_progression_group)
        if wheel_progression_group:
            return wheel_progression_group


def progression_builder(random_hand):
    progression = ()
    progression_counter = 1

    for i, rank in enumerate(random_hand):
        if i > 0:
            if (rank - random_hand[i - 1]) == -1:
                progression_counter += 1
                if progression_counter == 5:
                    progression = random_hand[i - 4:i + 1]
            else:
                progression_counter = 1
    return progression


def rank_combination_builder(draft_hand):
    ranks = dict(Counter(draft_hand))

    set_kickers = []
    pair_kickers = []
    high_card = []

    for rank in ranks.items():
        if rank[1] == 4:
            for kicker in ranks.items():
                if kicker[1] < 4:
                    return 7, rank[0], kicker[0]
        elif rank[1] == 3:
            for low_rank in ranks.items():
                if low_rank[0] != rank[0]:
                    if 1 < low_rank[1] <= 3:
                        return 6, rank[0], low_rank[0]
                    elif low_rank[1] == 1:
                        set_kickers.append(low_rank[0])
                        if len(set_kickers) == 4:
                            return 3, rank[0], set_kickers[0], set_kickers[1]
        elif rank[1] == 2:
            for low_rank in ranks.items():
                if low_rank[0] != rank[0]:
                    if low_rank[1] == 2:
                        for kicker in ranks.items():
                            if (kicker[0] != rank[0]) and (kicker[0] != low_rank[0]):
                                if kicker[1] <= 2:
                                    return 2, rank[0], low_rank[0], kicker[0]
                    elif low_rank[1] == 1:
                        pair_kickers.append(low_rank[0])
                        if len(pair_kickers) == 5:
                            return 1, rank[0], pair_kickers[0], pair_kickers[1], pair_kickers[2]
        elif rank[1] == 1:
            high_card.append(rank[0])
            if len(high_card) == 7:
                return 0, high_card[0], high_card[1], high_card[2], high_card[3], high_card[4]


# Получает список из семи карт (2 карманки + 5 доска), из которых игрок будет строить свою руку.
def made_combination_selector(pocket_hand):
    extended_hand = (pocket_hand + board)
    draft_hand = []
    for card_name in extended_hand:
        draft_hand.append([deck.get(card_name)[0], deck.get(card_name)[1]])
    draft_hand.sort(key=lambda x: x[0], reverse=True)

    suit_combination = suit_combination_builder(draft_hand)
    if suit_combination:
        return suit_combination
    else:
        draft_hand = list(map(lambda x: x[0], draft_hand))
        rank_combination = rank_combination_builder(draft_hand)
        if rank_combination[0] == 7 or rank_combination[0] == 6:
            return rank_combination
        else:
            draft_straight = list(Counter(draft_hand))
            straight = progression_selector(draft_straight)
            if straight:
                straight_rank = straight[0]
                return 4, straight_rank
            else:
                return rank_combination


# ____________________________________________СОЕДИНЕНИЕ С БАЗОЙ ДАННЫХ_________________________________________________

# with sql.connect('db_ranges.db') as connection:
#     cursor = connection.cursor()
#     cursor.execute('''DROP TABLE IF EXISTS co''')
#     cursor.execute('''CREATE TABLE IF NOT EXISTS co (
#         ranges TEXT NOT NULL PRIMARY KEY,
#         samples INTEGER NOT NULL DEFAULT 1,
#         gain REAL NOT NULL)''')


# _____________________________________________ОСНОВНОЙ ЦИКЛ ПРИЛОЖЕНИЯ_________________________________________________
while True:
    # Начинается раунд.
    # Отсчитываем номер раздачи и выводим на экран.
    samples += 1
    # Отключаем цикл при достижении таргета раздач.
    if samples == distributions_target + 1:
        break
    print(f'\n\nsample number - {samples}')

    # Банкролл героя также обнуляется для каждой ситуации, чтобы в конце раздачи определить чистую прибыль за раунд.
    cash = 0

    # Каждую раздачу алгоритм генерирует случайные диапазоны игроков.
    range1 = random.randint(0, 100)
    range2 = random.randint(0, 100)
    range3 = random.randint(0, 100)
    range4 = random.randint(0, 100)
    ranges = f'{range1} | {range2} {range3} {range4}'

    # Обнуляем также переменную количества игроков, участвующих в раздаче.
    # По ходу работы скрипта она будет меняться, если игроки будут сбрасывать карты.
    # По умолчанию, в начале раунда она равна количеству игроков за столом.
    plrs_in = plrs_num

    # Обнуляем контейнеры имён карманных карт игроков и контейнер имён карт борда.
    pocket_hand1 = ()
    pocket_hand2 = ()
    pocket_hand3 = ()
    pocket_hand4 = ()
    board = ()

    # Обнуляем значения типов карманных рук.
    hand1_label = ''
    hand2_label = ''
    hand3_label = ''
    hand4_label = ''

    # Обнуляем перечень комбинаций собранных игроками, а также контейнер всех комбинаций, полученных игроками за раунд.
    hand1 = ()
    hand2 = ()
    hand3 = ()
    hand4 = ()
    hands = []

    # Обнуляем количество победителей и размер банка.
    winners = 0
    bank = 0

    # Раздаём карты в зависимости от количества игроков, участвующих в раздаче.
    if plrs_num == 4:
        round_cards = random.sample(deck.keys(), 13)
        pocket_hand1 = (round_cards[0], round_cards[4])
        pocket_hand2 = (round_cards[1], round_cards[5])
        pocket_hand3 = (round_cards[2], round_cards[6])
        pocket_hand4 = (round_cards[3], round_cards[7])
        board = (round_cards[8], round_cards[9], round_cards[10], round_cards[11], round_cards[12])

    elif plrs_num == 3:
        round_cards = random.sample(deck.keys(), 11)
        if not plr1:
            pocket_hand2 = (round_cards[0], round_cards[3])
            pocket_hand3 = (round_cards[1], round_cards[4])
            pocket_hand4 = (round_cards[2], round_cards[5])
        elif not plr2:
            pocket_hand1 = (round_cards[0], round_cards[3])
            pocket_hand3 = (round_cards[1], round_cards[4])
            pocket_hand4 = (round_cards[2], round_cards[5])
        elif not plr3:
            pocket_hand1 = (round_cards[0], round_cards[3])
            pocket_hand2 = (round_cards[1], round_cards[4])
            pocket_hand4 = (round_cards[2], round_cards[5])
        elif not plr4:
            pocket_hand1 = (round_cards[0], round_cards[3])
            pocket_hand2 = (round_cards[1], round_cards[4])
            pocket_hand3 = (round_cards[2], round_cards[5])
        board = (round_cards[6], round_cards[7], round_cards[8], round_cards[9], round_cards[10])

    elif plrs_num == 2:
        round_cards = random.sample(deck.keys(), 9)
        if plr1:
            pocket_hand1 = (round_cards[0], round_cards[2])
            if plr2:
                pocket_hand2 = (round_cards[1], round_cards[3])
            elif plr3:
                pocket_hand3 = (round_cards[1], round_cards[3])
            elif plr4:
                pocket_hand4 = (round_cards[1], round_cards[3])
        else:
            if plr2:
                pocket_hand2 = (round_cards[0], round_cards[2])
                if plr3:
                    pocket_hand3 = (round_cards[1], round_cards[3])
                elif plr4:
                    pocket_hand4 = (round_cards[1], round_cards[3])
            else:
                pocket_hand3 = (round_cards[0], round_cards[2])
                pocket_hand4 = (round_cards[1], round_cards[3])
        board = (round_cards[4], round_cards[5], round_cards[6], round_cards[7], round_cards[8])

    else:
        print('NO GAME')
        break

    # Важнейший блок программы.
    # 1. Производит расчёт игроков с банком.
    # 2. Присваивает типы карманных рук.
    # 3. Принуждает игроков играть только в рамках заданного пользователем диапазона рук, иначе сбрасывает руку.
    # 4. Определяет комбинацию руки игрока.
    # 5. Присваивает выигрыш игроку, если до него все сбросили.
    if plr1:
        cash -= rake
        hand1_label = get_label(pocket_hand1)
        hand1_range = algorithm.get(hand1_label)[abs(plrs_in - 4)]
        if hand1_range <= range1:
            hand1 = made_combination_selector(pocket_hand1)
            hands.append(hand1)
            cash -= bet
            bank += bet
        else:
            plrs_in -= 1

    if plr2:
        if plrs_in > 1:
            hand2_label = get_label(pocket_hand2)
            hand2_range = algorithm.get(hand2_label)[abs(plrs_in - 4)]
            if hand2_range <= range2:
                hand2 = made_combination_selector(pocket_hand2)
                hands.append(hand2)
                bank += bet
            else:
                plrs_in -= 1
        else:
            # Отправляем статистику в БД.
            cash = decimal.Decimal(cash).quantize(decimal.Decimal('1.000'))
            with sql.connect('db_ranges.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO co (ranges, gain) VALUES ('{ranges}', {cash}) "
                               f"ON CONFLICT (ranges) DO UPDATE SET samples = samples+1, gain = gain+{cash}")
            continue

    if plr3:
        bank += sb
        if plrs_in > 1:
            hand3_label = get_label(pocket_hand3)
            hand3_range = algorithm.get(hand3_label)[abs(plrs_in - 4)]
            if hand3_range <= range3:
                hand3 = made_combination_selector(pocket_hand3)
                hands.append(hand3)
                bank += bet - sb
            else:
                plrs_in -= 1
        else:
            # Отправляем статистику в БД.
            cash = decimal.Decimal(cash).quantize(decimal.Decimal('1.000'))
            with sql.connect('db_ranges.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO co (ranges, gain) VALUES ('{ranges}', {cash}) "
                               f"ON CONFLICT (ranges) DO UPDATE SET samples = samples+1, gain = gain+{cash}")
            continue

    if plr4:
        bank += bb
        if plrs_in > 1:
            hand4_label = get_label(pocket_hand4)
            hand4_range = algorithm.get(hand4_label)[abs(plrs_in - 4)]
            if hand4_range <= range4:
                hand4 = made_combination_selector(pocket_hand4)
                hands.append(hand4)
                bank += bet - bb
        else:
            # Отправляем статистику в БД.
            cash = decimal.Decimal(cash).quantize(decimal.Decimal('1.000'))
            with sql.connect('db_ranges.db') as connection:
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO co (ranges, gain) VALUES ('{ranges}', {cash}) "
                               f"ON CONFLICT (ranges) DO UPDATE SET samples = samples+1, gain = gain+{cash}")
            continue

    # Определяем победившую комбинацию рук, считаем количество победителей и делим выигрыш.
    best_hand = sorted(hands, reverse=True)[0]
    for hand in hands:
        if hand == best_hand:
            winners += 1

    gain = bank / winners
    gain = decimal.Decimal(gain).quantize(decimal.Decimal('1.00'), decimal.ROUND_DOWN)
    if hand1 == best_hand:
        cash += gain

    cash = decimal.Decimal(cash).quantize(decimal.Decimal('1.000'))
    # Отправляем статистику в БД.
    with sql.connect('db_ranges.db') as connection:
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO co (ranges, gain) VALUES ('{ranges}', {cash}) "
                       f"ON CONFLICT (ranges) DO UPDATE SET samples = samples+1, gain = gain+{cash}")


# __________________________________________ВЫГРУЗКА ДАННЫХ ИЗ БД_______________________________________________________

with sql.connect('db_ranges.db') as connection:
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM co WHERE samples >= {samples_target} AND gain >= {gain_target} ORDER BY ranges')
    for db_smpl in cursor:
        print(db_smpl)

if check_unique_situation:
    ranges_target = f'{range1_target} | {range2_target} {range3_target} {range4_target}'
    with sql.connect('db_ranges.db') as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM co WHERE ranges = '{ranges_target}'")
        print(cursor.fetchall())

winsound.Beep(freq, duration)
