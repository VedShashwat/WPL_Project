from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update-game-profile/', views.update_game_profile, name='update_game_profile'),
    path('link-coc-account/', views.link_coc_account, name='link_coc_account'),
    path('link-cr-account/', views.link_cr_account, name='link_cr_account'),
    path('leaderboard-data/', views.leaderboard_data, name='leaderboard_data'),
    path('leaderboard-profile/<int:profile_id>/', views.leaderboard_profile_data, name='leaderboard_profile_data'),
    path('submit-post/', views.submit_post, name='submit_post'),
    path('vote-post/<int:post_id>/', views.vote_post, name='vote_post'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
    path('login/', views.auth_page, name='login'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]