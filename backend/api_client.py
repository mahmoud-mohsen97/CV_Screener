"""
API Client for Gemini AI integration.
Handles CV analysis and evaluation using the Gemini AI API.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from portkey import Portkey

class GeminiAIClient:
    def __init__(self, api_key: str):
        """Initialize the Gemini AI client."""
        self.portkey_client = Portkey(
            api_key=api_key,
            virtual_key=os.getenv("PORTKEY_VIRTUAL_KEY")
        )

    async def analyze_cv(
        self, 
        base64_images: List[str], 
        role_data: Dict
    ) -> Dict:
        """
        Analyze CV images using Gemini AI.
        
        Args:
            base64_images: List of base64 encoded CV images
            role_data: Job role requirements and criteria
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Prepare the prompt for CV analysis
            prompt = self._build_analysis_prompt(role_data)
            
            # Call Gemini AI API
            response = await self._call_gemini_api(
                base64_images=base64_images,
                prompt=prompt
            )
            
            # Parse and validate response
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error in CV analysis: {str(e)}")
            raise

    def _build_analysis_prompt(self, role_data: Dict) -> str:
        """Build the analysis prompt from role data."""
        return f"""
        Analyze this CV for the position of {role_data['position']}.
        
        Required Skills:
        {role_data['requirements_must_have']}
        
        Preferred Skills:
        {role_data['requirements_nice_to_have']}
        
        Please provide:
        1. Candidate's full name
        2. Email address
        3. Educational qualifications
        4. Years of experience
        5. Key skills assessment
        6. Match percentage for required skills
        7. Match percentage for preferred skills
        8. Overall recommendation (ACCEPT/REJECT/REVIEW)
        9. Justification for recommendation
        
        Format the response as JSON.
        """

    async def _call_gemini_api(
        self, 
        base64_images: List[str], 
        prompt: str
    ) -> Dict:
        """Call the Gemini AI API with retries."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = await self.portkey_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                *[{
                                    "type": "image",
                                    "image": img
                                } for img in base64_images]
                            ]
                        }
                    ],
                    model="gemini-pro-vision",
                    max_tokens=2000,
                    temperature=0.1
                )
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay * (2 ** attempt))

    def _parse_response(self, response: Dict) -> Dict:
        """Parse and validate the API response."""
        try:
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse JSON response
            result = json.loads(content)
            
            # Validate required fields
            required_fields = [
                "full_name", "email", "education", 
                "experience", "skills", "required_skills_match",
                "preferred_skills_match", "recommendation",
                "justification"
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
                    
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to parse API response: {str(e)}") 