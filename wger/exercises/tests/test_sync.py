# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
from unittest.mock import patch

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    Muscle,
)
from wger.exercises.sync import (
    delete_entries,
    sync_categories,
    sync_equipment,
    sync_exercises,
    sync_languages,
    sync_muscles,
)
from wger.utils.requests import wger_headers


class MockLanguageResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 24,
            "next": "http://localhost:8000/api/v2/language/?limit=20&offset=20",
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "short_name": "de",
                    "full_name": "Daitsch"
                },
                {
                    "id": 2,
                    "short_name": "en",
                    "full_name": "English"
                },
                {
                    "id": 3,
                    "short_name": "fr",
                    "full_name": "Français"
                },
                {
                    "id": 4,
                    "short_name": "es",
                    "full_name": "Español"
                },
                {
                    "id": 19,
                    "short_name": "eo",
                    "full_name": "Esperanto"
                }
            ]
        }
    # yapf: enable


class MockCategoryResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 6,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "A cooler, swaggier category"
                },
                {
                    "id": 2,
                    "name": "Another category"
                },
                {
                    "id": 3,
                    "name": "Yet another category"
                },
                {
                    "id": 4,
                    "name": "Calves"
                },
                {
                    "id": 5,
                    "name": "Cardio"
                },
                {
                    "id": 16,
                    "name": "Chest"
                }
            ]
        }
    # yapf: enable


class MockMuscleResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "Anterior testoid",
                    "name_en": "Testoulders",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-1.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-1.svg"
                },
                {
                    "id": 2,
                    "name": "Novum musculus nomen eius",
                    "name_en": "Testceps",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-2.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-2.svg"
                },
                {
                    "id": 3,
                    "name": "Biceps notusensis",
                    "name_en": "",
                    "is_front": False,
                    "image_url_main": "/static/images/muscles/main/muscle-3.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-3.svg"
                },
                {
                    "id": 10,
                    "name": "Pectoralis major",
                    "name_en": "Chest",
                    "is_front": True,
                    "image_url_main": "/static/images/muscles/main/muscle-10.svg",
                    "image_url_secondary": "/static/images/muscles/secondary/muscle-10.svg"
                },
            ]
        }
    # yapf: enable


class MockEquipmentResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 1,
                    "name": "Dumbbells"
                },
                {
                    "id": 2,
                    "name": "Kettlebell"
                },
                {
                    "id": 3,
                    "name": "A big rock"
                },
                {
                    "id": 42,
                    "name": "Gym mat"
                },
            ]
        }
    # yapf: enable


class MockDeletionLogResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 4,
            "next": None,
            "previous": None,
            "results": [
                {
                    "model_type": "base",
                    "uuid": "acad394936fb44819a72be2ddae2bc05",
                    "timestamp": "2023-01-30T19:32:56.761426+01:00",
                    "comment": "Exercise base with ID 1"
                },
                {
                    "model_type": "base",
                    "uuid": "577ee012-70c6-4517-b0fe-dcf340926ae7",
                    "timestamp": "2023-01-30T19:32:56.761426+01:00",
                    "comment": "Unknown Exercise base"
                },
                {
                    "model_type": "translation",
                    "uuid": "0ef4cec8-d9c9-464f-baf9-3dbdf20083cb",
                    "timestamp": "2023-01-30T19:32:56.764582+01:00",
                    "comment": "Translation that is not in this DB"
                },
                {
                    "model_type": "translation",
                    "uuid": "946afe7b54a644a69c36c3e31e6b4c3b",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "Translation with ID 3"
                },
                {
                    "model_type": "image",
                    "uuid": "c72b4463-48ae-4c7d-8093-2c347c38e05a",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "Unknown image"
                },
                {
                    "model_type": "video",
                    "uuid": "e0d25624-348b-4a23-adcd-17190f96f005",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "Unknown video"
                },
                {
                    "model_type": "foobar",
                    "uuid": "37b5813c76bd4658820a572d9dd93f31",
                    "timestamp": "2023-01-30T19:32:56.765350+01:00",
                    "comment": "UUID of existing translation but other model type"
                },
            ]
        }
    # yapf: enable


