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
    
    async def analyze_website_content(self, pages_data: List[Dict]) -> Dict:
        """Analyze website content and generate objective summary."""
        try:
            # Prepare content for analysis
            content_summary = self._prepare_content_for_analysis(pages_data)
            
            # Generate objective analysis without scoring
            objective_analysis = await self._generate_objective_summary(content_summary)
            
            return {
                'content_summary': objective_analysis,
                'messaging_analysis': objective_analysis
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
    
    async def _generate_objective_summary(self, content: str) -> str:
        """Generate an objective, factual summary of the website content."""
        prompt = f"""
        Analyze the following website content and provide a comprehensive, objective summary.
        
        Website Content:
        {content}
        
        Please provide a factual analysis that covers:
        1. What the website is about and its primary purpose
        2. The main products, services, or content offered
        3. Target audience and market positioning
        4. Key messaging themes and value propositions presented
        5. Content structure and organization across pages
        6. Notable features, functionality, or unique aspects
        
        Requirements:
        - Be completely objective and factual
        - Do not include subjective opinions, scores, or recommendations
        - Focus on describing what IS present, not what SHOULD be
        - Keep the summary between 500-1000 words
        - Use clear, professional language
        - Organize information logically with smooth transitions
        
        Write this as a cohesive analysis, not as bullet points or lists.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional content analyst. Provide objective, factual summaries without subjective evaluations or recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
                
        except Exception as e:
            print(f"Error generating objective summary: {e}")
            return "Unable to generate website summary due to analysis error."
    
    async def _analyze_messaging(self, content: str) -> MessagingAnalysis:
        """Analyze messaging using OpenAI."""
        prompt = f"""
        Analyze the following website content and provide a comprehensive messaging analysis.
        
        Website Content:
        {content}
        
        Please provide a JSON response with the following structure:
        {{
            "primary_message": "The main message this website conveys to visitors",
            "target_audience": "Who this website is primarily targeting",
            "value_proposition": "The core value proposition offered",
            "tone_and_voice": "Description of the brand's tone and voice",
            "key_themes": ["theme1", "theme2", "theme3"],
            "strengths": ["strength1", "strength2", "strength3"],
            "weaknesses": ["weakness1", "weakness2", "weakness3"]
        }}
        
        Focus on:
        - What message visitors would actually receive
        - How clear and compelling the messaging is
        - Whether the messaging is consistent across pages
        - How well it differentiates from competitors
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert marketing analyst specializing in website messaging analysis. Provide detailed, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            content_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group())
                return MessagingAnalysis(**analysis_data)
            else:
                # Fallback if JSON parsing fails
                return MessagingAnalysis(
                    primary_message="Unable to analyze primary message",
                    target_audience="Unable to identify target audience",
                    value_proposition="Unable to identify value proposition",
                    tone_and_voice="Unable to analyze tone and voice",
                    key_themes=["Analysis failed"],
                    strengths=["Analysis failed"],
                    weaknesses=["Analysis failed"]
                )
                
        except Exception as e:
            print(f"Error in messaging analysis: {e}")
            raise
    
    async def _calculate_scores(self, content: str, messaging_analysis: MessagingAnalysis) -> MessagingScores:
        """Calculate messaging scores using AI."""
        prompt = f"""
        Based on the website content and messaging analysis, provide numerical scores (0-100) for each category.
        
        Website Content Summary:
        {content[:1500]}...
        
        Messaging Analysis:
        - Primary Message: {messaging_analysis.primary_message}
        - Value Proposition: {messaging_analysis.value_proposition}
        - Strengths: {', '.join(messaging_analysis.strengths)}
        - Weaknesses: {', '.join(messaging_analysis.weaknesses)}
        
        Provide scores as JSON:
        {{
            "clarity": 85,
            "consistency": 75,
            "differentiation": 60,
            "proof": 70,
            "cta_strength": 80,
            "audience_fit": 90
        }}
        
        Scoring criteria:
        - Clarity: How clear and understandable is the message?
        - Consistency: How consistent is messaging across pages?
        - Differentiation: How well does it stand out from competitors?
        - Proof: How much social proof and credibility is shown?
        - CTA Strength: How compelling and clear are the calls-to-action?
        - Audience Fit: How well does it match the target audience?
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a marketing analyst. Provide objective numerical scores based on the content quality and effectiveness."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content_text = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                scores_data = json.loads(json_match.group())
                
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
            else:
                # Fallback scores
                return MessagingScores(
                    clarity=50, consistency=50, differentiation=50,
                    proof=50, cta_strength=50, audience_fit=50, overall=50
                )
                
        except Exception as e:
            print(f"Error calculating scores: {e}")
            raise
    
    async def _generate_quick_wins(self, content: str, messaging_analysis: MessagingAnalysis, scores: MessagingScores) -> List[str]:
        """Generate actionable quick wins based on analysis."""
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
        
        Provide a JSON array of specific, actionable recommendations:
        [
            "Add a clear value proposition statement to the homepage hero section",
            "Strengthen the main CTA button text to be more action-oriented",
            "Include customer testimonials or social proof elements",
            "Simplify the navigation menu to reduce cognitive load",
            "Add benefit-focused headlines instead of feature-focused ones"
        ]
        
        Focus on:
        - Easy to implement changes
        - High impact improvements
        - Specific, not generic advice
        - Address the lowest scoring areas first
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a conversion optimization expert. Provide specific, actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            content_text = response.choices[0].message.content
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                quick_wins = json.loads(json_match.group())
                return quick_wins
            else:
                # Fallback quick wins
                return [
                    "Clarify your main value proposition on the homepage",
                    "Strengthen call-to-action button text",
                    "Add social proof elements like testimonials",
                    "Improve headline clarity and benefit focus",
                    "Ensure consistent messaging across all pages"
                ]
                
        except Exception as e:
            print(f"Error generating quick wins: {e}")
            raise
