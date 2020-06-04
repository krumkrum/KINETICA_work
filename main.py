import requests
import numpy as np
import sqlite3
import time
import matplotlib.pylab as plt

### USD
### EUR
### CNY
### JPY
#                   #    1       1       10      100
#                   #    USD     EUR     CNY     JPY
                    #
### PreviousDate    #    68      75      64      64
                    #
### Date            #    70      80      65       70

### PreviousURL

### def X -> Y   68 RUR = 1 USD
###              100 RUR = 64 JPY
###              1 RUR = 0,64 JPY
###              43.52 JPY = 1 USD

### Ссылка
chars = ['USD', 'EUR', 'CNY', 'JPY']
murl = "https://www.cbr-xml-daily.ru/daily_json.js"

#answ = self.r.get(url)



#Date
#PreviousDate
#PreviousURL
#Timestamp
#Valute
#None


### main

### USD_x = [0]
### EUR_x = [1]
### CNY_x = [2]
### JPY_x = [3]

### y = data [4]


### For convert
### USD -> EUR_x CNY_x JPY_x

### EUR_x = [0]
### CNY_x = [1]
### jpy_x = [2]
### y = data [3]


class Table():

    def __init__(self):
        self.req = requests.Session()
        self.conn = sqlite3.connect("my.db")
        self.name = "money"
        self.chars = ['USD', 'EUR', 'CNY', 'JPY']
        self.n = 30 # дней для сбора статистики


        self.create_table()
        self.create_conv_table()

    def get_json(self, url):
        return self.req.get(url).json()

### создание таблицы для конвертированных
    def create_conv_table(self):

            for i in self.chars:

                try:

                    cursor = self.conn.cursor()
                    cursor.execute("""CREATE TABLE  {0} 
                    (USD real, EUR real, CNY real, JPY real, date text)""".format(i))
                    print(i, "created")

                except:
                    print(i, "already created")

### Создание таблицы
    def create_table(self):

        try:
            cursor = self.conn.cursor()
            cursor.execute("""CREATE TABLE  money 
            (USD real, EUR real, CNY real, JPY real, date text)""")
            print("money created")

        except:
            print("money already create")
            return 0

### Добавление данных по строчно
    def add_to_base(self, pack, name):

        cursor = self.conn.cursor() # Подключаемся

        sql = "INSERT INTO '{0}' VALUES (?,?,?,?,?)".format(name)

        cursor.execute(sql, pack) # Дабы избежать возможной sql иньекции к бд

        self.conn.commit() # Сохраняем

### Создание массива с данными (строка)
    def add_info(self):



        answ = self.get_json(murl) # Делаем запрос


        for i in range(self.n): # Количество дней за которую соберем статистику

            data = [] # Создаем пустой массив


            for k in self.chars: # Нахождение нужных нам валют

                data.append((answ['Valute'][k]['Value'])) #Добавление нужной валюты в массив



            data.append(answ['Date']) # Добавление в массив даты, от которой мы брали курсы

            self.add_to_base(data, "money") # Выгрузка массива в таблицу
            print("Данные за", data[4], " добавлены")


            next = "http://{0}".format((answ['PreviousURL'])[2:]) # Алгоритм берущий данные за пред идущий период
                                                            #   Возникла проблема с тем что ресурс распологающий данными
                                                            #   Не содержит в себе некоторых дней.
                                                            #   Разработчики сервиса связывают это,
                                                            #   с проблемами доступа к данным ЦБ
            answ = self.get_json(next)

            time.sleep(1)   # Для снижения нагрузки в тестовых целях
                            # Было принято решение не так часто отправлять запросы
                            # Ресурс просит не производить более чем 5 запросов в секунду
                            # Мы же слегка утрериовали это (ИСКЛЮЧИТЕЛЬНО В ЦЕЛЯХ ТЕСТА!)

### Показать главную базу данных
    def show_main_base(self):

        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM money")


        b = cursor.fetchall()

        return b

### Показать конвертированные базы
    def show_base(self, name):

        try:
            cursor = self.conn.cursor()
            sql = "SELECT * FROM '{0}'".format(name)
            cursor.execute(sql)

            d = cursor.fetchall()

            return d

        except:
            print("Неверное имя, доступные имена \n"
                      "USD , CNY, JPY, EUR")

### Функция выражения одной валюты черзе другую
    def to_express(self, currency, x, y):


        # Для иены
        if currency == "JPY":

            # if x == y: # Ведь не может 1 иена стоить 0,1 йен
            #     return 1

            return round((x/y), 4)
                #return round( (x/(y*100)), 4) # округление до 4 знака после запятой
                                            # Формат заданный изначально ( при желании можно изменить)

        # Для юаня
        elif currency == "CNY":
            # if x == y: # Ведь не может 1 юань стоить 0,1 юаней
            #     return 1
            #
            # else:
                # оставил эту строчку в случае если, я не правильно понял поставленную задачу
                #return round( (x/y)/10, 4 ) Спрятано для более красивой статистики
                # не совсем понял смысл выразить одну валюту через дргую то есть 100 иен 70 рублей
                # нужно было понимать как 100/70 йен за 1 рубль?


            return round( (x/y), 4) # округление до 4 знака после запятой
                                                   # Формат заданный изначально ( при желании можно изменить)

        # Для USD и EUR
        else:
            return round( (x/y), 4) # else потому как EUR и USD выражены за единицу
                                # Формат заданный изначально ( при желании можно изменить)

