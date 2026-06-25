"""Cadeia LangChain para perguntas acadêmicas."""

import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession

from agent.rag import RAGRetriever
from config.settings import Settings
from database.repository import EventRepository


SYSTEM_PROMPT = """Você é um assistente acadêmico local.
Responda em português com base exclusivamente no contexto fornecido.
Os dados representam "horários e eventos acadêmicos" simulados (temperatura, vento, umidade).
Se não houver dados suficientes, informe claramente.
Seja conciso e objetivo."""


class AcademicAgent:
    """Agente com RAG e suporte a Ollama, OpenAI ou modo mock."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.retriever = RAGRetriever(settings)
        self._llm = self._build_llm()

    def _build_llm(self) -> Any:
        provider = self.settings.llm_provider
        if provider == "openai" and self.settings.openai_api_key:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=self.settings.openai_model,
                api_key=self.settings.openai_api_key,
                temperature=0.2,
            )
        if provider == "ollama":
            from langchain_community.chat_models import ChatOllama

            return ChatOllama(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                temperature=0.2,
            )
        return None

    async def ask(self, session: AsyncSession, question: str) -> dict[str, Any]:
        context, fontes = await self.retriever.build_context(session, question)

        if self._llm is not None:
            return await self._ask_with_llm(question, context, fontes)

        answer = await self._mock_answer(session, question, context)
        return {
            "pergunta": question,
            "resposta": answer,
            "fontes": fontes,
            "provider": self.settings.llm_provider,
        }

    async def _ask_with_llm(
        self, question: str, context: str, fontes: list[str]
    ) -> dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    "Contexto dos dados acadêmicos:\n{context}\n\nPergunta: {question}",
                ),
            ]
        )
        chain = prompt | self._llm
        response = await chain.ainvoke({"context": context, "question": question})
        content = response.content if hasattr(response, "content") else str(response)

        return {
            "pergunta": question,
            "resposta": content,
            "fontes": fontes,
            "provider": self.settings.llm_provider,
        }

    async def _mock_answer(self, session: AsyncSession, question: str, context: str) -> str:
        """Respostas determinísticas quando LLM externo não está configurado."""
        q = question.lower()
        repo = EventRepository(session)

        if "última" in q or "ultima" in q:
            if "atualização" in q or "atualizacao" in q or "update" in q:
                latest = await repo.get_latest_update()
                if latest:
                    return f"A última atualização foi em {latest.recorded_at.strftime('%d/%m/%Y %H:%M:%S')}."
                return "Ainda não há atualizações registradas."

        if "temperatura" in q and ("alta" in q or "máxima" in q or "maxima" in q):
            max_temp = await repo.get_max_metric_today("temperature")
            if max_temp is not None:
                return f"A temperatura mais alta registrada hoje foi {max_temp}°C."
            return "Não há registros de temperatura para hoje."

        hours_match = re.search(r"(\d+)\s*hora", q)
        if hours_match or "últimas" in q or "ultimas" in q:
            hours = int(hours_match.group(1)) if hours_match else 2
            records = await repo.get_recent_updates(hours=hours)
            if not records:
                return f"Não há dados nas últimas {hours} hora(s)."
            lines = [f"Encontrei {len(records)} registro(s) nas últimas {hours} hora(s):"]
            for r in records[:10]:
                parts = []
                for m in r.metrics:
                    label = {"temperature": "Temp", "wind_speed": "Vento", "humidity": "Umidade"}.get(
                        m.metric_key, m.metric_key
                    )
                    parts.append(f"{label}: {m.metric_value}{m.unit}")
                lines.append(f"  • {r.recorded_at.strftime('%H:%M:%S')} — {', '.join(parts)}")
            if len(records) > 10:
                lines.append(f"  ... e mais {len(records) - 10} registro(s).")
            return "\n".join(lines)

        latest = await repo.get_latest_update()
        if latest:
            metrics_text = ", ".join(
                f"{m.metric_key}: {m.metric_value}{m.unit}" for m in latest.metrics
            )
            return (
                f"Com base nos dados mais recentes ({latest.recorded_at.strftime('%d/%m/%Y %H:%M')}): "
                f"{metrics_text}.\n\nContexto adicional:\n{context[:500]}"
            )

        return (
            "Não há dados suficientes no banco para responder. "
            "Aguarde o coletor registrar atualizações."
        )
