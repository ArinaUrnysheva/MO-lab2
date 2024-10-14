def check_simplex_table(c, A, b): #проверка симплекс-таблицы
    len_A = len(A[0])  #количество переменных
    for row in A: #проверка на то, что длина всех строк матицы одинакова
        if len(row) != len_A:
            return False  #длина строки не подходит

    if (len(c) != len_A) or (len(b) != len(A)):  #проверяем, что длины векторов c и b соответствуют количеству строк в A
        return False

    return True #проверка пройдена успешно

def check_simplex_response(c, A, b): #проверка на существование решений симплекс-метода
    if c.count(0) == len(c):
        return False  #все коэффициенты равны нулю

    for row in range(len(b)):
        if b[row] < 0:  #если есть отрицательный элемент в b
            for col in range(len(A[0])):
                if A[row][col] < 0:
                    return True  #существуют отрицательные коэффициенты
            return False  #нет подходящих коэффициентов

    return True

def create_simplex_table(c, A, b, f): #создание симплекс-таблицы
    table = []

    for i in range(len(A)):  #добавляем строки с коэффициентами b и А
        table.append([b[i]] + A[i])

    table.append([f] + c) #в конце добавляем строку с коэффициентами с и значением f

    return table

def print_simplex_table(simplex_table): #вывод красивой симплекс-таблицы

    max_length = 0

    for row in simplex_table:
        for j in row:
            length = len(str(float(j)))
            if length > max_length:
                max_length = length

    max_width = max_length + 2

    #выводим заголовки
    headers = ["b"] + [f"x{i+1}" for i in range(len(simplex_table[0]) - 1)]
    print(" | ".join(f"{header:>{max_width}}" for header in headers))
    print("-" * (max_width * len(headers) + 3 * (len(headers) - 1)))

    for i in range(len(simplex_table)):
        for j in simplex_table[i]:
            #выравнивание по правому краю, 2 знака после запятой
            print(f"{float(j):>{max_width}.2f}", end=" | ")
        print()

def find_simplex_resolve(c, A, b): #находим разрешающий элемент
    #проверяем, корректна ли симплекс-таблица
    if check_simplex_response(c, A, b):
        for row in range(len(b)):
            if b[row] < 0:
                for col in range(len(A[0])):
                    if A[row][col] < 0:
                        #возвращаем минимальное отношение для данного столбца
                        try:
                            return find_min_ratio(A, b, col)
                        except:
                            return ["inf"]

        c_max_value = max(c)
        #если максимальное значение меньше нуля
        if c_max_value < 0:
            return ["not"]

        c_max_index = c.index(c_max_value)
        try:
            return find_min_ratio(A, b, c_max_index)
        except:
            return ["inf"]

    else:
        return ["not"]

def find_min_ratio(A, b, min_ratio_col): #находим минимальное отношение для заданного столбца в симплекс-таблице
    min_ratio = float("inf")
    min_ratio_row = -1

    for row in range(len(A)):
        if A[row][min_ratio_col] == 0:
            continue

        ratio = b[row] / A[row][min_ratio_col]

        #обновляем минимальное отношение, если нашли новое
        if (ratio > 0) and (ratio < min_ratio):
            min_ratio = ratio
            min_ratio_row = row

    #если не найден подходящий индекс, выбрасываем ошибку
    if min_ratio_row == -1:
        raise ValueError("[ ! ] Нет допустимого разрешающего элемента.")

    return [A[min_ratio_row][min_ratio_col], min_ratio_row, min_ratio_col]


