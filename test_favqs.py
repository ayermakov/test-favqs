import requests
import pytest
import uuid

# Константи
BASE_URL = "https://favqs.com/api"
APP_TOKEN = "a2dbb35c4ad9b52eb59ba02d3c426bcd"

# Хедери за замовчуванням (тільки для доступу до API)
DEFAULT_HEADERS = {
    "Authorization": f'Token token="{APP_TOKEN}"',
    "Content-Type": "application/json"
}

class TestFavQs:
    def _generate_random_string(self):
        """Допоміжна функція для генерації унікальних даних"""
        return uuid.uuid4().hex[:10]

    def _create_user(self):
        """
        Допоміжна функція для створення користувача.
        Повертає response об'єкт створення, щоб тести могли брати з нього токен.
        """
        random_str = self._generate_random_string()
        login = f"user_{random_str}"
        email = f"{random_str}@example.com"
        password = "password123"

        payload = {
            "user": {
                "login": login,
                "email": email,
                "password": password
            }
        }

        response = requests.post(f"{BASE_URL}/users", json=payload, headers=DEFAULT_HEADERS)
        
        # Переконуємося, що користувач створений перед тим, як повертати дані
        assert response.status_code == 200, f"Не вдалося створити користувача: {response.text}"
        return response, email, password

    def test_create_and_get_user(self):
        """
        Перший тест: Створити користувача, дістати інформацію про нього 
        і перевірити відповідність полів login, email.
        """
        # 1. Створення користувача
        create_response, created_email, created_password = self._create_user()
        user_data = create_response.json()

        # Отримуємо дані створеного користувача та його токен сесії
        created_login = user_data["login"]
        user_token = user_data["User-Token"]

        # 2. Отримання інформації про користувача (GET запит)
        get_headers = DEFAULT_HEADERS.copy()
        get_headers["User-Token"] = user_token

        get_url = f"{BASE_URL}/users/{created_login}"
        get_response = requests.get(get_url, headers=get_headers)

        assert get_response.status_code == 200, "Не вдалося отримати інформацію про користувача"
        
        fetched_data = get_response.json()

        # 3. Перевірка полів
        assert fetched_data["login"] == created_login, "Логін не співпадає"
        assert fetched_data["account_details"]["email"] == created_email, "Email не співпадає"
        
        print(f"\n[Test 1] User created and verified: {created_login}")

    def test_update_user(self):
        """
        Другий тест: Оновлення користувача (login, email).
        Перевірка, що поля дійсно оновилися.
        """
        # 1. Підготовка: Створення користувача
        create_response, created_email, password = self._create_user()
        original_data = create_response.json()
        
        original_login = original_data["login"]
        user_token = original_data["User-Token"]

        # 2. Підготовка нових даних
        new_random = self._generate_random_string()
        new_login = f"updated_{new_random}"
        new_email = f"updated_{new_random}@example.com"

        update_payload = {
            "user": {
                "login": new_login,
                "email": new_email
            }
        }

        # Хедери для оновлення (Authorization + User-Token)
        update_headers = DEFAULT_HEADERS.copy()
        update_headers["User-Token"] = user_token

        # 3. Виконання запиту на оновлення (PUT)
        # Endpoint: /api/users/:login (де login - це ПОТОЧНИЙ логін)
        update_url = f"{BASE_URL}/users/{original_login}"
        
        update_response = requests.put(update_url, json=update_payload, headers=update_headers)
        
        assert update_response.status_code == 200, f"Помилка при оновленні: {update_response.text}"

        # 4. Отримання інформації про користувача для перевірки
        # Важливо: оскільки ми змінили логін, URL для GET запиту теж зміниться!
        get_url = f"{BASE_URL}/users/{new_login}"
        
        get_response = requests.get(get_url, headers=update_headers)
        
        assert get_response.status_code == 200, "Не вдалося отримати дані оновленого користувача"
        
        updated_user_data = get_response.json()

        # 5. Перевірка оновлених полів
        assert updated_user_data["login"] == new_login, f"Логін не оновився. Очікував {new_login}, отримав {updated_user_data['login']}"
        assert updated_user_data["account_details"]["email"] == new_email, f"Email не оновився. Очікував {new_email}, отримав {updated_user_data['email']}"

        print(f"\n[Test 2] User updated successfully from {original_login} to {new_login}")