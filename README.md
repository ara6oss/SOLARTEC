# Solar WhatsApp API Integration Project

This is a Django-based project that integrates with the WhatsApp API using GreenAPI for sending messages, multimedia files, locations, and performing Selenium automation.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Database Models](#database-models)
- [Selenium Automation](#selenium-automation)
- [Contributing](#contributing)
- [License](#license)

## Overview
This project integrates with WhatsApp via the Green API to provide automated messaging, multimedia sharing, location sharing, and Selenium-based navigation features. It includes functionality to interact with clients and notifications stored in PostgreSQL, providing an efficient messaging platform.

## Features
- Send text messages to WhatsApp users
- Send multimedia files (audio, video, images, etc.) to WhatsApp users
- Share geolocation data to WhatsApp users
- Retrieve notifications from WhatsApp API
- Automate browser tasks using Selenium

## Technologies Used
- **Django**: Backend framework for server-side logic
- **PostgreSQL**: Database for storing client and notification data
- **Green API**: WhatsApp API integration
- **Selenium**: Automated browser navigation
- **dotenv**: Managing environment variables

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip (Python package installer)
- Git

### Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/ara6oss/solar-whatsapp-api.git
   cd solar-whatsapp-api
   ```

2. **Create a Virtual Environment**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add the following variables:

   ```env
   API_URL="https://api.green-api.com"
   ID_INSTANCE="your_instance_id"
   API_TOKEN_INSTANCE="your_api_token"
   SECRET_KEY="your_django_secret_key"
   DB_NAME="your_db_name"
   DB_USER="your_db_user"
   DB_PASSWORD="your_db_password"
   DB_HOST="localhost"
   DB_PORT="5432"
   DEBUG=True
   ```

5. **Configure Database**

   Update the `DATABASES` setting in `settings.py`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.getenv('DB_NAME'),
           'USER': os.getenv('DB_USER'),
           'PASSWORD': os.getenv('DB_PASSWORD'),
           'HOST': os.getenv('DB_HOST'),
           'PORT': os.getenv('DB_PORT'),
       }
   }
   ```

6. **Run Migrations**

   ```sh
   python manage.py migrate
   ```

## Running the Server

To run the development server, use:

```sh
python manage.py runserver
```

The server will be accessible at `http://127.0.0.1:8000/`.

## API Endpoints

### Send Message
- **Endpoint**: `/api/v1/sendMessage/`
- **Method**: `POST`
- **Description**: Sends a text message to a WhatsApp user.
- **Payload** (JSON):
  ```json
  {
      "chatId": "recipient_phone_number",
      "message": "Your message here"
  }
  ```

### Send Multimedia
- **Endpoint**: `/api/v1/sendFile/`
- **Method**: `POST`
- **Description**: Sends a multimedia file to a WhatsApp user.
- **Form Data**:
  - `file`: The file to be sent
  - `chatId`: The recipient phone number
  - `caption`: Optional caption for the file

### Send Location
- **Endpoint**: `/api/v1/sendLocation/`
- **Method**: `POST`
- **Description**: Sends a geolocation to a WhatsApp user.
- **Payload** (JSON):
  ```json
  {
      "chatId": "recipient_phone_number",
      "nameLocation": "Location Name",
      "address": "Address Here",
      "latitude": 12.345678,
      "longitude": 98.765432
  }
  ```

### Get Notifications
- **Endpoint**: `/api/v1/getNotification/`
- **Method**: `GET`
- **Description**: Retrieves notifications from the Green API.

## Environment Variables
Ensure the following environment variables are set:
- `API_URL`: Base URL for the Green API
- `ID_INSTANCE`: Instance ID for Green API
- `API_TOKEN_INSTANCE`: API Token for authentication
- `SECRET_KEY`: Django secret key for security
- Database credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)

## Database Models
- **Client**: Stores user information.
- **Notification**: Stores information about the messages sent/received and their status.

The models are related via ForeignKey, linking `Notification` to `Client`.

## Selenium Automation
- **Endpoint**: `/api/v1/selenium/`
- **Method**: `GET`
- **Description**: Automates navigation to Green API documentation and clicking on specific elements.

## Contributing
Feel free to contribute to this project by creating pull requests or raising issues. Contributions are welcome and appreciated!

## License
This project is licensed under the MIT License.
