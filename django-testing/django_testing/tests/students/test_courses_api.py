import pytest
import random
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course

course_api = '/api/v1/courses/'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def one_course():
    return Course.objects.create(name='Pytest course')


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_one_course(client, course_factory):
    course = course_factory(_quantity=1)
    response = client.get(course_api + f'{course[0].id}/')
    data = response.json()
    assert response.status_code == 200
    assert data['name'] == course[0].name


@pytest.mark.django_db
def test_get_all_courses(client, course_factory):
    courses = course_factory(_quantity=3)
    response = client.get(course_api)
    data = response.json()
    assert response.status_code == 200
    for index, c in enumerate(data):
        assert c['name'] == courses[index].name


@pytest.mark.django_db
def test_filter_id(client, course_factory, one_course):
    base_id = one_course.id
    max_id = 10
    random_number = random.randint(base_id, max_id+base_id)
    courses = course_factory(_quantity=max_id)
    response = client.get(course_api, {'id': random_number})
    data = response.json()[0]
    assert response.status_code == 200
    assert data['id'] == courses[random_number-base_id-1].id


@pytest.mark.django_db
def test_filter_name(client, course_factory):
    max_id = 20
    random_number = random.randint(5, max_id)
    courses = course_factory(_quantity=max_id)
    random_name = courses[random_number - 1].name
    response = client.get(course_api, {'name': random_name})
    data = response.json()[0]
    assert response.status_code == 200
    assert data['name'] == courses[random_number - 1].name


@pytest.mark.django_db
def test_create_course(client, one_course):
    pre_course_count = Course.objects.count()
    response = client.post(course_api, {'name': 'Python for beginners'})
    course_count = Course.objects.count()
    assert response.status_code == 201
    assert pre_course_count + 1 == course_count


@pytest.mark.django_db
def test_update_course(client, one_course):
    course_id = one_course.id
    pattern_name = 'Java course'
    response = client.patch(course_api + f'{course_id}/', {'name': pattern_name})
    assert response.status_code == 200
    assert Course.objects.filter(id=course_id)[0].name == pattern_name


@pytest.mark.django_db
def test_delete_course(client, course_factory, one_course):
    base_id = one_course.id
    number_courses = 10
    del_id = base_id + 9
    course_factory(_quantity=number_courses)
    response = client.delete(course_api + f'{del_id}/')
    assert response.status_code == 204
    assert len(Course.objects.all()) == number_courses
    assert Course.objects.filter(id = del_id) != True
