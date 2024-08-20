from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

async def send_contact_phone_button():
    send_contact_phone = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Send my phone number", 
                            request_contact=True)]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    return send_contact_phone