# 🕵️‍♂️ Real Estate Scam Detector (Аналізатор нерухомості)

Цей інструмент автоматично аналізує свіжі оголошення квартир з [dom.ria.com](https://dom.ria.com) на ознаки шахрайства за допомогою великої мовної моделі (Llama 3.3 70B через Groq API). 
Кожному оголошенню присвоюється відсоток ризику від 0 до 100%, а результати відображаються у вигляді інтерактивних діаграм.

---

## 📸 Скріншоти роботи


### Головний інтерфейс додатку
<img width="1123" height="810" alt="image" src="https://github.com/user-attachments/assets/db3560f0-6dd6-4800-aa9f-784b20d7782f" />


### Результати аналізу (Інтерактивна діаграма) 
<img width="1023" height="816" alt="image" src="https://github.com/user-attachments/assets/8222bc92-ea7d-4070-a8d7-7af06c11c07f" />


---

## 🎯 Як це вирішує проблему

* ⏳ **До AI:** ручна перевірка одного оголошення займає 5–10 хвилин.
* ⚡ **Після AI:** 10 оголошень аналізуються всього за 30 секунд.
* 🧠 **Глибокий аналіз:** LLM виявляє тонкі ознаки шахрайства, які легко пропустити: копі-паст тексти, відсутність адреси, психологічний тиск на терміновість.

## 🗂 Структура проєкту
```text
RealtyAnalysis/
├── app.py                  # Tkinter GUI — головний додаток
├── scraping.py             # Збір оголошень з dom.ria.com API
├── database.py             # Ініціалізація pages.db та запис даних
├── AIanalyst.py            # Groq LLM з tool calling
├── procesing_from_ai.py    # Парсинг відповіді AI → result_by_AI.db
├── built_diagram.py        # Побудова Plotly діаграм
├── pages.db                # БД з оголошеннями (генерується автоматично)
├── result_by_AI.db         # БД з результатами аналізу (генерується)
├── .env                    # API ключі (НЕ комітити в Git!)
├── .gitignore              
├── requirements.txt        
└── README.md
```
## Встановлення
 
### 1. Клонування репозиторію
 
```bash
git clone https://github.com/YOUR_USERNAME/real-estate-scam-detector.git
cd real-estate-scam-detector
```
 
### 2. Створення virtual environment
 
```bash
# Windows
python -m venv venv
venv\Scripts\activate
 
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
 
### 3. Встановлення залежностей
 
```bash
pip install -r requirements.txt
```
 
### 4. Отримання API ключа Groq
 
1. Перейдіть на [console.groq.com](https://console.groq.com)
2. Зареєструйтесь або увійдіть
3. Перейдіть у **API Keys → Create API Key**
4. Скопіюйте ключ — він починається з `gsk_`
### 5. Налаштування .env
 
Створіть файл `.env` у кореневій директорії:
 
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
 
> ⚠️ Ніколи не комітьте `.env` у Git. Переконайтесь що він є у `.gitignore`.
 
---
 
## Запуск
 
**Крок 1** — зібрати оголошення з dom.ria.com:
 
```bash
python database.py
```
 
**Крок 2** — запустити AI-аналіз:
 
```bash
python procesing_from_ai.py
```
 
**Крок 3** — відкрити інтерфейс:
 
```bash
python app.py
```
 
---
 
## Шкала оцінки шахрайства
 
| Ризик | Вердикт | Ознаки |
|---|---|---|
| 0–20% | Справжнє | Детальний опис, конкретна адреса, розумна ціна, контакти |
| 21–50% | Сумнівне | Деякі деталі відсутні, ціна трохи занижена |
| 51–80% | Підозріле | Немає адреси, немає контактів, аномально низька ціна |
| 81–100% | Шахрайство | Тиск на терміновість, вимога передоплати |
 
---
 
## requirements.txt
 
```
openai>=1.0.0
python-dotenv>=1.0.0
requests>=2.31.0
plotly>=5.0.0
```
 
---
 
## .gitignore
 
```
.env
*.db
__pycache__/
venv/
*.pyc
```
 
---
 
## Вирішення проблем
 
**ModuleNotFoundError** — переконайтесь що активований venv і встановлені залежності:
```bash
pip install -r requirements.txt
```
 
**GROQ_API_KEY not found** — перевірте що файл `.env` існує і ключ починається з `gsk_`.
 
**JSONDecodeError при запуску procesing_from_ai.py** — модель іноді повертає не JSON. Запустіть скрипт ще раз.
 
**Порожня діаграма в app.py** — спочатку запустіть `database.py`, потім `procesing_from_ai.py`.
 
**Tkinter не відкривається (Linux)**:
```bash
sudo apt-get install python3-tk
```
 
