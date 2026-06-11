#!/bin/bash

# Путь к твоей папке проекта
REPO_DIR="/storage/emulated/0/Download/CoverRepo"
BACKUP_DIR="$REPO_DIR/Backups"

# Создаем папку для бэкапов, если её ещё нет
mkdir -p "$BACKUP_DIR"

# Генерируем имя файла с текущей датой и временем
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/manager_backup_$TIMESTAMP.py"

# Проверяем, существует ли сам менеджер
if [ -f "$REPO_DIR/manager.py" ]; then
    cp "$REPO_DIR/manager.py" "$BACKUP_FILE"
    echo -e "\n✅ Локальное сохранение создано!"
    echo -e "Файл сохранен как: Backups/manager_backup_$TIMESTAMP.py"
else
    echo -e "\n❌ Ошибка: Файл manager.py не найден в папке проекта!"
fi
