from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
import requests,json,cloudscraper
from rest_framework.response import Response
from .serializers import AiChatSerializer,RegisterSerializer,LoginSerializer
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

# Create your views here.
GEMINI_API_KEY = "AIzaSyB206AXvkDhchrCo1qXtZsc4ihFqC5NRcQ"

proxies = {
    "http": "http://103.125.174.62:8080"
}

def link_scraper(link):
    scraper = cloudscraper.create_scraper()
    scraper.proxies.update(proxies)
    html_content = scraper.get(link).text 
    return html_content


def chat_gemini(msg,scrape_html=None):
    if scrape_html == None:
        complete_msg = {
        "contents": [{
            "parts":[{"text": f"{msg}"}]
            }]
        }
        complete_msg_json = json.dumps(complete_msg)
        res = requests.post(url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",data=f'{complete_msg_json}')
    else:  
        complete_msg_link = {
        "contents": [{
            "parts":[{"text": f"summarize the content : {scrape_html}"}]
            }]
        }
        complete_msg_json_link = json.dumps(complete_msg_link)
        res = requests.post(url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",data=f'{complete_msg_json_link}')

    
    return res

class AiChatApi(GenericViewSet):
    serializer_class = AiChatSerializer
    # permission_classes = [IsAuthenticated]

    def ai_create(self,request):
        user_message = request.data.get('message') 
        if "https" in user_message:
            scrape_html_content = link_scraper(user_message)
            chat_res = chat_gemini(user_message,scrape_html_content)
        else:
            chat_res = chat_gemini(user_message)
        
        if chat_res.status_code == 400:
            return Response(chat_res.json(),status=status.HTTP_400_BAD_REQUEST)
        
        return Response(chat_res.json())
    
class UserApiView(GenericViewSet):
    serializer_class = RegisterSerializer

    def get_serializer_class(self):
        if self.action == 'register':
            return RegisterSerializer
        else:
            return LoginSerializer

    def register(self,request):
        password = request.data.get('password')
        hash_password = make_password(password)
        data = request.data.copy()
        data['password'] = hash_password
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            token,_ = Token.objects.get_or_create(user=user)    
            return Response({'token':token.key},status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def login(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email,password=password)

        if user !=  None:
            token,_ = Token.objects.get_or_create(user=user)    
            return Response({'token':token.key})
        else:
            return Response({'error':'Invalid credentials'},status=status.HTTP_400_BAD_REQUEST)