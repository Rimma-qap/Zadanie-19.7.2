from json.decoder import JSONDecodeError

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class PetFriends:
    """Библиотека содержит API-запросы к сайту PetFriends"""

    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_url(self, url, pet_id=None):
        """Получение абсолютного пути API"""
        if pet_id:
            return f"{self.base_url}{url}{pet_id}"
        return f"{self.base_url}{url}"

    def get_headers(self, auth_key, content_type=None):
        """Получение базовых заголовков"""
        return {"auth_key": auth_key, "Content-Type": content_type}

    def resp_decode(self, resp):
        """Декодирование ответа"""
        status_code = resp.status_code

        try:
            result = resp.json()
        except JSONDecodeError:
            result = resp.text

        return status_code, result

    def get_api_key(self, email, password):
        """Получение API-ключа"""
        headers = {"email": email, "password": password}
        url = self.get_url("api/key")
        resp = requests.get(url=url, headers=headers)
        return self.resp_decode(resp)

    def get_list_of_pets(self, auth_key, filter):
        """Получение списка питомцев"""
        headers = self.get_headers(auth_key)
        params = {"filter": filter}
        url = self.get_url("api/pets")
        resp = requests.get(url=url, headers=headers, params=params)
        return self.resp_decode(resp)

    def add_new_pet(self, auth_key, name, animal_type, age, pet_photo):
        """Добавление питомца с фото"""
        data = MultipartEncoder(
            fields={
                "name": name,
                "animal_type": animal_type,
                "age": str(age),
                "pet_photo": (pet_photo, open(pet_photo, "rb"), "image/jpeg"),
            }
        )
        headers = self.get_headers(auth_key, data.content_type)
        url = self.get_url("api/pets")
        resp = requests.post(url=url, data=data, headers=headers)
        return self.resp_decode(resp)

    def delete_pet(self, auth_key, pet_id):
        """Удаление питомца"""
        headers = self.get_headers(auth_key)
        url = self.get_url("api/pets/", pet_id)
        resp = requests.delete(url=url, headers=headers)
        return self.resp_decode(resp)

    def update_pet_info(self, auth_key, pet_id, name, animal_type, age):
        """Обновление информации о питомце"""
        data = {"name": name, "animal_type": animal_type, "age": age}
        headers = self.get_headers(auth_key)
        url = self.get_url("api/pets/", pet_id)
        resp = requests.put(url=url, data=data, headers=headers)
        return self.resp_decode(resp)

    def create_pet_simple(self, auth_key, name, animal_type, age):
        """Добавление нового питомца без фото"""
        headers = self.get_headers(auth_key)
        data = {"name": name, "animal_type": animal_type, "age": age}
        url = self.get_url("/api/create_pet_simple")
        resp = requests.post(url=url, data=data, headers=headers)
        return self.resp_decode(resp)

    def set_pet_photo(self, auth_key, pet_id, pet_photo):
        """Добавление фото к существующему питомцу"""
        data = MultipartEncoder(
            fields={
                "pet_photo": (pet_photo, open(pet_photo, "rb"), "image/jpeg"),
            }
        )
        headers = self.get_headers(auth_key, data.content_type)
        url = self.get_url("api/pets/set_photo/", pet_id)
        resp = requests.post(url=url, data=data, headers=headers)
        return self.resp_decode(resp)
