@echo off
:: ==============================================
:: Автоматическая установка системы гостиницы
:: ==============================================

:: 1. Установка MySQL Connector/Python
echo Устанавливаем mysql-connector-python...
pip install mysql-connector-python

:: 2. Инициализация базы данных
echo Создаем базу данных и таблицы...
python hotel_init.py

:: 3. Проверка подключения
echo Проверяем подключение к MySQL...
mysql -u root -pI143214303p -e "USE hotel_db; SHOW TABLES;" || (
    echo ОШИБКА! Не удалось подключиться к MySQL
    pause
    exit /b
)

:: 4. Запуск приложения
echo Запускаем графический интерфейс...
start python hotel_gui.py

echo Установка завершена успешно!
pause