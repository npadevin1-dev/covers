import json
import os
import subprocess
import time # Добавили модуль для работы со временем

DB_FILE = "/storage/emulated/0/Download/CoverRepo/songs.json"
REPO_DIR = "/storage/emulated/0/Download/CoverRepo"
SITE_URL = "https://npadevin1-dev.github.io/covers/"

def load_songs():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_songs(songs):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(songs, f, indent=4, ensure_ascii=False)

def open_browser():
    # Генерируем уникальный хвост на основе текущего времени (оптимизация против кэша)
    nocache_url = f"{SITE_URL}?t={int(time.time())}"
    print(f"Открываю браузер (кэш сброшен): {nocache_url}")
    subprocess.run(["termux-open", nocache_url], check=False)

def sync_to_github():
    print("\nСинхронизация с сервером...")
    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Обновление списка песен"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("Изменения успешно отправлены на сайт!\n")

def main():
    while True:
        print("\n--- ПАНЕЛЬ УПРАВЛЕНИЯ САЙТОМ ---")
        print("1. Посмотреть список песен")
        print("2. Добавить новую песню")
        print("3. Удалить песню")
        print("4. Перейти на сайт (открыть в браузере)")
        print("0. Выход")
        
        choice = input("Выберите действие: ")
        songs = load_songs()
        
        if choice == '1':
            print("\n--- ДОБАВЛЕННЫЕ ПЕСНИ ---")
            if not songs:
                print("Список пуст.")
            for i, s in enumerate(songs, 1):
                print(f"{i}. '{s['title']}' — {s['author']}")
                
        elif choice == '2':
            print("\n--- ДОБАВЛЕНИЕ ---")
            title = input("Название песни: ").strip()
            author = input("Автор: ").strip()
            url = input("Ссылка на Dropbox: ").strip()
            
            if not title:
                print("Название не может быть пустым.")
                continue
                
            songs.append({"title": title, "author": author, "url": url})
            save_songs(songs)
            print(f"Песня '{title}' добавлена.")
            sync_to_github()
            
            check_site = input("Открыть сайт в браузере для проверки? (y/n): ").strip().lower()
            if check_site == 'y' or check_site == 'н':
                print("Подожди 10 секунд, чтобы сервер GitHub успел принять файлы...")
                time.sleep(10) # Небольшая пауза, чтобы изменения успели примениться на GitHub
                open_browser()
                
        elif choice == '3':
            print("\n--- УДАЛЕНИЕ ---")
            if not songs:
                print("На сайте пока нет песен для удаления.")
                continue
                
            print("Выберите номер песни, которую нужно удалить:")
            for i, s in enumerate(songs, 1):
                print(f"{i}. '{s['title']}' — {s['author']}")
            print("0. Отмена")
            
            try:
                idx = int(input("\nВведите номер: "))
                if idx == 0:
                    print("Удаление отменено.")
                    continue
                if 1 <= idx <= len(songs):
                    removed_song = songs.pop(idx - 1)
                    save_songs(songs)
                    print(f"Песня '{removed_song['title']}' успешно удалена!")
                    sync_to_github()
                else:
                    print("Неверный номер.")
            except ValueError:
                print("Ошибка: нужно ввести число.")
                
        elif choice == '4':
            open_browser()
            
        elif choice == '0':
            break
        else:
            print("Неверная команда.")

if __name__ == "__main__":
    main()
