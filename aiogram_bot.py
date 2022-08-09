import logging
from aiogram import Bot, Dispatcher, executor, types 
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from pytube import YouTube
import config 
import os 

bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands = "start")
async def start(message: types.Message):
    await message.answer(f"Здраствуйте {message.from_user.full_name}!\nДобро пожаловать в наш бот!\nВведите комманду /help - чтобы узнать что может делать наш бот")

@dp.message_handler(commands='help')
async def help(message: types.Message):
    await message.answer(f"Вот наши комманды: \n/start - запустить бота\n/help - получить информация о коммандах\n/audio - конвентировать видео в mp3")

class Download(StatesGroup):
    download = State()


class DownloadVideo(StatesGroup):
    download = State()

def download_audio(url, type = "audio"):
    yt = YouTube(url)
    if type == 'audio':
        yt.streams.filter(only_audio=True).first().download("audio", f"{yt.title}.mp3")
        return f"{yt.title}.mp3"

def download_video(url, type = "video"):
    yt = YouTube(url)
    if type == 'video':
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download("video", f"{yt.title}.mp4")
        return f"{yt.title}.mp4"

@dp.message_handler(commands='audio')
async def audio(message: types.Message):
    await message.answer("Отправьте ссылку на видео и я вам отправлю его в виде музыки")
    await Download.download.set()

@dp.message_handler(commands='video')
async def audio(message: types.Message):
    await message.answer("Отправьте ссылку на видео и я вам отправлю его в формате видео")
    await DownloadVideo.download.set()

@dp.message_handler(state=Download.download)
async def down_audio(message: types.Message, state: FSMContext):
    await message.answer("Скачиваем файл, ожидайте...")
    title = download_audio(message.text)
    audio = open(f'audio/{title}', 'rb')
    await message.answer("Все скачалось, вот держи")
    try:
        await bot.send_audio(message.chat.id, audio)
    except:
        await message.answer("Произошла ошибка, попробуйте еще раз")
    os.remove(f'audio/{title}')
    await state.finish()

@dp.message_handler(state=DownloadVideo.download)
async def down_video(message: types.Message, state: FSMContext):
    await message.answer("Скачиваем файл, ожидайте...")
    title = download_video(message.text)
    video = open(f'video/{title}', 'rb')
    await message.answer("Все скачалось, вот держи")
    try:
        await bot.send_video(message.chat.id, video)
    except:
        await message.answer("Произошла ошибка, попробуйте еще раз")
    os.remove(f'video/{title}')
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)