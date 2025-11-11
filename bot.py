# from aiogram import Bot, Dispatcher, types
# import asyncio

# # tokenni bu yerga kiriting
#TOKEN = "8484092381:AAEORrxngeZe7OQZKHyBLCHMFUeCkiE4RTs"

# # Bot va Dispatcher obyektlarini yaratamiz
# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot)

# # Oddiy echo handler
# @dp.message_handler()
# async def echo(message: types.Message):
#     await message.answer(message.text)

# # Asosiy funksiya
# async def main():
#     print("Bot ishga tushdi... ✅")
#     await dp.start_polling()

# # Dastur kirish nuqtasi
# if __name__ == "__main__":
#     asyncio.run(main())






import os
import re
import asyncio
from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# Bot tokenini shu yerga yozing
TOKEN = "8484092381:AAEORrxngeZe7OQZKHyBLCHMFUeCkiE4RTs"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Fayl nomlarini xavfsiz qilish
def safe_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", "_", name)
    return name

# Foydalanuvchi bo'yicha qidiruv natijalarini saqlash
search_results = {}

# Foydalanuvchi so'z yuborganda qidiruv
@dp.message()
async def search_music(message: types.Message):
    query = message.text.strip()
    if not query:
        await message.answer("❌ Iltimos, qidiruv so'zini kiriting!")
        return
    if query == "/start":
        return await message.answer("Botga xush kelibsiz!") 
    await message.answer("🔎 Qidirilmoqda...")

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            videos = info.get('entries', [])

        if not videos:
            await message.answer("❌ Hech nima topilmadi.")
            return

        # Inline tugmalar yaratish
        buttons = []
        for i, vid in enumerate(videos):
            title = vid['title']
            buttons.append([InlineKeyboardButton(
                text=f"{i+1}. {title[:50]}{'...' if len(title) > 50 else ''}",
                callback_data=str(i)
            )])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        search_results[message.from_user.id] = videos

        await message.answer("Natijalardan birini tanlang:", reply_markup=keyboard)

    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

# Foydalanuvchi tugmani bosganda audio yuborish
@dp.callback_query()
async def download_selected(call: types.CallbackQuery):
    user_id = call.from_user.id
    index = int(call.data)

    if user_id not in search_results:
        await call.message.answer("❌ Qidiruv natijalari topilmadi.")
        return

    video = search_results[user_id][index]
    file_name = safe_filename(f"audios/{video['title']}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'outtmpl': file_name
    }

    try:
        progress_msg = await call.message.answer("⬇️ Yuklanmoqda...")

        # Video yuklash
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video['webpage_url']])

        # Audio faylni InputFile orqali yuborish
        # with open(file_name, "rb") as f:
        #     audio_file = types.InputFile(f)
        #     await call.message.answer_audio(audio=audio_file, title=video['title'])
        
        print(file_name)
        audio_file = FSInputFile(path=file_name)  # Use FSInputFile
        await call.message.answer_audio(audio=audio_file, title=video['title'])
        await progress_msg.delete()
        os.remove(file_name)
        del search_results[user_id]

    except Exception as e:
        await call.message.answer(f"❌ Yuklashda xatolik yuz berdi: {str(e)}")

# Botni ishga tushurish
async def main():
    print("Bot ishga tushdi... ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