### Обработчик выражения
    def convertor(self):

            # Перебираем все значения в таблице
            for bn in self.chars:

                for i in self.show_main_base():
                    data = []

                    # Для иены
                    if bn == "JPY":
                        for k, n in enumerate(i[0:4]):

                            data.append(self.to_express(bn, i[3], i[k]))

                        data.append(i[4])

                        self.add_to_base(data, "JPY")


                    # Для юаня
                    elif bn == "CNY":
                        for k, n in enumerate(i[0:4]):
                            data.append(self.to_express(bn, i[2], i[k]))

                        data.append(i[4])

                        self.add_to_base(data, "CNY")


                    # Для евро
                    elif bn == "EUR":
                        for k, n in enumerate(i[0:4]):
                            data.append(self.to_express(bn, i[1], i[k]))

                        data.append(i[4])

                        self.add_to_base(data, "EUR")



                    # Для доллара
                    elif bn == "USD":
                        for k, n in enumerate(i[0:4]):
                            data.append(self.to_express(bn, i[0], i[k]))

                        data.append(i[4])

                        self.add_to_base(data, "USD")

    # подготовка данных для создания графиков с конвертацией

    def to_drawer_conv(self, name):

        b = self.show_base(name)

        eur = []
        jpy = []
        cny = []
        usd = []
        date = []



        if name == 'USD':
            for i in b:
                eur.append(i[1])
                jpy.append(i[2])
                cny.append(i[3])
                date.append((i[4])[8:10])

            data = {name: {'EUR': eur,
                           'CNY': cny,
                           'JPY': jpy,
                           'date': date
                           }
                        }


        elif name == "JPY":
            for i in b:
                eur.append(i[1]*100)
                usd.append(i[0]*100)
                cny.append(i[3]*100)
                date.append((i[4])[8:10])

            data = {name: {'EUR': eur,
                           'CNY': cny,
                           'USD': usd,
                           'date': date
                           }
                    }

        elif name == "CNY":
            for i in b:
                eur.append(i[1]*10)
                jpy.append(i[2]*10)
                usd.append(i[0]*10)
                date.append((i[4])[8:10])
            data = {name: {'EUR': eur,
                           'USD': usd,
                           'JPY': jpy,
                           'date': date
                           }
                    }



        elif name == "EUR":

            for i in b:
                usd.append(i[0])
                jpy.append(i[2])
                cny.append(i[3])
                date.append((i[4])[8:10])

            data = {name: {'USD': usd,
                           'CNY': cny,
                           'JPY': jpy,
                           'date': date
                           }
                    }

        else:
            return 0


        return data

    # подготовка данных для создания графика
    def to_drawer_main(self):
        b = self.show_main_base()

        eur = []
        jpy = []
        cny = []
        usd = []
        date = []

        for i in b:
            usd.append(i[0])
            eur.append(i[1])
            jpy.append(i[2])
            cny.append(i[3])
            date.append((i[4])[8:10])

        data = {
               'USD': usd,
               'EUR': eur,
               'CNY': cny,
               'JPY': jpy,
               'date': date
                }

        return data

###
# 0 Проверить таблицу USD на корректность!
# 1 алгоритм !
# 2 построить графики !
###

class Graf():
    def __init__(self):

        self.fig = plt.figure()


        # размер поля для графика
        egrid = (4, 2)

        #Описание осей для графиков
        self.ax1 = plt.subplot2grid(egrid, (0, 0), colspan=2, rowspan=2)
        self.ax1.set_title("Курсы валют")
        self.ax1.set_ylabel("Стоимость в рублях")
        self.ax1.set_xlabel("Дата формата м-д")
        self.ax1.grid()


        self.ax2 = plt.subplot2grid(egrid, (2, 0))
        self.ax2.set_ylabel("--> USD")
        self.ax2.set_xlabel("Дата формата м-д")
        self.ax2.grid()

        self.ax3 = plt.subplot2grid(egrid, (2, 1))
        self.ax3.set_ylabel("--> EUR")
        self.ax3.set_xlabel("Дата формата м-д")
        self.ax3.grid()

        self.ax4 = plt.subplot2grid(egrid, (3, 0))
        self.ax4.set_ylabel("--> CNY")
        self.ax4.set_xlabel("Дата формата м-д")
        self.ax4.grid()

        self.ax5 = plt.subplot2grid(egrid, (3, 1))
        self.ax5.set_ylabel("--> JPY")
        self.ax5.set_xlabel("Дата формата м-д")
        self.ax5.grid()


    # создание главного графика
    def main_graf(self, data):

        for v in data:

            if v == 'date':
                break

            self.fig.axes[0].scatter(data['date'], data[v], label='{0}'.format(v), s=10)
        self.ax1.legend()

    # создание график с конвертацией
    def conv_tables(self, data, n):
        for i in data:
            for k in data[i]:
                if k == 'date':
                    break

                self.fig.axes[n+1].scatter(data[i]['date'], data[i][k], label='{0}'.format(k))

        if n == 0:
            self.ax2.legend()
        elif n == 1:
            self.ax3.legend()
        elif n == 2:
            self.ax4.legend()
        elif n == 3:
            self.ax5.legend()



if __name__ == '__main__':
    t = Table()

    if t.show_main_base() == []:
        print("worked")
        t.add_info()

        for i in t.chars:
            t.convertor()
        print("Включите повторно чтобы посмотреть графики")

    else:
        g = Graf()
        g.main_graf(t.to_drawer_main())


        for n, i in enumerate(chars):
            k = t.to_drawer_conv(i)
            g.conv_tables(k, n)


        plt.show()


# #Примечание по заданию
#         1) сайт указаный для выполненния задания работает не всегда
#         корректно в связи с этим на графике присутсвует артефакты.