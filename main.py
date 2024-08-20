from fastapi import FastAPI,HTTPException

app = FastAPI()

import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from bson.json_util import dumps, loads 
# Load JSON data
with open('courses.json', 'r') as file:
    courses = json.load(file)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Coursesdata']

# # Drop existing collections if any
# db.courses.drop()

# Create collections
course_collection = db['courses']

# Create indices
course_collection.create_index({
    'course_title':1,
    'date':-1,
    'total_course_rating':-1
})

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
                '_id':ObjectId(),
                'title': i['name'], 
                'text': i['text'],
                'total_rating':0.0,
                'average_rating':0.0,
                'total_rating_count':0
            })
        course['chapters'] = temp_chapters
        course_collection.insert_one(course)

# parse_courses(courses)
# print("Data inserted into MongoDB sucessfully.")


@app.get('/fetch-all-courses')
async def get_all_course(domain: str | None = None):
    try:
        sorted_data = []
        if domain:
            sorted_data = course_collection.find({ "domain": { "$elemMatch": { "$eq":domain } } }).sort({
            'name':1,
            'date':-1,
            'course_average_rating':-1
            })
            temp_data = list(sorted_data)
            if(len(list(temp_data)) == 0):
                raise HTTPException(status_code=404,detail=f"No record found with the following domain: {domain}")
            sorted_data = temp_data
        else:
            sorted_data = course_collection.find({}).sort({
            'name':1,
            'date':-1,
            'course_average_rating':-1
            })
        result_data = []
        for i in list(sorted_data):
            chapters_count = []
            for j in i['chapters']:
                chapters_count.append({
                     '_id':str(j['_id']),
                    'title':j['title'],
                    'text': j['text'],
                    'total_rating':j['total_rating'],
                    'average_rating':j['average_rating'],
                    'total_rating_count':j['total_rating_count']
                })
            result_data.append({
                '_id':str(i['_id']),
                'name':i['name'],
                'date':i['date'],
                'description':i['description'],
                'domain':i['domain'],
                'chapters':chapters_count,
                'course_average_rating':i['course_average_rating'],
                'total_course_rating':i['total_course_rating'],
                'course_rating_count':i['course_rating_count']
            })
        return list(result_data)
    except HTTPException as http_error:
        raise http_error  
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@app.get('/fetch-specific-record/{course_id}')
async def get_specific_record(course_id: str):
    try:
        course_object_id = ObjectId(course_id)
        data = course_collection.find_one({"_id":course_object_id})
        if data:
            chapters_count = []
            for j in data['chapters']:
                chapters_count.append({
                     '_id':str(j['_id']),
                    'title':j['title'],
                    'text': j['text'],
                    'total_rating':j['total_rating'],
                    'average_rating':j['average_rating'],
                    'total_rating_count':j['total_rating_count']
                })
            specific_data = {
              '_id':str(data['_id']),
                'name':data['name'],
                'date':data['date'],
                'description':data['description'],
                'domain':data['domain'],
                'chapters':chapters_count,
                'course_average_rating':data['course_average_rating'],
                'total_course_rating':data['total_course_rating'],
                'course_rating_count':data['course_rating_count']         
            }
            return specific_data
        else:
            raise HTTPException(status_code=404,detail="No record found with provided course_id")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(e)
        return HTTPException(status_code=500,detail=str(e))
    


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
            resultant_data = {
                '_id':str(data['_id']),
                'chapters': {
                    '_id': str(chapter['_id']),
                    'title': chapter['title'],
                    'text': chapter['text'],
                    'total_rating':chapter['total_rating'],
                    'average_rating':chapter['average_rating'],
                    'total_rating_count':chapter['total_rating_count']
                }
            }
            return resultant_data
        else:
            raise HTTPException(status_code=404,detail=f"No record found with provided chapter_id: {chapter_id}")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.post('/add-rating/{chapter_id}',status_code=201)
async def give_rating(chapter_id: str,rating: Rating):
    try:
        #updating chapter count,total
        course_collection.update_one(
        {
            'chapters._id':ObjectId(chapter_id)
        },
        {
            "$inc":{
                "chapters.$.total_rating_count":1,
                "chapters.$.total_rating":rating.rating_value
            }
        })
        temp_chapter_data = course_collection.find_one(
            {
                'chapters._id':ObjectId(chapter_id)
            },
            {
                'chapters.$':1
            }
        )
        tp_chapter = temp_chapter_data['chapters']
        #updating average rating
        course_collection.update_one({
            'chapters._id':ObjectId(chapter_id)
        },{
            
                "$set":
                {
             "chapters.$.average_rating":(tp_chapter[0]['total_rating']/tp_chapter[0]['total_rating_count'])
                }
            
        })

        course_collection.update_one(
                {
                    '_id':ObjectId(temp_chapter_data['_id'])
                },
                {
                    "$inc":{
                        "course_rating_count":1,
                        "total_course_rating":rating.rating_value
                    }
                }
        )
        temp_course_data = course_collection.find_one({
            "_id":ObjectId(temp_chapter_data['_id'])
        })
        if temp_chapter_data:
            course_collection.update_one(
                {
                    "_id":ObjectId(temp_chapter_data['_id'])
                },
                {
                    "$set":{
                        "course_average_rating":(temp_course_data['total_course_rating']/temp_course_data['course_rating_count'])
                    }
                }
            )
            resultant_data = course_collection.find_one({
            "_id":ObjectId(temp_chapter_data['_id'])
            })
            chapters_count = []
            for j in resultant_data['chapters']:
                chapters_count.append({
                     '_id':str(j['_id']),
                    'title':j['title'],
                    'text': j['text'],
                    'total_rating':j['total_rating'],
                    'average_rating':j['average_rating'],
                    'total_rating_count':j['total_rating_count']
                })
            specific_data = {
              '_id':str(resultant_data['_id']),
                'name':resultant_data['name'],
                'date':resultant_data['date'],
                'description':resultant_data['description'],
                'domain':resultant_data['domain'],
                'chapters':chapters_count,
                'course_average_rating':resultant_data['course_average_rating'],
                'total_course_rating':resultant_data['total_course_rating'],
                'course_rating_count':resultant_data['course_rating_count']         
            }
            return specific_data
        else:
            raise HTTPException(status_code=404,detail=f"No record found with the following chapter id: {chapter_id}")
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@app.get('/')
async def main():
    return {
        'message': 'hello world'
    }