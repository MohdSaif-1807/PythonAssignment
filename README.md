# FastAPI Application with MongoDB Atlas Integration

This project demonstrate the use FlaskAPI with API endpoints, with a test suite.

### Accessing the Application

**In order to run the FastAPI application on the local system:**
  1. we need to clone the repository with the command:

    ```
      git clone 'https://github.com/MohdSaif-1807/PythonAssignment'
    ```
  2. In order to start the FlaskAPI application we need to type the command as follows:
     
     ```
     flaskapi dev main.py
    ```

Once we start the application, we can access the FastAPI application at:

```
http://localhost:8000
```

You can explore the API documentation and interact with the endpoints directly from your browser using FastAPI's interactive Swagger UI.

## API Endpoints

1. **Get All Courses**

   ```
   GET /fetch-all-courses/
   ```

   **Query Parameters:**
   - `domain` (optional): Filter courses by domain.
  
  **Screenshot to fetch all records:**

  ![Screenshot (3)](https://github.com/user-attachments/assets/f285d227-79ab-472d-aa8d-8699cda34760)

  **Screenshot to fetch records based on domain:**
  
  ![Screenshot (4)](https://github.com/user-attachments/assets/f5c685c7-99d4-4ab9-84e6-cfafa84dc894)


2. **Get Course Overview**

   ```
   GET /fetch-specific-record/{course_id}/
   ```

   **Path Parameters:**
   - `course_id`: The ID of the course to retrieve.

  **Screenshot to fetch specific record:**

  ![Screenshot (5)](https://github.com/user-attachments/assets/f3b748fd-11eb-441e-a9b2-282bff99870c)


3. **Get Chapter Information**

   ```
   GET /fetch-specific-chapter-from-record/{chapter_id}/
   ```

   **Path Parameters:**
   - `chapter_id`: The ID of the chapter.

  **Screenshot to get specific chapter information:**
  
  ![Screenshot (6)](https://github.com/user-attachments/assets/b34d53c3-02e4-49a4-ab26-02c51794a276)


4. **Rate a Chapter**

   ```
   POST /add-rating/{chapter_id}/
   ```

   **Path Parameters:**
   - `chapter_id`: The ID of the chapter.

   **Request Body:**

   ```json
   {
     "rating_value": integer
   }
   ```

   **screenshot to give ratings to a specific chapter:**
   
   ![Screenshot (7)](https://github.com/user-attachments/assets/b6c8153b-f40b-4545-8d93-53655acdc50a)


**Testing the Application**

In order to run the Test script for API's we need to run the command as follows:

  ```
  pytest test.py
  ```
**screenshot for the result of the TestScript**

![Screenshot (8)](https://github.com/user-attachments/assets/e483fcc0-7b5f-45fc-a19a-7eb6af0555ad)




Thank you for using this FastAPI application!

```

Make sure to replace placeholders such as `your-email@example.com`, `yourusername`, and `your-repository` with your actual details. Adjust the content if there are additional specifics or features you want to highlight.