def simplex_table_iteration(c, A, b, f, simplex_resolve):
    """
    Функция для выполнения одной итерации симплекс-метода.

    Параметры:
    c : list
        Коэффициенты целевой функции.
    A : list of lists
        Матрица ограничений системы.
    b : list
        Вектор правых частей ограничений (свободные коэффициенты).
    f : float
        Текущее значение целевой функции.
    simplex_resolve : tuple
        Кортеж, содержащий информацию о разрешающем элементе:
        (значение разрешающего элемента, строка, столбец).

    Возврат:
    new_c : list
        Обновленные коэффициенты целевой функции.
    new_A : list of lists
        Обновленная матрица ограничений.
    new_b : list
        Обновленный вектор правых частей (свободные коэффициенты).
    new_f : float
        Обновленное значение целевой функции.
    """

    #получаем значение разрешающего элемента
    new_simplex_resolve = 1 / simplex_resolve[0]

    new_c = [0] * len(c)  #инициализируем новый вектор коэффициентов целевой функции
    new_b = [0] * len(b)  #инициализируем новый вектор правых частей
    new_A = [[0 for _ in range(len(A[0]))] for _ in range(len(A))]  # Инициализируем новую матрицу ограничений

    #заполняем колонну A
    for i in range(len(A)):
        if i == simplex_resolve[1]:  #текущая строка разрешающего элемента
            new_A[i][simplex_resolve[2]] = new_simplex_resolve #нашли и обновили разрешающий элемент
        else:  #обновляем разрешающий столбец
            new_A[i][simplex_resolve[2]] = A[i][simplex_resolve[2]] / simplex_resolve[0] * -1

    #обновляем коэффициенты целевой функции для разрешающего столбца
    new_c[simplex_resolve[2]] = c[simplex_resolve[2]] / simplex_resolve[0] * -1

    #заполняем строку A для разрешающего элемента
    for i in range(len(A[0])):
        if i == simplex_resolve[2]: #пропускаем разрешающий столбец
            continue
        new_A[simplex_resolve[1]][i] = A[simplex_resolve[1]][i] / simplex_resolve[0]

    #обновляем вектор правых частей для разрешающего элемента
    new_b[simplex_resolve[1]] = b[simplex_resolve[1]] / simplex_resolve[0]

    #обновляем остальные коэффициенты целевой функции
    for i in range(len(c)):
        if i == simplex_resolve[2]:
            continue
        new_c[i] = c[i] - (A[simplex_resolve[1]][i] * c[simplex_resolve[2]]) / (simplex_resolve[0])

    #обновляем вектор правых частей для остальных строк
    for i in range(len(b)):
        if i == simplex_resolve[1]:
            continue
        new_b[i] = b[i] - ((A[i][simplex_resolve[2]] * b[simplex_resolve[1]]) / simplex_resolve[0])

    #обновляем матрицу ограничений
    for i in range(len(A)):
        for j in range(len(A[0])):
            if (i == simplex_resolve[1]) or (j == simplex_resolve[2]):
                continue
            new_A[i][j] = A[i][j] - ((A[i][simplex_resolve[2]] * A[simplex_resolve[1]][j]) / simplex_resolve[0])

    #обновляем значение целевой функции
    new_f = f - ((c[simplex_resolve[2]] * b[simplex_resolve[1]]) / simplex_resolve[0])

    return new_c, new_A, new_b, new_f

def to_dual_task(c, A, b, minimize): #составление двойственной задачи
    new_c = b.copy()
    new_b = [-x for x in c]

    #создаем новую матрицу A для двойственной задачи
    #размерность new_A: количество столбцов A x количество строк A
    new_A = [[0 for _ in range(len(A))] for _ in range(len(A[0]))]

    #заполняем новую матрицу A, транспонируя оригинальную матрицу A
    for row in range(len(A)):
        for col in range(len(A[0])):
            new_A[col][row] = A[row][col] * -1

    return new_c, new_A, new_b, not minimize


def simplexsus(minimize, c, A, b, f): #основная функцмя симплекс-метода
    #проверка условий
    if check_simplex_table(c, A, b):
        print("[ + ] Check: OK")

        #инвертируем c, если ищем минимум
        if minimize:
            for i in range(len(c)):
                c[i] *= -1

        while (max(c) > 0) or (min(b) < 0):
            simplex_table = create_simplex_table(c, A, b, f)  #создание симплекс-таблицы
            print_simplex_table(simplex_table)  #вывод симплекс-таблицы

            simplex_resolve = find_simplex_resolve(c, A, b)  #поиск и выбор разрешающего элемента

            #обработка результатов нахождения разрешающего элемента
            if simplex_resolve == ["not"]:
                print("[ - ] There's no answer")
                return 1
            if simplex_resolve == ["inf"]:
                print("[ - ] Infinite number of solutions")
                return 1

            print("[ * ] The resolving element is found:", simplex_resolve)

            c, A, b, f = simplex_table_iteration(c, A, b, f, simplex_resolve)

        #найдено оптимальное решение
        print("\n[ + ] OPTI ANS")
        simplex_table = create_simplex_table(c, A, b, f)  #создание симплекс-таблицы
        print_simplex_table(simplex_table)  #вывод симплекс-таблицы

    else:
        print("[ - ] Check: BAD")
        return 1

    if minimize:
        print("[ * ] The function goes to the minimum")
        return f

    print("[ * ] The function goes to the maximum")
    return f * -1


def main(): #инициализация значений и вызов симплекс-метода
    minimize = False                            #необходимость минимизации
    c = [8, 6, 2]                      #коэффициенты целевой функции
    A = [[2, 1, 1], [1, 4, 0], [0, 0.5, 1]]       #ограничения
    b = [4, 3, 6]                                #правая часть ограничений
    f = 0

    c, A, b, minimize = to_dual_task(c, A, b, minimize)
    print("[ + ] Ans:", simplexsus(minimize, c, A, b, f))

    return 0


if __name__ == "__main__":
    main()