class MockExerciseResponse:

    def __init__(self):
        self.status_code = 200
        self.content = b''

    # yapf: disable
    @staticmethod
    def json():
        return {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": 123,
                    "uuid": "1b020b3a-3732-4c7e-92fd-a0cec90ed69b",
                    "creation_date": "2022-10-11",
                    "category": {
                        "id": 2,
                        "name": "Another category"
                    },
                    "muscles": [
                        {
                            "id": 2,
                            "name": "Biceps testii",
                            "name_en": "Testceps",
                            "is_front": True,
                            "image_url_main": "/static/images/muscles/main/muscle-2.svg",
                            "image_url_secondary": "/static/images/muscles/secondary/muscle-2.svg"
                        }
                    ],
                    "muscles_secondary": [
                        {
                            "id": 4,
                            "name": "Bigus Pectoralis",
                            "name_en": "Testch",
                            "is_front": True,
                            "image_url_main": "/static/images/muscles/main/muscle-4.svg",
                            "image_url_secondary": "/static/images/muscles/secondary/muscle-4.svg"
                        }
                    ],
                    "equipment": [
                        {
                            "id": 2,
                            "name": "Kettlebell"
                        }
                    ],
                    "license": {
                        "id": 2,
                        "full_name": "Creative Commons Attribution Share Alike 4",
                        "short_name": "CC-BY-SA 4",
                        "url": "https://creativecommons.org/licenses/by-sa/4.0/deed.en"
                    },
                    "license_author": "Mr X",
                    "images": [],
                    "exercises": [
                        {
                            "id": 100,
                            "uuid": "c788d643-150a-4ac7-97ef-84643c6419bf",
                            "name": "Zweihandiges Kettlebell",
                            "exercise_base": 123,
                            "description": "Hier könnte Ihre Werbung stehen!",
                            "creation_date": "2015-08-03",
                            "language": 1,
                            "aliases": [
                                "Kettlebell mit zwei Händen"
                            ],
                            "notes": [
                                "Wichtig die Übung richtig zu machen"
                            ],
                            "license": 2,
                            "license_author": "Tester von der Testen",
                            "author_history": [
                                "wger Team",
                                "Jürgen",
                                "Tester von der Testen"
                            ]
                        },
                        {
                            "id": 101,
                            "uuid": "ab4185dd-2e68-4579-af1f-0c03957c0a9e",
                            "name": "2 Handed Kettlebell Swing",
                            "exercise_base": 123,
                            "description": "TBD",
                            "creation_date": "2023-08-03",
                            "language": 2,
                            "aliases": [],
                            "notes": [],
                            "license": 2,
                            "license_author": "Tester McTest",
                            "author_history": [
                                "Mrs Winterbottom",
                                "Tester McTest"
                            ]
                        }
                    ],
                    "variations": 47,
                    "videos": [],
                    "author_history": [
                        "Mrs Winterbottom"
                    ],
                    "total_authors_history": [
                        "Mrs Winterbottom",
                        "Tester McTest",
                        "wger Team",
                        "Jürgen",
                        "Tester von der Testen"
                    ]
                },
                {
                    "id": 2,
                    "uuid": "ae3328ba-9a35-4731-bc23-5da50720c5aa",
                    "creation_date": "2022-10-11",
                    "category": {
                        "id": 3,
                        "name": "Yet another category"
                    },
                    "muscles": [
                        {
                            "id": 2,
                            "name": "Biceps testii",
                            "name_en": "Testceps",
                            "is_front": True,
                            "image_url_main": "/static/images/muscles/main/muscle-2.svg",
                            "image_url_secondary": "/static/images/muscles/secondary/muscle-2.svg"
                        }
                    ],
                    "muscles_secondary": [
                        {
                            "id": 4,
                            "name": "Bigus Pectoralis",
                            "name_en": "Testch",
                            "is_front": True,
                            "image_url_main": "/static/images/muscles/main/muscle-4.svg",
                            "image_url_secondary": "/static/images/muscles/secondary/muscle-4.svg"
                        }
                    ],
                    "equipment": [
                        {
                            "id": 2,
                            "name": "Kettlebell"
                        }
                    ],
                    "license": {
                        "id": 2,
                        "full_name": "Creative Commons Attribution Share Alike 4",
                        "short_name": "CC-BY-SA 4",
                        "url": "https://creativecommons.org/licenses/by-sa/4.0/deed.en"
                    },
                    "license_author": "Mr X",
                    "images": [],
                    "exercises": [
                        {
                            "id": 123,
                            "uuid": "7524ca8d-032e-482d-ab18-40e8a97851f6",
                            "name": "A new, better, updated name",
                            "exercise_base": 2,
                            "description": "Two Handed Russian Style Kettlebell swing",
                            "creation_date": "2015-08-03",
                            "language": 1,
                            "aliases": [
                                "A new alias here",
                                "yet another name"
                            ],
                            "notes": [
                                "Foobar",
                            ],
                            "license": 2,
                            "license_author": "Mr X",
                            "author_history": [
                                "Mr X"
                            ]
                        },
                        {
                            "id": 345,
                            "uuid": "581338a1-8e52-405b-99eb-f0724c528bc8",
                            "name": "Balançoire Kettlebell à 2 mains",
                            "exercise_base": 2,
                            "description": "Balançoire Kettlebell à deux mains de style russe",
                            "creation_date": "2015-08-03",
                            "language": 3,
                            "aliases": [],
                            "notes": [],
                            "license": 2,
                            "license_author": "Mr Y",
                            "author_history": [
                                "Mr Y",
                                "Mr Z"
                            ]
                        }
                    ],
                    "variations": 47,
                    "videos": [],
                    "author_history": [
                        "Mr X"
                    ],
                    "total_authors_history": [
                        "Mr X",
                        "Mr Z"
                    ]
                },
            ]
        }
    # yapf: enable


