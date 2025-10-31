"""
Simple Direct OpenAI API analyzer for security vulnerabilities.
This bypasses CAMEL framework for immediate demo functionality.
"""

import os
import json
import openai
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SimpleAIAnalyzer:
    """Direct OpenAI API analyzer for security code review."""
    
    def __init__(self):
        """Initialize with OpenAI API key from environment."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Configure for old OpenAI library (v0.28.0)
        openai.api_key = self.api_key
        self.model = os.getenv('AI_MODEL', 'gpt-4o-mini')
        
        # Convert model name format
        model_map = {
            'GPT_4O_MINI': 'gpt-4o-mini',
            'GPT_4O': 'gpt-4o',
            'GPT_4': 'gpt-4',
            'GPT_3_5_TURBO': 'gpt-3.5-turbo'
        }
        self.model = model_map.get(self.model, 'gpt-4o-mini')
        
    def analyze_vulnerabilities(
        self,
        file_path: str,
        file_content: str,
        issues: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze security vulnerabilities using direct OpenAI API call.
        
        Args:
            file_path: Path to the vulnerable file
            file_content: Content of the file
            issues: List of detected vulnerabilities
            
        Returns:
            Dictionary with fixes and recommendations
        """
        try:
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(file_path, file_content, issues)
            
            logger.info(f"Calling OpenAI API ({self.model}) for {file_path}")
            
            # Call OpenAI API (v0.28.0 style)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert security code reviewer. Analyze vulnerabilities and provide secure fixes in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Extract response
            ai_response = response['choices'][0]['message']['content']
            
            logger.info(f"Received OpenAI response for {file_path}")
            
            # Parse the response
            return self._parse_ai_response(ai_response, file_path, issues)
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}", exc_info=True)
            return {
                'error': str(e),
                'file': file_path,
                'fixes': [],
                'recommendations': []
            }
    
    def _create_analysis_prompt(
        self,
        file_path: str,
        file_content: str,
        issues: List[Dict]
    ) -> str:
        """Create a structured prompt for AI analysis with severity-based prioritization."""
        
        # Sort issues by severity for emphasis
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_issues = sorted(issues, key=lambda x: severity_order.get(x.get('severity', 'low'), 4))
        
        # Group by severity for better presentation
        issues_by_severity = {}
        for issue in sorted_issues:
            severity = issue.get('severity', 'low')
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        # Build issues text with severity grouping
        issues_text_parts = []
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in issues_by_severity:
                severity_upper = severity.upper()
                issues_text_parts.append(f"\n### {severity_upper} SEVERITY ({len(issues_by_severity[severity])} issues):")
                for i, issue in enumerate(issues_by_severity[severity], 1):
                    issues_text_parts.append(
                        f"{i}. **{issue['type']}** (Line {issue.get('line', 'N/A')})\n"
                        f"   - Tool: {issue['tool']}\n"
                        f"   - Message: {issue['message']}\n"
                    )
        
        issues_text = "\n".join(issues_text_parts)
        
        prompt = f"""# Security Code Review Task

## File: `{file_path}`

## Detected Vulnerabilities (Prioritized by Severity):
{issues_text}

**IMPORTANT**: Address CRITICAL and HIGH severity issues first, then MEDIUM and LOW.

## Source Code:
```
{file_content}
```

## Your Task:
Analyze EACH vulnerability thoroughly and provide:
1. **Root Cause**: Why the vulnerability exists
2. **Security Impact**: Potential damage if exploited (especially for CRITICAL/HIGH)
3. **Fixed Code**: Complete, secure code with inline comments
4. **Explanation**: Why your fix works and how it mitigates the risk
5. **Best Practices**: Recommendations to prevent similar issues

## Response Format (JSON):
Return your response as a JSON object with this structure:
```json
{{
  "fixes": [
    {{
      "vulnerability_type": "string",
      "line_number": number,
      "severity": "critical|high|medium|low",
      "root_cause": "string",
      "security_impact": "string",
      "original_code": "string",
      "fixed_code": "string",
      "explanation": "string"
    }}
  ],
  "recommendations": [
    {{
      "title": "string",
      "description": "string",
      "priority": "high|medium|low"
    }}
  ]
}}
```

Provide practical, production-ready fixes. Be specific and actionable. Prioritize CRITICAL and HIGH severity issues."""
        
        return prompt
    
    def _parse_ai_response(
        self,
        ai_response: str,
        file_path: str,
        issues: List[Dict]
    ) -> Dict[str, Any]:
        """Parse AI response and structure it properly."""
        
        try:
            # Try to extract JSON from the response
            # AI might wrap it in markdown code blocks
            if '```json' in ai_response:
                start = ai_response.find('```json') + 7
                end = ai_response.find('```', start)
                json_str = ai_response[start:end].strip()
            elif '```' in ai_response:
                start = ai_response.find('```') + 3
                end = ai_response.find('```', start)
                json_str = ai_response[start:end].strip()
            else:
                json_str = ai_response.strip()
            
            # Parse JSON
            parsed = json.loads(json_str)
            
            # Sort fixes by severity (critical > high > medium > low)
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            fixes = sorted(
                parsed.get('fixes', []),
                key=lambda x: severity_order.get(x.get('severity', 'low'), 4)
            )
            
            return {
                'file': file_path,
                'fixes': fixes,
                'recommendations': parsed.get('recommendations', []),
                'raw_response': ai_response
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            
            # Fallback: Create structured response from text
            return {
                'file': file_path,
                'fixes': self._extract_fixes_from_text(ai_response, issues),
                'recommendations': self._extract_recommendations_from_text(ai_response),
                'raw_response': ai_response
            }
    
    def _extract_fixes_from_text(
        self,
        text: str,
        issues: List[Dict]
    ) -> List[Dict]:
        """Extract fixes from unstructured AI response."""
        
        fixes = []
        
        # Simple heuristic: create one fix per issue
        for issue in issues:
            fix = {
                'vulnerability_type': issue['type'],
                'line_number': issue.get('line', 0),
                'severity': issue['severity'],
                'root_cause': 'Security vulnerability detected',
                'security_impact': f"{issue['severity']} severity issue",
                'original_code': issue.get('code_snippet', 'N/A'),
                'fixed_code': 'See AI analysis for fix details',
                'explanation': text[:500]  # First 500 chars as explanation
            }
            fixes.append(fix)
        
        return fixes
    
    def _extract_recommendations_from_text(self, text: str) -> List[Dict]:
        """Extract recommendations from unstructured AI response."""
        
        recommendations = [
            {
                'title': 'Security Code Review',
                'description': text[:300],  # First 300 chars
                'priority': 'high'
            }
        ]
        
        return recommendations
