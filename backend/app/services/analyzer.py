from typing import Dict, List
import json
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.core.config import settings
from app.schemas.analysis import MessagingAnalysis, MessagingScores


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _trim_to_tokens(text: str, max_tokens: int) -> str:
    """Trim text to roughly max_tokens tokens, trying to cut at sentence/line boundaries."""
    if _approx_tokens(text) <= max_tokens:
        return text
    cut = max_tokens * 4
    trimmed = text[:cut]
    idx = max(trimmed.rfind("\n"), trimmed.rfind(". "), trimmed.rfind("! "), trimmed.rfind("? "))
    return trimmed if idx < 0 else trimmed[:idx+1]


def _extract_output_text(response) -> str:
    """Extract main output from Response API."""
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text
    if hasattr(response, "output") and response.output:
        for item in response.output:
            content = getattr(item, "content", None)
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                for sub in content:
                    if hasattr(sub, "text") and sub.text:
                        return sub.text
                    if hasattr(sub, "content") and sub.content:
                        return sub.content
            if hasattr(item, "text") and item.text:
                return item.text
    if hasattr(response, "reasoning") and response.reasoning:
        summary = getattr(response.reasoning, "summary", None)
        if summary:
            return summary
    return ""


class WebsiteAnalyzer:
    """Uses GPT to summarize and analyze website content."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.ANALYSIS_MODEL
        self.max_output_tokens = min(settings.MAX_TOKENS_PER_ANALYSIS, 12000)

    def _prepare_content(self, pages: List[Dict]) -> str:
        """Compile key information from crawled pages into a summary string."""
        parts = []
        for page in pages[:settings.MAX_PAGES_PER_SITE]:
            section = []
            url = page.get("url", "Unknown")
            section.append(f"=== PAGE: {url} ===")
            if page.get("title"):
                section.append(f"TITLE: {page['title']}")
            if page.get("meta_description"):
                section.append(f"META: {page['meta_description']}")
            if page.get("h1_tags"):
                h1 = ", ".join(page["h1_tags"])[:300]
                section.append(f"H1s: {h1}")
            if page.get("cta_texts"):
                cta = ", ".join(page["cta_texts"][:5])[:200]
                section.append(f"CTAs: {cta}")
            if page.get("content"):
                content = _trim_to_tokens(page["content"], 250)
                section.append(f"CONTENT: {content}")
            parts.append("\n".join(section))
        full = "\n\n".join(parts)
        return _trim_to_tokens(full, 6000)

    async def analyze_website_content(self, pages: List[Dict], job_id: str = None) -> Dict:
        """Perform full analysis: summary, messaging analysis, scores, quick wins."""
        content = self._prepare_content(pages)
        summary = await self._generate_summary(content, job_id)
        messaging = await self._analyze_messaging(content)
        scores = await self._calculate_scores(content, messaging)
        recommendations = await self._generate_quick_wins(content, messaging, scores)
        return {
            "content_summary": summary,
            "messaging_analysis": messaging,
            "scores": scores,
            "quick_wins": recommendations,
        }

    async def _generate_summary(self, content: str, job_id: str = None) -> str:
        """Generate an objective summary of website content UP TO 500 words."""
        instructions = "You are a professional content analyst. Provide objective, factual summaries without subjective evaluations or recommendations."
        prompt = f"""
        Analyze the following website content and provide a comprehensive, objective summary.

        Website Content:
        {content}

        Please provide a factual analysis that covers:
        1) What the website is about and its primary purpose
        2) The main products, services, or content offered
        3) Target audience and market positioning
        4) Key messaging themes and value propositions presented
        5) Content structure and organization across pages
        6) Notable features, functionality, or unique aspects

        Requirements:
        - Be completely objective and factual
        - Do not include subjective opinions, scores, or recommendations
        - Focus on describing what IS present, not what SHOULD be
        - Keep the summary between 500-1000 words
        - Use clear, professional language
        - Organize information logically with smooth transitions

        Write this as a cohesive analysis, not as bullet points or lists.
        """.strip()
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=self.max_output_tokens,
            )
            if job_id:
                await self._log_usage(job_id, response, "summary")
            text = response.choices[0].message.content
            return (text or "Unable to extract summary").strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Unable to generate summary due to analysis error."

    async def _analyze_messaging(self, content: str) -> MessagingAnalysis:
        """Analyze messaging and return structured JSON."""
        instructions = "You are an expert marketing analyst specializing in website messaging analysis. Provide detailed, actionable insights."
        prompt = f"""
        Analyze the following website content and provide a comprehensive messaging analysis.

        Website Content:
        {content}

        Focus on:
        - What message visitors would actually receive
        - How clear and compelling the messaging is
        - Whether the messaging is consistent across pages
        - How well it differentiates from competitors

        Respond strictly as a single JSON object matching the provided schema.
        """.strip()
        response = await self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=self.max_output_tokens,
            response_format=MessagingAnalysis
        )
        return response.choices[0].message.parsed

    async def _calculate_scores(self, content: str, analysis: MessagingAnalysis) -> MessagingScores:
        """Calculate messaging scores based on analysis."""
        instructions = "You are a marketing analyst. Provide objective numerical scores based on the content quality and effectiveness."
        prompt = f"""
