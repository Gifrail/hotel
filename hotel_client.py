import mysql.connector
from mysql.connector import Error
import datetime

class HotelDB:
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='I143214303p',
                database='hotel_db'
            )
            if self.connection.is_connected():
                print("Успешное подключение к базе данных")
                return True
        except Error as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Отключено от базы данных")
    
    def get_available_rooms(self, start_date, end_date):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT r.* FROM rooms r
                WHERE r.is_available = TRUE
                AND r.room_id NOT IN (
                    SELECT b.room_id FROM bookings b
                    WHERE (
                        (b.check_in_date < %s AND b.check_out_date > %s) OR
                        (b.check_in_date BETWEEN %s AND %s) OR
                        (b.check_out_date BETWEEN %s AND %s)
                    )
                    AND b.booking_status = 'confirmed'
                )
            """
            cursor.execute(query, (end_date, start_date, start_date, end_date, start_date, end_date))
            return cursor.fetchall()
        except Error as e:
            print(f"Ошибка поиска номеров: {e}")
            return []
    
    def add_booking(self, client_id, room_id, check_in, check_out):
        try:
            cursor = self.connection.cursor()
            
            # Проверка доступности номера
            available = self.get_available_rooms(check_in, check_out)
            if not any(room['room_id'] == room_id for room in available):
                print("Номер недоступен на выбранные даты")
                return False
            
            # Расчет стоимости
            cursor.execute("SELECT price_per_night FROM rooms WHERE room_id = %s", (room_id,))
            price = cursor.fetchone()[0]
            nights = (check_out - check_in).days
            total = price * nights
            
            # Добавление брони
            cursor.execute(
                "INSERT INTO bookings (client_id, room_id, check_in_date, check_out_date, total_price) "
                "VALUES (%s, %s, %s, %s, %s)",
                (client_id, room_id, check_in, check_out, total)
            )
            self.connection.commit()
            print(f"Бронирование создано. Стоимость: {total} руб.")
            return True
        except Error as e:
            print(f"Ошибка бронирования: {e}")
            self.connection.rollback()
            return False

def main():
    db = HotelDB()
    if not db.connect():
        return
    
    try:
        while True:
            print("\nМеню:")
            print("1. Найти свободные номера")
            print("2. Создать бронирование")
            print("0. Выход")
            
            choice = input("Выберите действие: ")
            
            if choice == "1":
                print("\nПоиск свободных номеров")
                start = input("Дата заезда (ГГГГ-ММ-ДД): ")
                end = input("Дата выезда (ГГГГ-ММ-ДД): ")
                
                try:
                    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
                    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
                    
                    rooms = db.get_available_rooms(start_date, end_date)
                    print("\nДоступные номера:")
                    for room in rooms:
                        print(f"№{room['room_number']} ({room['room_type']}) - {room['price_per_night']} руб./ночь")
                except ValueError:
                    print("Неверный формат даты")
            
            elif choice == "2":
                print("\nНовое бронирование")
                client_id = input("ID клиента: ")
                room_id = input("ID номера: ")
                start = input("Дата заезда (ГГГГ-ММ-ДД): ")
                end = input("Дата выезда (ГГГГ-ММ-ДД): ")
                
                try:
                    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
                    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
                    db.add_booking(int(client_id), int(room_id), start_date, end_date)
                except (ValueError, TypeError):
                    print("Ошибка ввода данных")
            
            elif choice == "0":
                break
            
            else:
                print("Неверный выбор")
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()