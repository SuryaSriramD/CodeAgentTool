"""
Multi-Agent Bridge for Deep Vulnerability Analysis.
Connects the scanner to the CodeAgent multi-agent system for enhanced analysis.
"""

import os
import json
import shutil
import tempfile
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from camel.typing import ModelType
from codeagent.chat_chain import ChatChain


logger = logging.getLogger(__name__)


class CamelBridge:
    """
    Orchestrates the multi-agent CodeAgent system for deep vulnerability analysis.
    
    This bridge transforms vulnerability scan results into tasks for a team of AI agents
    (Security Tester, Programmer, Code Reviewer) that collaborate to provide:
    - Root cause analysis
    - Security impact assessment  
    - Concrete code fixes
    - Best practice recommendations
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        model_type: ModelType = ModelType.GPT_4
    ):
        """
        Initialize the multi-agent bridge.
        
        Args:
            config_dir: Path to CompanyConfig directory (optional)
            model_type: LLM model to use for agents
        """
        # Set up config paths
        if config_dir is None:
            # Try to find CompanyConfig in parent directory
            scanner_dir = Path(__file__).parent.parent
            project_root = scanner_dir.parent
            config_dir_path = project_root / "CompanyConfig" / "Default"
            
            # If not found, use a minimal embedded config
            if not config_dir_path.exists():
                config_dir_path = scanner_dir / "CompanyConfig" / "Default"
            
            self.config_dir = config_dir_path
        else:
            self.config_dir = Path(config_dir)
        
        self.config_path = self.config_dir / "ChatChainConfig.json"
        self.config_phase_path = self.config_dir / "PhaseConfig.json"
        self.config_role_path = self.config_dir / "RoleConfig.json"
        
        # Create minimal config if needed
        if not self.config_path.exists():
            self._create_minimal_config()
        
        self.model_type = model_type
        
        logger.info(f"CamelBridge initialized with model {model_type.value}")
    
    async def process_vulnerabilities(
        self,
        job_id: str,
        report: Dict[str, Any],
        workspace_path: str
    ) -> Dict[str, Any]:
        """
        Process vulnerability report through multi-agent system.
        
        This is the main entry point that orchestrates the entire analysis process.
        
        Args:
            job_id: Scanner job ID
            report: Vulnerability scan report
            workspace_path: Path to scanned code workspace
            
        Returns:
            Enhanced report with AI-generated analyses and fixes
        """
        logger.info(f"Starting multi-agent analysis for job {job_id}")
        
        enhanced_issues = []
        
        # Process each file's issues
        for file_report in report.get('files', []):
            file_path = file_report['path']
            issues = file_report['issues']
            
            if not issues:
                continue
            
            # Focus on critical and high severity issues
            critical_high = [i for i in issues if i['severity'] in ['critical', 'high']]
            
            if critical_high:
                logger.info(f"Analyzing {len(critical_high)} critical/high issues in {file_path}")
                
                # Run multi-agent analysis
                ai_analysis = await self._analyze_with_agents(
                    job_id=job_id,
                    file_path=file_path,
                    issues=critical_high,
                    workspace_path=workspace_path
                )
                
                enhanced_issues.append({
                    'file': file_path,
                    'issues_analyzed': len(critical_high),
                    'original_issues': critical_high,
                    'ai_analysis': ai_analysis
                })
        
        # Generate summary
        summary = self._create_enhanced_summary(enhanced_issues, report)
        
        logger.info(f"Multi-agent analysis complete for job {job_id}: {len(enhanced_issues)} files analyzed")
        
        return {
            'job_id': job_id,
            'status': 'complete',
            'enhanced_issues': enhanced_issues,
            'summary': summary,
            'meta': {
                'ai_model_used': self.model_type.value,
                'min_severity_analyzed': 'high',
                'generated_at': report.get('meta', {}).get('generated_at')
            }
        }
    
    async def _analyze_with_agents(
        self,
        job_id: str,
        file_path: str,
        issues: List[Dict],
        workspace_path: str
    ) -> Dict[str, Any]:
        """
        Analyze vulnerabilities using the multi-agent CodeAgent system.
        
        This method:
        1. Reads the vulnerable file
        2. Creates a security review task prompt
        3. Initializes the ChatChain with AI agents
        4. Runs the agent conversation
        5. Extracts and structures the recommendations
        
        Args:
            job_id: Job identifier
            file_path: Path to file with issues
            issues: List of vulnerability issues
            workspace_path: Root workspace path
            
        Returns:
            Structured AI analysis with fixes
        """
        try:
            # Read the vulnerable file
            full_path = os.path.join(workspace_path, file_path)
            if not os.path.exists(full_path):
                return {
                    'error': f'File not found: {file_path}',
                    'file': file_path
                }
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            
            # Create the task prompt for the AI agents
            task_prompt = self._create_security_review_prompt(
                file_path=file_path,
                issues=issues,
                file_content=file_content
            )
            
            # Create project name for this analysis
            project_name = f"security_fix_{job_id}_{Path(file_path).stem}"
            
            logger.info(f"Initializing ChatChain for {file_path}")
            
            # Initialize the multi-agent system
            chat_chain = ChatChain(
                config_path=str(self.config_path),
                config_phase_path=str(self.config_phase_path),
                config_role_path=str(self.config_role_path),
                task_prompt=task_prompt,
                project_name=project_name,
                org_name="security_scan",
                model_type=self.model_type,
                code_path=workspace_path
            )
            
            # Execute the multi-agent review process
            logger.info(f"Running multi-agent analysis for {file_path}")
            chat_chain.pre_processing()
            chat_chain.make_recruitment()
            chat_chain.execute_chain()
            chat_chain.post_processing()
            
            # Extract recommendations from the generated output
            warehouse_path = Path(__file__).parent.parent.parent / "WareHouse" / f"{project_name}_security_scan_{chat_chain.start_time}"
            
            recommendations = self._extract_agent_recommendations(warehouse_path)
            
            logger.info(f"Successfully completed multi-agent analysis for {file_path}")
            
            return {
                'file': file_path,
                'analysis': recommendations.get('analysis', ''),
                'suggested_fix': recommendations.get('fix', ''),
                'explanation': recommendations.get('explanation', ''),
                'security_impact': recommendations.get('security_impact', ''),
                'best_practices': recommendations.get('best_practices', [])
            }
            
        except Exception as e:
            logger.error(f"Multi-agent analysis failed for {file_path}: {e}", exc_info=True)
            return {
                'error': str(e),
                'file': file_path,
                'issues': issues
            }
    
    def _create_security_review_prompt(
        self,
        file_path: str,
        issues: List[Dict],
        file_content: str
    ) -> str:
        """
        Create a comprehensive security review prompt for the AI agents.
        
        This prompt guides the multi-agent system to focus on:
        - Understanding the vulnerabilities
        - Analyzing root causes
        - Proposing secure fixes
        - Providing best practices
        """
        prompt = f"""# Security Vulnerability Review Task

