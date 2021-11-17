# -*- coding: utf-8 -*-
import cx_Oracle
from datetime import datetime
import time
import hashlib
from progress.bar import Bar

cursor, connection = None, None


input_request = input('Вы хотите создать новую заявку (Да/Нет): ')
if input_request == 'Да' or input_request == 'lf':
    FIRST_NAME_EMP_START = input('Введите Ваше Имя: ')
    LAST_NAME_EMP_START = input('Введите Вашу Фамилию: ')
    DATE_START = datetime.now()

    try:
        cx_Oracle.init_oracle_client(
            r"Полный путь до instantclient")
        connection = cx_Oracle.connect(user='', password='', dsn='')
        cursor = connection.cursor()

        cursor.execute(
            'select FIRST_NAME, LAST_NAME from dev.CORE_T1_EMPLOYEES WHERE FIRST_NAME = :FNC and LAST_NAME = :LNC',
            FNC = FIRST_NAME_EMP_START, LNC = LAST_NAME_EMP_START)
        var = cursor.fetchall()
        FLAG_EMP = False
        for line in var:
            if line == (FIRST_NAME_EMP_START, LAST_NAME_EMP_START):
                FLAG_EMP = True
                cursor.execute(
                    'select employees__id from dev.CORE_T1_EMPLOYEES WHERE FIRST_NAME = :FNC and LAST_NAME = :LNC',
                    FNC = FIRST_NAME_EMP_START, LNC = LAST_NAME_EMP_START)
                EMPLOYEE_ID = cursor.fetchall()

        if FLAG_EMP:
            INPUT_PASSWORD = input('Введите Ваш пароль: ')
            check_password = hashlib.sha256(INPUT_PASSWORD.encode('utf-8')).hexdigest()
            cursor.execute(
                'select PASSWORD from dev.CORE_T1_PASSWORDS WHERE PASSWORD = :IPAS',
                IPAS = check_password)
            PASSWORD_LIST = cursor.fetchall()
            if check_password in PASSWORD_LIST[0]:
                print('Вы вошли в систему')
            else:
                print('Вы ввели неверный пароль')

        else:
            print('Вас нет в системе!')

        FIRST_NAME_CLIENT = input('Введите имя клиента: ')
        LAST_NAME_CLIENT = input('Введите фамилию клиента: ')
        SALARY = int(input('Введите средний ежемесячный доход клиента за последние три месяца: '))
        SUM_REQUEST = int(input('Введите запрошенную сумму: '))
        DELAY = input('Положительная ли у клиента кредитная история? (Да/Нет): ')
        TIME = int(input('Введите желаемые сроки погашения кредита (месяцев): '))

        cursor.execute('select FIRST_NAME ,LAST_NAME from dev.CORE_T1_CLIENTS')
        var = cursor.fetchall()
        FLAG_CLI = False
        for line in var:
            if line == (FIRST_NAME_CLIENT,LAST_NAME_CLIENT):
                FLAG_CLI = True
        if FLAG_CLI == False:
            cursor.execute('''INSERT INTO dev.CORE_T1_CLIENTS(FIRST_NAME ,LAST_NAME,salary) VALUES (:FN,:LN,:SA)''',
                           FN = FIRST_NAME_CLIENT, LN = LAST_NAME_CLIENT, SA = SALARY)
        # Находим id клиента
        cursor.execute('select clients__id from dev.CORE_T1_CLIENTS WHERE FIRST_NAME = :FNC and LAST_NAME = :LNC',
                       FNC = FIRST_NAME_CLIENT, LNC = LAST_NAME_CLIENT)
        CLIENT_ID = cursor.fetchall()


        cursor.execute(
            '''INSERT INTO dev.CORE_T1_APPLICATIONS(CLIENT__ID,REQUEST_AMOUNT,ACCEPTED) VALUES (:CID,:SR,:AC)''',
            CID = CLIENT_ID[0][0], SR = SUM_REQUEST, AC = 1)
        # Находим APPLICATION_ID
        cursor.execute('select APPLICATION__ID from dev.CORE_T1_APPLICATIONS WHERE CLIENT__ID = :CID',
                       CID = CLIENT_ID[0][0])
        APPLICATION_ID = cursor.fetchall()

        cursor.execute(
            '''INSERT INTO dev.CORE_T1_APPLICATION_STATUSES(APPLICATION___ID,STATUS___ID,EMPLOYEE___ID,START_DATE,END_DATE) VALUES (:AID,:SID,:EID,:SD,:ED)''',
            AID = APPLICATION_ID[0][0], SID = 23, EID = EMPLOYEE_ID[0][0], SD = datetime.now(),
            ED = datetime.now())

        # На данном этапе производится расчет процентной ставки
        if TIME > 1 and TIME <= 3:
            RATE = '18.52%'
            RATE_M = 0.01543
        if TIME > 3 and TIME <= 12:
            RATE = '14.48%'
            RATE_M = 0.01206
        if TIME > 12 and TIME <= 36:
            RATE = '13.69%'
            RATE_M = 0.011408
        if TIME > 36:
            RATE = '10.17%'
            RATE_M = 0.008725

        # На данном этапе производится расчет ежемесячного платежа по кредиту, а также 50% ежемесячного дохода клиента
        MON_PAY = SUM_REQUEST * ((RATE_M * ((1 + RATE_M) ** TIME)) / ((((1 + RATE_M) ** TIME)) - 1))
        HALF_SALARY = SALARY / 2

        print("Ожидайте...")
        time.sleep(3)

        # Если ежемесячный платеж не превышает 50% ежемесячного дохода клиента, кредит будет одобрен. Если превышает, заявка будет находится на рассмотрении
        if HALF_SALARY < MON_PAY or DELAY == 'Нет':
            STATUS = 'ОТКАЗАНО'
            cursor.execute(
                '''INSERT INTO dev.CORE_T1_APPLICATION_STATUSES(APPLICATION___ID,STATUS___ID,EMPLOYEE___ID,START_DATE,END_DATE) VALUES (:AID,:SID,:EID,:SD,:ED)''',
                AID = APPLICATION_ID[0][0], SID = 25, EID = EMPLOYEE_ID[0][0], SD = datetime.now(),
                ED = datetime.now())
            SUM_Approved = 0
        elif HALF_SALARY >= MON_PAY:
            STATUS = 'ОДОБРЕНО'
            cursor.execute(
                '''INSERT INTO dev.CORE_T1_APPLICATION_STATUSES(APPLICATION___ID,STATUS___ID,EMPLOYEE___ID,START_DATE,END_DATE) VALUES (:AID,:SID,:EID,:SD,:ED)''',
                AID = APPLICATION_ID[0][0], SID = 24, EID = EMPLOYEE_ID[0][0], SD = datetime.now(),
                ED = datetime.now())
            SUM_Approved = SUM_REQUEST

        # Если у клиента негативная кредитная история, в выдаче кредита будет отказано


        DATE_END = datetime.now()
        connection.commit()
    except cx_Oracle.DatabaseError as e:
        raise e

    except BaseException as e:
        raise e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print()
    print(f'Дата создания заявки: {DATE_START}')
    print(f'ФИO сотрудника, создавшего заявку: {FIRST_NAME_EMP_START} {LAST_NAME_EMP_START}')
    # print("Дата последнего изменения:", DATE_CH)
    # print("ФИO сотрудника, совершившего последние изменения:", NAME_EMP_CH)
    # print("Дата закрытия заявки", DATE_END)
    # print("ФИO сотрудника, закрывшего заявки:", NAME_EMP_END)
    print(f'ФИО клиента: {FIRST_NAME_CLIENT}, {LAST_NAME_CLIENT}')
    print(f'Статус заявки: {STATUS}')
    print(f'Запрошенная сумма: {SUM_REQUEST}')
    print(f'Одобренная сумма: {SUM_Approved}')
    print(f'Процентная ставка: {RATE}')
    print(f'Дата закрытия заявки {datetime.now()}')

    #создание лог файла
    list_bar = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    bar = Bar('Создание лог-файла...', max = len(list_bar), suffix = '%(percent)d%%', fill = '█')
    for i in list_bar:
      bar.next()
      with open('log.txt', 'w') as file:
        file.write(f'Дата создания заявки: {datetime.now()} \n')
        file.write(f'ФИO сотрудника, создавшего заявку: {FIRST_NAME_EMP_START} {LAST_NAME_EMP_START} \n')
        file.write(f'ФИО клиента: {FIRST_NAME_CLIENT}, {LAST_NAME_CLIENT} \n')
        file.write(f'Статус заявки: {STATUS} \n')
        file.write(f'Запрошенная сумма: {SUM_REQUEST} \n')
        file.write(f'Одобренная сумма: {SUM_Approved} \n')
        file.write(f'Процентная ставка: {RATE} \n')
        file.write(f'Дата закрытия заявки {datetime.now()} \n')
    bar.finish()

elif input_request == '\q' or input_request == 'Нет':
    print('Хорошего дня!')
