from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId # type: ignore
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv

# Initialize FastAPI
app = FastAPI()

# Load environment variables
load_dotenv()

# Load JSON data
with open('courses.json', 'r') as file:
    courses = json.load(file)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URL"))
db = client['Coursesdata']

# Drop existing collections if any (Uncomment to use)
# db.courses.drop()

# Create collection
course_collection = db['courses']

# Create indices
course_collection.create_index([
    ('name', 1),
    ('date', -1),
    ('course_average_rating', -1)
])

class Rating(BaseModel):
    rating_value: float

# Convert data to the correct format and insert into MongoDB
def parse_courses(courses):
    for course in courses:
        course['date'] = datetime.fromtimestamp(course['date'])
        course['total_course_rating'] = 0
        course['course_average_rating'] = 0
        course['course_rating_count'] = 0
        temp_chapters = []
        for i in course['chapters']:
            temp_chapters.append({
                '_id': ObjectId(),
                'title': i['title'],
                'text': i['contents'],
                'total_rating': 0.0,
                'average_rating': 0.0,
                'total_rating_count': 0
            })
        course['chapters'] = temp_chapters
        course_collection.insert_one(course)

# Uncomment to parse and insert data into MongoDB
# parse_courses(courses)
# print("Data inserted into MongoDB successfully.")

@app.get('/fetch-all-courses')
async def get_all_courses(domain: str | None = None):
    try:
        query = {}
        if domain:
            query['domain'] = domain
        sorted_data = course_collection.find(query).sort([
            ('name', 1),
            ('date', -1),
            ('course_average_rating', -1)
        ])
        result_data = []
        for course in sorted_data:
            chapters_count = []
            for chapter in course['chapters']:
                chapters_count.append({
                    '_id': str(chapter['_id']),
                    'title': chapter['title'],
                    'text': chapter['text'],
                    'total_rating': chapter['total_rating'],
                    'average_rating': chapter['average_rating'],
                    'total_rating_count': chapter['total_rating_count']
                })
            result_data.append({
                '_id': str(course['_id']),
                'name': course['name'],
                'date': course['date'],
                'description': course['description'],
                'domain': course['domain'],
                'chapters': chapters_count,
                'course_average_rating': course['course_average_rating'],
                'total_course_rating': course['total_course_rating'],
                'course_rating_count': course['course_rating_count']
            })
        if not result_data:
            raise HTTPException(status_code=404, detail=f"No records found for domain: {domain}")
        return result_data
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/fetch-specific-record/{course_id}')
async def get_specific_record(course_id: str):
    try:
        course_object_id = ObjectId(course_id)
        course = course_collection.find_one({"_id": course_object_id})
        if course:
            chapters_count = []
            for chapter in course['chapters']:
                chapters_count.append({
                    '_id': str(chapter['_id']),
                    'title': chapter['title'],
                    'text': chapter['text'],
                    'total_rating': chapter['total_rating'],
                    'average_rating': chapter['average_rating'],
                    'total_rating_count': chapter['total_rating_count']
                })
            return {
                '_id': str(course['_id']),
                'name': course['name'],
                'date': course['date'],
                'description': course['description'],
                'domain': course['domain'],
                'chapters': chapters_count,
                'course_average_rating': course['course_average_rating'],
                'total_course_rating': course['total_course_rating'],
                'course_rating_count': course['course_rating_count']
            }
        else:
            raise HTTPException(status_code=404, detail="No record found with the provided course_id")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/fetch-specific-chapter-from-record/{chapter_id}')
async def get_specific_chapter(chapter_id: str):
    try:
        data = course_collection.find_one(
            {
                "chapters._id": ObjectId(chapter_id)
            },
            {
                "chapters.$": 1
            }
        )
        if data:
            chapter = data["chapters"][0]
            return {
                '_id': str(data['_id']),
                'chapters': {
                    '_id': str(chapter['_id']),
                    'title': chapter['title'],
                    'text': chapter['text'],
                    'total_rating': chapter['total_rating'],
                    'average_rating': chapter['average_rating'],
                    'total_rating_count': chapter['total_rating_count']
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"No record found with provided chapter_id: {chapter_id}")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/add-rating/{chapter_id}', status_code=201)
async def give_rating(chapter_id: str, rating: Rating):
    try:
        # Update chapter rating
        result = course_collection.update_one(
            {'chapters._id': ObjectId(chapter_id)},
            {
                "$inc": {
                    "chapters.$.total_rating_count": 1,
                    "chapters.$.total_rating": rating.rating_value
                }
            }
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"No record found with the following chapter_id: {chapter_id}")

        # Update chapter average rating
        chapter_data = course_collection.find_one(
            {'chapters._id': ObjectId(chapter_id)},
            {'chapters.$': 1}
        )
        if not chapter_data:
            raise HTTPException(status_code=404, detail="Chapter data not found")

        chapter = chapter_data['chapters'][0]
        average_rating = chapter['total_rating'] / chapter['total_rating_count']

        course_collection.update_one(
            {'chapters._id': ObjectId(chapter_id)},
            {
                "$set": {
                    "chapters.$.average_rating": average_rating
                }
            }
        )

        # Update course ratings
        course_id = chapter_data['_id']
        course_collection.update_one(
            {'_id': ObjectId(course_id)},
            {
                "$inc": {
                    "course_rating_count": 1,
                    "total_course_rating": rating.rating_value
                }
            }
        )

        # Recalculate course average rating
        course_data = course_collection.find_one({'_id': ObjectId(course_id)})
        if course_data:
            course_average_rating = course_data['total_course_rating'] / course_data['course_rating_count']
            course_collection.update_one(
                {'_id': ObjectId(course_id)},
                {
                    "$set": {
                        "course_average_rating": course_average_rating
                    }
                }
            )

            # Return updated course data
            chapters_count = []
            for chapter in course_data['chapters']:
                chapters_count.append({
                    '_id': str(chapter['_id']),
                    'title': chapter['title'],
                    'text': chapter['text'],
                    'total_rating': chapter['total_rating'],
                    'average_rating': chapter['average_rating'],
                    'total_rating_count': chapter['total_rating_count']
                })
            return {
                '_id': str(course_data['_id']),
                'name': course_data['name'],
                'date': course_data['date'],
                'description': course_data['description'],
                'domain': course_data['domain'],
                'chapters': chapters_count,
                'course_average_rating': course_data['course_average_rating'],
                'total_course_rating': course_data['total_course_rating'],
                'course_rating_count': course_data['course_rating_count']
            }
        else:
            raise HTTPException(status_code=404, detail=f"No record found with course_id: {course_id}")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
async def main():
    return {'message': 'hello world'}
