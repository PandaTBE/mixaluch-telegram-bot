
import re

import requests
from telebot import TeleBot

from config import ADMIN_TOKEN, HOST_URL, TELEGRAM_BOT_API_KEY, TELEGRAM_CHAT_ID

# Объявление переменной бота
bot = TeleBot(TELEGRAM_BOT_API_KEY, threaded=False)

ORDER_STATUS_NAMES_MAP = {
    "IN_PROCESS": "В обработке",
    "ACCEPTED": "Принят",
    "COLLECTED": "Собран",
    "IN_DELIVERY": "В доставке",
    "COMPLETED": "Выполнен",
}

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
        Изменение статуса заказа
    """

    status_regexp = "Статус заказа:  \D+(?=Заказчик)"

    order_id = call.data.split(",")[0]
    order_status = call.data.split(",")[1]
    admin_token = ADMIN_TOKEN

    message_text = call.message.text

    new_message = re.sub(
        status_regexp, f"Статус заказа:  {ORDER_STATUS_NAMES_MAP.get(order_status, '?')}\n\n", message_text
    )

    try:
        response = requests.patch(
            f"{HOST_URL}/api/orders/{order_id}/",
            data={"status": order_status},
            headers={"Authorization": f"Token {admin_token}"},
        )
        response.raise_for_status()
        bot.edit_message_text(
            chat_id=TELEGRAM_CHAT_ID,
            text=new_message,
            message_id=call.message.message_id,
            reply_markup=call.message.reply_markup,
            parse_mode="html",
        )
    except requests.exceptions.HTTPError as err:
        print(">>> Ошибка при изменении статуса заказа ботом:   ", err)


bot.enable_save_next_step_handlers(delay=2)  # Сохранение обработчиков
bot.load_next_step_handlers()  # Загрузка обработчиков
bot.infinity_polling()  # Бесконечный цикл бота
