from aiogram import Router, types
from aiogram.fsm import state
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from asgiref.sync import sync_to_async

from bot.buttons import send_contact_phone_button
from login.models import TgToken

router = Router()

class LogInState(state.StatesGroup):
    PHONE_NUMBER = state.State()
    LOGIN = state.State()


@router.message(Command('start'))
async def send_welcome(message: types.Message, state: FSMContext):
    phone_button = await send_contact_phone_button()
    await message.reply(
             f"Hello {message.from_user.full_name}, What is your phone number?", 
              reply_markup=phone_button
              )
    await state.set_state(LogInState.PHONE_NUMBER)

@router.message(LogInState.PHONE_NUMBER)
async def process_phone_number(message: types.Message, state: FSMContext):
        if message.content_type ==  types.ContentType.CONTACT:
            await state.update_data(
                 phone_number=message.contact.phone_number
            )

            phone_number = (await state.get_data()).get('phone_number')
            await send_token_message(
                message, 
                message.from_user.id, 
                phone_number,
                full_name=message.from_user.full_name
            )
            await state.set_state(LogInState.LOGIN)
        else:
            await message.answer(('Old code is active.'))

@router.message(Command('login'), LogInState.LOGIN)
async def process_token(message: types.Message, state: FSMContext):
    phone_number = (await state.get_data()).get('phone_number') 
    if phone_number:
        await send_token_message(
            message, 
            message.from_user.id, 
            phone_number,
            message.from_user.full_name
        )
    else:
        await message.answer('No phone number found. Please send your phone number first.')

async def send_token_message(message: types.Message, tg_id: int, phone_number: str, full_name: str):
    token = await sync_to_async(TgToken.create_otp_for_tg)(
        phone_number=phone_number, 
        tg_id=tg_id,
        full_name=full_name
    )
    if token:
        await message.reply(f"`{token}`", parse_mode="MarkdownV2")
        await message.answer('Send /login to get new code.')
    else:
        await message.answer('Old code is active.')
