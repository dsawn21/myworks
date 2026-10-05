import json, os, secrets, string

#Файлы лежат в папке, что и программа
FOLDER = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(FOLDER, "accounts.json")


#Вспомогательные функции 

def clear():
    """Стирает всё с экрана."""
    os.system("cls" if os.name == "nt" else "clear")


def wait():
    """Ждём, пока пользователь прочитает результат."""
    input("\nEnter — вернуться в меню...")


def yes(text):
    """Проверяет, ответил ли пользователь «да»."""
    return text.strip().lower() in ("да", "д", "yes", "y")


def load_accounts():
    """Читает базу из json-файла."""
    if not os.path.exists(JSON_FILE):
        return {}

    with open(JSON_FILE, encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("Файл accounts.json повреждён. База пустая.")
            return {}


def save_accounts(accounts):
    """Сохраняет базу в json-файл."""
    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(accounts, file, ensure_ascii=False, indent=2)


def read_txt_line(line):
    """
    Читает одну строку из txt.
    Пример: steam | login | password
    Также работает с : ; или пробелами.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    for sep in "|:;":
        if sep in line:
            word, login, password, *_ = [part.strip() for part in line.split(sep)]
            if word and login and password:
                return word.lower(), login, password

    parts = line.split()
    if len(parts) >= 3:
        return parts[0].lower(), parts[1], parts[2]

    return None


def create_password(length=8, with_symbols=True):
    """Создаёт случайный пароль нужной длины."""
    chars = string.ascii_letters + string.digits
    if with_symbols:
        chars += "!@#$%&*-_"

    return "".join(secrets.choice(chars) for _ in range(length))

def ask_number(prompt, default):
    """Спрашивает число. Enter — значение по умолчанию."""
    text = input(prompt).strip()
    if not text:
        return default

    try:
        number = int(text)
    except ValueError:
        print("Нужно ввести число.")
        return None

    return number


#Команды меню

def add_account():
    accounts = load_accounts()

    print("Кодовое слово — короткое имя, например: steam, google\n")
    word = input("Кодовое слово: ").strip().lower()
    if not word:
        print("Нельзя оставить пустым.")
        return

    if word in accounts and not yes(input(f"'{word}' уже есть. Перезаписать? (да/нет): ")):
        print("Отменено.")
        return

    login = input("Логин: ").strip()

    if yes(input("Сгенерировать пароль автоматически? (да/нет): ")):
        password = create_password()
        print(f"Сгенерированный пароль: {password}")
    else:
        password = input("Пароль: ").strip()

    if not login or not password:
        print("Логин и пароль нужно заполнить.")
        return

    accounts[word] = {"login": login, "password": password}
    save_accounts(accounts)
    print(f"Готово! Запись '{word}' сохранена.")


def find_account():
    accounts = load_accounts()
    word = input("Кодовое слово: ").strip().lower()

    if word not in accounts:
        print("Не найдено.")
        return

    record = accounts[word]
    print(f"\n[{word}]")
    print(f"Логин:  {record['login']}")
    print(f"Пароль: {record['password']}")


def list_keywords():
    accounts = load_accounts()
    if not accounts:
        print("База пуста.")
        return

    print(f"Кодовые слова ({len(accounts)}):\n")
    for word in sorted(accounts):
        print(f"  • {word}")


def show_all_accounts():
    accounts = load_accounts()
    if not accounts:
        print("База пуста.")
        return

    print(f"Все записи ({len(accounts)}):\n")
    for word in sorted(accounts):
        record = accounts[word]
        print(f"  [{word}]  {record['login']}  /  {record['password']}")


def delete_account():
    accounts = load_accounts()
    word = input("Какую запись удалить? ").strip().lower()

    if word not in accounts:
        print("Такой записи нет.")
        return

    if yes(input(f"Точно удалить '{word}'? (да/нет): ")):
        del accounts[word]
        save_accounts(accounts)
        print("Удалено.")
    else:
        print("Отменено.")

    accounts = load_accounts()

    # Показываем дубликаты, если есть
    doubles = [item for item in new_records if item[1] in accounts]
    if doubles:
        print(f"\nУже есть в базе ({len(doubles)}):")
        for number, word, _, _ in doubles:
            print(f"  строка {number}: {word}")

        if not yes(input("\nПерезаписать их? (да/нет): ")):
            new_records = [item for item in new_records if item[1] not in accounts]
            if not new_records:
                print("Импорт отменён.")
                return

    for _, word, login, password in new_records:
        accounts[word] = {"login": login, "password": password}

    save_accounts(accounts)
    print(f"\nИмпортировано: {len(new_records)} записей.")


def generate_password_menu():
    print("=== Генератор паролей ===\n")

    length = ask_number("Длина пароля (Enter = 16): ", 16)
    if length is None:
        return
    if length < 4:
        print("Минимальная длина — 4 символа.")
        return
    if length > 128:
        print("Максимальная длина — 128 символов.")
        return

    with_symbols = yes(input("Добавить символы !@#$? (да/нет, Enter = да): ") or "да")
    password = create_password(length, with_symbols)

    print(f"\nВаш пароль:\n{password}")

    if not yes(input("\nСохранить этот пароль в базу? (да/нет): ")):
        return

    accounts = load_accounts()
    word = input("Кодовое слово для записи: ").strip().lower()
    if not word:
        print("Кодовое слово нельзя оставить пустым.")
        return

    if word in accounts and not yes(input(f"'{word}' уже есть. Перезаписать? (да/нет): ")):
        print("Отменено.")
        return

    login = input("Логин: ").strip()
    if not login:
        print("Логин нужно заполнить.")
        return

    accounts[word] = {"login": login, "password": password}
    save_accounts(accounts)
    print(f"Готово! Запись '{word}' сохранена.")


# --- Главное меню ---

MENU = """
   === Менеджер паролей ===
 | 1. Добавить запись         |
 | 2. Найти по кодовому слову | 
 | 3. Показать кодовые слова  |
 | 4. Показать все записи     |
 | 5. Удалить запись          |
 | 6. Сгенерировать пароль    |
 | 7. Выход                   |
"""

COMMANDS = {
    "1": add_account,
    "2": find_account,
    "3": list_keywords,
    "4": show_all_accounts,
    "5": delete_account,
    "6": generate_password_menu,
    "7": exit
    
}


def main():
    while True:
        clear()
        print("База: accounts.json\n")
        print(MENU)

        choice = input("Выберите пункт: ").strip()

        if choice == "8":
            clear()
            print("Пока!")
            break

        command = COMMANDS.get(choice)
        if command is None:
            print("Такого пункта нет.")
        else:
            clear()
            command()

        wait()


if __name__ == "__main__":
    main()
