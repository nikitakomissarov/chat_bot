
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import dotenv_values
from google.cloud import dialogflow
import json
import logging
from logging.handlers import TimedRotatingFileHandler

config = dotenv_values('.env')

TOKEN = config['TOKEN']
SESSION_ID = config['CHAT_ID']
GOOGLE_APPLICATION_CREDENTIALS = open(config['GOOGLE'])

credentials = json.loads(GOOGLE_APPLICATION_CREDENTIALS.read())

logger_info = logging.getLogger('loggerinfo')
logger_error = logging.getLogger("loggererror")
handler = TimedRotatingFileHandler("app.log", when='D', interval=30, backupCount=1)
handler_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def detect_intent_texts(project_id, session_id, texts, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    logger_info.info("Session path: {}\n".format(session))

    text_input = dialogflow.TextInput(text=texts, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    logger_info.info("=" * 20)
    logger_info.info("Query text: {}".format(response.query_result.query_text))
    logger_info.info(
        "Detected intent: {} (confidence: {})\n".format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence,
        ))

    answer = (format(response.query_result.fulfillment_text))
    return answer

async def start(update, context):
    await update.message.reply_text("The bot's been started")

async def echo(update, context):
    try:
        language_code = update.message.from_user.language_code
        text = update.message.text
        session_id = update.message.chat['id']
        google_reply = detect_intent_texts(credentials['quota_project_id'], session_id, text, language_code)
        print(google_reply)
        if google_reply != "":
            google_reply = google_reply
        else:
            google_reply = 'Я вас не понимаю'
        await update.message.reply_text(google_reply)
    except Exception as err:
        logger_error.exception(err)

def main():
    if __name__ == '__main__':

        handler.setFormatter(handler_format)

        logger_info.setLevel(logging.INFO)
        logger_info.addHandler(handler)

        logger_error.setLevel(logging.ERROR)
        logger_error.addHandler(handler)

        logger_info.info("here we go")
        try:
            application = Application.builder().token(TOKEN).build()

            application.add_handler(CommandHandler('start', start))
            application.add_handler(MessageHandler(filters.TEXT, echo))

            application.run_polling()
        except Exception as err:
            logger_error.exception(err)

if __name__ == '__main__':
    main()