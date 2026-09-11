import os

import requests
from dotenv import load_dotenv


load_dotenv()


class LLMClient:

    def __init__(
        self,
        model="openai/gpt-4o-mini"
    ):

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.model = model

        self.url = (
            "https://openrouter.ai/api/v1/chat/completions"
        )

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set."
            )

    def generate(
        self,
        prompt,
        system_message=None,
        max_tokens=512
    ):

        messages = []

        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = requests.post(
            self.url,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]


def main():

    client = LLMClient()

    answer = client.generate(
        "Say hello in one short sentence."
    )

    print("LLM response:")
    print(answer)


if __name__ == "__main__":
    main()