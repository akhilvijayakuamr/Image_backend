from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', views.UserRegister.as_view(), name="register"), #-> User Register url
    path('verify/', views.UserVerify.as_view(), name="verify"), #-> User Verification url
    path('login/', views.UserLogin.as_view(), name="login"), #-> User Login url
    path('email/', views.UserEmail.as_view(), name='email'), #-> User email verification url
    path('reset/', views.ResetPassword.as_view(), name="reset"), #-> User reset pasword url
    path('create/', views.CreateBlog.as_view(), name="create"), #-> User Create blog
    path('all_post/', views.GetAllPost.as_view(), name="all_post"), #-> Get all posts
    path('refresh/', TokenRefreshView.as_view(), name="refresh_token"), #-> Get refresh token
    path('update_image/', views.UpdateImage.as_view(), name="update_image"), #-> Update Image
    path('delete_image/', views.DeleteImageView.as_view(), name="delete_image"), #-> Delete Image
    path('update_unique/', views.UpdateUniqueImage.as_view(), name="update_unique"), #-> Update uniq image
]
