import io
from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from PIL import Image, ImageDraw, ImageFont
import config

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher()

class CommandState:
    waiting_for_name = "waiting_for_name"


@dp.message_handler(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username

    await message.answer(
        "Введи команду /create, щоб створити сертифікат GoITeens"
    )

@dp.message_handler(Command("create"))
async def create(message: types.Message, state: FSMContext):
    await message.answer("Введіть своє ім'я, щоб згенерувати сертифікат!")

    await state.set_state(CommandState.waiting_for_name)

@dp.message_handler(state=CommandState.waiting_for_name)
async def send_certificate(message: types.Message, state: FSMContext):
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

if __name__ == "__main__":
    import keep_alive
    keep_alive.keep_alive()

    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
