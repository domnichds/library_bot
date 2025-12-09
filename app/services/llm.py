import asyncio

import aiohttp

from app.config.llm import LLM_API_KEY, LLM_FOLDER_ID, LLM_URL


class LLMError(RuntimeError):
    pass


async def ask_book_question(
    book_full_name: str,
    question: str,
    *,
    timeout: float = 30.0,
) -> str:
    """
    Простой асинхронный вызов Yandex LLM, возвращает текст ответа.
    Бросает LLMError при проблемах (нет ключа, сеть, пустой ответ).
    """

    if not LLM_API_KEY or not LLM_FOLDER_ID:
        raise LLMError("LLM_API_KEY и/или LLM_FOLDER_ID не заданы в окружении")

    system_prompt = (
        f"Ты — эксперт‑библиотекарь. Отвечай кратко и по сути на вопросы о книге «{book_full_name}». "
        "Не раскрывай ключевых спойлеров. Пиши по-русски, 2–6 предложений, без эмодзи и разметки."
        "Не пиши вступлений и заключений, сразу переходи к ответу."
        "Если пользователь задаёт вопрос, не относящийся к книге, вежливо попроси его уточнить."
        "Если текст вопроса хоть немного отличен от вопроса о книге, ответь, что ты можешь отвечать только на вопросы о книгах."
    )

    payload = {
        "modelUri": f"gpt://{LLM_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {"stream": False, "temperature": 0.2, "maxTokens": 1024},
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": (question or "").strip()},
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {LLM_API_KEY}",
    }

    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(LLM_URL, headers=headers, json=payload) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    raise LLMError(f"LLM вернул {resp.status}: {text}")
                data = await resp.json()
    except aiohttp.ClientError as exc:
        raise LLMError(f"Ошибка запроса к LLM: {exc}") from exc

    alternatives = data.get("result", {}).get("alternatives", [])
    if not alternatives:
        raise LLMError(f"Пустой ответ от LLM: {data}")

    message = alternatives[0].get("message", {})
    text = message.get("text", "")
    if not text or not isinstance(text, str):
        raise LLMError(f"Пустой текст в ответе LLM: {data}")

    return text.strip()


if __name__ == "__main__":
    print(asyncio.run(ask_book_question("Война и мир", "хуй")))