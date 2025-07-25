from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import logging
import traceback

class GenerateToken(APIView):
    
    """
    View to obtain token for the provided username and password.
    """
    
    def get_user(self, username, password):
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        return user
    
    def post(self, request, *args, **kwargs):
        
        try:
        
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return Response({"success" : False, "message" : "Please enter valid credentials"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = self.get_user(username, password)
            
            if not user:
                return Response({"success" : False, "message" : "User not authorized"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if not user.check_password(password):
                return Response({
                    "success" : False,
                    "message" : "Invalid password"
                }, status=400)

            token, created = Token.objects.get_or_create(user=user)
            
            return Response({"token": token.key, "success" : True}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.exception(e)
            logging.exception(traceback.format_exc())
            return Response({
                "success" : False,
                "message" : "Internal Server Error"
            }, status=500)
        