Based on the website content and messaging analysis, provide numerical scores (0-100) for each category.

Website Content (truncated):
{content[:1500]}

Messaging Analysis:
- Primary Message: {analysis.primary_message}
- Value Proposition: {analysis.value_proposition}
- Strengths: {', '.join(analysis.strengths)}
- Weaknesses: {', '.join(analysis.weaknesses)}

Scoring criteria:
- Clarity
- Consistency
- Differentiation
- Proof
- CTA Strength
- Audience Fit

Respond strictly as a single JSON object matching the provided schema.
""".strip()
        response = await self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=self.max_output_tokens,
            response_format=MessagingScores
        )
        scores = response.choices[0].message.parsed
        # Calculate overall score
        individual_scores = [
            scores.clarity,
            scores.consistency,
            scores.differentiation,
            scores.proof,
            scores.cta_strength,
            scores.audience_fit,
        ]
        overall = sum(individual_scores) // len(individual_scores)
        scores.overall = overall
        return scores

    async def _generate_quick_wins(self, content: str, analysis: MessagingAnalysis, scores: MessagingScores) -> List[str]:
        """Generate quick win recommendations as JSON."""
        instructions = "You are a conversion optimization expert. Provide specific, actionable recommendations."
        prompt = f"""
Based on the website analysis, provide 5-7 specific, actionable "quick wins" that could immediately improve the website's messaging.

Current Weaknesses: {', '.join(analysis.weaknesses)}

Lowest Scores:
- Clarity: {scores.clarity}/100
- Consistency: {scores.consistency}/100
- Differentiation: {scores.differentiation}/100
- Proof: {scores.proof}/100
- CTA Strength: {scores.cta_strength}/100
- Audience Fit: {scores.audience_fit}/100

Focus on:
- Easy to implement changes
- High impact improvements
- Specific, not generic advice
- Address the lowest scoring areas first

Respond strictly as a JSON object: {{"recommendations": ["..."]}}.
""".strip()
        class QuickWinsResponse(BaseModel):
            recommendations: List[str]
        response = await self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=self.max_output_tokens,
            response_format=QuickWinsResponse
        )
        return response.choices[0].message.parsed.recommendations

    async def _log_usage(self, job_id: str, response, operation: str):
        """Log cost and usage from response."""
        try:
            from app.services.cost_tracking_service import get_cost_tracking_service
            from app.core.cost_config import OPENAI_COSTS, PRIMARY_MODEL
            from app.core.database import get_db
            usage = getattr(response, "usage", None)
            if not usage:
                return
            input_tokens = getattr(usage, "prompt_tokens", 0)
            output_tokens = getattr(usage, "completion_tokens", 0)
            total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)
            model_costs = OPENAI_COSTS.get(PRIMARY_MODEL, OPENAI_COSTS.get("gpt-5-nano", {}))
            input_cost = model_costs.get("input", 0.0)
            output_cost = model_costs.get("output", 0.0)
            total_cost = input_tokens * input_cost + output_tokens * output_cost
            async for db in get_db():
                service = get_cost_tracking_service(db)
                await service.log_cost(
                    service="openai",
                    operation=f"{PRIMARY_MODEL}-{operation}",
                    cost_amount=total_cost,
                    job_id=job_id,
                    tokens_used=total_tokens,
                    requests_count=1,
                    description=f"OpenAI {PRIMARY_MODEL} API call",
                    extra_data={
                        "model": PRIMARY_MODEL,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "input_cost_per_token": input_cost,
                        "output_cost_per_token": output_cost,
                    }
                )
                break
        except Exception as e:
            print(f"Usage logging error: {e}")