## File Under Review
**Path**: `{file_path}`

## Detected Security Issues

"""
        
        for i, issue in enumerate(issues, 1):
            prompt += f"""### Issue #{i}: {issue['type']}
- **Severity**: {issue['severity'].upper()}
- **Line**: {issue.get('line', 'N/A')}
- **Tool**: {issue['tool']}
- **Description**: {issue['message']}
- **Initial Suggestion**: {issue.get('suggestion', 'N/A')}

"""
        
        prompt += f"""## Source Code

```
{file_content}
```

## Your Mission

As a security team, you need to:

1. **Root Cause Analysis**: Explain why each vulnerability exists and how it could be exploited
2. **Security Impact**: Assess the potential damage if these vulnerabilities are exploited
3. **Code Fix**: Provide complete, production-ready code that fixes ALL the issues
4. **Explanation**: Clearly explain what changes you made and why they work
5. **Best Practices**: List concrete best practices to prevent similar issues in the future

## Requirements

- The fixed code MUST be syntactically correct and executable
- The fix should address the root cause, not just symptoms
- Include inline comments explaining security-critical parts
- Focus on practical, actionable recommendations
- Consider the broader security context of the application

Please work together as a team to provide a comprehensive security review.
"""
        
        return prompt
    
    def _extract_agent_recommendations(self, warehouse_path: Path) -> Dict[str, Any]:
        """
        Extract structured recommendations from the multi-agent output.
        
        The ChatChain typically generates a manual.md file with the analysis.
        This method parses that output into a structured format.
        """
        recommendations = {
            'analysis': '',
            'fix': '',
            'explanation': '',
            'security_impact': '',
            'best_practices': []
        }
        
        try:
            # Look for the generated manual/report
            manual_file = warehouse_path / 'manual.md'
            
            if not manual_file.exists():
                # Try alternative locations
                for potential_file in warehouse_path.glob('*.md'):
                    manual_file = potential_file
                    break
            
            if manual_file and manual_file.exists():
                with open(manual_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the content into sections
                recommendations = self._parse_agent_output(content)
            else:
                logger.warning(f"No manual.md found in {warehouse_path}")
                recommendations['explanation'] = "Analysis completed but output file not found"
            
        except Exception as e:
            logger.error(f"Failed to extract recommendations from {warehouse_path}: {e}")
            recommendations['error'] = str(e)
        
        return recommendations
    
    def _parse_agent_output(self, content: str) -> Dict[str, Any]:
        """
        Parse the markdown output from agents into structured data.
        
        This method looks for key sections and extracts:
        - Security analysis
        - Code fixes
        - Explanations
        - Best practices
        """
        import re
        
        result = {
            'analysis': '',
            'fix': '',
            'explanation': content,  # Full content as fallback
            'security_impact': '',
            'best_practices': []
        }
        
        # Extract code blocks (likely the fixed code)
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        if code_blocks:
            result['fix'] = code_blocks[0].strip()
        
        # Extract security analysis section
        analysis_match = re.search(
            r'(?:Security Analysis|Root Cause|Vulnerability Analysis)[\s:]*\n+(.*?)(?=\n#{1,3}|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if analysis_match:
            result['analysis'] = analysis_match.group(1).strip()
        
        # Extract security impact
        impact_match = re.search(
            r'(?:Security Impact|Impact Assessment|Risk)[\s:]*\n+(.*?)(?=\n#{1,3}|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if impact_match:
            result['security_impact'] = impact_match.group(1).strip()
        
        # Extract best practices (look for lists)
        practices_match = re.search(
            r'(?:Best Practices?|Recommendations?|Prevention)[\s:]*\n+((?:[-*]\s+.+\n?)+)',
            content,
            re.IGNORECASE
        )
        if practices_match:
            practices_text = practices_match.group(1)
            result['best_practices'] = [
                line.strip('- *').strip()
                for line in practices_text.split('\n')
                if line.strip().startswith(('-', '*'))
            ]
        
        return result
    
    def _create_enhanced_summary(
        self,
        enhanced_issues: List[Dict],
        original_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a comprehensive summary of the multi-agent analysis."""
        
        # Get original summary
        original_summary = original_report.get('summary', {})
        
        total_files_scanned = len(original_report.get('files', []))
        files_with_issues = len([f for f in original_report.get('files', []) if f.get('issues')])
        files_analyzed = len(enhanced_issues)
        
        total_issues_analyzed = sum(
            ei.get('issues_analyzed', 0)
            for ei in enhanced_issues
        )
        
        fixes_generated = sum(
            1 for ei in enhanced_issues
            if ei.get('ai_analysis', {}).get('suggested_fix')
        )
        
        return {
            'total_files_scanned': total_files_scanned,
            'files_with_issues': files_with_issues,
            'files_analyzed_by_ai': files_analyzed,
            'issues_analyzed_by_ai': total_issues_analyzed,
            'ai_fixes_generated': fixes_generated,
            'severity_breakdown': original_summary,
            'status': 'complete'
        }
    
    def _create_minimal_config(self):
        """
        Create minimal configuration files if CompanyConfig doesn't exist.
        
        This provides fallback configs for the multi-agent system.
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create minimal ChatChainConfig.json if needed
        if not self.config_path.exists():
            minimal_chain_config = {
                "chain": [
                    {
                        "phase": "CodeSecurityAnalyst",
                        "phaseType": "SimplePhase",
                        "max_turn_step": 3,
                        "need_reflect": "False"
                    },
                    {
                        "phase": "CodeReviewModification",
                        "phaseType": "SimplePhase",
                        "max_turn_step": 3,
                        "need_reflect": "False"
                    }
                ],
                "recruitments": ["Security Tester", "Programmer", "Code Reviewer"],
                "clear_structure": "True",
                "gui_design": "False",
                "git_management": "False",
                "incremental_develop": "False",
                "self_improve": "False"
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(minimal_chain_config, f, indent=2)
            
            logger.info(f"Created minimal config at {self.config_path}")
        
        # Create minimal PhaseConfig.json if needed
        if not self.config_phase_path.exists():
            minimal_phase_config = {
                "CodeSecurityAnalyst": {
                    "assistant_role_name": "Programmer",
                    "user_role_name": "Security Tester",
                    "phase_prompt": [
                        "Analyze the detected security vulnerabilities and explain their impact"
                    ]
                },
                "CodeReviewModification": {
                    "assistant_role_name": "Code Reviewer",
                    "user_role_name": "Programmer",
                    "phase_prompt": [
                        "Review the code and provide secure fixes for all vulnerabilities"
                    ]
                }
            }
            
            with open(self.config_phase_path, 'w') as f:
                json.dump(minimal_phase_config, f, indent=2)
            
            logger.info(f"Created minimal phase config at {self.config_phase_path}")
        
        # Create minimal RoleConfig.json if needed
        if not self.config_role_path.exists():
            minimal_role_config = {
                "Chief Executive Officer": [
                    "You are the project coordinator for security code review.",
                    "Orchestrate the analysis process between security testers and programmers.",
                    "Ensure comprehensive vulnerability remediation and quality standards."
                ],
                "Counselor": [
                    "You are an expert advisor who provides feedback and recommendations.",
                    "Review the work done by other roles and suggest improvements.",
                    "Ensure best practices are followed and quality is maintained."
                ],
                "Security Tester": [
                    "You are a security expert who analyzes code vulnerabilities.",
                    "Identify security risks and explain how they can be exploited.",
                    "Provide clear, actionable security recommendations."
                ],
                "Programmer": [
                    "You are an experienced programmer who writes secure code.",
                    "Fix security vulnerabilities while maintaining functionality.",
                    "Write clean, well-documented, production-ready code."
                ],
                "Code Reviewer": [
                    "You are a senior code reviewer focused on security.",
                    "Review fixes to ensure they address the root cause.",
                    "Verify that the code follows security best practices."
                ]
            }
            
            with open(self.config_role_path, 'w') as f:
                json.dump(minimal_role_config, f, indent=2)
            
            logger.info(f"Created minimal role config at {self.config_role_path}")
