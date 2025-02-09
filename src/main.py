# msgfmt -v src/locales/en_US/LC_MESSAGES/messages.po -o src/locales/en_US/LC_MESSAGES/messages.mo
# msgfmt -v src/locales/ru_RU/LC_MESSAGES/messages.po -o src/locales/ru_RU/LC_MESSAGES/messages.mo
# chmod -R 755 src/locales/en_US/LC_MESSAGES/
# chmod -R 755 src/locales/ru_RU/LC_MESSAGES/

from loguru import logger
from config import set_logger, set_language


set_language('ru_RU')
set_logger()
