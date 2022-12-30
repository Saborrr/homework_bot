import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import RequestExceptionError, WrongResponseCode

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='homework.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверяем, что есть все токены.
    Если нет хотя бы одного, то останавливаем бота.
    """
    logger.info('Проверка наличия всех токенов')
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,))


def send_message(bot, message):
    """Функция отправки сообщения в чат Telegram."""
    try:
        logger.info(f'Сообщение в чат {TELEGRAM_CHAT_ID}: {message}')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as telegram_error:
        logger.error(f'Сообщение в Telegram не отправлено: {telegram_error}')
    else:
        logging.debug(f'Сообщение отправлено {message}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = {'from_date': timestamp}
    try:
        hw_status = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if hw_status.status_code != HTTPStatus.OK:
            raise WrongResponseCode(f'Ошибка {hw_status.status_code}')
        return hw_status.json()
    except requests.exceptions.RequestException as request_error:
        message_error = f'Код ответа API (RequestException): {request_error}'
        logger.error(message_error)
        raise RequestExceptionError(message_error) from request_error
    except json.JSONDecodeError as value_error:
        message_error = f'Код ответа API (ValueError): {value_error}'
        logger.error(message_error)
        raise json.JSONDecodeError(message_error) from value_error


def check_response(response):
    """Проверяем ответ API на корректность."""
    logging.info('Проверка ответа от API')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')
    if 'homeworks' not in response or 'current_date' not in response:
        raise KeyError('Отсутствует ключ')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('Ответ API не является списком')
    return homeworks


def parse_status(homework):
    """Получаем информацию о домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        raise KeyError('Отсутствует ключ "status" в ответе API')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    error_cache_message = ''
    if not check_tokens():
        logger.critical('Ошибка переменных окружения')
        sys.exit('Ошибка переменных окружения')
    while True:
        try:
            response = get_api_answer(timestamp)
            hw_list = check_response(response)
            if hw_list:
                send_message(bot, parse_status(hw_list[0]))
            else:
                logger.debug('Нет новых статусов')
                raise Exception('Нет новых статусов')
        except Exception as error:
            logger.error(error)
            message_error = str(error)
            if message_error != error_cache_message:
                send_message(bot, message_error)
                error_cache_message = message_error
        finally:
            timestamp = response.get('current_date')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
