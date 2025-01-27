from rest_framework.views import APIView
from .models import CustomUser, ImageModel
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer, BlogImageSerializer, CustomTokenObtainPairSerializer
from .email import send_otp_mail, send_otp_reset
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from django.db.models import Max
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .auth import get_user_from_token
from rest_framework.permissions import AllowAny


# Create your views here.



# Register View

class UserRegister(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        first_name = request.data.get("firstname")
        last_name = request.data.get("lastname")
        username = request.data.get("username")
        email = request.data.get("email")
        phone_number = request.data.get("phonenumber")
        password = request.data.get("password")
        confirm_password = request.data.get("confirmpassword")
        
        if CustomUser.objects.filter(email=email).exists():
            return Response({"message":"Email is already exist"}, status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).exists():
            return Response({"message":"Username is already exist"}, status=status.HTTP_400_BAD_REQUEST)
        if password!=confirm_password:
            return Response({"message":"Password do not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'username':username,
            'first_name':first_name,
            'last_name':last_name,
            'email':email,
            'phone_number':phone_number,
            'password':password
        }
        
        serializer = CustomUserSerializer(data=data)
        
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()

            send_otp_mail(serializer.data['email'])

            return Response({"message":"Registration Successfully Plese check your email for conformation"}, status=status.HTTP_201_CREATED)
        except:
            return Response(
                {"message": "User is not created"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            
            
# User verify

class UserVerify(APIView):
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        print("its working")
        email = request.data.get("email")
        otp = request.data.get("otp")
        
        if(email):
            try:
                user = CustomUser.objects.filter(email=email).first()
                if(otp):
                    if(user.otp==otp):
                        user.is_verified = True
                        user.save()
                        return Response({"message":"Verification Successfully"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message":"Verification Unsuccessfully"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"message":"Verification Unsuccessfully"}, status=status.HTTP_404_NOT_FOUND)
            except CustomUser.DoesNotExist:
                return Response({"message":"User is not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
             return Response({"message":"Verification Unsuccessfully"}, status=status.HTTP_404_NOT_FOUND)
          
          
            
# User login

class UserLogin(TokenObtainPairView):
    
    permission_classes = [AllowAny]
    
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        
        
        try:
            response = super().post(request, *args, **kwargs)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        data = response.data
        access_token = data.get('access', None)
        
        if access_token:
            user_id = get_user_from_token(access_token)
            user = CustomUser.objects.get(id=user_id)
            if(user is None):
                return Response({"message":"User Does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            
            response.data["email"] = user.email
            response.data["userId"] = str(user.id)
            response.data["message"] = "Login Successfully"
            
            return Response(response.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"User Does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# User Email verification

class UserEmail(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        email = request.data.get("email")
        
        try:
            user = CustomUser.objects.get(email=email)
            send_otp_reset(user.email)
            return Response({"message":"Plese check your email for conformation"}, status=status.HTTP_201_CREATED)
        except CustomUser.DoesNotExist:
            return Response({"message":"User not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
#  User reset email

class ResetPassword(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")
        confirmpassword = request.data.get("confirmpassword")
        
        if(not email or not otp or not password or not confirmpassword):
            return Response({"message": "All fields (email, otp, password, confirmpassword) are required."},status=status.HTTP_400_BAD_REQUEST,)
        if(password!=confirmpassword):
            return Response({"message":"Password and Confirm password do not match.."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.objects.get(email=email)
            if(user.otp != otp):
                return Response({"message":"Password reset unsuccessfully"}, status=status.HTTP_404_NOT_FOUND)
            user.set_password(password)
            user.save()
            return Response({"message":"Password reset successfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message":"Password reset unsuccessfully"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# Create Blog view
        
class CreateBlog(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        user = request.user
        
        try:
            user = CustomUser.objects.get(id=user.id)
        except CustomUser.DoesNotExist:
            return Response({"message":"User not found"}, status=status.HTTP_400_BAD_REQUEST)
            
        images_data = []
        for i in range(len(request.data)//4):
            image_data = {
                'user':user.id,
                'image': request.data.get(f'{i}[file]'),
                'title': request.data.get(f'{i}[title]'),
                'order': int(request.data.get(f'{i}[order]',0))
            }
            images_data.append(image_data)

        if not images_data:
            return Response({"message":"No Images Provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        max_order = ImageModel.objects.aggregate(Max('order'))['order__max']
        current_order = (max_order + 1) if max_order is not None else 1
        created_images = []
        
        for image_data in images_data:
            image_data['order'] = current_order
            current_order +=1
            serializer = BlogImageSerializer(data=image_data)
            if serializer.is_valid():
                serializer.save()
                created_images.append(serializer.data)
            else:
                return Response(
                    {"message": "Error with one of the images"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Images uploaded successfully"},status=status.HTTP_201_CREATED)
    
    
    
# Get all post

class GetAllPost(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        user = request.user

        try:
            user = CustomUser.objects.get(id=user.id)
            images = ImageModel.objects.filter(user=user.id).order_by('order')
            if images.exists():
                serializer = BlogImageSerializer(images, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No images found for this user."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message":"User not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# Update Image

class UpdateImage(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        user = request.user
        user_id = user.id  
        source = request.data.get('sourceId')
        destination = request.data.get('destinationId')
        
        try:
            image1 = ImageModel.objects.get(id=int(source))
            image2 = ImageModel.objects.get(id=int(destination))
           
            if (image1.user.id == user_id and image2.user.id == user_id):
                image1.order, image2.order = image2.order, image1.order
                image1.title, image2.title = image2.title, image1.title
                image2.save()
                image1.save()
                return Response({"message":"Successfully updata"}, status=status.HTTP_200_OK)
            else :
                return Response({"message":"This user have no access to update images"}, status=status.HTTP_400_BAD_REQUEST)
        except ImageModel.DoesNotExist:
            return Response({"message":"Image not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
# Delete Image view

class DeleteImageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        
        image_id = request.data.get('ImageDelete')
        user = request.user
        
        try:
            image = ImageModel.objects.get(id = int(image_id))
            if (user.id == image.user.id):
                image.delete()
                return Response({"message":"Image deleted successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"User have't permission to delete this image"}, status=status.HTTP_200_OK)
        except ImageModel.DoesNotExist:
            return Response({"message":"Image does not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
# Update unique image

class UpdateUniqueImage(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        
        user = request.user
        post_id = request.data.get('postId', None)
        image = request.FILES.get('image', None)
        title = request.data.get('postTitle', None)
        
        if post_id is None:
            return Response({"message":"The post data is not provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = ImageModel.objects.get(id=int(post_id))
            if(post.user.id == user.id):
                if image is not None:
                    post.image = image
                if title is not None:
                    post.title = title
                post.save()
                return Response({"message":"Updated successfully"},status=status.HTTP_200_OK)
            else:
                return Response({"message":"This user have't permision to edit this image"}, status=status.HTTP_400_BAD_REQUEST)    
        except ImageModel.DoesNotExist:
            return Response({"message":"The image is not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
                

        
       
            
                        
                
            
            

            
        
