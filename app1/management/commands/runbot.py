from django.core.management import BaseCommand
from app1.views import *
from telegram.ext import CommandHandler, MessageHandler, Application, filters, CallbackQueryHandler, ApplicationBuilder
from simplebot.settings import TOKEN


class Command(BaseCommand):
    def handle(self, *args, **options):
        application = Application.builder().token(TOKEN).build()
        # application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.TEXT, handle_msg))
        application.add_handler(CallbackQueryHandler(inline_handler))
        application.run_polling(read_timeout=30, timeout=10000)