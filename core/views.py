import logging

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm
from .models import ChatMessage, PlayerProfile, Post
from .utils import fetch_coc_player, fetch_cr_player

logger = logging.getLogger(__name__)

GAME_CONFIG = {
	'coc': {
		'label': 'Clash of Clans',
		'post_prefix': '[COC]',
	},
	'cr': {
		'label': 'Clash Royale',
		'post_prefix': '[CR]',
	},
}


def _display_name(user):
	full_name = user.get_full_name().strip()
	return full_name if full_name else user.username


def _player_reputation(user):
	profile, _ = PlayerProfile.objects.get_or_create(user=user)
	return profile.reputation


def _serialize_chat_message(chat_message):
	return {
		'id': chat_message.id,
		'user': _display_name(chat_message.user),
		'message': chat_message.message,
		'timestamp': chat_message.timestamp.isoformat(),
	}


def _strip_game_prefix(content):
	for game in GAME_CONFIG.values():
		prefix = f"{game['post_prefix']} "
		if content.startswith(prefix):
			return content[len(prefix):]
	return content


def auth_page(request):
	if request.user.is_authenticated:
		return redirect('community_home')

	login_form = AuthenticationForm(request, data=request.POST or None)
	signup_form = CustomUserCreationForm(request.POST or None)
	active_panel = 'login'

	if request.method == 'POST':
		form_type = request.POST.get('form_type')
		active_panel = form_type if form_type in {'login', 'signup'} else 'login'

		if form_type == 'login' and login_form.is_valid():
			auth_login(request, login_form.get_user())
			return redirect('community_home')

		if form_type == 'signup' and signup_form.is_valid():
			user = signup_form.save()
			if user.email:
				try:
					send_mail(
						subject='Welcome to MetaSync',
						message=(
							f'Hi {user.username},\n\n'
							'Thanks for joining MetaSync. Your account is ready, and you can now explore '
							'the dashboard, leaderboard, community feed, and global chat.\n\n'
							'Good luck and have fun!\n'
						),
						from_email=None,
						recipient_list=[user.email],
						fail_silently=False,
					)
				except Exception as exc:
					logger.warning(f'Welcome email failed for user {user.username}: {exc}')
			auth_login(request, user)
			messages.success(request, 'Account created successfully.')
			return redirect('community_home')

	return render(request, 'registration/login.html', {
		'login_form': login_form,
		'signup_form': signup_form,
		'active_panel': active_panel,
	})


@login_required
def community_home(request):
	profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	global_posts = []
	for post in Post.objects.select_related('author').order_by('-created_at')[:50]:
		author_profile, _ = PlayerProfile.objects.get_or_create(user=post.author)
		global_posts.append({
			'id': post.id,
			'author_profile_id': author_profile.id,
			'author_name': _display_name(post.author),
			'author_reputation': author_profile.reputation,
			'content': _strip_game_prefix(post.content),
			'created_at': post.created_at,
			'votes': post.votes,
		})

	return render(request, 'core/community_home.html', {
		'profile': profile,
		'global_posts': global_posts,
	})


