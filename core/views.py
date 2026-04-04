import logging
import time

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import PlayerProfile
from .utils import fetch_coc_player

logger = logging.getLogger(__name__)


def auth_page(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	login_form = AuthenticationForm(request, data=request.POST or None)
	signup_form = CustomUserCreationForm(request.POST or None)
	active_panel = 'login'

	if request.method == 'POST':
		form_type = request.POST.get('form_type')
		active_panel = form_type if form_type in {'login', 'signup'} else 'login'

		if form_type == 'login' and login_form.is_valid():
			auth_login(request, login_form.get_user())
			return redirect('dashboard')

		if form_type == 'signup' and signup_form.is_valid():
			user = signup_form.save()
			auth_login(request, user)
			messages.success(request, 'Account created successfully.')
			return redirect('dashboard')

	return render(request, 'registration/login.html', {
		'login_form': login_form,
		'signup_form': signup_form,
		'active_panel': active_panel,
	})


@login_required
def dashboard(request):
	profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	return render(request, 'core/dashboard.html', {'profile': profile})


@login_required
@require_POST
def update_game_profile(request):
	game_id = request.POST.get('game_id', '').strip()
	platform = request.POST.get('platform', '').strip()

	if not game_id or not platform:
		return JsonResponse({'success': False, 'message': 'Game ID and platform are required.'}, status=400)

	time.sleep(2)

	profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	profile.game_id = game_id
	profile.current_rank = 'Gold'
	profile.win_rate = 55.0
	profile.save()

	return JsonResponse({
		'success': True,
		'message': 'Game account linked successfully.',
		'game_id': profile.game_id,
		'current_rank': profile.current_rank,
		'win_rate': profile.win_rate,
		'platform': platform,
	})


@login_required
@require_POST
def link_coc_account(request):
	player_tag = request.POST.get('player_tag', '').strip()
	if not player_tag:
		return JsonResponse({'success': False, 'message': 'player_tag is required.'}, status=400)

	try:
		logger.info(f'Fetching CoC player for tag: {player_tag}')
		player_data = fetch_coc_player(player_tag)
		profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

		normalized_tag = player_tag.upper().strip()
		if normalized_tag.startswith('%23'):
			normalized_tag = f'#{normalized_tag[3:]}'
		elif not normalized_tag.startswith('#'):
			normalized_tag = f'#{normalized_tag}'

		profile.player_tag = normalized_tag
		profile.game_id = player_data['name'] or profile.game_id
		profile.trophies = int(player_data['trophies'])
		profile.townhall_level = int(player_data['townHallLevel'])
		profile.exp_level = int(player_data['expLevel'])
		profile.save()

		logger.info(f'Successfully linked CoC account for user {request.user.username}')
	except ValueError as exc:
		logger.error(f'ValueError linking CoC: {str(exc)}')
		return JsonResponse({'success': False, 'message': str(exc)}, status=400)
	except RuntimeError as exc:
		logger.error(f'RuntimeError linking CoC: {str(exc)}')
		return JsonResponse({'success': False, 'message': str(exc)}, status=502)
	except Exception as exc:
		logger.error(f'Unexpected error linking CoC: {str(exc)}', exc_info=True)
		return JsonResponse({'success': False, 'message': 'Failed to link account. Please check the player tag.'}, status=502)

	return JsonResponse({
		'success': True,
		'player_tag': profile.player_tag,
		'name': player_data['name'],
		'trophies': profile.trophies,
		'townHallLevel': profile.townhall_level,
		'expLevel': profile.exp_level,
	})
