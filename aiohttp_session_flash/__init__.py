"""
Session flash messages for aiohttp.web
"""

from functools import partial

from aiohttp_session import get_session

SESSION_KEY = REQUEST_KEY = 'flash'


def flash(request, message):
	request[REQUEST_KEY].append(message)


def pop_flash(request):
	flash = request[REQUEST_KEY]
	request[REQUEST_KEY] = []
	return flash


async def middleware(app, handler):
	async def process(request):
		session = await get_session(request)
		flash_incoming = session.get(SESSION_KEY, [])
		request[REQUEST_KEY] = flash_incoming[:]  # copy flash for modification
		try:
			response = await handler(request)
		finally:
			flash_outgoing = request[REQUEST_KEY]
			if flash_outgoing != flash_incoming:
				if flash_outgoing:
					session[SESSION_KEY] = flash_outgoing
				else:
					del session[SESSION_KEY]
		return response

	return process


async def context_processor(request):
	return {
		'get_flashed_messages': partial(pop_flash, request),
	}
