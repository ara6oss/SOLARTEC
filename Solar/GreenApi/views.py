import json
import os
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views import View
from dotenv import load_dotenv
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from GreenApi.models import Client, Notification

# Load environment variables
load_dotenv()


class GreenAPIService:
    def __init__(self):
        self.api_url = os.getenv('API_URL')
        self.id_instance = os.getenv('ID_INSTANCE')
        self.api_token_instance = os.getenv('API_TOKEN_INSTANCE')

    def get_url(self, endpoint):
        return f"{self.api_url}/waInstance{self.id_instance}/{endpoint}/{self.api_token_instance}"

    def send_request(self, url, payload=None, files=None, method='post'):
        headers = {'Content-Type': 'application/json'}
        try:
            if method == 'post':
                response = requests.post(url, json=payload, files=files, headers=headers)
            else:
                response = requests.get(url, headers=headers)
            return response, None
        except requests.exceptions.RequestException as e:
            return None, str(e)

    def create_client_if_not_exists(self, chat_id):
        try:
            client = Client.objects.get(phone_number=chat_id)
        except Client.DoesNotExist:
            client = Client.objects.create(phone_number=chat_id, name="Unknown")
        return client

    def create_notification(self, client, message_type, direction, content, status):
        Notification.objects.create(
            client=client,
            message_type=message_type,
            direction=direction,
            content=content,
            status=status
        )


class sendMessageView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.green_api_service = GreenAPIService()

    def post(self, request, *args, **kwargs):
        try:
            request_data = json.loads(request.body)
            chat_id = request_data.get('chatId')
            message = request_data.get('message')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        if not chat_id or not message:
            return JsonResponse({'error': 'Phone number and message are required.'}, status=400)

        send_message_url = self.green_api_service.get_url('sendMessage')
        payload = {"chatId": f"{chat_id}@c.us", "message": message}

        response, error = self.green_api_service.send_request(send_message_url, payload=payload)
        if error:
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': error}, status=500)

        response_data = response.json()
        if response.status_code == 200:
            client = self.green_api_service.create_client_if_not_exists(chat_id)
            self.green_api_service.create_notification(client, 'text', 'outgoing', message, 'sent')
            return JsonResponse({'success': 'Message sent successfully.', 'data': response_data}, status=200)
        else:
            return JsonResponse({'error': 'Failed to send message.', 'details': response_data}, status=response.status_code)


class sendMultimediaView(View):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        chat_id = request.POST.get('chatId')
        caption = request.POST.get('caption', '')

        if not chat_id or not file:
            return JsonResponse({'error': 'Phone number, file, and media type are required.'}, status=400)

        file_path = default_storage.save(file.name, ContentFile(file.read()))
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        api_url = os.getenv('API_URL')
        id_instance = os.getenv('ID_INSTANCE')
        api_token_instance = os.getenv('API_TOKEN_INSTANCE')
        send_file_url = f"{api_url}/waInstance{id_instance}/sendFileByUpload/{api_token_instance}"

        payload = {
            'chatId': f"{chat_id}@c.us",
            'caption': caption
        }
        files = {
            'file': (file.name, open(full_file_path, 'rb'), file.content_type)
        }

        try:
            response = requests.post(send_file_url, data=payload, files=files)
            response_data = response.json()
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
            default_storage.delete(file_path)
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': str(e)}, status=500)



class sendLocationView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.green_api_service = GreenAPIService()

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            chat_id = data.get('chatId')
            name_location = data.get('nameLocation')
            address = data.get('address')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

        if not all([chat_id, name_location, address, latitude, longitude]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        send_location_url = self.green_api_service.get_url('sendLocation')
        payload = {
            "chatId": f"{chat_id}@c.us",
            "nameLocation": name_location,
            "address": address,
            "latitude": latitude,
            "longitude": longitude
        }

        response, error = self.green_api_service.send_request(send_location_url, payload=payload)
        if error:
            return JsonResponse({'error': 'An error occurred while sending the request.', 'details': error}, status=500)

        response_data = response.json()
        if response.status_code == 200:
            client = self.green_api_service.create_client_if_not_exists(chat_id)
            self.green_api_service.create_notification(client, 'location', 'outgoing', [name_location, address, latitude, longitude], 'sent')
            return JsonResponse({'success': 'Location sent successfully.', 'data': response_data}, status=200)
        else:
            return JsonResponse({'error': 'Failed to send location.', 'details': response_data}, status=response.status_code)


class getNotificationView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.green_api_service = GreenAPIService()

    def get(self, request):
        receive_timeout = request.GET.get('receiveTimeout', 10)
        get_notification_url = self.green_api_service.get_url('receiveNotification') + f"?receiveTimeout={receive_timeout}"

        response, error = self.green_api_service.send_request(get_notification_url, method='get')
        if error:
            return JsonResponse({'error': 'An error occurred while retrieving the notification.', 'details': error}, status=500)

        response_data = response.json()
        if response.status_code == 200:
            return JsonResponse({'success': 'Notification retrieved successfully.', 'data': response_data}, status=200)
        else:
            return JsonResponse({'error': 'Failed to retrieve notification.', 'details': response_data}, status=response.status_code)
        

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
        

