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
            for alb in data["albums"]:
                if "gif_url" not in alb: alb["gif_url"] = ""
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
    subprocess.run(["git", "commit", "-m", "Обновление медиатеки и оформлений"], check=False)
    subprocess.run(["git", "push"], check=False)
    print("Изменения успешно отправлены на сайт!\n")

def main():
    while True:
        print("\n=== ЦЕНТРАЛЬНЫЙ СХРОН УПРАВЛЕНИЯ ===")
        print("1. Посмотреть ГЛОБАЛЬНЫЙ список песен")
        print("2. Добавить кавер в ГЛОБАЛЬНЫЙ список")
        print("3. Удалить кавер из ГЛОБАЛЬНОГО списка")
        print("---------------------------------------------")
        print("4. Список Альбомов")
        print("5. Создать НОВЫЙ Альбом")
        print("6. Редактировать Альбом (Добавить песню / Изменить данные)")
        print("7. Удалить Альбом")
        print("---------------------------------------------")
        print("8. Перейти на сайт")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        data = load_data()
        
        if choice == '1':
            print("\n--- ВСЕ ТВОИ ЗАГРУЖЕННЫЕ ПЕСНИ ---")
            if not data["all_songs"]: print("Список пуст.")
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
            if not data["all_songs"]: print("Удалять нечего."); continue
            for i, s in enumerate(data["all_songs"], 1):
                print(f"{i}. '{s['title']}' — {s['author']}")
            try:
                idx = int(input("Введите номер трека для полного удаления: "))
                if 1 <= idx <= len(data["all_songs"]):
                    removed = data["all_songs"].pop(idx - 1)
                    for alb in data["albums"]:
                        alb["songs"] = [s for s in alb["songs"] if s['url'] != removed['url']]
                    save_data(data)
                    print(f"Песня '{removed['title']}' полностью уничтожена.")
                    sync_to_github()
                else: print("Неверный номер.")
            except ValueError: print("Ошибка ввода.")

        elif choice == '4':
            print("\n--- ТЕКУЩИЕ АЛЬБОМЫ НА САЙТЕ ---")
            if not data["albums"]: print("Альбомов нет.")
            for i, a in enumerate(data["albums"], 1):
                has_gif = "[GIF есть]" if a.get("gif_url") else "[Без обложки]"
                print(f"{i}. Альбом: '{a['title']}' | {has_gif} (Песен: {len(a['songs'])})")

        elif choice == '5':
            print("\n--- СОЗДАНИЕ АЛЬБОМА ---")
            title = input("Название альбома: ").strip()
            author = input("Автор альбома: ").strip()
            if not title: print("Название не может быть пустым."); continue
            data["albums"].append({"title": title, "author": author, "songs": [], "gif_url": ""})
            save_data(data)
            print(f"Альбом '{title}' успешно создан.")
            sync_to_github()

        elif choice == '6':
            print("\n--- РЕДАКТИРОВАНИЕ АЛЬБОМА ---")
            if not data["albums"]: print("Сначала создайте альбом."); continue
            for i, a in enumerate(data["albums"], 1):
                print(f"{i}. '{a['title']}' — {a['author']}")
            try:
                a_idx = int(input("Выберите номер альбома для редактирования: "))
                if not (1 <= a_idx <= len(data["albums"])): print("Неверный номер."); continue
                
                selected_album = data["albums"][a_idx - 1]
                print(f"\nВыбран альбом: '{selected_album['title']}'")
                print("1. Добавить песню в этот альбом")
                print("2. Изменить данные (Название/Автор/GIF обложка)")
                print("0. Отмена")
                
                sub_choice = input("Выберите действие: ").strip()
                
                if sub_choice == '1':
                    if not data["all_songs"]: print("В глобальной базе нет песен."); continue
                    print("\nКакую песню добавить в этот альбом?")
                    for i, s in enumerate(data["all_songs"], 1):
                        print(f"{i}. '{s['title']}' — {s['author']}")
                    
                    s_idx = int(input("Введи номер песни: "))
                    if 1 <= s_idx <= len(data["all_songs"]):
                        song_to_add = data["all_songs"][s_idx - 1]
                        if any(s['url'] == song_to_add['url'] for s in selected_album["songs"]):
                            print("Эта песня уже в альбоме.")
                        else:
                            selected_album["songs"].append(song_to_add)
                            save_data(data)
                            print(f"Песня успешно добавлена!")
                            sync_to_github()
                    else: print("Неверный номер трека.")
                    
                elif sub_choice == '2':
                    print(f"\nСтарое название: {selected_album['title']}")
                    new_title = input("Новое название (Enter чтобы пропустить): ").strip()
                    print(f"Старый автор: {selected_album['author']}")
                    new_author = input("Новый автор (Enter чтобы пропустить): ").strip()
                    print(f"Текущая GIF ссылка: {selected_album.get('gif_url', 'Отсутствует')}")
                    new_gif = input("Новая ссылка на GIF с Dropbox: ").strip()
                    
                    changed = False
                    if new_title: selected_album['title'] = new_title; changed = True
                    if new_author: selected_album['author'] = new_author; changed = True
                    if new_gif: selected_album['gif_url'] = new_gif; changed = True
                        
                    if changed:
                        save_data(data)
                        print("Данные альбома успешно изменены!")
                        sync_to_github()
                    else: print("Изменений нет.")
                else: print("Отмена.")
            except ValueError: print("Ошибка ввода.")

        elif choice == '7':
            print("\n--- УДАЛЕНИЕ АЛЬБОМА ---")
            if not data["albums"]: print("Нет альбомов."); continue
            for i, a in enumerate(data["albums"], 1):
                print(f"{i}. '{a['title']}' — {a['author']}")
            try:
                idx = int(input("Выберите номер альбома для удаления: "))
                if 1 <= idx <= len(data["albums"]):
                    data["albums"].pop(idx - 1)
                    save_data(data)
                    print("Альбом удален.")
                    sync_to_github()
                else: print("Неверный номер.")
            except ValueError: print("Ошибка.")

        elif choice == '8': open_browser()
        elif choice == '0': break
        else: print("Неверная команда.")

if __name__ == "__main__":
    main()
