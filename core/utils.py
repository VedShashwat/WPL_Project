import logging
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_coc_player(player_tag):
    cleaned = (player_tag or '').strip().upper()
    if not cleaned:
        raise ValueError('Player tag is required.')

    if cleaned.startswith('%23'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('#'):
        cleaned = cleaned[1:]

    encoded_tag = quote(f'#{cleaned}', safe='')

    token = (settings.COC_API_KEY or '').strip()
    if not token:
        raise RuntimeError('COC_API_KEY is not configured.')

    logger.info(f'Fetching player: {encoded_tag}')
    try:
        response = requests.get(
            f'https://api.clashofclans.com/v1/players/{encoded_tag}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=15,
        )

        logger.info(f'CoC API response status: {response.status_code}')

        if response.status_code != 200:
            logger.error(f'CoC API error: {response.text}')
            raise RuntimeError(f'Clash of Clans API request failed with status {response.status_code}. {response.text}')

        data = response.json()
        return {
            'name': data.get('name', ''),
            'trophies': data.get('trophies', 0),
            'townHallLevel': data.get('townHallLevel', 0),
            'expLevel': data.get('expLevel', 0),
        }
    except requests.RequestException as e:
        logger.error(f'Request error: {str(e)}')
        raise RuntimeError(f'Failed to connect to Clash of Clans API: {str(e)}')


def fetch_cr_player(player_tag):
    cleaned = (player_tag or '').strip().upper()
    if not cleaned:
        raise ValueError('Player tag is required.')

    if cleaned.startswith('%23'):
        cleaned = cleaned[3:]
    elif cleaned.startswith('#'):
        cleaned = cleaned[1:]

    encoded_tag = quote(f'#{cleaned}', safe='')

    token = (settings.CR_API_KEY or '').strip()
    if not token:
        raise RuntimeError('CR_API_KEY is not configured.')

    logger.info(f'Fetching Clash Royale player: {encoded_tag}')
    try:
        response = requests.get(
            f'https://api.clashroyale.com/v1/players/{encoded_tag}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=15,
        )

        logger.info(f'Clash Royale API response status: {response.status_code}')

        if response.status_code != 200:
            logger.error(f'Clash Royale API error: {response.text}')
            raise RuntimeError(f'Clash Royale API request failed with status {response.status_code}. {response.text}')

        data = response.json()
        return {
            'name': data.get('name', ''),
            'trophies': data.get('trophies', 0),
            'bestTrophies': data.get('bestTrophies', 0),
        }
    except requests.RequestException as e:
        logger.error(f'Request error: {str(e)}')
        raise RuntimeError(f'Failed to connect to Clash Royale API: {str(e)}')