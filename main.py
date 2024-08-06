import io
from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from PIL import Image, ImageDraw, ImageFont
import config

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Массив користувачів
users = [{"name": "test testing", "email": "test@gmail.com"}]

class CommandState:
    waiting_for_email = "waiting_for_email"

@dp.message_handler(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Введи команду /create, щоб створити сертифікат GoITeens"
    )

@dp.message_handler(Command("create"))
async def create(message: types.Message, state: FSMContext):
    await message.answer("Введіть свою електронну пошту, щоб згенерувати сертифікат!")
    await state.set_state(CommandState.waiting_for_email)

@dp.message_handler(state=CommandState.waiting_for_email)
async def handle_email(message: types.Message, state: FSMContext):
    email = message.text

    # Перевірка електронної пошти
    user = next((u for u in users if u["email"] == email), None)
    
    if user:
        user_name = user["name"]
        
        # Генерація сертифікату
        clock = await bot.send_message(message.chat.id, "⏳")
        
        await asyncio.sleep(1)

        with Image.open("template.png") as im:
            draw = ImageDraw.Draw(im)
            font_path = "OpenSans-SemiBold.ttf"
            font_size = 75
            font = ImageFont.truetype(font_path, font_size)
            
            # Використовуйте textbbox для отримання розміру тексту
            text_bbox = draw.textbbox((0, 0), user_name, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            image_width, image_height = im.size
            text_position = ((image_width - text_width) // 2, 1233)
            
            draw.text(text_position, user_name, font=font)

            image_buffer = io.BytesIO()
            im.save(image_buffer, format="PNG")
            image_buffer.seek(0)

        await asyncio.sleep(1)

        await bot.delete_message(message.chat.id, clock.message_id)
        await message.answer_photo(image_buffer)
        await state.finish()
    else:
        await message.answer("Пошта не вірна, спробуйте знову.")
        await state.set_state(CommandState.waiting_for_email)

if __name__ == "__main__":
    import keep_alive
    keep_alive.keep_alive()

    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
