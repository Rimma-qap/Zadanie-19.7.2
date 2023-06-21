import os

import pytest

from api import PetFriends
from settings import (
    invalid_email,
    invalid_password,
    valid_email,
    valid_password,
)

pf = PetFriends()


class TestPetFriends:
    def setup_class(self):
        _, result = pf.get_api_key(valid_email, valid_password)
        self.auth_key = result["key"]

    def test_get_api_key_valid_user(
        self,
        email=valid_email,
        password=valid_password,
    ):
        """Проверяем, что код статуса 200 и
        в переменной result содержится слово key"""

        status, result = pf.get_api_key(email, password)
        assert status == 200
        assert "key" in result

    def test_get_api_key_invalid_user(self):
        """Проверяем, что код статуса 403"""

        status, result = pf.get_api_key(invalid_email, valid_password)
        assert status == 403

        status, result = pf.get_api_key(invalid_email, invalid_password)
        assert status == 403

        status, result = pf.get_api_key(valid_email, invalid_password)
        assert status == 403

    def test_get_all_pets_with_valid_key(self, filter=""):
        """Проверяем, что код статуса 200 и список всех питомцев не пустой."""

        status, result = pf.get_list_of_pets(self.auth_key, filter)
        assert status == 200
        assert len(result["pets"]) > 0

    def test_get_all_pets_with_invalid_key(self, filter=""):
        """Проверяем, что код статуса 403"""

        status, result = pf.get_list_of_pets("1234", filter)
        assert status == 403

    def test_get_my_pets(self, filter="my_pets"):
        """Проверяем, что код статуса 200"""

        status, result = pf.get_list_of_pets(self.auth_key, filter)
        assert status == 200

    @pytest.mark.xfail(reason="баг с некорректным фильтром со статусом 500")
    def test_get_pets_with_invalid_filter(self, filter="my_pet"):
        """Проверяем, что код статуса 400"""

        status, result = pf.get_list_of_pets(self.auth_key, filter)
        assert status == 400

    def test_add_pet_with_valid_data(
        self,
        name="Баксик",
        animal_type="кот",
        age=12,
        pet_photo="images/baks.jpeg",
    ):
        """Проверяем, что код статуса 200 и что список с добавленными
        данными не пустой."""

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        status, result = pf.add_new_pet(
            self.auth_key,
            name,
            animal_type,
            age,
            pet_photo,
        )
        assert status == 200
        assert result["name"] == name
        assert result["age"] == str(age)
        assert result["animal_type"] == animal_type
        assert result["pet_photo"] is not None

    def test_delete_pet(self):
        """Проверяем возможность удаления питомца"""

        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        if len(my_pets["pets"]) == 0:
            pf.add_new_pet(
                self.auth_key,
                "Баксик",
                "кот",
                "10",
                "images/baks.jpeg",
            )
            _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        pet_id = my_pets["pets"][0]["id"]

        status, _ = pf.delete_pet(self.auth_key, pet_id)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        assert status == 200
        assert pet_id not in my_pets.values()

    @pytest.mark.xfail(reason="пользователь может удалять только своих питомцев")
    def test_delete_alien_pet(self):
        """Проверяем возможность удаления чужого питомца"""

        _, pets = pf.get_list_of_pets(self.auth_key, "")
        pet_id = pets["pets"][0]["id"]

        status, _ = pf.delete_pet(self.auth_key, pet_id)
        _, my_pets = pf.get_list_of_pets(self.auth_key, "")

        assert status == 400

    def test_update_pet_info(
        self,
        name="Зверь",
        animal_type="тигр",
        age=5,
    ):
        """Проверяем возможность изменения данных питомца"""

        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        if len(my_pets["pets"]) > 0:
            pet_id = my_pets["pets"][0]["id"]
            status, result = pf.update_pet_info(
                self.auth_key, pet_id, name, animal_type, age
            )
            assert status == 200
            assert result["name"] == name
            assert result["animal_type"] == animal_type
            assert result["age"] == str(age)

    def test_add_pets_with_valid_data_without_photo(
        self, name="Баксик", animal_type="кот", age=10
    ):
        """Проверяем возможность добавления нового питомца без фото"""

        status, result = pf.create_pet_simple(
            self.auth_key,
            name,
            animal_type,
            age,
        )

        assert status == 200
        assert result["name"] == name
        assert result["animal_type"] == animal_type
        assert result["age"] == str(age)

    def test_add_pet_photo(self, pet_photo="images/aktan.jpeg"):
        """Проверяем возможность добавления новой фотографии питомца"""

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

        if len(my_pets["pets"]) > 0:
            pet_id = my_pets["pets"][0]["id"]
            status, result = pf.set_pet_photo(
                self.auth_key,
                pet_id,
                pet_photo,
            )

            _, my_pets = pf.get_list_of_pets(self.auth_key, "my_pets")

            assert status == 200
            assert result["pet_photo"] == my_pets["pets"][0]["pet_photo"]
