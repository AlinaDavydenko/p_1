from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessagesRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    """Business logic for talking to the LLM and managing chat history."""

    def __init__(
        self,
        messages_repo: ChatMessagesRepository,
        llm_client: OpenRouterClient,
    ) -> None:
        self._messages_repo = messages_repo
        self._llm_client = llm_client

    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: str | None,
        max_history: int,
        temperature: float,
    ) -> str:
        messages: list[dict[str, str]] = []

        if system:
            messages.append({"role": "system", "content": system})

        history = await self._messages_repo.get_recent_messages(user_id, max_history)
        for item in history:
            messages.append({"role": item.role, "content": item.content})

        messages.append({"role": "user", "content": prompt})

        await self._messages_repo.add_message(user_id, role="user", content=prompt)

        answer = await self._llm_client.chat_completion(messages, temperature=temperature)

        await self._messages_repo.add_message(user_id, role="assistant", content=answer)

        return answer

    async def get_history(self, user_id: int) -> list[ChatMessage]:
        return await self._messages_repo.get_all_messages(user_id)

    async def clear_history(self, user_id: int) -> None:
        await self._messages_repo.delete_history(user_id)
