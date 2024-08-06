from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import io
from PIL import Image, ImageDraw, ImageFont
import asyncio

API_TOKEN = '7061386650:AAHuEge8iJdl1nuhRtehZ8ek2Kbh_JBn9M0'

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

@router.message(state=CommandState.waiting_for_name)
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

if __name__ == "__main__":
    import keep_alive
    keep_alive.keep_alive()

    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
