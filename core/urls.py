from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('update-game-profile/', views.update_game_profile, name='update_game_profile'),
    path('link-coc-account/', views.link_coc_account, name='link_coc_account'),
    path('leaderboard-data/', views.leaderboard_data, name='leaderboard_data'),
    path('leaderboard-profile/<int:profile_id>/', views.leaderboard_profile_data, name='leaderboard_profile_data'),
    path('submit-post/', views.submit_post, name='submit_post'),
    path('vote-post/<int:post_id>/', views.vote_post, name='vote_post'),
    path('login/', views.auth_page, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]