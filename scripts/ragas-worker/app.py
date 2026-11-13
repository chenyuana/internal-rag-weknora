"""Private, stateless Ragas scoring service. Never expose its port publicly."""
import asyncio
import hmac
import math
import os

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from ragas.dataset_schema import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference, LLMContextRecall

app = FastAPI()
slots = asyncio.Semaphore(2)


class Judge(BaseModel):
    model: str
    base_url: str
    api_key: str = ''
    headers: dict[str, str] = {}


class Sample(BaseModel):
    judge: Judge | None = None
    user_input: str = Field(min_length=1, max_length=32000)
    response: str = Field(min_length=1, max_length=64000)
    retrieved_contexts: list[str] = Field(min_length=1, max_length=100)
    reference: str | None = None


@app.post('/score')
async def score(sample: Sample, authorization: str = Header(default='')):
    token = os.environ.get('RAGAS_WORKER_TOKEN', '')
    if not token or not hmac.compare_digest(authorization, 'Bearer ' + token):
        raise HTTPException(401, 'Invalid worker token')
    if sample.judge is None:
        raise HTTPException(503, '请选择已配置的问答模型')
    if not all(c.strip() for c in sample.retrieved_contexts):
        raise HTTPException(422, 'Empty context')
    sample.retrieved_contexts = list(dict.fromkeys(sample.retrieved_contexts))
    context_chars = sum(map(len, sample.retrieved_contexts))
    if context_chars > 1000000:
        raise HTTPException(422, f'上下文共 {context_chars:,} 字符，超过 1,000,000 字符上限。请减少上下文后重试；未截断原文。')
    async with slots:
        llm = LangchainLLMWrapper(ChatOpenAI(
            model=sample.judge.model, base_url=sample.judge.base_url,
            api_key=sample.judge.api_key or 'local-model', default_headers=sample.judge.headers, temperature=0,
            timeout=65, max_retries=0,
        ))
        metrics = [Faithfulness(llm=llm), LLMContextPrecisionWithoutReference(llm=llm)]
        if sample.reference and sample.reference.strip():
            metrics.append(LLMContextRecall(llm=llm))
        row = SingleTurnSample(**sample.model_dump(exclude={"judge"}))
        scores, errors = {}, {}
        for metric in metrics:
            try:
                value = float(await asyncio.wait_for(metric.single_turn_ascore(row), timeout=(80 if metric.name == 'faithfulness' else 35 if metric.name == 'context_recall' else 50)))
                if not math.isfinite(value):
                    raise ValueError('Non-finite score')
                scores[metric.name] = value
            except asyncio.TimeoutError:
                errors[metric.name] = '该指标评分超时，上下文较长；可重试或减少评测上下文'
            except Exception as exc:
                print('Ragas metric failed:', metric.name, type(exc).__name__, flush=True)
                # Provider exceptions can contain credentials or document text.
                errors[metric.name] = '评分失败，请检查模型兼容性或重试'
        return {'scores': scores, 'errors': errors, 'judge_model': sample.judge.model, 'ragas_version': '0.2.15'}
