"""
Bridge between vulnerability scanner and CodeAgent AI.
Converts scan reports into AI-reviewable format.
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import directly from codeagent instead of run.py to avoid command-line parsing
from codeagent.chat_chain import ChatChain
from camel.typing import ModelType


class AgentBridge:
    """Connects vulnerability scanner to CodeAgent AI for intelligent analysis."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the bridge.
        
        Args:
            config_dir: Path to CompanyConfig directory
        """
        if config_dir is None:
            # Default to project root CompanyConfig
            self.config_dir = Path(__file__).parent.parent.parent / "CompanyConfig" / "Default"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_path = self.config_dir / "ChatChainConfig.json"
        self.config_phase_path = self.config_dir / "PhaseConfig.json"
        self.config_role_path = self.config_dir / "RoleConfig.json"
    
    async def process_vulnerabilities(
        self, 
        job_id: str,
        report: Dict[str, Any],
        workspace_path: str
    ) -> Dict[str, Any]:
        """
        Process vulnerability report through AI agent.
        
        Args:
            job_id: Scanner job ID
            report: Vulnerability scan report
            workspace_path: Path to scanned code workspace
            
        Returns:
            Enhanced report with AI-generated fixes and recommendations
        """
        enhanced_issues = []
        
        # Process each file's issues
        for file_report in report.get('files', []):
            file_path = file_report['path']
            issues = file_report['issues']
            
            if not issues:
                continue
            
            # Group issues by severity for prioritization
            critical_high = [i for i in issues if i['severity'] in ['critical', 'high']]
            
            if critical_high:
                # Get AI review for critical/high issues
                ai_analysis = await self._analyze_with_ai(
                    job_id=job_id,
                    file_path=file_path,
                    issues=critical_high,
                    workspace_path=workspace_path
                )
                
                enhanced_issues.append({
                    'file': file_path,
                    'original_issues': critical_high,
                    'ai_analysis': ai_analysis
                })
        
        return {
            'job_id': job_id,
            'enhanced_issues': enhanced_issues,
            'summary': self._create_enhanced_summary(enhanced_issues)
        }
    
    async def _analyze_with_ai(
        self,
        job_id: str,
        file_path: str,
        issues: List[Dict],
        workspace_path: str
    ) -> Dict[str, Any]:
        """
        Analyze issues using CodeAgent AI.
        
        Args:
            job_id: Job identifier
            file_path: Path to file with issues
            issues: List of vulnerability issues
            workspace_path: Root workspace path
            
        Returns:
            AI analysis with fixes and recommendations
        """
        try:
            # Read the vulnerable file
            full_path = os.path.join(workspace_path, file_path)
            if not os.path.exists(full_path):
                return {'error': 'File not found', 'file': file_path}
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            
            # Create review prompt
            review_prompt = self._create_review_prompt(file_path, issues, file_content)
            
            # Create temporary commit files (CodeAgent expects this format)
            temp_dir = tempfile.mkdtemp(prefix=f'ai_review_{job_id}_')
            commit_file = os.path.join(temp_dir, 'commit.txt')
            context_file = os.path.join(temp_dir, 'context.txt')
            
            # Write vulnerable code as "commit"
            with open(commit_file, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # Write issues as context
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(issues, indent=2))
            
            # Initialize ChatChain for AI review
            chat_chain = ChatChain(
                config_path=str(self.config_path),
                config_phase_path=str(self.config_phase_path),
                config_role_path=str(self.config_role_path),
                task_prompt=review_prompt,
                project_name=f"vuln_fix_{job_id}",
                org_name="security_scan",
                model_type=ModelType.GPT_4,
                code_path=None
            )
            
            # Execute AI review
            chat_chain.pre_processing()
            chat_chain.make_recruitment()
            chat_chain.execute_chain()
            chat_chain.post_processing()
            
            # Extract AI recommendations from generated output
            warehouse_path = Path(__file__).parent.parent.parent / "WareHouse" / f"vuln_fix_{job_id}"
            
            recommendations = self._extract_recommendations(warehouse_path)
            
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return {
                'file': file_path,
                'analysis': recommendations.get('analysis', ''),
                'suggested_fix': recommendations.get('fix', ''),
                'explanation': recommendations.get('explanation', ''),
                'security_impact': recommendations.get('security_impact', '')
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'file': file_path,
                'issues': issues
            }
    
    def _create_review_prompt(
        self, 
        file_path: str, 
        issues: List[Dict], 
        file_content: str
    ) -> str:
        """Create AI review prompt from vulnerability issues."""
        
        prompt = f"""Security Vulnerability Analysis Request

File: {file_path}

Detected Vulnerabilities:
"""
        
        for i, issue in enumerate(issues, 1):
            prompt += f"""
{i}. {issue['severity'].upper()} - {issue['type']}
   Line: {issue.get('line', 'N/A')}
   Tool: {issue['tool']}
   Message: {issue['message']}
   Suggestion: {issue.get('suggestion', 'N/A')}
"""
        
        prompt += f"""

File Content:
```
{file_content}
```

Please provide:
1. Detailed security analysis of these vulnerabilities
2. Root cause explanation
3. Secure code revision to fix ALL issues
4. Best practices to prevent similar issues
5. Security impact assessment

Focus on providing actionable, production-ready fixes.
"""
        
        return prompt
    
    def _extract_recommendations(self, warehouse_path: Path) -> Dict[str, str]:
        """Extract AI recommendations from ChatChain output."""
        
        recommendations = {
            'analysis': '',
            'fix': '',
            'explanation': '',
            'security_impact': ''
        }
        
        try:
            # Look for generated manual.md or similar output
            manual_file = warehouse_path / 'manual.md'
            if manual_file.exists():
                with open(manual_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse sections (customize based on your output format)
                if 'Security Analysis:' in content:
                    sections = content.split('Security Analysis:')
                    if len(sections) > 1:
                        recommendations['analysis'] = sections[1].split('\n\n')[0].strip()
                
                if 'Code Revision:' in content or 'revised code:' in content:
                    # Extract code blocks
                    import re
                    code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
                    if code_blocks:
                        recommendations['fix'] = code_blocks[0].strip()
                
                recommendations['explanation'] = content
            
        except Exception as e:
            recommendations['error'] = str(e)
        
        return recommendations
    
    def _create_enhanced_summary(self, enhanced_issues: List[Dict]) -> Dict[str, Any]:
        """Create summary of AI-enhanced analysis."""
        
        total_files = len(enhanced_issues)
        total_issues = sum(len(ei['original_issues']) for ei in enhanced_issues)
        
        fixes_generated = sum(
            1 for ei in enhanced_issues 
            if ei.get('ai_analysis', {}).get('suggested_fix')
        )
        
        return {
            'files_analyzed': total_files,
            'issues_analyzed': total_issues,
            'ai_fixes_generated': fixes_generated,
            'status': 'complete'
        }
