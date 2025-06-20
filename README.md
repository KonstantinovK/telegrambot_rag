# Техническая документация Telegram-бот с интеграцией AnythingLLM + LM Studio

## Оглавление
1. [Введение](#Head)
2. [Архитектура проекта](#Archi)
3. [Настройка окружения](#Arround)
4. [API](#API)
5. [Примеры использования](#Samples)
6. [Заключение](#Concl)
7. [Ссылки](#Links)

---
<a name="Head"><h2>Введение</h2></a>

Этот проект представляет собой Telegram-бота, который взаимодействует с AnythingLLM — инструментом для работы с языковыми моделями (LLM), в нашем случае используется как инструмент для загрузки документов и создания RAG архива. AnythingLLM имеет интеграцию  и взаимодействует с LM Studio, инструментом для локального развертывания модели ИИ.  Бот предоставляет доступ к ИИ-модели только авторизованным пользователям, что делает его удобным решением для команд, которые хотят использовать ИИ в своих рабочих процессах.

---
<a name="Archi"><h2>Архитектура проекта</h2></a>

Проект состоит из следующих компонентов:

1. **Telegram-бот**: Обрабатывает команды и сообщения от пользователей.
2. **AnythingLLM**: Создание RAG архива, обработка запросов к языковой модели.
3. **LM Studio**: Backend для обработки запросов ИИ моделью.
4. **Python-скрипт**: Связывает Telegram-бота и AnythingLLM, обрабатывает авторизацию и запросы.


### Схема взаимодействия

```
Пользователь -> Telegram-бот -> Python-скрипт -> AnythingLLM ->LM Studio -> Ответ -> Пользователь
```


---
<a name="Arround"><h2>Настройка окружения</h2></a>

### 1. Установка зависимостей

Убедитесь, что у вас установлен Python 3.8 или выше. Затем установите необходимые зависимости:

Copy
```bash
pip install python-telegram-bot requests
```


### 2. Настройка Telegram-бота

1. Откройте Telegram и найдите бота **BotFather**.

2. Создайте нового бота с помощью команды `/newbot`.

3. Сохраните токен, который BotFather предоставит вам.
	*731334xxxx:AAFKLc947b-b26Qnkpiv5ysz-jxxxxx_X_X*

### 3. Настройка AnythingLLM

Убедитесь, что AnythingLLM запущен и доступен по API. В нашем примере мы используем эндпоинт для доступа к чату:

```
http://localhost:3001/api/v1/workspace/mit_rag/chat
```

При создании workspace в AnythingLLM, использовали название MIT_RAG (для API используется нижний регистр: mit_rag)

Есть много примеров по настройке и связке LM Studio и AnythingLLM в Youtube. Gjlробно на этом останавливаться не буду.

Проверить доступность API AnythingLLM можно двумя способами, в первом через обычный браузер, смотрим доступность документации

```
http://localhost:3001/api/docs/
```

второй способ через терминал, стоит обратить внимание на тип авторизации Bearer, без его прямого указания API присылает ответы Not found, либо No valid api key found.


```bash
curl -H 'Authorization: Bearer 0T6J029-6EP49KR-N5E0PDJ-BC351R6' http://localhost:3001/api/v1/workspaces
```

### 4. Настройка переменных окружения

Создайте файл `.env` и добавьте в него следующие переменные:

```Python
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ANYTHINGLLM_API_URL=http://localhost:3001/api/v1/workspace/mit_rag/chat
ANYTHINGLLM_API_TOKEN=YOUR_ANYTHINGLLM_API_TOKEN
AUTH_PASSWORD=7777
```


---
<a name="API"><h2>API</h2></a>

### 1. Telegram-бот

- **Команда `/start`**: Запускает бота и запрашивает пароль для авторизации.
    
- **Команда `/cancel`**: Отменяет текущую сессию авторизации.
    
- **Обработка текстовых сообщений**: После авторизации пользователь может отправлять сообщения, которые будут обрабатываться AnythingLLM.
    

### 2. AnythingLLM

- **Эндпоинт `POST /api/v1/workspace/{slug}/chat`**: Принимает JSON-запрос с полями:
    
    - `message`: Текст сообщения.
        
    - `mode`: Режим работы (`query` или `chat`).
        
    - `sessionId`: Идентификатор сессии (опционально).
        
    - `attachments`: Вложения (опционально).
        

---
<a name="Samples"><h2>Примеры использования</h2></a>

### 1. Запуск бота

Запустите бота с помощью команды:

```bash
python mitbot_v1.py
```


### 2. Авторизация

1. Пользователь запускает бота командой `/start`.
    
2. Бот попросит ввести пароль:
    
```
Привет! Я бот-помощник аналитической команды MIT. Чтобы получить доступ к общению со мной, введи пароль, который ты наверняка знаешь :)
```
    
    
3. Пользователь вводит пароль:
    
```bash
7777
```
    
    
4. Бот подтверждает авторизацию:
    
```bash
Авторизация успешна! Теперь ты можешь задавать вопросы.
```


### 3. Взаимодействие с ИИ

1. Пользователь задаёт вопрос:
    
```bash
Привет, как дела?
```
    
2. Бот отвечает:
    
```bash
Привет! У меня всё отлично, а у тебя?
```
    

---
<a name="Concl"><h2>Заключение</h2></a>

Документация демонстрирует, как создать Telegram-бота с интеграцией AnythingLLM+LM Studio. Такой бот может быть полезен для команд, которые хотят использовать ИИ в своих рабочих процессах, обеспечивая при этом безопасность и контроль доступа.

---
<a name="Links"><h2>Ссылки</h2></a>

- [Документация python-telegram-bot](https://docs.python-telegram-bot.org/)
- [Как запустить RAG-файл на Llama 3.1](https://www.youtube.com/watch?v=Zot6DepayZM&t=627s)
---

2025 Moscow. TG @clockber
