import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
import io
from PIL import Image, ImageDraw, ImageFont
import flask

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class CommandState:
    waiting_for_name = "waiting_for_name"

@router.message(Command("start"))
async def start_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username

    await message.answer(
        "Введи команду /create, щоб створити сертифікат GoITeens"
    )

@router.message(Command("create"))
async def create_command_handler(message: types.Message, state: FSMContext):
    await message.answer("Введіть своє ім'я, щоб згенерувати сертифікат!")
    await state.set_state(CommandState.waiting_for_name)

@router.message(StateFilter(CommandState.waiting_for_name))
async def send_certificate_handler(message: types.Message, state: FSMContext):
    clock = await bot.send_message(message.chat.id, "⏳")
    
    await asyncio.sleep(1)

    with Image.open("template.png") as im:
        draw = ImageDraw.Draw(im)
        font_path = "OpenSans-SemiBold.ttf"
        font_size = 75
        font = ImageFont.truetype(font_path, font_size)
        
        # Використовуйте textbbox для отримання розміру тексту
        text_bbox = draw.textbbox((0, 0), message.text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        image_width, image_height = im.size
        text_position = ((image_width - text_width) // 2, 1233)
        
        draw.text(text_position, message.text, font=font)

        image_buffer = io.BytesIO()
        im.save(image_buffer, format="PNG")
        image_buffer.seek(0)

    await asyncio.sleep(1)

    await bot.delete_message(message.chat.id, clock.message_id)
    await message.answer_photo(image_buffer)
    await state.finish()

dp.include_router(router)

app = flask.Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = flask.request.get_data(as_text=True)
    update = types.Update.parse_raw(json_str)
    asyncio.run(dp.process_update(update))
    return '', 200

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8000)
