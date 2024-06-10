### Project Description: contact_API

**contact_API** is a powerful and user-friendly API designed to manage your contacts efficiently. With a sleek interface and robust functionality, it supports essential CRUD operations—Create, Read, Update, and Delete—ensuring seamless management of your contact information.

#### Key Features:

1. **User-Friendly Interface**: Easily manage your contacts with an intuitive and responsive interface.
2. **Complete CRUD Operations**: Effortlessly create new contacts, view existing ones, update details, and delete contacts as needed.
3. **Additional Functionalities**:
   - **Birthday Reminder**: Retrieve contacts who have birthdays within the next 7 days, ensuring you never miss an important date.
   - **Advanced Search**: Perform searches using any piece of information related to a contact, making it simple to find exactly who you're looking for.
4. **Developer Tools**:
   - **Debug Functionality**: Flood the database with fake data for testing and experimentation.
   - **Database Management**: Clear the entire database with a single click, providing a fresh slate for your development needs.
5. **Data Validation**: Input data types are rigorously validated using Pydantic schemas, ensuring data integrity and consistency.

#### How to Run:

1. **Clone the Repository**:
   ```sh
   git clone <repo_url>
   ```

2. **Create and Activate a Virtual Environment**:
   - **Create Virtual Environment**:
     ```sh
     python -m venv env
     ```
   - **Activate Virtual Environment** (Linux/Mac):
     ```sh
     source env/bin/activate
     ```
     **Activate Virtual Environment** (Windows):
     ```sh
     .\env\Scripts\activate
     ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Create .env file**
   ```sh
   touch .env
   ```
5. **In .env**
   add those variables in your .env file:
   ```
   SECRET_KEY = your JWT secret
   SECRET_KEY_EMAIL = your JWT secret for email token
   SENDER = email address for smtp server
   PASSWORD = password for email address

   CLOUD_NAME = cloudinary name
   CLOUD_KEY = cloudinary key
   CLOUD_SECRET = cloudinary secret
   ```
   
7. **Run Docker Compose**:
   ```sh
   docker-compose up
   ```

8. **Run the Application**:
   ```sh
   python main.py
   ```

#### Technologies Used:

- **Python**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Pydantic**
- **Docker**
- **Poetry**
- **smtp**
- **cloudinaryAPI**

Unlock the full potential of your contact management with **contact_API**—a blend of simplicity, efficiency, and powerful features tailored for developers and users alike.
