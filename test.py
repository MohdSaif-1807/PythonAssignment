import requests
from pydantic import BaseModel
from bson import ObjectId
import datetime
from typing import List

class Chapter(BaseModel):
    _id: ObjectId
    title: str
    text: str
    total_rating: float
    average_rating: float
    total_rating_count: int


class Specific_Chapter(BaseModel):
    _id: ObjectId
    chapters: Chapter

class Courses(BaseModel):
    _id: ObjectId
    name: str
    date: datetime.datetime
    description: str
    domain:List[str]
    chapters: List[Chapter]
    course_average_rating: float
    total_course_rating: float
    course_rating_count: float


def test_fetching_available_courses():
    domain = ""
    url = "http://127.0.0.1:8000/fetch-all-courses"
    response = requests.get(f"{url}?domain={domain}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list),"Response should be a list"
    for i in data:
        try:
            course = Courses(**i)
            assert isinstance(course,Courses), "Response should be of Course Type"
            if domain:
                for j in i['domain']:
                    assert j == domain
        except Exception as e:
            assert False, f"Validation error: {str(e)}"


def test_fetching_of_specific_course():
    course_id = "66c4259676f7980192ddb982"
    url = "http://127.0.0.1:8000/fetch-specific-record"
    response = requests.get(f"{url}/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,dict), "Response should be a dictionary"
    try:
        if data['_id'] == course_id:
            course = Courses(**data)
            assert isinstance(course,Courses), "Response should be of Course type"
        else:
            assert False,"Response id is not matched with course_id"
    except Exception as e:
        assert False, f"Validation error: {str(e)}"


def test_fetching_of_specific_chapter():
    chapter_id = "66c4259676f7980192ddb970"
    url = "http://127.0.0.1:8000/fetch-specific-chapter-from-record"
    response = requests.get(f"{url}/{chapter_id}")
    data = response.json()
    assert isinstance(data,dict)
    temp_chapters = data['chapters']
    try:
        if temp_chapters['_id'] == chapter_id:
            chapter = Specific_Chapter(**data)
            assert isinstance(chapter,Specific_Chapter), "Response should be of Specific_Chapter type"
        else:
            assert False,"Response id is not matched with chapter_id"
    except Exception as e:
        assert False, f"Validation error: {str(e)}"


def test_add_new_rating():
    chapter_id = "66c4259676f7980192ddb970"
    url = f"http://127.0.0.1:8000/add-rating/{chapter_id}"
    body_json = {
        "rating_value" : 5
    }
    response = requests.post(url,json=body_json)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data,dict)
    try:
        course = Courses(**data)
        assert isinstance(course,Courses), "Response should be of Course Type"
    except Exception as e:
        assert False, f"Something went wrong {str(e)}"


test_fetching_available_courses()
test_fetching_of_specific_course()
test_fetching_of_specific_chapter()
test_add_new_rating()