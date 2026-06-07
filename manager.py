import json
import os
import subprocess
import time

DB_FILE = "/storage/emulated/0/Download/CoverRepo/songs.json"
REPO_DIR = "/storage/emulated/0/Download/CoverRepo"
SITE_URL = "https://npadevin1-dev.github.io/covers/"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"albums": [], "all_songs": []}
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if "albums" not in data: data["albums"] = []
            if "all_songs" not in data: data["all_songs"] = []
            return data
        except json.JSONDecodeError:
            return {"albums": [], "all_songs": []}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def open_browser():
    nocache_url = f"{SITE_URL}?t={int(time.time())}"
    print(f"Открываю браузер: {nocache_url}")
    subprocess.run(["termux-open", nocache_url], check=False)

def sync_to_github():
    print("\nСинхронизация с сервером GitHub...")
    os.chdir(REPO_DIR)
    subprocess.run(["git", "add", "."], check=False)
    subprocess.run(["git", "commit", "-m", "Обновление медиатеки"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("Изменения успешно отправлены на сайт!\n")

def main():
    while True:
        print("\n=== ЦЕНТРАЛЬНЫЙ СХРОН УПРАВЛЕНИЯ ===")
        print("1. Посмотреть ГЛОБАЛЬНЫЙ список песен (видишь только ты)")
        print("2. Добавить кавер в ГЛОБАЛЬНЫЙ список")
        print("3. Удалить кавер из ГЛОБАЛЬНОГО списка")
        print("---------------------------------------------")
        print("4. Список Альбомов")
        print("5. Создать НОВЫЙ Альбом")
        print("6. Редактировать Альбом (Добавить песню в него)")
        print("7. Удалить Альбом")
        print("---------------------------------------------")
        print("8. Перейти на сайт")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        data = load_data()
        
        if choice == '1':
            print("\n--- ВСЕ ТВОИ ЗАГРУЖЕННЫЕ ПЕСНИ ---")
            if not data["all_songs"]:
                print("Список пуст.")
            for i, s in enumerate(data["all_songs"], 1):
                print(f"{i}. '{s['title']}' — {s['author']}")
                
        elif choice == '2':
            print("\n--- ДОБАВЛЕНИЕ НОВОГО КАВЕРА ---")
            title = input("Название песни: ").strip()
            author = input("Автор/Исполнитель: ").strip()
            url = input("Ссылка на Dropbox: ").strip()
            if not title or not url:
                print("Ошибка: Название и ссылка обязательны.")
                continue
            data["all_songs"].append({"title": title, "author": author, "url": url})
            save_data(data)
            print(f"Песня '{title}' сохранена в глобальную базу.")
            sync_to_github()
            
        elif choice == '3':
            print("\n--- УДАЛЕНИЕ КАВЕРА ---")
            if not data["all_songs"]:
                print("Удалять нечего."); continue
            for i, s in enumerate(data["all_songs"], 1):
                print(f"{i}. '{s['title']}' — {s['author']}")
            try:
                idx = int(input("Введите номер трека для полного удаления: "))
                if 1 <= idx <= len(data["all_songs"]):
                    removed = data["all_songs"].pop(idx - 1)
                    # Также вычищаем песню из всех альбомов, где она могла быть
                    for alb in data["albums"]:
                        alb["songs"] = [s for s in alb["songs"] if s['url'] != removed['url']]
                    save_data(data)
                    print(f"Песня '{removed['title']}' полностью уничтожена.")
                    sync_to_github()
                else: print("Неверный номер.")
            except ValueError: print("Ошибка ввода.")

        elif choice == '4':
            print("\n--- ТЕКУЩИЕ АЛЬБОМЫ НА САЙТЕ ---")
            if not data["albums"]:
                print("Альбомов нет.")
            for i, a in enumerate(data["albums"], 1):
                print(f"{i}. Альбом: '{a['title']}' | Автор: '{a['author']}' (Песен: {len(a['songs'])})")

        elif choice == '5':
            print("\n--- СОЗДАНИЕ АЛЬБОМА ---")
            title = input("Название альбома: ").strip()
            author = input("Автор альбома: ").strip()
            if not title: print("Название не может быть пустым."); continue
            data["albums"].append({"title": title, "author": author, "songs": []})
            save_data(data)
            print(f"Альбом '{title}' успешно создан.")
            sync_to_github()

        elif choice == '6':
            print("\n--- РЕДАКТИРОВАНИЕ АЛЬБОМА ---")
            if not data["albums"]: print("Сначала создайте альбом."); continue
            for i, a in enumerate(data["albums"], 1):
                print(f"{i}. '{a['title']}' — {a['author']}")
            try:
                a_idx = int(input("Выберите номер альбома для наполнения: "))
                if not (1 <= a_idx <= len(data["albums"])): print("Неверный номер."); continue
                
                if not data["all_songs"]: print("В глобальной базе нет песен. Сначала добавьте через пункт 2."); continue
                print("\nКакую песню добавить в этот альбом?")
                for i, s in enumerate(data["all_songs"], 1):
                    print(f"{i}. '{s['title']}' — {s['author']}")
                
                s_idx = int(input("Введи номер песни: "))
                if 1 <= s_idx <= len(data["all_songs"]):
                    selected_song = data["all_songs"][s_idx - 1]
                    # Проверяем дубликаты в альбоме
                    if any(s['url'] == selected_song['url'] for s in data["albums"][a_idx - 1]["songs"]):
                        print("Эта песня уже добавлена в этот альбом.")
                    else:
                        data["albums"][a_idx - 1]["songs"].append(selected_song)
                        save_data(data)
                        print(f"Песня добавлена в альбом!")
                        sync_to_github()
                else: print("Неверный номер трека.")
            except ValueError: print("Ошибка ввода.")

        elif choice == '7':
            print("\n--- УДАЛЕНИЕ АЛЬБОМА ---")
            if not data["albums"]: print("Нет альбомов для удаления."); continue
            for i, a in enumerate(data["albums"], 1):
                print(f"{i}. '{a['title']}' — {a['author']}")
            try:
                idx = int(input("Выберите номер альбома для удаления: "))
                if 1 <= idx <= len(data["albums"]):
                    removed = data["albums"].pop(idx - 1)
                    save_data(data)
                    print(f"Альбом '{removed['title']}' удален с сайта.")
                    sync_to_github()
                else: print("Неверный номер.")
            except ValueError: print("Ошибка.")

        elif choice == '8':
            open_browser()
        elif choice == '0':
            break
        else:
            print("Неверная команда.")

if __name__ == "__main__":
    main()
