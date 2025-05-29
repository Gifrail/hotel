import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Подключение к серверу MySQL без указания базы данных
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Создаем базу данных
            cursor.execute("CREATE DATABASE IF NOT EXISTS hotel_db")
            print("База данных hotel_db создана или уже существует")
            
            # Подключаемся к созданной базе данных
            cursor.execute("USE hotel_db")
            
            # Создаем таблицы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    passport_number VARCHAR(20) UNIQUE NOT NULL,
                    phone_number VARCHAR(15),
                    email VARCHAR(50)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id INT AUTO_INCREMENT PRIMARY KEY,
                    room_number VARCHAR(10) UNIQUE NOT NULL,
                    room_type VARCHAR(30) NOT NULL,
                    price_per_night DECIMAL(10, 2) NOT NULL,
                    capacity INT NOT NULL,
                    description TEXT,
                    is_available BOOLEAN DEFAULT TRUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    booking_id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id INT NOT NULL,
                    room_id INT NOT NULL,
                    check_in_date DATE NOT NULL,
                    check_out_date DATE NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    booking_status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
                    FOREIGN KEY (client_id) REFERENCES clients(client_id),
                    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
                )
            """)
            
            # Добавляем тестовые данные
            cursor.execute("SELECT COUNT(*) FROM clients")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO clients (first_name, last_name, passport_number, phone_number, email)
                    VALUES 
                        ('Иван', 'Иванов', '1234567890', '+79101234567', 'ivan@example.com'),
                        ('Петр', 'Петров', '0987654321', '+79107654321', 'petr@example.com')
                """)
                
                cursor.execute("""
                    INSERT INTO rooms (room_number, room_type, price_per_night, capacity, description)
                    VALUES
                        ('101', 'Стандартный', 2500.00, 2, 'Номер с одной кроватью'),
                        ('201', 'Люкс', 5000.00, 2, 'Просторный номер с гостиной')
                """)
            
            connection.commit()
            print("Таблицы и тестовые данные успешно созданы")
            
    except Error as e:
        print(f"Ошибка: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Соединение закрыто")

if __name__ == "__main__":
    print("Инициализация базы данных гостиницы...")
    create_database()