@login_required
def game_room(request, game_name):
	selected_game = (game_name or '').lower().strip()
	if selected_game not in GAME_CONFIG:
		return redirect('community_home')

	profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	game_info = GAME_CONFIG[selected_game]
	post_prefix = game_info['post_prefix']

	if selected_game == 'coc':
		leaderboard_qs = (
			PlayerProfile.objects.select_related('user')
			.order_by('-trophies', '-townhall_level', 'user__username')
		)
		is_linked = bool(profile.player_tag)
		current_tag = profile.player_tag
		link_endpoint = 'link_coc_account'
	else:
		leaderboard_qs = (
			PlayerProfile.objects.select_related('user')
			.order_by('-cr_trophies', '-cr_best_trophies', 'user__username')
		)
		is_linked = bool(profile.cr_player_tag)
		current_tag = profile.cr_player_tag
		link_endpoint = 'link_cr_account'

	leaderboard = []
	for rank, row in enumerate(leaderboard_qs[:50], start=1):
		if selected_game == 'coc':
			main_score = row.trophies
			secondary_score = row.townhall_level
		else:
			main_score = row.cr_trophies
			secondary_score = row.cr_best_trophies

		leaderboard.append({
			'rank': rank,
			'player_name': _display_name(row.user),
			'reputation': row.reputation,
			'main_score': main_score,
			'secondary_score': secondary_score,
		})

	room_posts = []
	for post in Post.objects.select_related('author').filter(content__startswith=f'{post_prefix} ').order_by('-created_at')[:50]:
		author_profile, _ = PlayerProfile.objects.get_or_create(user=post.author)
		room_posts.append({
			'id': post.id,
			'author_profile_id': author_profile.id,
			'author_name': _display_name(post.author),
			'author_reputation': author_profile.reputation,
			'content': _strip_game_prefix(post.content),
			'created_at': post.created_at,
			'votes': post.votes,
		})

	return render(request, 'core/game_room.html', {
		'profile': profile,
		'selected_game': selected_game,
		'game_label': game_info['label'],
		'leaderboard': leaderboard,
		'room_posts': room_posts,
		'is_linked': is_linked,
		'current_tag': current_tag,
		'link_endpoint': link_endpoint,
	})


@login_required
def dashboard(request):
	profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	community_posts = []
	for post in Post.objects.select_related('author').order_by('-created_at')[:20]:
		author_profile, _ = PlayerProfile.objects.get_or_create(user=post.author)
		community_posts.append({
			'id': post.id,
			'author_profile_id': author_profile.id,
			'author_name': _display_name(post.author),
			'author_reputation': author_profile.reputation,
			'content': post.content,
			'created_at': post.created_at,
			'votes': post.votes,
		})
	chat_messages = list(
		ChatMessage.objects.select_related('user').order_by('-timestamp')[:20]
	)
	chat_messages.reverse()
	return render(request, 'core/dashboard.html', {
		'profile': profile,
		'community_posts': community_posts,
		'chat_messages': chat_messages,
	})


@login_required
def leaderboard_data(request):
	profiles = (
		PlayerProfile.objects.select_related('user')
		.order_by('-trophies', '-exp_level', 'user__username')
	)

	results = []
	for index, profile in enumerate(profiles, start=1):
		results.append({
			'rank': index,
			'profile_id': profile.id,
			'player_name': _display_name(profile.user),
			'reputation': profile.reputation,
			'trophies': profile.trophies,
			'townhall_level': profile.townhall_level,
		})

	return JsonResponse({'players': results})


