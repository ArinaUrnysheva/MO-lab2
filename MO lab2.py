# Проверка корректности данных
def check_simplex_table(c, A, b):
    len_A = len(A[0])  # Количество переменных

    # Проверяет, что все строки матрицы A имеют одинаковую длину и содержат допустимые значения
    for row in A:
        if len(row) != len_A:
            return False  # Длина строки не соответствует ожидаемой

    # Проверяем, что длины векторов c и b соответствуют количеству строк в A
    if (len(c) != len_A) or (len(b) != len(A)):
        return False

    # Проверка пройдена успешно
    return True

# Проверяем, существуют ли решения симплекс-метода
def check_simplex_response(c, A, b):
    if c.count(0) == len(c):
        return False  # Все коэффициенты равны нулю

    for row in range(len(b)):
        if b[row] < 0:                      # Если есть отрицательный элемент в b
            for col in range(len(A[0])):
                if min(A[row]) >= 0:
                    return False            # Нет подходящих коэффициентов

    return True  # Существуют отрицательные коэффициенты

# Проверяем корректность решения, полученного симплекс-методом
def check_simplex_answer(c, b, f, var_row, var_col):
    check_f = 0

    for i in range(len(var_row)):
        if var_row[i] in var_col:
            check_f += b[i] * c[var_col.index(var_row[i]) - 1]

    if round(check_f, 2) == round(f, 2):
        return True
    return False

# Создаем симплекс-таблицу
def create_simplex_table(c, A, b, f):
    table = []

    # Формируем таблицу, добавляя строки с b и A
    for i in range(len(A)):
        table.append([b[i]] + A[i])

    # Добавляем строку с коэффициентами c
    table.append([f] + c)

    return table

# Создаем имена переменных для симплекс-метода
def create_simplex_variables(A):
    var_col = ["Si0"] + [f"y{i+1}" for i in range(len(A[0]))]
    var_row = [f"y{i+len(var_col)}" for i in range(len(A))] + ["F "]
    return var_row, var_col

# Выводим симплекс-таблицу
def print_simplex_table(simplex_table, var_row, var_col):
    print()

    # Определяем максимальную ширину для форматирования
    # max_width = max(len(str(float(j))) for row in simplex_table for j in row) + 2
    max_width = 6

    # Выводим заголовки
    headers = [var_col[i] for i in range(len(simplex_table[0]))]
    print("    ", " | ".join(f"{header:>{max_width}}" for header in headers))
    print("----", "-" * (max_width * len(headers) + 4 * (len(headers) - 1)), sep="")

    for i in range(len(simplex_table)):
        print(var_row[i], end=" | ")

        for j in simplex_table[i]:
            # Выравнивание по правому краю, 2 знака после запятой
            if j == 0:
                print(f"{float(0):>{max_width}.2f}", end=" | ")
            else:
                print(f"{round(float(j), 2):>{max_width}.2f}", end=" | ")
        print()

# Находим разрешающий элемент. Выводим информацию о минимальном отношении



def find_simplex_resolve(c, A, b):
    if check_simplex_response(c, A, b):
        # Проверяем, корректна ли симплекс-таблица

        for row in range(len(b)):
            if b[row] < 0:
                for col in range(len(A[0])):
                    if A[row][col] < 0:
                        # Возвращаем минимальное отношение для данного столбца
                        try:
                            return find_min_ratio(A, b, col)
                        except:
                            return ["inf"]

        c_max_value = max(c)
        if c_max_value < 0:
            # Если максимальное значение меньше нуля
            return ["not"]

        c_max_index = c.index(c_max_value)
        try:
            return find_min_ratio(A, b, c_max_index)
        except:
            return ["inf"]

    else:
        return ["not"]


# Находим минимальное отношение для заданного столбца симплекс-таблицы
def find_min_ratio(A, b, min_ratio_col):
    min_ratio = float("inf")
    min_ratio_row = -1

    for row in range(len(A)):
        if A[row][min_ratio_col] == 0:
            continue

        ratio = b[row] / A[row][min_ratio_col]

        # Обновляем минимальное отношение, если нашли новое
        if (ratio > 0) and (ratio < min_ratio):
            min_ratio = ratio
            min_ratio_row = row

    # Если не найден подходящий индекс, выбрасываем ошибку
    if min_ratio_row == -1:
        raise ValueError("[ ! ] Нет допустимого разрешающего элемента.")

    return [A[min_ratio_row][min_ratio_col], min_ratio_row, min_ratio_col]

# Меняем местами эл-ты в двух списках на основе указаний, полученных из решения симплекс-метода
def swap_variables(var_row, var_col, simplex_resolve):
    var_row[simplex_resolve[1]], var_col[simplex_resolve[2] + 1] = var_col[simplex_resolve[2] + 1], var_row[simplex_resolve[1]]
    return var_row, var_col

