import json
import os
import requests
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from GreenApi.models import Client, Notification

# Load environment variables
load_dotenv()

class sendMessageView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Получение данных из JSON запроса
            request_data = json.loads(request.body)
            chat_id = request_data.get('chatId')
            message = request_data.get('message')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        if not chat_id or not message:
            return JsonResponse({'error': 'Phone number and message are required.'}, status=400)
        

        # Получение конфиденциальных данных из .env
        api_url = os.getenv('API_URL')
        id_instance = os.getenv('ID_INSTANCE')
        api_token_instance = os.getenv('API_TOKEN_INSTANCE')


        # Формирование URL для отправки сообщения
        send_message_url = f"{api_url}/waInstance{id_instance}/sendMessage/{api_token_instance}"

        # Создание данных для отправки запроса к Green API
        payload = {
            "chatId": f"{chat_id}@c.us",
            "message": message
        }

        # Отправка POST-запроса к Green API
        try:
            response = requests.post(send_message_url, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                try:
                    client = Client.objects.get(phone_number=chat_id)
                except Client.DoesNotExist:
                    client = Client.objects.create(phone_number=chat_id, name="Unknown")

                Notification.objects.create(
                client=client,
                message_type='text',
                direction='outgoing',
                content=message,
                status='sent'
        )
                
                return JsonResponse({'success': 'Message sent successfully.', 'data': response_data}, status=200)
            else:
                return JsonResponse({'error': 'Failed to send message.', 'details': response_data}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': str(e)}, status=500)
        
class sendMultimediaView(View):
    def post(self, request, *args, **kwargs):
        # Получение данных из запроса
        file = request.FILES.get('file')
        chat_id = request.POST.get('chatId')
        caption = request.POST.get('caption', '')

        if not chat_id or not file:
            return JsonResponse({'error': 'Phone number, file, and media type are required.'}, status=400)

        # Сохранение файла временно
        file_path = default_storage.save(file.name, ContentFile(file.read()))
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # Получение конфиденциальных данных из .env
        api_url = os.getenv('API_URL')
        id_instance = os.getenv('ID_INSTANCE')
        api_token_instance = os.getenv('API_TOKEN_INSTANCE')

        # Формирование URL для отправки файла
        send_file_url = f"{api_url}/waInstance{id_instance}/sendFileByUpload/{api_token_instance}"

        # Создание данных для отправки запроса к Green API
        payload = {
            'chatId': f"{chat_id}@c.us",
            'caption': caption
        }
        files = {
            'file': (file.name, open(full_file_path, 'rb'), file.content_type)
        }
        
        # Отправка POST-запроса к Green API
        try:
            response = requests.post(send_file_url, data=payload, files=files)
            response_data = response.json()

            # Удаление временного файла
            default_storage.delete(file_path)

            if response.status_code == 200:
                try:
                    client = Client.objects.get(phone_number=chat_id)
                except Client.DoesNotExist:
                    client = Client.objects.create(phone_number=chat_id, name="Unknown")

                Notification.objects.create(
                client=client,
                message_type='file',
                direction='outgoing',
                content=[chat_id, files],
                status='sent'
        )
                return JsonResponse({'success': 'File sent successfully.', 'data': response_data}, status=200)
            else:
                return JsonResponse({'error': 'Failed to send file.', 'details': response_data}, status=response.status_code)
        except requests.exceptions.RequestException as e:
            # Удаление временного файла в случае ошибки
            default_storage.delete(file_path)
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': str(e)}, status=500)



class SendLocationView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Получение данных из JSON-запроса
            data = json.loads(request.body)
            chat_id = data.get('chatId')
            name_location = data.get('nameLocation')
            address = data.get('address')
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            # Проверка наличия обязательных параметров
            if not all([chat_id, name_location, address, latitude, longitude]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            # Получение конфиденциальных данных из .env
            api_url = os.getenv('API_URL')
            id_instance = os.getenv('ID_INSTANCE')
            api_token_instance = os.getenv('API_TOKEN_INSTANCE')

            # Формирование URL для отправки местоположения
            send_location_url = f"{api_url}/waInstance{id_instance}/sendLocation/{api_token_instance}"

            # Создание данных для отправки запроса к Green API
            payload = {
                "chatId": f"{chat_id}@c.us",
                "nameLocation": name_location,
                "address": address,
                "latitude": latitude,
                "longitude": longitude
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(send_location_url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                try:
                    client = Client.objects.get(phone_number=chat_id)
                except Client.DoesNotExist:
                    client = Client.objects.create(phone_number=chat_id, name="Unknown")

                Notification.objects.create(
                client=client,
                message_type='location',
                direction='outgoing',
                content=[name_location, address, latitude, longitude],
                status='sent'
        )
                return JsonResponse({'success': 'Location sent successfully.', 'data': response_data}, status=200)
            else:
                return JsonResponse({'error': 'Failed to send location.', 'details': response_data}, status=response.status_code)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': str(e)}, status=500)
        

class getNotification(View):
    def get(self, request):
        api_url = os.getenv('API_URL')
        id_instance = os.getenv('ID_INSTANCE')
        api_token_instance = os.getenv('API_TOKEN_INSTANCE')
        receiveTimeout = request.GET.get('receiveTimeout', 10)
        get_notification_url = f"{api_url}/waInstance{id_instance}/receiveNotification/{api_token_instance}?receiveTimeout={receiveTimeout}"

        headers = {
                'Content-Type': 'application/json'
            }
        
        response = requests.get(get_notification_url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            return JsonResponse({'success': 'Notification retrieved successfully.', 'data': response_data}, status=200)
        else:
                return JsonResponse({'error': 'Failed to retrieve notification.', 'details': response_data}, status=response.status_code)
        
class selenium(View):
    def get(self, request, *args, **kwargs):
    
        driver = webdriver.Chrome()
        driver.maximize_window()

        try:

            driver.get("https://green-api.com/docs/")
            wait = WebDriverWait(driver, 5)

            documentation_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Документация API']")))
            documentation_link.click()

            sending_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Отправка']")))
            sending_link.click()

            send_text_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Отправить текст']")))
            send_text_link.click()

            return JsonResponse({"success": True, "message": "Navigation completed successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

        finally:
            driver.quit()
        