class TestSyncMethods(WgerTestCase):

    @patch('requests.get', return_value=MockLanguageResponse())
    def test_language_sync(self, mock_request):
        self.assertEqual(Language.objects.count(), 3)
        self.assertEqual(Language.objects.get(pk=1).full_name, 'Deutsch')

        sync_languages(lambda x: x)
        mock_request.assert_called_with(
            'https://wger.de/api/v2/language/',
            headers=wger_headers(),
        )
        self.assertEqual(Language.objects.get(pk=1).full_name, 'Daitsch')
        self.assertEqual(Language.objects.get(pk=5).full_name, 'Esperanto')
        self.assertEqual(Language.objects.count(), 5)

    @patch('requests.get', return_value=MockCategoryResponse())
    def test_categories_sync(self, mock_request):
        self.assertEqual(ExerciseCategory.objects.count(), 4)
        self.assertEqual(ExerciseCategory.objects.get(pk=1).name, 'Category')

        sync_categories(lambda x: x)
        mock_request.assert_called_with(
            'https://wger.de/api/v2/exercisecategory/',
            headers=wger_headers(),
        )
        self.assertEqual(ExerciseCategory.objects.count(), 6)
        self.assertEqual(ExerciseCategory.objects.get(pk=1).name, 'A cooler, swaggier category')
        self.assertEqual(ExerciseCategory.objects.get(pk=16).name, 'Chest')

    @patch('requests.get', return_value=MockMuscleResponse())
    def test_muscle_sync(self, mock_request):
        self.assertEqual(Muscle.objects.count(), 6)
        self.assertEqual(Muscle.objects.get(pk=2).name, 'Biceps testii')
        self.assertFalse(Muscle.objects.get(pk=2).is_front)
        sync_muscles(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/muscle/',
            headers=wger_headers(),
        )
        self.assertEqual(Muscle.objects.count(), 7)
        self.assertTrue(Muscle.objects.get(pk=2).is_front)
        self.assertEqual(Muscle.objects.get(pk=2).name, 'Novum musculus nomen eius')
        self.assertEqual(Muscle.objects.get(pk=10).name, 'Pectoralis major')

    @patch('requests.get', return_value=MockEquipmentResponse())
    def test_equipment_sync(self, mock_request):
        self.assertEqual(Equipment.objects.count(), 3)
        self.assertEqual(Equipment.objects.get(pk=3).name, 'Something else')
        sync_equipment(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/equipment/',
            headers=wger_headers(),
        )
        self.assertEqual(Equipment.objects.count(), 4)
        self.assertEqual(Equipment.objects.get(pk=3).name, 'A big rock')
        self.assertEqual(Equipment.objects.get(pk=42).name, 'Gym mat')

    @patch('requests.get', return_value=MockDeletionLogResponse())
    def test_deletion_log(self, mock_request):
        self.assertEqual(ExerciseBase.objects.count(), 8)
        self.assertEqual(Exercise.objects.count(), 11)
        delete_entries(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/deletion-log/?limit=100',
            headers=wger_headers(),
        )
        self.assertEqual(ExerciseBase.objects.count(), 7)
        self.assertEqual(Exercise.objects.count(), 8)
        self.assertRaises(Exercise.DoesNotExist, Exercise.objects.get, pk=3)
        self.assertRaises(ExerciseBase.DoesNotExist, ExerciseBase.objects.get, pk=1)

    @patch('requests.get', return_value=MockExerciseResponse())
    def test_exercise_sync(self, mock_request):
        self.assertEqual(ExerciseBase.objects.count(), 8)
        self.assertEqual(Exercise.objects.count(), 11)
        base = ExerciseBase.objects.get(uuid='ae3328ba-9a35-4731-bc23-5da50720c5aa')
        self.assertEqual(base.category_id, 2)

        sync_exercises(lambda x: x)

        mock_request.assert_called_with(
            'https://wger.de/api/v2/exercisebaseinfo/?limit=100',
            headers=wger_headers(),
        )
        self.assertEqual(ExerciseBase.objects.count(), 9)
        self.assertEqual(Exercise.objects.count(), 14)

        # New base was created
        new_base = ExerciseBase.objects.get(uuid='1b020b3a-3732-4c7e-92fd-a0cec90ed69b')
        self.assertEqual(new_base.category_id, 2)
        self.assertEqual([e.id for e in new_base.equipment.all()], [2])
        self.assertEqual([m.id for m in new_base.muscles.all()], [2])
        self.assertEqual([m.id for m in new_base.muscles_secondary.all()], [4])

        translation_de = new_base.get_exercise('de')
        self.assertEqual(translation_de.language_id, 1)
        self.assertEqual(translation_de.name, 'Zweihandiges Kettlebell')
        self.assertEqual(translation_de.description, 'Hier könnte Ihre Werbung stehen!')
        self.assertEqual(translation_de.alias_set.first().alias, 'Kettlebell mit zwei Händen')
        self.assertEqual(
            translation_de.exercisecomment_set.first().comment,
            'Wichtig die Übung richtig zu machen',
        )

        translation_en = new_base.get_exercise('en')
        self.assertEqual(translation_en.language_id, 2)
        self.assertEqual(translation_en.name, '2 Handed Kettlebell Swing')
        self.assertEqual(translation_en.description, 'TBD')

        # Existing base was updated
        base = ExerciseBase.objects.get(uuid='ae3328ba-9a35-4731-bc23-5da50720c5aa')
        self.assertEqual(base.category_id, 3)

        translation_de = base.get_exercise('de')
        self.assertEqual(translation_de.name, 'A new, better, updated name')
        self.assertEqual(translation_de.pk, 2)
        self.assertEqual(translation_de.alias_set.count(), 2)
        self.assertEqual(translation_de.alias_set.all()[0].alias, 'yet another name')
        self.assertEqual(translation_de.alias_set.all()[1].alias, 'A new alias here')

        self.assertEqual(translation_de.exercisecomment_set.count(), 1)
        self.assertEqual(translation_de.exercisecomment_set.first().comment, 'Foobar')

        translation_fr = base.get_exercise('fr')
        self.assertEqual(str(translation_fr.uuid), '581338a1-8e52-405b-99eb-f0724c528bc8')