# Функция для выполнения одной итерации симплекс-метода
def simplex_table_iteration(c, A, b, f, simplex_resolve):
    # Получаем значение разрешающего элемента
    new_simplex_resolve = 1 / simplex_resolve[0]

    new_c = [0] * len(c)  # Инициализируем новый вектор коэффициентов целевой функции
    new_b = [0] * len(b)  # Инициализируем новый вектор правых частей
    new_A = [[0 for _ in range(len(A[0]))] for _ in range(len(A))]  # Инициализируем новую матрицу ограничений

    # Заполняем колонну A
    for i in range(len(A)):
        if i == simplex_resolve[1]:  # Текущая строка разрешающего элемента
            new_A[i][simplex_resolve[2]] = new_simplex_resolve
        else:  # Остальные строки
            new_A[i][simplex_resolve[2]] = (A[i][simplex_resolve[2]] / simplex_resolve[0] * -1)

    # Обновляем коэффициенты целевой функции для разрешающего столбца
    new_c[simplex_resolve[2]] = c[simplex_resolve[2]] / simplex_resolve[0] * -1

    # Заполняем строку A для разрешающего элемента
    for i in range(len(A[0])):
        if i == simplex_resolve[2]:
            continue
        new_A[simplex_resolve[1]][i] = A[simplex_resolve[1]][i] / simplex_resolve[0]

    # Обновляем вектор правых частей для разрешающего элемента
    new_b[simplex_resolve[1]] = b[simplex_resolve[1]] / simplex_resolve[0]

    # Обновляем остальные коэффициенты целевой функции
    for i in range(len(c)):
        if i == simplex_resolve[2]:
            continue
        new_c[i] = c[i] - (A[simplex_resolve[1]][i] * c[simplex_resolve[2]]) / (simplex_resolve[0])

    # Обновляем вектор правых частей для остальных строк
    for i in range(len(b)):
        if i == simplex_resolve[1]:
            continue
        new_b[i] = b[i] - ((A[i][simplex_resolve[2]] * b[simplex_resolve[1]]) / simplex_resolve[0])

    # Обновляем матрицу ограничений
    for i in range(len(A)):
        for j in range(len(A[0])):
            if (i == simplex_resolve[1]) or (j == simplex_resolve[2]):
                continue
            new_A[i][j] = A[i][j] - ((A[i][simplex_resolve[2]] * A[simplex_resolve[1]][j]) / simplex_resolve[0])

    # Обновляем значение целевой функции
    new_f = f - ((c[simplex_resolve[2]] * b[simplex_resolve[1]]) / simplex_resolve[0])

    return new_c, new_A, new_b, new_f

# Преобразуем заданные параметры для двойственной задачи
def to_dual_task(c, A, b, minimize):
    new_c = b.copy()
    new_b = [-x for x in c]

    # Создаем новую матрицу A для двойственной задачи
    # Размерность new_A: количество столбцов A x количество строк A
    new_A = [[0 for _ in range(len(A))] for _ in range(len(A[0]))]

    # Заполняем новую матрицу A, транспонируя оригинальную матрицу A
    for row in range(len(A)):
        for col in range(len(A[0])):
            new_A[col][row] = A[row][col] * -1

    return new_c, new_A, new_b, not minimize

# Основная функция симплекс-метода
# Выполняет проверки входных данных и находит решение
def simplexsus(c, A, b, f, minimize):
    # Проверка условий
    if check_simplex_table(c, A, b):
        print("[ + ] Check: OK")
        old_b = b.copy()

        # Инвертируем c, если ищем минимум
        if minimize:
            for i in range(len(c)):
                c[i] *= -1

        var_row, var_col = create_simplex_variables(A)  # Создание обозначений симплекс-таблицы
        old_var_row = var_row.copy()

        while (max(c) > 0) or (min(b) < 0):
            simplex_table = create_simplex_table(c, A, b, f)        # Создание симплекс-таблицы
            print_simplex_table(simplex_table, var_row, var_col)    # Вывод симплекс-таблицы
            simplex_resolve = find_simplex_resolve(c, A, b)         # Поиск и выбор разрешающего элемента

            # Обработка результатов нахождения разрешающего элемента
            if simplex_resolve == ["not"]:
                print("[ - ] There's no answer")
                return 1
            if simplex_resolve == ["inf"]:
                print("[ - ] Infinite number of solutions")
                return 1

            print("[ * ] The resolving element is found:", round(simplex_resolve[0], 2), simplex_resolve[1:])

            var_row, var_col = swap_variables(var_row, var_col, simplex_resolve)
            c, A, b, f = simplex_table_iteration(c, A, b, f, simplex_resolve)

        # Найдено оптимальное решение
        print("\n[ + ] OPTI ANS")
        simplex_table = create_simplex_table(c, A, b, f)        # Создание симплекс-таблицы
        print_simplex_table(simplex_table, var_row, var_col)    # Вывод симплекс-таблицы

    else:
        print("[ - ] Check: BAD TABLE")
        return 1

    if check_simplex_answer(c, old_b, f, old_var_row, var_col):
        if minimize:
            print("[ * ] The function goes to the minimum")
            return round(f, 2)

        else:
            print("[ * ] The function goes to the maximum")
            return round(f * -1, 2)

    print("[ - ] Check: BAD ANS")
    return -1

# Инициализация значений и вывод решения симплекс-метода
def main():
    minimize = False  # Необходимость минимизации
    c = [8, 6, 2]  # Коэффициенты целевой функции
    A = [[2, 1, 1], [1, 4, 0], [0, 0.5, 1]]  # Ограничения
    b = [4, 3, 6]  # Правая часть ограничений
    f = 0

    c, A, b, minimize = to_dual_task(c, A, b, minimize)
    print("[ + ] Ans:", simplexsus(c, A, b, f, minimize))

    return 0


if __name__ == "__main__":
    main()
