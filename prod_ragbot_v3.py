from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import requests
import asyncio

# Токен бота
TELEGRAM_TOKEN = 'YOUR_TOKEN'
# URL API AnythingLLM
ANYTHINGLLM_API_URL = 'http://localhost:3001/api/v1/workspace/mit_rag/chat'
# Токен авторизации
ANYTHINGLLM_API_TOKEN = 'GET_TOKEN_FROM_ANTHLLM'
# Пароль для доступа
AUTH_PASSWORD = '7777'

# Состояния для ConversationHandler
AUTH, CHAT = range(2)

# Функция для анимации ожидания
async def animate_processing(update: Update, processing_message):
    dots = ["", ".", "..", "..."]
    while True:
        for dot in dots:
            try:
                await processing_message.edit_text(f"Ваш запрос обрабатывается{dot}")
                await asyncio.sleep(0.5)  # Интервал между изменениями
            except Exception:
                # Если сообщение было удалено или изменено, прекращаем анимацию
                return

# Функция для обработки старта
async def start(update: Update, context: CallbackContext):
    # Инициализация user_data, если это первый вызов
    if 'authorized' not in context.user_data:
        context.user_data['authorized'] = False
        context.user_data['auth_attempts'] = 0

    # Если пользователь уже авторизован, переходим в режим чата
    if context.user_data['authorized']:
        await update.message.reply_text('Ты уже авторизован. Можешь задавать вопросы!')
        return CHAT

    # Если не авторизован, отправляем приветственное сообщение
    await update.message.reply_text(
        'Привет! Я бот-помощник аналитической команды MIT. '
        'Чтобы получить доступ к общению со мной, введи пароль, который ты наверняка знаешь :)'
    )
    return AUTH

# Функция для обработки ввода пароля
async def auth(update: Update, context: CallbackContext):
    user_message = update.message.text

    # Лимит попыток авторизации
    context.user_data['auth_attempts'] += 1

    if user_message == AUTH_PASSWORD:
        context.user_data['authorized'] = True
        context.user_data['auth_attempts'] = 0  # Сброс счетчика попыток
        await update.message.reply_text('Авторизация успешна! Теперь ты можешь задавать вопросы.')
        return CHAT
    else:
        if context.user_data['auth_attempts'] >= 3:
            await update.message.reply_text('Слишком много попыток. Авторизация отменена.')
            return ConversationHandler.END
        await update.message.reply_text('Неверный пароль. Попробуй ещё раз.')
        return AUTH

# Функция для обработки текстовых сообщений (чат)
async def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    # Отправляем сообщение о том, что запрос обрабатывается
    processing_message = await update.message.reply_text("Ваш запрос обрабатывается...")

    # Запускаем анимацию ожидания
    animation_task = asyncio.create_task(animate_processing(update, processing_message))

    try:
        print(f"Отправка запроса к AnythingLLM: {user_message}")
        # Формируем JSON-запрос
        payload = {
            "message": user_message,
            "mode": "chat",
            "sessionId": str(update.message.chat_id)
        }
        # Отправляем POST-запрос
        response = requests.post(
            ANYTHINGLLM_API_URL,
            headers={
                "Authorization": f"Bearer {ANYTHINGLLM_API_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=20
        )
        response.raise_for_status()  # Проверка на ошибки HTTP
        print(f"Ответ от AnythingLLM: {response.status_code}, {response.text}")

        # Извлекаем ответ из поля "textResponse"
        llm_response = response.json().get("textResponse", "Не удалось получить ответ.")

        # Останавливаем анимацию и редактируем сообщение
        animation_task.cancel()
        await processing_message.edit_text(llm_response)
    except requests.exceptions.Timeout:
        animation_task.cancel()
        await processing_message.edit_text("Сервер не отвечает. Попробуйте позже.")
    except requests.exceptions.ConnectionError:
        animation_task.cancel()
        await processing_message.edit_text("Ошибка подключения к серверу. Проверьте интернет.")
    except requests.exceptions.RequestException as e:
        animation_task.cancel()
        await processing_message.edit_text(f"Ошибка при запросе к серверу: {str(e)}")
    except Exception as e:
        animation_task.cancel()
        print(f"Неожиданная ошибка: {e}")
        await processing_message.edit_text(f"Произошла ошибка: {str(e)}")

# Функция для отмены авторизации
async def cancel(update: Update, context: CallbackContext):
    context.user_data['authorized'] = False
    context.user_data['auth_attempts'] = 0
    await update.message.reply_text('Авторизация отменена. Используй /start, чтобы начать заново.')
    return ConversationHandler.END

# Основная функция
def main():
    # Создаем Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth)],
            CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрация обработчиков
    application.add_handler(conv_handler)

    # Запуск бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()