import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления гостиницей")
        self.root.geometry("1000x700")
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, 
                                 relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X)
        
        # Подключение к MySQL
        self.connection = self.connect_to_db()
        if not self.connection:
            root.destroy()
            return
        
        # Создаем GUI
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_clients_tab()
        self.create_rooms_tab()
        self.create_bookings_tab()
        
        self.update_status("Готово")
    
    def connect_to_db(self):
        """Подключение к MySQL без пароля"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='hotel_db'
            )
            self.update_status("Успешное подключение к MySQL")
            return conn
        except Error as e:
            messagebox.showerror("Ошибка", 
                f"Не удалось подключиться к MySQL:\n{e}\n\n"
                "Убедитесь, что:\n"
                "1. MySQL сервер запущен\n"
                "2. Пользователь 'root' имеет доступ без пароля\n"
                "3. База данных 'hotel_db' существует")
            return None
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def create_clients_tab(self):
        """Вкладка для работы с клиентами"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Клиенты")
        
        # Таблица клиентов
        self.clients_tree = ttk.Treeview(tab, columns=("ID", "Имя", "Фамилия", "Паспорт", "Телефон", "Email"), 
                                       show="headings")
        for col in ("ID", "Имя", "Фамилия", "Паспорт", "Телефон", "Email"):
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель кнопок
        btn_frame = tk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_client).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_clients).pack(side=tk.LEFT, padx=5)
        
        self.refresh_clients()
    
    def refresh_clients(self):
        """Обновление списка клиентов"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM clients")
            rows = cursor.fetchall()
            
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            for row in rows:
                self.clients_tree.insert("", tk.END, values=row)
            
            self.update_status(f"Загружено {len(rows)} клиентов")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {e}")
    
    def add_client(self):
        """Добавление нового клиента"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        
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
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO clients (first_name, last_name, passport_number, phone_number, email) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        entries["first_name"].get(),
                        entries["last_name"].get(),
                        entries["passport"].get(),
                        entries["phone"].get(),
                        entries["email"].get()
                    )
                )
                self.connection.commit()
                self.refresh_clients()
                dialog.destroy()
                messagebox.showinfo("Успех", "Клиент добавлен")
            except Error as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить клиента: {e}")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), columnspan=2, pady=10)
    
    def create_rooms_tab(self):
        """Вкладка для работы с номерами"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Номера")
        
        # Таблица номеров
        self.rooms_tree = ttk.Treeview(tab, columns=("ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"), 
                                     show="headings")
        for col in ("ID", "Номер", "Тип", "Цена", "Вместимость", "Статус", "Описание"):
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель кнопок
        btn_frame = tk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_room).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_rooms).pack(side=tk.LEFT, padx=5)
        
        self.refresh_rooms()
    
    def refresh_rooms(self):
        """Обновление списка номеров"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT room_id, room_number, room_type, price_per_night, capacity, 
                       CASE WHEN is_available THEN 'Свободен' ELSE 'Занят' END, description 
                FROM rooms
            """)
            rows = cursor.fetchall()
            
            for item in self.rooms_tree.get_children():
                self.rooms_tree.delete(item)
            
            for row in rows:
                self.rooms_tree.insert("", tk.END, values=row)
            
            self.update_status(f"Загружено {len(rows)} номеров")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить номера: {e}")
    
    def add_room(self):
        """Добавление нового номера"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить номер")
        
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
        
        # Значения по умолчанию
        entries["type"].insert(0, "Стандартный")
        entries["capacity"].insert(0, "2")
        
        def save():
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO rooms (room_number, room_type, price_per_night, capacity, description) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        entries["number"].get(),
                        entries["type"].get(),
                        float(entries["price"].get()),
                        int(entries["capacity"].get()),
                        entries["description"].get()
                    )
                )
                self.connection.commit()
                self.refresh_rooms()
                dialog.destroy()
                messagebox.showinfo("Успех", "Номер добавлен")
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность числовых значений")
            except Error as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить номер: {e}")
        
        tk.Button(dialog, text="Сохранить", command=save).grid(row=len(fields), columnspan=2, pady=10)
    
    def create_bookings_tab(self):
        """Вкладка для работы с бронированиями"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Бронирования")
        
        # Таблица бронирований
        self.bookings_tree = ttk.Treeview(tab, columns=("ID", "Клиент", "Номер", "Заезд", "Выезд", "Стоимость", "Статус"), 
                                        show="headings")
        for col in ("ID", "Клиент", "Номер", "Заезд", "Выезд", "Стоимость", "Статус"):
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель кнопок
        btn_frame = tk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Добавить", command=self.add_booking).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отменить", command=self.cancel_booking).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_bookings).pack(side=tk.LEFT, padx=5)
        
        self.refresh_bookings()
    
    def refresh_bookings(self):
        """Обновление списка бронирований"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.booking_id, 
                       CONCAT(c.first_name, ' ', c.last_name) AS client_name,
                       r.room_number,
                       b.check_in_date,
                       b.check_out_date,
                       b.total_price,
                       CASE 
                           WHEN b.booking_status = 'confirmed' THEN 'Подтверждено'
                           WHEN b.booking_status = 'cancelled' THEN 'Отменено'
                           ELSE 'Завершено'
                       END AS status
                FROM bookings b
                JOIN clients c ON b.client_id = c.client_id
                JOIN rooms r ON b.room_id = r.room_id
                ORDER BY b.check_in_date
            """)
            rows = cursor.fetchall()
            
            for item in self.bookings_tree.get_children():
                self.bookings_tree.delete(item)
            
            for row in rows:
                self.bookings_tree.insert("", tk.END, values=(
                    row["booking_id"],
                    row["client_name"],
                    row["room_number"],
                    row["check_in_date"],
                    row["check_out_date"],
                    row["total_price"],
                    row["status"]
                ))
            
            self.update_status(f"Загружено {len(rows)} бронирований")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить бронирования: {e}")
    
    def add_booking(self):
        """Добавление нового бронирования"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новое бронирование")
        dialog.geometry("400x300")
        
        try:
            # Загружаем клиентов и свободные номера
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT client_id, CONCAT(first_name, ' ', last_name) AS name FROM clients")
            clients = cursor.fetchall()
            
            cursor.execute("SELECT room_id, room_number FROM rooms WHERE is_available = TRUE")
            rooms = cursor.fetchall()
            
            if not clients:
                messagebox.showerror("Ошибка", "Нет клиентов для бронирования")
                dialog.destroy()
                return
            
            if not rooms:
                messagebox.showerror("Ошибка", "Нет свободных номеров")
                dialog.destroy()
                return
            
            # Поля формы
            tk.Label(dialog, text="Клиент:").pack(pady=5)
            client_var = tk.StringVar()
            client_combobox = ttk.Combobox(dialog, textvariable=client_var, state="readonly")
            client_combobox['values'] = [f"{c['name']} (ID: {c['client_id']})" for c in clients]
            client_combobox.pack(fill=tk.X, padx=10, pady=5)
            client_combobox.current(0)
            
            tk.Label(dialog, text="Номер:").pack(pady=5)
            room_var = tk.StringVar()
            room_combobox = ttk.Combobox(dialog, textvariable=room_var, state="readonly")
            room_combobox['values'] = [f"№{r['room_number']} (ID: {r['room_id']})" for r in rooms]
            room_combobox.pack(fill=tk.X, padx=10, pady=5)
            room_combobox.current(0)
            
            tk.Label(dialog, text="Дата заезда:").pack(pady=5)
            check_in_entry = tk.Entry(dialog)
            check_in_entry.pack(fill=tk.X, padx=10, pady=5)
            check_in_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            
            tk.Label(dialog, text="Дата выезда:").pack(pady=5)
            check_out_entry = tk.Entry(dialog)
            check_out_entry.pack(fill=tk.X, padx=10, pady=5)
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
                    
                    # Проверяем доступность номера
                    cursor.execute("""
                        SELECT COUNT(*) FROM bookings 
                        WHERE room_id = %s AND booking_status = 'confirmed'
                        AND (
                            (check_in_date < %s AND check_out_date > %s) OR
                            (check_in_date BETWEEN %s AND %s) OR
                            (check_out_date BETWEEN %s AND %s)
                        )
                    """, (room_id, check_out, check_in, check_in, check_out, check_in, check_out))
                    
                    if cursor.fetchone()[0] > 0:
                        messagebox.showerror("Ошибка", "Номер уже забронирован на выбранные даты")
                        return
                    
                    # Получаем цену номера
                    cursor.execute("SELECT price_per_night FROM rooms WHERE room_id = %s", (room_id,))
                    price = cursor.fetchone()[0]
                    nights = (check_out - check_in).days
                    total = price * nights
                    
                    # Создаем бронирование
                    cursor.execute("""
                        INSERT INTO bookings (client_id, room_id, check_in_date, check_out_date, total_price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (client_id, room_id, check_in, check_out, total))
                    
                    # Обновляем статус номера
                    cursor.execute("UPDATE rooms SET is_available = FALSE WHERE room_id = %s", (room_id,))
                    
                    self.connection.commit()
                    self.refresh_bookings()
                    self.refresh_rooms()
                    dialog.destroy()
                    messagebox.showinfo("Успех", "Бронирование создано")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать бронирование: {e}")
            
            tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
            
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            dialog.destroy()
    
    def cancel_booking(self):
        """Отмена бронирования"""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите бронирование для отмены")
            return
        
        booking_id = self.bookings_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите отменить бронирование?"):
            try:
                cursor = self.connection.cursor()
                
                # Получаем информацию о бронировании
                cursor.execute("SELECT room_id FROM bookings WHERE booking_id = %s", (booking_id,))
                room_id = cursor.fetchone()[0]
                
                # Отменяем бронирование
                cursor.execute("""
                    UPDATE bookings SET booking_status = 'cancelled' 
                    WHERE booking_id = %s
                """, (booking_id,))
                
                # Освобождаем номер, если нет других активных бронирований
                cursor.execute("""
                    UPDATE rooms SET is_available = TRUE 
                    WHERE room_id = %s AND NOT EXISTS (
                        SELECT 1 FROM bookings 
                        WHERE room_id = %s 
                        AND booking_status = 'confirmed'
                        AND check_out_date > CURDATE()
                    )
                """, (room_id, room_id))
                
                self.connection.commit()
                self.refresh_bookings()
                self.refresh_rooms()
                messagebox.showinfo("Успех", "Бронирование отменено")
            except Error as e:
                messagebox.showerror("Ошибка", f"Не удалось отменить бронирование: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()