from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.FeedView.as_view(), name='feed'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
    path('complete-profile/', views.CompleteProfileView.as_view(), name='complete_profile'),
    path('upload-photo/', views.UploadPhotoView.as_view(), name='upload_photo'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('post/new/', views.CreatePostView.as_view(), name='create_post'),
    path('post/<uuid:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('reels/', views.ExploreView.as_view(), name='explore'),
    path('explore/', RedirectView.as_view(url='/reels/', permanent=True)),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/<uuid:pk>/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/<uuid:pk>/<str:list_type>/', views.FollowersListView.as_view(), name='follow_list'),
    path('search/', views.SearchView.as_view(), name='search'),

    path('api/users/', include('users.urls')),
    path('api/post/', include('post.urls')),
]

if not settings.CLOUDINARY_STORAGE['CLOUD_NAME']:
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    else:
        urlpatterns += [
            re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        ]