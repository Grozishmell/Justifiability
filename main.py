import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fractions import Fraction
import json


error_price_possible = Fraction(1, 3)
error_price_expected = Fraction(2, 3)
steps = 1
all_a_index = 0.0

text_to_number_map1 = {'спокойное': 1, 'спокойное с отдельеными периодами неустойчивости': 12,
                       'неустойчивое': 2, 'неустойчивое с отдельными (слабо) возмущенными периодами': 23,
                       'слабо возмущенное': 3, 'слабо возмущенное (с отдельными умеренно возмущенными периодами)': 34,
                       'умеренно возмущенное': 4,
                       'умеренно возмущенное (с отдельными сильно возмущенными периодами)': 45,
                       'сильно возмущенное': 5}

text_to_number_map2 = {'возможно спокойное': 1, 'возможно спокойное с отдельными периодами неустойчивости': 12,
                       'возможно неустойчивое': 2,
                       'возможно неустойчивое с отдельными (слабо) возмущенными периодами': 23,
                       'возможно слабо возмущенное': 3,
                       'возможно слабо возмущенное (с отдельными умеренно возмущенными периодами)': 34,
                       'возможно умеренно возмущенное': 4,
                       'возможно умеренно возмущенное (с отдельными сильно возмущенными периодами)': 45,
                       'возможно сильно возмущенное': 5,
                       'ожидается спокойное': 1, 'ожидается спокойное с отдельными периодами неустойчивости': 12,
                       'ожидается неустойчивое': 2,
                       'ожидается неустойчивое с отдельными (слабо) возмущенными периодами': 23,
                       'ожидается слабо возмущенное': 3,
                       'ожидается слабо возмущенное (с отдельными умеренно возмущенными периодами)': 34,
                       'ожидается умеренно возмущенное': 4,
                       'ожидается умеренно возмущенное (с отдельными сильно возмущенными периодами)': 45,
                       }

DAY = 31


