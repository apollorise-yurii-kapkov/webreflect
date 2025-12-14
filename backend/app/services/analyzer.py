from typing import Dict, List, Optional
import openai
from openai import AsyncOpenAI
import json
import re

from app.core.config import settings
from app.schemas.analysis import MessagingAnalysis, MessagingScores


class WebsiteAnalyzer:
    """AI-powered website content analyzer."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.ANALYSIS_MODEL
        self.max_tokens = settings.MAX_TOKENS_PER_ANALYSIS
    
    async def analyze_website_content(self, pages_data: List[Dict], job_id: str = None) -> Dict:
        """Analyze website content and generate objective summary."""
        try:
            # Prepare content for analysis
            content_summary = self._prepare_content_for_analysis(pages_data)
            
            # Generate objective analysis without scoring
            objective_analysis = await self._generate_objective_summary(content_summary, job_id)
            
            return {
                'content_summary': objective_analysis,
                'messaging_analysis': None
            }
            
        except Exception as e:
            print(f"Error analyzing website content: {e}")
            raise
    
    def _prepare_content_for_analysis(self, pages_data: List[Dict]) -> str:
        """Prepare and summarize content from all pages."""
        content_parts = []
        
        for page in pages_data:
            page_content = f"=== PAGE: {page.get('url', 'Unknown')} ===\n"
            
            if page.get('title'):
                page_content += f"TITLE: {page['title']}\n"
            
            if page.get('meta_description'):
                page_content += f"META: {page['meta_description']}\n"
            
            if page.get('h1_tags'):
                page_content += f"H1s: {', '.join(page['h1_tags'])}\n"
            
            if page.get('cta_texts'):
                page_content += f"CTAs: {', '.join(page['cta_texts'][:5])}\n"  # Limit CTAs
            
            if page.get('content'):
                # Limit content length per page
                content = page['content'][:2000] + "..." if len(page['content']) > 2000 else page['content']
                page_content += f"CONTENT: {content}\n"
            
            content_parts.append(page_content)
        
        return "\n\n".join(content_parts)
    
    async def _generate_objective_summary(self, content: str, job_id: str = None) -> str:
        """Generate an objective, narrative summary of the website content."""
        prompt = f"""
        You are a mirror reflecting what a website communicates to visitors. Analyze the following website content and write a clear, objective narrative about what this website tells the world.

        Website Content:
        {content}

        Write a reflection in a storytelling style that answers:
        - Who are these people/company and what do they do?
        - What is their core offering or mission?
        - What makes them stand out or what are they strong at?
        - What message does a visitor actually receive when landing on this site?
        - Who seems to be their target audience?

        IMPORTANT GUIDELINES:
        - Write a direct narrative reflection of the website
        - Be objective and factual — describe what IS there, not what SHOULD be
        - Use a natural, conversational but professional tone
        - Do NOT use phrases like "I found", "I checked", "The analysis shows", or "Based on the content"
        - Do NOT give scores, ratings, or recommendations
        - Do NOT use bullet points or lists — write flowing paragraphs
        - Keep it concise: 150-250 words maximum
        - If something is unclear or missing from the site, say so honestly
        - Focus on the MESSAGING — what story does this website tell?

        Start directly with the reflection. Example start: "This website presents itself as..." or "The company positions itself as..."
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a website reflection mirror — you objectively describe what a website communicates to visitors. Write in a natural, narrative style. Be factual and honest, never promotional or critical."},
                    {"role": "user", "content": prompt}
                ],
            )
            
            # Log OpenAI API cost if job_id is provided
            if job_id:
                from app.services.cost_tracking_service import get_cost_tracking_service
                from app.core.cost_config import OPENAI_COSTS, PRIMARY_MODEL
                from app.core.database import get_db
                
                # Get actual token usage from OpenAI response
                usage = response.usage
                input_tokens = usage.prompt_tokens
                output_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
                
                # Get cost per token for the model
                model_costs = OPENAI_COSTS.get(PRIMARY_MODEL, OPENAI_COSTS.get("gpt-5-nano"))
                input_cost_per_token = model_costs.get("input", 0.0000005)
                output_cost_per_token = model_costs.get("output", 0.0000015)
                
                # Calculate total cost (input + output tokens have different prices)
                total_cost = (input_tokens * input_cost_per_token) + (output_tokens * output_cost_per_token)
                
                # Log the cost
                async for db in get_db():
                    cost_service = get_cost_tracking_service(db)
                    await cost_service.log_cost(
                        service="openai",
                        operation=f"{PRIMARY_MODEL}-analysis",
                        cost_amount=total_cost,
                        job_id=job_id,
                        tokens_used=total_tokens,
                        requests_count=1,
                        description=f"OpenAI {PRIMARY_MODEL} API call for analysis",
                        extra_data={
                            "model": PRIMARY_MODEL,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "input_cost_per_token": input_cost_per_token,
                            "output_cost_per_token": output_cost_per_token
                        }
                    )
                    break
            
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"Error generating objective summary: {e}")
            return "Unable to generate website summary due to analysis error."
    
    async def _analyze_messaging(self, content: str) -> MessagingAnalysis:
        """Analyze messaging using OpenAI with structured outputs."""
        prompt = f"""
        Analyze the following website content and provide a comprehensive messaging analysis.
        
        Website Content:
        {content}
        
        Focus on:
        - What message visitors would actually receive
        - How clear and compelling the messaging is
        - Whether the messaging is consistent across pages
        - How well it differentiates from competitors
        """
        
        # Define the response schema for structured outputs
        response_schema = {
            "type": "object",
            "properties": {
                "primary_message": {
                    "type": "string",
                    "description": "The main message this website conveys to visitors"
                },
                "target_audience": {
                    "type": "string", 
                    "description": "Who this website is primarily targeting"
                },
                "value_proposition": {
                    "type": "string",
                    "description": "The core value proposition offered"
                },
                "tone_and_voice": {
                    "type": "string",
                    "description": "Description of the brand's tone and voice"
                },
                "key_themes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key themes found in the messaging"
                },
                "strengths": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "description": "Messaging strengths identified"
                },
                "weaknesses": {
                    "type": "array",
                    "items": {"type": "string"}, 
                    "description": "Messaging weaknesses identified"
                }
            },
            "required": ["primary_message", "target_audience", "value_proposition", "tone_and_voice", "key_themes", "strengths", "weaknesses"],
            "additionalProperties": False
        }
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert marketing analyst specializing in website messaging analysis. Provide detailed, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "messaging_analysis",
                        "schema": response_schema
                    }
                }
            )
            
            # With structured outputs, the response is guaranteed to be valid JSON
            content_text = response.choices[0].message.content
            analysis_data = json.loads(content_text)
            return MessagingAnalysis(**analysis_data)
                
        except Exception as e:
            print(f"Error in messaging analysis: {e}")
            raise
    
    async def _calculate_scores(self, content: str, messaging_analysis: MessagingAnalysis) -> MessagingScores:
        """Calculate messaging scores using AI with structured outputs."""
        prompt = f"""
        Based on the website content and messaging analysis, provide numerical scores (0-100) for each category.
        
        Website Content Summary:
        {content[:1500]}...
        
        Messaging Analysis:
        - Primary Message: {messaging_analysis.primary_message}
        - Value Proposition: {messaging_analysis.value_proposition}
        - Strengths: {', '.join(messaging_analysis.strengths)}
        - Weaknesses: {', '.join(messaging_analysis.weaknesses)}
        
        Scoring criteria:
        - Clarity: How clear and understandable is the message?
        - Consistency: How consistent is messaging across pages?
        - Differentiation: How well does it stand out from competitors?
        - Proof: How much social proof and credibility is shown?
        - CTA Strength: How compelling and clear are the calls-to-action?
        - Audience Fit: How well does it match the target audience?
        """
        
        # Define the response schema for structured outputs
        scores_schema = {
            "type": "object",
            "properties": {
                "clarity": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How clear and understandable is the message"
                },
                "consistency": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How consistent is messaging across pages"
                },
                "differentiation": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How well does it stand out from competitors"
                },
                "proof": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How much social proof and credibility is shown"
                },
                "cta_strength": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How compelling and clear are the calls-to-action"
                },
                "audience_fit": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "How well does it match the target audience"
                }
            },
            "required": ["clarity", "consistency", "differentiation", "proof", "cta_strength", "audience_fit"],
            "additionalProperties": False
        }
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing analyst. Provide objective numerical scores based on the content quality and effectiveness."},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "messaging_scores",
                        "schema": scores_schema
                    }
                }
            )
            
            # With structured outputs, the response is guaranteed to be valid JSON
            content_text = response.choices[0].message.content
            scores_data = json.loads(content_text)
            
            # Calculate overall score
            individual_scores = [
                scores_data.get('clarity', 50),
                scores_data.get('consistency', 50),
                scores_data.get('differentiation', 50),
                scores_data.get('proof', 50),
                scores_data.get('cta_strength', 50),
                scores_data.get('audience_fit', 50)
            ]
            overall_score = sum(individual_scores) // len(individual_scores)
            
            return MessagingScores(
                clarity=scores_data.get('clarity', 50),
                consistency=scores_data.get('consistency', 50),
                differentiation=scores_data.get('differentiation', 50),
                proof=scores_data.get('proof', 50),
                cta_strength=scores_data.get('cta_strength', 50),
                audience_fit=scores_data.get('audience_fit', 50),
                overall=overall_score
            )
                
        except Exception as e:
            print(f"Error calculating scores: {e}")
            raise
    
    async def _generate_quick_wins(self, content: str, messaging_analysis: MessagingAnalysis, scores: MessagingScores) -> List[str]:
        """Generate actionable quick wins based on analysis with structured outputs."""
        prompt = f"""
        Based on the website analysis, provide 5-7 specific, actionable "quick wins" that could immediately improve the website's messaging.
        
        Current Weaknesses: {', '.join(messaging_analysis.weaknesses)}
        
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
        """
        
        # Define the response schema for structured outputs
        quick_wins_schema = {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A specific, actionable recommendation for improving website messaging"
                    },
                    "minItems": 5,
                    "maxItems": 7,
                    "description": "List of quick win recommendations"
                }
            },
            "required": ["recommendations"],
            "additionalProperties": False
        }
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a conversion optimization expert. Provide specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "quick_wins",
                        "schema": quick_wins_schema
                    }
                }
            )
            
            # With structured outputs, the response is guaranteed to be valid JSON
            content_text = response.choices[0].message.content
            response_data = json.loads(content_text)
            return response_data.get('recommendations', [])
                
        except Exception as e:
            print(f"Error generating quick wins: {e}")
            raise
