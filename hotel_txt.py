import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления гостиницей (TXT-версия)")
        self.root.geometry("1000x700")
        
        # Инициализируем статусную переменную в самом начале
        self.status_var = tk.StringVar()
        self.status_var.set("Инициализация...")
        
        # Создаем папку для данных
        self.data_dir = "hotel_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Файлы для хранения данных
        self.clients_file = os.path.join(self.data_dir, "clients.txt")
        self.rooms_file = os.path.join(self.data_dir, "rooms.txt")
        self.bookings_file = os.path.join(self.data_dir, "bookings.txt")
        
        # Инициализируем файлы данных
        self.init_files()
        
        # Создаем GUI
        self.create_gui()
        
        # Загружаем начальные данные
        self.refresh_all()
    
    def init_files(self):
        """Создает файлы с заголовками, если их нет"""
        if not os.path.exists(self.clients_file):
            with open(self.clients_file, 'w', encoding='utf-8') as f:
                f.write("ID|Имя|Фамилия|Паспорт|Телефон|Email\n")
        
        if not os.path.exists(self.rooms_file):
            with open(self.rooms_file, 'w', encoding='utf-8') as f:
                f.write("ID|Номер|Тип|Цена|Вместимость|Статус|Описание\n")
            # Добавляем тестовые номера
            test_rooms = [
                "1|101|Стандартный|2500|2|Свободен|Номер с одной кроватью",
                "2|201|Люкс|5000|2|Свободен|Просторный номер с гостиной"
            ]
            with open(self.rooms_file, 'a', encoding='utf-8') as f:
                f.write("\n".join(test_rooms) + "\n")
        
        if not os.path.exists(self.bookings_file):
            with open(self.bookings_file, 'w', encoding='utf-8') as f:
                f.write("ID|ID_Клиента|ID_Номера|Заезд|Выезд|Стоимость|Статус\n")
    
    def load_data(self, filename):
        """Загружает данные из файла в список словарей"""
        data = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                headers = f.readline().strip().split('|')
                for line in f:
                    values = line.strip().split('|')
                    if len(values) == len(headers):
                        data.append(dict(zip(headers, values)))
        return data
    
    def save_data(self, filename, headers, data):
        """Сохраняет данные в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("|".join(headers) + "\n")
            for item in data:
                f.write("|".join(str(item[h]) for h in headers) + "\n")
    
    def create_gui(self):
        """Создает графический интерфейс"""
        # Создаем статус-бар внизу окна
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка клиентов
        self.create_clients_tab()
        
        # Вкладка номеров
        self.create_rooms_tab()
        
        # Вкладка бронирований
        self.create_bookings_tab()
    
    def refresh_all(self):
        """Обновляет все вкладки"""
        self.refresh_clients()
        self.refresh_rooms()
        self.refresh_bookings()
        self.update_status("Готово")
    
    def update_status(self, message):
        """Обновляет статусную строку"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def create_clients_tab(self):
        """Создает вкладку для работы с клиентами"""
        self.clients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_tab, text="Клиенты")
        
        # Таблица клиентов
        self.clients_tree = ttk.Treeview(self.clients_tab, 
                                       columns=("ID", "Имя", "Фамилия", "Паспорт", "Телефон", "Email"), 
                                       show="headings")
        
        # Настраиваем колонки
        for col in ("ID", "Имя", "Фамилия", "Паспорт", "Телефон", "Email"):
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)
        
        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.clients_tab, orient="vertical", command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем элементы
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель кнопок
        btn_frame = tk.Frame(self.clients_tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_client).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_clients).pack(side=tk.LEFT, padx=5)
    
    def refresh_clients(self):
        """Обновляет список клиентов"""
        self.update_status("Загрузка клиентов...")
        
        # Очищаем таблицу
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        # Загружаем данные
        clients = self.load_data(self.clients_file)
        
        # Заполняем таблицу
        for client in clients:
            self.clients_tree.insert("", tk.END, values=(
                client.get("ID", ""),
                client.get("Имя", ""),
                client.get("Фамилия", ""),
                client.get("Паспорт", ""),
                client.get("Телефон", ""),
                client.get("Email", "")
            ))
        
        self.update_status(f"Загружено {len(clients)} клиентов")
    
    def add_client(self):
        """Добавляет нового клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        fields = [
            ("Имя", "first_name"),
            ("Фамилия", "last_name"),
            ("Номер паспорта", "passport"),
            ("Телефон", "phone"),
            ("Email", "email")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            tk.Label(dialog, text=label+":").grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entries[name] = tk.Entry(dialog)
            entries[name].grid(row=i, column=1, padx=5, pady=5)
        
        def save():
            # Проверяем заполненность полей
            if not all(entry.get() for entry in entries.values()):
                messagebox.showwarning("Ошибка", "Все поля должны быть заполнены")
                return
            
            # Генерируем ID
            clients = self.load_data(self.clients_file)
            new_id = max(int(c["ID"]) for c in clients) + 1 if clients else 1
            
            # Создаем нового клиента
            new_client = {
                "ID": str(new_id),
                "Имя": entries["first_name"].get(),
                "Фамилия": entries["last_name"].get(),
                "Паспорт": entries["passport"].get(),
                "Телефон": entries["phone"].get(),
                "Email": entries["email"].get()
            }
            
            # Сохраняем
            clients.append(new_client)
            self.save_data(self.clients_file, ["ID", "Имя", "Фамилия", "Паспорт", "Телефон", "Email"], clients)
            
            # Обновляем интерфейс
            self.refresh_clients()
            dialog.destroy()
            messagebox.showinfo("Успех", "Клиент успешно добавлен")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), columnspan=2, pady=10)
    
    # Аналогичные методы для номеров и бронирований
    def create_rooms_tab(self):
        """Создает вкладку для работы с номерами"""
        self.rooms_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.rooms_tab, text="Номера")
        
        # Таблица номеров
        self.rooms_tree = ttk.Treeview(self.rooms_tab, 
                                     columns=("ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"), 
                                     show="headings")
        
        for col in ("ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"):
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.rooms_tab, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = tk.Frame(self.rooms_tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_room).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_rooms).pack(side=tk.LEFT, padx=5)
    
    def refresh_rooms(self):
        """Обновляет список номеров"""
        self.update_status("Загрузка номеров...")
        
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        rooms = self.load_data(self.rooms_file)
        for room in rooms:
            self.rooms_tree.insert("", tk.END, values=(
                room.get("ID", ""),
                room.get("Номер", ""),
                room.get("Тип", ""),
                room.get("Цена", ""),
                room.get("Вместимость", ""),
                room.get("Статус", ""),
                room.get("Описание", "")
            ))
        
        self.update_status(f"Загружено {len(rooms)} номеров")
    
    def add_room(self):
        """Добавляет новый номер"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить номер")
        dialog.transient(self.root)
        dialog.grab_set()
        
        fields = [
            ("Номер", "number"),
            ("Тип", "type"),
            ("Цена за ночь", "price"),
            ("Вместимость", "capacity"),
            ("Описание", "description")
        ]
        
        entries = {}
        for i, (label, name) in enumerate(fields):
            tk.Label(dialog, text=label+":").grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entries[name] = tk.Entry(dialog)
            entries[name].grid(row=i, column=1, padx=5, pady=5)
        
        # Устанавливаем значения по умолчанию
        entries["type"].insert(0, "Стандартный")
        entries["capacity"].insert(0, "2")
        
        def save():
            try:
                # Проверяем данные
                if not all(entry.get() for name, entry in entries.items() if name != "description"):
                    messagebox.showwarning("Ошибка", "Обязательные поля не заполнены")
                    return
                
                # Генерируем ID
                rooms = self.load_data(self.rooms_file)
                new_id = max(int(r["ID"]) for r in rooms) + 1 if rooms else 1
                
                # Создаем новый номер
                new_room = {
                    "ID": str(new_id),
                    "Номер": entries["number"].get(),
                    "Тип": entries["type"].get(),
                    "Цена": entries["price"].get(),
                    "Вместимость": entries["capacity"].get(),
                    "Статус": "Свободен",
                    "Описание": entries["description"].get()
                }
                
                # Сохраняем
                rooms.append(new_room)
                self.save_data(self.rooms_file, ["ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"], rooms)
                
                # Обновляем интерфейс
                self.refresh_rooms()
                dialog.destroy()
                messagebox.showinfo("Успех", "Номер успешно добавлен")
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность ввода числовых значений")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), columnspan=2, pady=10)
    
    def create_bookings_tab(self):
        """Создает вкладку для работы с бронированиями"""
        self.bookings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bookings_tab, text="Бронирования")
        
        # Таблица бронирований
        self.bookings_tree = ttk.Treeview(self.bookings_tab, 
                                        columns=("ID", "Клиент", "Номер", "Заезд", "Выезд", "Стоимость", "Статус"), 
                                        show="headings")
        
        for col in ("ID", "Клиент", "Номер", "Заезд", "Выезд", "Стоимость", "Статус"):
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(self.bookings_tab, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_frame = tk.Frame(self.bookings_tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_booking).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отменить", command=self.cancel_booking).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_bookings).pack(side=tk.LEFT, padx=5)
    
    def refresh_bookings(self):
        """Обновляет список бронирований"""
        self.update_status("Загрузка бронирований...")
        
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        
        bookings = self.load_data(self.bookings_file)
        clients = {c["ID"]: f"{c['Имя']} {c['Фамилия']}" for c in self.load_data(self.clients_file)}
        rooms = {r["ID"]: r["Номер"] for r in self.load_data(self.rooms_file)}
        
        for booking in bookings:
            self.bookings_tree.insert("", tk.END, values=(
                booking.get("ID", ""),
                clients.get(booking.get("ID_Клиента", ""), "?"),
                rooms.get(booking.get("ID_Номера", ""), "?"),
                booking.get("Заезд", ""),
                booking.get("Выезд", ""),
                booking.get("Стоимость", ""),
                booking.get("Статус", "")
            ))
        
        self.update_status(f"Загружено {len(bookings)} бронирований")
    
    def add_booking(self):
        """Добавляет новое бронирование"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новое бронирование")
        dialog.transient(self.root)
        dialog.grab_set()
        
        try:
            # Загружаем клиентов и свободные номера
            clients = self.load_data(self.clients_file)
            rooms = [r for r in self.load_data(self.rooms_file) if r.get("Статус") == "Свободен"]
            
            if not clients:
                messagebox.showerror("Ошибка", "Нет клиентов для бронирования")
                dialog.destroy()
                return
            
            if not rooms:
                messagebox.showerror("Ошибка", "Нет свободных номеров")
                dialog.destroy()
                return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            dialog.destroy()
            return
        
        # Поля формы
        tk.Label(dialog, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        client_var = tk.StringVar()
        client_combobox = ttk.Combobox(dialog, textvariable=client_var, state="readonly")
        client_combobox['values'] = [f"{c['Имя']} {c['Фамилия']} (ID: {c['ID']})" for c in clients]
        client_combobox.grid(row=0, column=1, padx=5, pady=5)
        client_combobox.current(0)
        
        tk.Label(dialog, text="Номер:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        room_var = tk.StringVar()
        room_combobox = ttk.Combobox(dialog, textvariable=room_var, state="readonly")
        room_combobox['values'] = [f"{r['Тип']} №{r['Номер']} (ID: {r['ID']})" for r in rooms]
        room_combobox.grid(row=1, column=1, padx=5, pady=5)
        room_combobox.current(0)
        
        tk.Label(dialog, text="Дата заезда:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        check_in_entry = tk.Entry(dialog)
        check_in_entry.grid(row=2, column=1, padx=5, pady=5)
        check_in_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(dialog, text="Дата выезда:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        check_out_entry = tk.Entry(dialog)
        check_out_entry.grid(row=3, column=1, padx=5, pady=5)
        check_out_entry.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        
        def save():
            try:
                # Извлекаем ID из выбранных значений
                client_id = client_combobox.get().split("(ID: ")[1][:-1]
                room_id = room_combobox.get().split("(ID: ")[1][:-1]
                
                # Проверяем даты
                check_in = datetime.strptime(check_in_entry.get(), "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_entry.get(), "%Y-%m-%d").date()
                
                if check_out <= check_in:
                    messagebox.showerror("Ошибка", "Дата выезда должна быть позже даты заезда")
                    return
                
                # Получаем цену номера
                rooms_data = self.load_data(self.rooms_file)
                room = next(r for r in rooms_data if r["ID"] == room_id)
                price = float(room["Цена"])
                nights = (check_out - check_in).days
                total = price * nights
                
                # Генерируем ID бронирования
                bookings = self.load_data(self.bookings_file)
                new_id = max(int(b["ID"]) for b in bookings) + 1 if bookings else 1
                
                # Создаем бронирование
                new_booking = {
                    "ID": str(new_id),
                    "ID_Клиента": client_id,
                    "ID_Номера": room_id,
                    "Заезд": check_in.strftime("%Y-%m-%d"),
                    "Выезд": check_out.strftime("%Y-%m-%d"),
                    "Стоимость": str(total),
                    "Статус": "Подтверждено"
                }
                
                # Обновляем статус номера
                for r in rooms_data:
                    if r["ID"] == room_id:
                        r["Статус"] = "Занят"
                
                # Сохраняем изменения
                bookings.append(new_booking)
                self.save_data(self.bookings_file, ["ID", "ID_Клиента", "ID_Номера", "Заезд", "Выезд", "Стоимость", "Статус"], bookings)
                self.save_data(self.rooms_file, ["ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"], rooms_data)
                
                # Обновляем интерфейс
                self.refresh_bookings()
                self.refresh_rooms()
                dialog.destroy()
                messagebox.showinfo("Успех", "Бронирование успешно создано")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать бронирование: {str(e)}")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=4, columnspan=2, pady=10)
    
    def cancel_booking(self):
        """Отменяет выбранное бронирование"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование для отмены")
            return
        
        booking_id = self.bookings_tree.item(selected[0])['values'][0]
        
        try:
            # Загружаем данные
            bookings = self.load_data(self.bookings_file)
            rooms = self.load_data(self.rooms_file)
            
            # Находим бронирование
            booking = next(b for b in bookings if b["ID"] == str(booking_id))
            
            # Обновляем статус
            booking["Статус"] = "Отменено"
            
            # Освобождаем номер, если нет других активных бронирований
            room_id = booking["ID_Номера"]
            active_bookings = [b for b in bookings 
                             if b["ID_Номера"] == room_id 
                             and b["Статус"] == "Подтверждено"
                             and b["ID"] != booking_id]
            
            if not active_bookings:
                for room in rooms:
                    if room["ID"] == room_id:
                        room["Статус"] = "Свободен"
            
            # Сохраняем изменения
            self.save_data(self.bookings_file, ["ID", "ID_Клиента", "ID_Номера", "Заезд", "Выезд", "Стоимость", "Статус"], bookings)
            self.save_data(self.rooms_file, ["ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"], rooms)
            
            # Обновляем интерфейс
            self.refresh_bookings()
            self.refresh_rooms()
            messagebox.showinfo("Успех", "Бронирование отменено")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отменить бронирование: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()