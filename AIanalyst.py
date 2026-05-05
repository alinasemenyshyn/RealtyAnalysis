import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv


class AIanalyst:
    def __init__(self):
        self.my_tools = [{
            "type": "function",
            "function": {
                "name": "get_flat_descriptions",
                "description": "Retrieves apartment listing descriptions from a local SQLite database. "
                               "Always start with offset=0 and increment by the value "
                               "of 'limit' on each subsequent call until an empty string is returned.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "string",
                            "description": "Use 10 as the batch size."
                        },
                        "offset": {
                            "type": "string",
                            "description": "Skip records. Start at 0, then 10, 20, 30..."
                        }
                    },
                    "required": ["limit", "offset"],
                }
            }
        }]

        self.SYSTEM_PROMPT = """You are an expert real estate fraud detection agent. 
          Your task is to analyze every apartment listing in the database and identify scam listings.

          CRITICAL LANGUAGE RULE: You MUST write ALL analysis and verdicts exclusively in Ukrainian.

          Follow this exact procedure:
          1. Call get_flat_descriptions with limit=10 and offset=0.
          2. Analyze the returned listings for scams (low price, fake photos, urgent payment, etc).
          3. Call get_flat_descriptions again with offset incremented by 10.
          4. Repeat until the tool returns "NO_MORE_LISTINGS".
          5. After all batches are processed, output the final result STRICTLY AND ONLY as a JSON object.

          The JSON format MUST be exactly like this:
          {
            "listings": [
              {
                "excerpt": "Короткий текст оголошення...",
                "scam_probability": 85,
                "verdict": "Шахрайство",
                "reason": "Ваша причина українською мовою"
              }
            ]
          }
          Do not include any Markdown, explanations, or text outside the JSON block."""

        self.client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def get_flat_descriptions(self, limit, offset):
        with sqlite3.connect('pages.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''
                           SELECT description
                           FROM pages
                           ORDER BY id DESC
                           LIMIT ? OFFSET ?
                           ''', (limit, offset))
            results = cursor.fetchall()
            descriptions_list = [row[0] for row in results]
            return "\n\n".join(descriptions_list)

    def text_analysis(self):
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "Починай аналіз бази! Коли закінчиш, видай фінальний JSON."}
        ]

        while True:
            # noinspection PyTypeChecker
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0,
                tools=self.my_tools,
                tool_choice="auto",
                parallel_tool_calls=False
            )

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            messages.append(message)

            if finish_reason == "tool_calls" and message.tool_calls:
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)

                    limit_val = int(args.get("limit", 10))
                    offset_val = int(args.get("offset", 0))

                    print(f"ШІ завантажує квартири: limit={limit_val}, offset={offset_val}")

                    result = self.get_flat_descriptions(
                        limit=limit_val,
                        offset=offset_val
                    )

                    if not result:
                        result = "NO_MORE_LISTINGS"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    })

            elif finish_reason == "stop":
                print("Аналіз завершено, повертаю JSON!")
                return message.content
            else:
                break