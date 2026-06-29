from django.views.generic import TemplateView
from django.shortcuts import render

class LoginView(TemplateView):
    template_name = 'login.html'

class SignupView(TemplateView):
    template_name = 'signup.html'

class VerifyView(TemplateView):
    template_name = 'verify.html'

class CompleteProfileView(TemplateView):
    template_name = 'complete_profile.html'

class UploadPhotoView(TemplateView):
    template_name = 'upload_photo.html'

class ForgotPasswordView(TemplateView):
    template_name = 'forgot_password.html'

class ResetPasswordView(TemplateView):
    template_name = 'reset_password.html'

class FeedView(TemplateView):
    template_name = 'feed.html'

class CreatePostView(TemplateView):
    template_name = 'create_post.html'

class PostDetailView(TemplateView):
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_id'] = self.kwargs['pk']
        return context

class ProfileView(TemplateView):
    template_name = 'profile.html'

class SettingsView(TemplateView):
    template_name = 'settings.html'


class FollowersListView(TemplateView):
    template_name = 'followers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs['pk']
        context['list_type'] = self.kwargs.get('list_type', 'followers')
        return context


class ExploreView(TemplateView):
    template_name = 'explore.html'

class SearchView(TemplateView):
    template_name = 'search.html'

class UserProfileView(TemplateView):
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs['pk']
        return context
