from django.shortcuts import render
from telegram.ext import CallbackContext
from telegram import Update
from .models import User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from time import sleep
CHANNELS = [("Siz buni blarmidingiz", -1001928509371, 'https://t.me/siz_buni_blarmidingiz')]
# Create your views here.


def buttons(type=None):
    btn = []
    if type == "lang":
        btn = [[InlineKeyboardButton("Русский язык", callback_data='rus')], [InlineKeyboardButton('Uzbek tili', callback_data='uzb')]]
    elif type == 'start':
        btn = [[InlineKeyboardButton('start', callback_data='start')]]
    elif type == 'insta':
        btn = [[InlineKeyboardButton('Insta Function', callback_data='insta')]]
    elif type == 'check':
        btn = [[InlineKeyboardButton('Подписался', callback_data='check')]]
    elif type == 'channels':
        for i in CHANNELS:
            btn.append([InlineKeyboardButton(i[0], url=i[2])])
        btn.append([InlineKeyboardButton('Подписался', callback_data='check')])
    return InlineKeyboardMarkup(btn)


def text(language, command, user=None):
    dict = {
        'uzb': {
            1: f"Assalomu alaykum, {user.first_name}\nBu maxfiy bot boʻlib, u bilan oʻsha funksiyalarni ulashingiz mumkin!\n\nBot ishga tushishini xohlaysizmi?\n“Start” tugmasini bosing.",
            2: "Kerakli funktsiyani tanlash bilan boshlaylik:",
            3: "Ajoyib, boshlaymiz!\n\nInstagram usernamingizni kiriting:",
            4: "🤔ushbu botdan foydalanishni davom ettirish uchun homiylarimizning kanallariga obuna boʻlishingiz kerak\n\nUlar tufayli bizning botimiz mutlaqo bepul va sizdan hech qanday sarmoya talab qilmaydi!\n\nObuna boʻlgandan soʻng 'Подписался' tugmasini bosing.",
            5: "Xizmat ishga tushdi, Instagramni 24 soat ichida tekshiring.",
            6: "Siz hali barcha kanalarga obuna bo'lmadingiz!",
            7: "Suniy Intelektda yaratilgan bot tez, oson va qulay. \n\nSinab ko'ring: <a href='https://t.me/chatgpt_officia1_bot'>ChatGPT-3</a>"
        },
        "rus": {
            1: f"Привет, {user.first_name}\nЭто секретный бот с помощью которого, ты сможешь подключить те самые функции!\n\nХочешь, чтобы бот приступил к работе?\nТогда нажимай 'start'",
            2: 'Давай начнем с выбора нужной функции:',
            3: "Супер, приступим!\n\nВведите ник вашего профиля:",
            4: "🤔Упс.. чтобы продолжить пользоваться данным ботом, необходимо подписаться на каналы наших спонсоров\n\nБлагодаря им наш бот абсолютно бесплатный и не требует какого либо вложения средств с твоей стороны!\n\nПосле подписки жми кнопку 'Подписался'",
            5: "Сервис начал работу, проверьте Инстаграм в течении 24час.",
            6: "Вы еще не подписаны на все каналы!",
            7: "Бот, построенный на искусственном интеллекте, быстрый, простой и удобный. \n\nПопробуйте: <a href='https://t.me/chatgpt_officia1_bot'>ChatGPT-3</a>"
        }
    }
    return dict[language][command]


async def start(update: Update, context: CallbackContext):
    client = update.effective_user
    user = User.objects.filter(user_id=client.id).first()
    if user is None:
        User.objects.create(user_id=client.id, state=1)
        await update.message.reply_text("🇷🇺 - Выберите язык!\n🇺🇿 - Tilni tanlang!", reply_markup=buttons(type='lang'))
    else:
        user = User.objects.filter(user_id=client.id).first()
        try:
            await update.message.reply_text(text(language=user.language, command=1, user=client), reply_markup=buttons(type='start'))
            User.objects.filter(user_id=client.id).update(state=2)
        except KeyError:
            await update.message.reply_text("🇷🇺 - Выберите язык!\n🇺🇿 - Tilni tanlang!", reply_markup=buttons(type='lang'))


async def handle_msg(update: Update, context: CallbackContext):
    client = update.effective_user
    user = User.objects.filter(user_id=client.id).first()
    if user is None:
        User.objects.create(user_id=client.id)
        await update.message.reply_text("🇷🇺 - Выберите язык!\n🇺🇿 - Tilni tanlang!", reply_markup=buttons(type='lang'))
    if user.state == 4:
        await update.message.reply_text("Загрузка..")
        sleep(3)
        await update.message.reply_text("Анализ..")
        sleep(3)
        await update.message.reply_text(text(language=user.language, command=4, user=client), reply_markup=buttons(type='channels'))
        User.objects.filter(user_id=client.id).update(state=5)


async def inline_handler(update: Update, context: CallbackContext):
    client = update.effective_user
    user = User.objects.filter(user_id=client.id).first()
    query = update.callback_query
    if user.state == 1:
        await query.message.delete()
        User.objects.filter(user_id=client.id).update(state=2, language=query.data)
        user = User.objects.filter(user_id=client.id).first()
        await update.callback_query.message.reply_text(text(language=user.language, command=1, user=client), reply_markup=buttons(type='start'))
    elif user.state == 2:
        await query.edit_message_reply_markup()
        await update.callback_query.message.reply_text(text(language=user.language, command=2, user=client), reply_markup=buttons(type='insta'))
        User.objects.filter(user_id=client.id).update(state=3)
    elif user.state == 3:
        await query.edit_message_reply_markup()
        await update.callback_query.message.reply_text(text(language=user.language, command=3, user=client))
        User.objects.filter(user_id=client.id).update(state=4)
    elif user.state == 5:
        await query.message.delete()
        btn = []
        count = 0
        for channel in CHANNELS:
            subscribed = await context.bot.getChatMember(user_id=client.id, chat_id=channel[1])
            if subscribed['status'] in ['member', 'creator', 'administrator']:
                count += 1
            else:
                btn.append(
                    [InlineKeyboardButton(text=channel[0], url=channel[2])]
                )
        if count != len(CHANNELS):
            btn.append([InlineKeyboardButton(text='Подписался✅', callback_data='check')])
            await update.callback_query.message.reply_text(text(user.language, 6, client),
                                            reply_markup=InlineKeyboardMarkup(btn))
            return 0
        await update.callback_query.message.reply_text(text(user.language, 5, client))
        await update.callback_query.message.reply_text(text(user.language, 7, client))