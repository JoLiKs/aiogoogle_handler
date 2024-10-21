import asyncio
import datetime
import logging
import os
import random

import httplib2
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.management import BaseCommand
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from keys import sheetId, botToken

logging.basicConfig(level=logging.INFO)
# Объект бота


bot = Bot(token=botToken)
# Диспетчер
dp = Dispatcher()




credentials = ServiceAccountCredentials.from_json_keyfile_name('../keysgoogle.json',
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API


async def scheduled(wait_for):
    global sheet_values, values
    pass


# Хэндлер на команду /start

@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"photo{random.randint(1, 1000)}.jpg")


class AIter:   #упрощенный аналог range для async for
    def __init__(self, N):
        self.i = 0
        self.N = N

    def __aiter__(self):
        return self

    async def __anext__(self):
        i = self.i
        #print(f"start {i}")
        await asyncio.sleep(0.7)
        #print(f"end {i}")
        if i >= self.N:
            raise StopAsyncIteration
        self.i += 1
        return i


@dp.message(F.text == '/start')
async def isOffice(message: Message, state: FSMContext):
    await message.answer('Ожидаю новых клиентов...')
    files = os.listdir()
    builder = InlineKeyboardBuilder()
    values = []
    sheet_values = 0
    async for i in AIter(150000):

        await asyncio.sleep(1)
        results = service.spreadsheets().values().batchGet(spreadsheetId=sheetId,
                                                           ranges=[f"A2:C4550"],
                                                           valueRenderOption='UNFORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        res2 = results['valueRanges'][0]['values']
        print(sheet_values)
        if sheet_values == 0:
            sheet_values = len(res2)
            continue
        if len(res2) != sheet_values:
            values = res2
            sheet_values = len(res2)
        await asyncio.sleep(4)
        if values != []:
            try:
                res = f'Новый клиент\n\nНомер: {values[-1][1]} Данные: {values[-1][2]}'
            except:
                res = f'Новый клиент\n\nНомер: {values[-1][1]} Данные: не указано'
            await message.answer(res)
            values = []
            continue

@dp.callback_query(F.data)
async def send_random_value(callback: types.CallbackQuery):
    f = open(callback.data, 'r')
    await callback.message.answer(''.join(f.readlines()))
    f.close()


async def main():
    await dp.start_polling(bot)




if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(5))
    try:
        loop.run_until_complete(dp.start_polling(bot))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
