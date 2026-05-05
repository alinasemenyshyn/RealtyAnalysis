import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_flat_descriptions(limit, offset):
   with sqlite3.connect('pages.db') as connection:
        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT description
            FROM pages
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        results = cursor.fetchall()
        descriptions_list = [row[0] for row in results]
        return "\n\n".join(descriptions_list)

my_tools = [{
        "type": "function",
        "function": {
            "name": "get_flat_descriptions",
            "description": "Retrieves apartment listing descriptions from a local SQLite database. "
                "Use this tool whenever the user asks to analyze, summarize, or review "
                "property listings. Always start with offset=0 and increment by the value "
                "of 'limit' on each subsequent call until an empty string is returned, "
                "which signals that all listings have been processed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "string",
                        "description":  "The number of apartment descriptions to retrieve per call. "
                            "Use 2 as the default batch size unless instructed otherwise."
                    },
                    "offset": {
                        "type": "string",
                        "description": "The number of records to skip before starting retrieval. "
                            "Set to 0 for the first call, then increment by 'limit' on "
                            "each subsequent call (e.g. 0, 5, 10, 15, 20, 25...). "
                            "Stop calling when the returned text is empty."
                    }
                },
                "required": ["limit", "offset"],
            }
        }
    }]
SYSTEM_PROMPT = """You are an expert real estate fraud detection agent. \
Your task is to analyze every apartment listing in the database and identify scam listings.

CRITICAL LANGUAGE RULE: You MUST write ALL output exclusively in Ukrainian language. \
Every word of your analysis, verdicts, summaries, and reports must be in Ukrainian. \
Do not use English in your responses under any circumstances.

Follow this exact procedure:
1. Call get_flat_descriptions with limit=5 and offset=0.
2. For each listing in the batch, evaluate scam likelihood based on these red flags:
   - Unrealistically low price for the area or size
   - Vague or copy-pasted description with no specific details
   - Pressure tactics ("urgent", "only today", "first come first served")
   - Missing key info (no address, no photos mentioned, no owner contact)
   - Requests for advance payment or deposit before viewing
   - Too-good-to-be-true amenities or conditions
   - Inconsistent or contradictory details within the listing
3. Call get_flat_descriptions again with offset incremented by 5.
4. Repeat until the tool returns an empty string.
5. After all batches are processed, output a final structured report.

## Звіт про виявлення шахрайства

### Результати по кожному оголошенню
Для кожного оголошення напиши:
- Короткий уривок (перші 60 символів)
- Ймовірність шахрайства: 0–100%
- Вердикт: ✅ Справжнє / ⚠️ Підозріле / 🚨 Шахрайство
- Причина: одне речення з поясненням вердикту

### Підсумок
- Всього проаналізовано оголошень
- Кількість: Справжніх / Підозрілих / Шахрайських
- Загальний відсоток шахрайства (%)
- Найпоширеніші патерни шахрайства
- Топ-3 найпідозріліших оголошення з детальним розбором

Будь точним, послідовним і скептичним. За замовчуванням підозрюй, якщо деталей бракує."""

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

def text_analysis():
    messages = [
        {"role": "system",
         "content": SYSTEM_PROMPT,
         },
        {"role": "user",
         "content": """Відповідай ВИКЛЮЧНО у форматі JSON, без жодного тексту поза JSON:
            {
              "listings": [
                {
                  "excerpt": "перші 60 символів",
                  "scam_probability": 75,
                  "verdict": "suspicious",
                  "reason": "причина українською"
                }
              ]
            }"""
         }
    ]
    while True:
        # noinspection PyTypeChecker
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0,
            tools=my_tools,
            tool_choice="auto",
            parallel_tool_calls=False
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        messages.append(message)

        if finish_reason == "tool_calls" and message.tool_calls:
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments)

                result = get_flat_descriptions(
                    limit=int(args.get("limit", 5)),
                    offset=int(args.get("offset", 0))
                )

                if not result:
                    result = "NO_MORE_LISTINGS"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        elif finish_reason == "stop":
            return message.content
        else:
            break


if __name__ == "__main__":
    print(text_analysis())