@login_required
def leaderboard_profile_data(request, profile_id):
	try:
		profile = PlayerProfile.objects.select_related('user').get(pk=profile_id)
	except PlayerProfile.DoesNotExist:
		return JsonResponse({'success': False, 'message': 'Profile not found.'}, status=404)

	return JsonResponse({
		'success': True,
		'profile': {
			'player_name': _display_name(profile.user),
			'reputation': profile.reputation,
			'player_tag': profile.player_tag,
			'trophies': profile.trophies,
			'townhall_level': profile.townhall_level,
			'exp_level': profile.exp_level,
			'cr_player_tag': profile.cr_player_tag,
			'cr_trophies': profile.cr_trophies,
			'cr_best_trophies': profile.cr_best_trophies,
		},
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


@login_required
@require_POST
def link_cr_account(request):
	player_tag = request.POST.get('player_tag', '').strip()
	if not player_tag:
		return JsonResponse({'success': False, 'message': 'player_tag is required.'}, status=400)

	try:
		logger.info(f'Fetching Clash Royale player for tag: {player_tag}')
		player_data = fetch_cr_player(player_tag)
		profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

		normalized_tag = player_tag.upper().strip()
		if normalized_tag.startswith('%23'):
			normalized_tag = f'#{normalized_tag[3:]}'
		elif not normalized_tag.startswith('#'):
			normalized_tag = f'#{normalized_tag}'

		profile.cr_player_tag = normalized_tag
		profile.cr_trophies = int(player_data['trophies'])
		profile.cr_best_trophies = int(player_data['bestTrophies'])
		profile.save()

		logger.info(f'Successfully linked Clash Royale account for user {request.user.username}')
	except ValueError as exc:
		logger.error(f'ValueError linking Clash Royale: {str(exc)}')
		return JsonResponse({'success': False, 'message': str(exc)}, status=400)
	except RuntimeError as exc:
		logger.error(f'RuntimeError linking Clash Royale: {str(exc)}')
		return JsonResponse({'success': False, 'message': str(exc)}, status=502)
	except Exception as exc:
		logger.error(f'Unexpected error linking Clash Royale: {str(exc)}', exc_info=True)
		return JsonResponse({'success': False, 'message': 'Failed to link Clash Royale account. Please check the player tag.'}, status=502)

	return JsonResponse({
		'success': True,
		'player_tag': profile.cr_player_tag,
		'name': player_data['name'],
		'trophies': profile.cr_trophies,
		'bestTrophies': profile.cr_best_trophies,
	})


@login_required
@require_POST
def submit_post(request):
	content = request.POST.get('content', '').strip()
	if not content:
		return JsonResponse({'success': False, 'message': 'Post content is required.'}, status=400)

	game_name = request.POST.get('game_name', '').strip().lower()
	if game_name in GAME_CONFIG:
		stored_content = f"{GAME_CONFIG[game_name]['post_prefix']} {content}"
	else:
		stored_content = content

	post = Post.objects.create(author=request.user, content=stored_content)
	author_profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
	reputation = _player_reputation(request.user)

	return JsonResponse({
		'success': True,
		'post': {
			'id': post.id,
			'author_name': _display_name(request.user),
			'author_profile_id': author_profile.id,
			'author_reputation': reputation,
			'content': content,
			'game_name': game_name if game_name in GAME_CONFIG else '',
			'created_at': post.created_at.isoformat(),
			'votes': post.votes,
		},
	})


@login_required
@require_POST
def vote_post(request, post_id):
	action = request.POST.get('action', '').strip().lower()
	if action not in {'upvote', 'downvote'}:
		return JsonResponse({'success': False, 'message': 'Invalid vote action.'}, status=400)

	try:
		with transaction.atomic():
			post = Post.objects.select_for_update().select_related('author').get(pk=post_id)
			author_profile, _ = PlayerProfile.objects.select_for_update().get_or_create(user=post.author)

			vote_delta = 1 if action == 'upvote' else -1
			reputation_delta = 1 if action == 'upvote' else -1

			Post.objects.filter(pk=post.pk).update(votes=F('votes') + vote_delta)
			PlayerProfile.objects.filter(pk=author_profile.pk).update(reputation=F('reputation') + reputation_delta)

			post.refresh_from_db(fields=['votes'])
			author_profile.refresh_from_db(fields=['reputation'])
	except Post.DoesNotExist:
		return JsonResponse({'success': False, 'message': 'Post not found.'}, status=404)

	return JsonResponse({
		'success': True,
		'post_id': post.id,
		'votes': post.votes,
		'author_reputation': author_profile.reputation,
			'author_profile_id': author_profile.id,
		'action': action,
	})


@login_required
@require_POST
def send_message(request):
	message = request.POST.get('message', '').strip()
	if not message:
		return JsonResponse({'success': False, 'message': 'Message cannot be empty.'}, status=400)

	chat_message = ChatMessage.objects.create(user=request.user, message=message)
	return JsonResponse({'success': True, 'chat_message': _serialize_chat_message(chat_message)})


@login_required
def get_messages(request):
	after_id = request.GET.get('after_id', '').strip()
	chat_qs = ChatMessage.objects.select_related('user')

	if after_id.isdigit():
		messages = list(chat_qs.filter(id__gt=int(after_id)).order_by('timestamp')[:20])
	else:
		messages = list(chat_qs.order_by('-timestamp')[:20])
		messages.reverse()

	return JsonResponse({'messages': [_serialize_chat_message(message) for message in messages]})