class WeatherApp:
    def __init__(self, root):
        """
        Конструктор класса WeatherApp. Инициализирует основные компоненты приложения.

        :param root: корневой виджет приложения Tkinter
        """
        self.root = root
        self.root.title("Приложение - Оправдываемость")
        self.root.resizable(width=False, height=False)
        self.font_size = 12
        self.station_data = {}

        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', self.font_size))
        self.style.configure('TLabel', font=('Arial', self.font_size))
        self.style.configure('TCombobox', font=('Arial', self.font_size))
        self.style.configure('TEntry', font=('Arial', self.font_size))

        self.error_price_possible = Fraction(1, 3)
        self.error_price_expected = Fraction(2, 3)

        self.create_widgets()

        self.load_station_data("Визе")
        self.load_month()

    def create_widgets(self):
        """
        Создает виджеты приложения.
        """
        self.entry_var3 = [ttk.Entry(self.root, textvariable=tk.DoubleVar()) for _ in range(DAY)]
        self.total_probability_var = tk.DoubleVar()

        ttk.Label(self.root, text="Станция").grid(row=0, column=0)
        ttk.Label(self.root, text="Месяц").grid(row=0, column=1)
        ttk.Label(self.root, text="Число").grid(row=0, column=2)
        ttk.Label(self.root, text="Прогноз").grid(row=0, column=3)
        ttk.Label(self.root, text="Факт").grid(row=0, column=4)
        ttk.Label(self.root, text="Вероятность").grid(row=0, column=5)

        self.combo_station = ttk.Combobox(self.root, values=["Визе", "Диксон", "Амдерма", "Ловозеро"])
        self.combo_station.grid(row=1, column=0)
        self.combo_station.set("Визе")
        self.combo_station.bind("<<ComboboxSelected>>", self.load_station_data_on_select)

        self.combo_month = ttk.Combobox(self.root,
                                        values=["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август",
                                                "Сентябрь",
                                                "Октябрь", "Ноябрь", "Декабрь"])
        self.combo_month.grid(row=1, column=1)
        self.combo_month.set("Январь")
        self.combo_month.bind("<<ComboboxSelected>>", self.update_month)

        self.combo_var1 = [ttk.Combobox(self.root, values=list(text_to_number_map2.keys())) for _ in range(DAY)]
        self.combo_var2 = [ttk.Combobox(self.root, values=list(text_to_number_map1.keys())) for _ in range(DAY)]

        for row in range(1, DAY + 1):
            ttk.Label(self.root, text=str(row)).grid(row=row, column=2)
            self.combo_var1[row - 1].grid(row=row, column=3)
            self.set_combo_width(self.combo_var1[row - 1], text_to_number_map2)

            self.combo_var2[row - 1].grid(row=row, column=4)
            self.set_combo_width(self.combo_var2[row - 1], text_to_number_map1)

            self.entry_var3[row - 1].grid(row=row, column=5)

        ttk.Button(self.root, text="Проверить вероятность", command=self.check_probability).grid(row=32, column=0,
                                                                                                 columnspan=6)
        ttk.Button(self.root, text="Завершить", command=self.update_information).grid(row=33, column=5, columnspan=6)

        ttk.Button(self.root, text="Сохранить", command=self.save_data_to_file).grid(row=33, column=0, columnspan=6)

    def load_month(self):
        """
        Загружает выбранный месяц из файла при инициализации приложения.
        """
        station = self.combo_station.get()
        try:
            with open(f"{station}_month.json", "r") as file:
                data = json.load(file)
                month = data.get("month", "Январь")
                self.combo_month.set(month)
                self.update_month(None)
        except FileNotFoundError:
            pass

    def finish_and_update_information(self):
        """
        Завершает и обновляет информацию о погоде.
        """
        massiv_station = ('Визе', 'Диксон', 'Амдерма', 'Ловозеро')

        for station in massiv_station:
            self.combo_station.set(station)
            self.update_information()

    def save_data_to_file(self):
        """
        Сохраняет данные о погоде в файл.
        """
        station = self.combo_station.get()
        self.save_month()  # Сохраняем выбранный месяц
        self.save_station_data(station)

    def save_month(self):
        """
        Сохраняет выбранный месяц в файл.
        """
        station = self.combo_station.get()
        month = self.combo_month.get()  # Получаем выбранный месяц
        with open(f"{station}_month.json", "w") as file:  # Сохраняем месяц в файл
            json.dump({"month": month}, file)

    def load_station_data_on_select(self, event):
        """
        Загружает данные о погоде для выбранной станции.
        """
        station = self.combo_station.get()
        self.load_station_data(station)

    def load_station_data(self, station):
        """
        Загружает данные о погоде для указанной станции из файла.
        """
        # Очищаем данные перед загрузкой новых
        for combo1, combo2, entry in zip(self.combo_var1, self.combo_var2, self.entry_var3):
            combo1.set('')
            combo2.set('')
            entry.delete(0, tk.END)
        try:
            with open(f"{station}_data.json", "r") as file:
                data = json.load(file)
                for i, value in enumerate(data["combo_var1"]):
                    self.combo_var1[i].set(value)
                for i, value in enumerate(data["combo_var2"]):
                    self.combo_var2[i].set(value)
                for i, value in enumerate(data["entry_var3"]):
                    self.entry_var3[i].insert(0, value)
                self.combo_station.set(station)
        except FileNotFoundError:
            pass  # Если файл данных для станции не найден, просто пропустить

    def update_month(self, event):
        """
        Обновляет видимость комбобоксов в зависимости от выбранного месяца.
        """
        month = self.combo_month.get()
        year = datetime.now().year
        day = self.get_days_in_month(month, year)

        for row in range(1, DAY + 1):
            if row <= day:
                self.combo_var1[row - 1].grid()
                self.combo_var2[row - 1].grid()
                self.entry_var3[row - 1].grid()
            else:
                self.combo_var1[row - 1].grid_remove()
                self.combo_var2[row - 1].grid_remove()
                self.entry_var3[row - 1].grid_remove()
                self.combo_var1[row - 1].set('')
                self.combo_var2[row - 1].set('')
                self.entry_var3[row - 1].delete(0, tk.END)

    def save_station_data(self, station):
        """
        Сохраняет данные о погоде для указанной станции в файл.
        """
        data = {
            "combo_var1": [combo.get() for combo in self.combo_var1],
            "combo_var2": [combo.get() for combo in self.combo_var2],
            "entry_var3": [entry.get() for entry in self.entry_var3]
        }
        with open(f"{station}_data.json", "w") as file:
            json.dump(data, file)

    def get_days_in_month(self, month, year):
        """
        Определяет количество дней в указанном месяце.
        """
        if month in ["Январь", "Март", "Май", "Июль", "Август", "Октябрь", "Декабрь"]:
            return 31
        elif month in ["Апрель", "Июнь", "Сентябрь", "Ноябрь"]:
            return 30
        elif month == "Февраль":
            return 29 if self.is_leap_year(year) else 28

    def is_leap_year(self, year):
        """
        Проверяет, является ли год високосным.
        """
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return True
        return False

    def set_combo_width(self, combo, text_to_number_map):
        """
        Устанавливает ширину комбобокса в зависимости от максимальной длины элемента.
        """
        max_length = max(len(word) for word in text_to_number_map.keys())
        combo.config(width=max_length + 1)

    def check_probability(self):
        """
        Проверяет вероятность прогноза погоды и вычисляет ошибку.
        """
        forecast_results = []
        massive_true_forecast = []
        expected_list = []

        for row in range(1, DAY + 1):
            text_value1 = self.combo_var1[row - 1].get()
            text_value2 = self.combo_var2[row - 1].get()

            value1 = text_to_number_map2.get(text_value1, -1)
            value2 = text_to_number_map1.get(text_value2, -1)

            forecast_results.append(value1)
            massive_true_forecast.append(value2)

            if text_value1.startswith('ожидается'):
                expected = 1
            elif text_value1.startswith('возможно'):
                expected = 0
            else:
                expected = 2

            expected_list.append(expected)
            expected2 = 0.0

            if value2 == value1 or value1 // 10 == value2:
                expected2 = 1.0
            elif len(str(value1)) == 2 and len(str(value2)) == 1 and (value1 // 10) + 1 < value2:
                expected2 = 0.0
            elif (value1 % 10) == (value1 // 10) + value2:
                expected2 = 0.0
            elif len(str(value1)) == 1 and len(str(value2)) == 1:
                if expected == 1:
                    if value2 == value1 - 1:
                        expected2 = self.error_price_expected
                    elif value2 == value1 + 1:
                        expected2 = self.error_price_possible
                else:
                    if value2 == value1 - 1:
                        expected2 = self.error_price_possible
                    elif value2 == value1 + 1:
                        expected2 = self.error_price_expected
            elif len(str(value1)) == 2 and len(str(value2)) == 2:
                if expected == 1:
                    if (value1 // 10 + value1 % 10) / 2 < (value2 // 10 + value2 % 10) / 2:
                        expected2 = self.error_price_possible
                    else:
                        expected2 = self.error_price_expected
                else:
                    if (value1 // 10 + value1 % 10) / 2 < (value2 // 10 + value2 % 10) / 2:
                        expected2 = self.error_price_expected
                    else:
                        expected2 = self.error_price_possible
            elif len(str(value1)) == 2:
                if expected == 0:
                    if (value1 // 10 + value1 % 10) / 2 > value2 or value1 % 10 == value2:
                        expected2 = self.error_price_expected
                    else:
                        expected2 = self.error_price_possible
                else:
                    if (value2 // 10 + value2 % 10) / 2 > value1:
                        expected2 = self.error_price_expected
                    else:
                        expected2 = self.error_price_possible
            elif len(str(value2)) == 2:
                if expected == 0:
                    if (value1 // 10 + value1 % 10) / 2 > value2 or value2 % 10 == value1:
                        expected2 = self.error_price_possible
                    else:
                        expected2 = self.error_price_expected
                else:
                    if (value1 // 10 + value1 % 10) / 2 > value2:
                        expected2 = self.error_price_possible
                    else:
                        expected2 = self.error_price_expected
            else:
                expected2 = 0.0

            if not text_value1 or not text_value2:
                expected2 = 0.0

            self.entry_var3[row - 1].delete(0, tk.END)
            self.entry_var3[row - 1].insert(0, str(expected2))

        self.update_total_probability()

    def update_total_probability(self):
        """
        Обновляет общую вероятность на основе введенных данных.
        """
        total_probability = sum(Fraction(self.entry_var3[i].get()) for i in range(DAY))
        self.total_probability_var.set(float(total_probability))

    def update_information(self):
        """
        Обновляет информацию о погоде и вычисляет среднюю вероятность для всех станций.
        """
        global all_a_index

        # Сохраняем состояние текущей станции
        current_station = self.combo_station.get()

        # Получаем текущий месяц
        month = self.combo_month.get()
        year = datetime.now().year
        day = self.get_days_in_month(month, year)

        # Определяем видимые комбобоксы для текущего месяца
        visible_combobox_indexes = [i for i in range(1, DAY + 1) if i <= day]

        # Проверка наличия пустых значений в комбобоксах прогноз, факт и текстовом поле вероятности
        for index in visible_combobox_indexes:
            combo1_value = self.combo_var1[index - 1].get()
            combo2_value = self.combo_var2[index - 1].get()
            entry_value = self.entry_var3[index - 1].get()

            if not combo1_value or not combo2_value or not entry_value:
                messagebox.showerror("Error", "Заполните все поля прогноза, факта и вероятности перед завершением.")
                return

        # Продолжаем обновление информации как и прежде
        filled_entries = [entry.get() for entry in self.entry_var3 if entry.get()]

        self.load_station_data("Визе")
        self.combo_station.set("Визе")

        filled_entries = [entry.get() for entry in self.entry_var3 if entry.get()]

        # Словарь для замены значений вероятностей
        probability_replacements = {'1/3': 1 / 3, '2/3': 2 / 3, '1.0': 1.0, '0.0': 0.0, '1': 1.0, '0': 0.0}

        probability_array = [float(probability_replacements.get(entry, 0.0)) for entry in filled_entries]

        # Определяем количество дней в текущем месяце
        day = len(visible_combobox_indexes)

        a_index = sum(probability_array) / day

        self.total_probability_var.set(a_index)

        messagebox.showinfo("Info", f"Вероятность за месяц станции Визе = {a_index}.")
        all_a_index += a_index

        massiv_station = ["Диксон", "Амдерма", "Ловозеро"]

        for station in massiv_station:
            self.combo_station.current((self.combo_station.current() + 1) % len(self.combo_station["values"]))
            self.load_station_data(station)

            filled_entries = [entry.get() for entry in self.entry_var3 if entry.get()]

            probability_array = [float(probability_replacements.get(entry, 0.0)) for entry in filled_entries]

            a_index = sum(probability_array) / day

            self.total_probability_var.set(a_index)

            messagebox.showinfo("Info", f"Вероятность за месяц станции {station} = {a_index}.")
            all_a_index += a_index

        messagebox.showinfo("Info",
                            f"Вероятность по всем 4 станциям = {all_a_index / 4}. В процентах: {all_a_index / 4 * 100} %")

        root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()