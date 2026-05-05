import os
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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

        self.SYSTEM_PROMPT = """Analyze each listing carefully. You MUST assign realistic scam_probability values:
        - 0-20%: detailed description, specific address, reasonable price, owner contact
        - 21-50%: some details missing, price slightly low, vague location  
        - 51-80%: no address, no contacts, unusually low price, copy-paste text
        - 81-100%: pressure tactics, advance payment demanded, too good to be true
        
        NEVER assign 0% unless the listing is clearly legitimate with full details.
        Be skeptical by default.

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
                "page_id": 12345,
                "excerpt": "Короткий текст оголошення...",
                "scam_probability": 85,
                "verdict": "Шахрайство",
                "reason": "Ваша причина українською мовою"
              }
            ]
          }
          "page_id must be taken from the [ID:XXXXX] prefix in each listing text."
          
          Do not include any Markdown, explanations, or text outside the JSON block."""

        self.client = OpenAI(
            api_key=os.environ.get("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    def get_flat_descriptions(self, limit, offset):
        with sqlite3.connect('pages.db') as connection:
            cursor = connection.cursor()
            cursor.execute('''
                           SELECT id, description
                           FROM pages
                           ORDER BY id DESC
                           LIMIT ? OFFSET ?
                           ''', (limit, offset))

            results = cursor.fetchall()
            descriptions_list = [f"[ID:{row[0]}] {row[1]}" for row in results]
            return "\n\n".join(descriptions_list)

    def text_analysis(self):
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "Починай аналіз бази! Коли закінчиш, видай фінальний JSON."}
        ]

        while True:
            # noinspection PyTypeChecker
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
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
                content = message.content or ""
                if '{' not in content:
                    raise ValueError(f"Model returned non-JSON: {content[:200]}")
                return content

if __name__ == '__main__':
    ai = AIanalyst()
    print(ai.text_analysis())