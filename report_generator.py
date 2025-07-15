"""
HTML Report Generator for LLM Penetration Testing
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from config import TestResult, VulnerabilityResult, TestCase


class HTMLReportGenerator:
    """Generate HTML reports for vulnerability testing results"""
    
    def __init__(self, config):
        self.config = config
        
    async def generate_report(self, results: TestResult) -> str:
        """Generate HTML report and return file path"""
        report_dir = Path(self.config.output_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate report filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"llm_pentest_report_{timestamp}.html"
        report_path = report_dir / report_filename
        
        # Generate HTML content
        html_content = self._generate_html_content(results)
        
        # Write report to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_html_content(self, results: TestResult) -> str:
        """Generate complete HTML report content"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Penetration Testing Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header(results)}
        {self._generate_summary(results)}
        {self._generate_vulnerability_sections(results)}
        {self._generate_footer()}
    </div>
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
        """
        return html
    
    def _generate_header(self, results: TestResult) -> str:
        """Generate report header"""
        return f"""
        <header class="report-header">
            <h1>🔍 LLM Penetration Testing Report</h1>
            <div class="report-meta">
                <div class="meta-item">
                    <strong>Target Model:</strong> {results.target_model}
                </div>
                <div class="meta-item">
                    <strong>Tester Model:</strong> {results.tester_model}
                </div>
                <div class="meta-item">
                    <strong>Test Date:</strong> {results.start_time.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div class="meta-item">
                    <strong>Duration:</strong> {results.duration:.2f} seconds
                </div>
            </div>
        </header>
        """
    
    def _generate_summary(self, results: TestResult) -> str:
        """Generate executive summary"""
        total_tests = sum(v.total_tests for v in results.vulnerabilities)
        total_passed = sum(v.passed_tests for v in results.vulnerabilities)
        total_failed = sum(v.failed_tests for v in results.vulnerabilities)
        
        # Count vulnerabilities by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for vuln in results.vulnerabilities:
            if vuln.severity:
                severity_counts[vuln.severity] += 1
        
        # Determine overall risk level
        if severity_counts["HIGH"] > 0:
            risk_level = "HIGH"
            risk_class = "risk-high"
        elif severity_counts["MEDIUM"] > 0:
            risk_level = "MEDIUM"
            risk_class = "risk-medium"
        elif severity_counts["LOW"] > 0:
            risk_level = "LOW"
            risk_class = "risk-low"
        else:
            risk_level = "INFO"
            risk_class = "risk-info"
        
        return f"""
        <section class="summary">
            <h2>📊 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Overall Risk Level</h3>
                    <div class="risk-badge {risk_class}">{risk_level}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Tests</h3>
                    <div class="stat-number">{total_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>Passed Tests</h3>
                    <div class="stat-number passed">{total_passed}</div>
                </div>
                <div class="summary-card">
                    <h3>Failed Tests</h3>
                    <div class="stat-number failed">{total_failed}</div>
                </div>
            </div>
            
            <div class="severity-breakdown">
                <h3>Vulnerability Severity Breakdown</h3>
                <div class="severity-stats">
                    <div class="severity-item high">
                        <span class="severity-label">HIGH</span>
                        <span class="severity-count">{severity_counts['HIGH']}</span>
                    </div>
                    <div class="severity-item medium">
                        <span class="severity-label">MEDIUM</span>
                        <span class="severity-count">{severity_counts['MEDIUM']}</span>
                    </div>
                    <div class="severity-item low">
                        <span class="severity-label">LOW</span>
                        <span class="severity-count">{severity_counts['LOW']}</span>
                    </div>
                    <div class="severity-item info">
                        <span class="severity-label">INFO</span>
                        <span class="severity-count">{severity_counts['INFO']}</span>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _generate_vulnerability_sections(self, results: TestResult) -> str:
        """Generate sections for each vulnerability"""
        sections = []
        
        for vuln in results.vulnerabilities:
            sections.append(self._generate_vulnerability_section(vuln))
        
        return "\n".join(sections)
    
    def _generate_vulnerability_section(self, vuln: VulnerabilityResult) -> str:
        """Generate section for a single vulnerability"""
        severity_class = f"severity-{vuln.severity.lower()}" if vuln.severity else "severity-info"
        
        test_cases_html = self._generate_test_cases_html(vuln.test_cases)
        recommendations_html = self._generate_recommendations_html(vuln.recommendations)
        
        # Generate successful injections section
        successful_injections_html = ""
        if vuln.successful_injections:
            successful_injections_html = self._generate_successful_injections_html(vuln.successful_injections)
        
        # Generate most effective prompts section
        effective_prompts_html = ""
        if vuln.most_effective_prompts:
            effective_prompts_html = self._generate_effective_prompts_html(vuln.most_effective_prompts)
        
        return f"""
        <section class="vulnerability">
            <div class="vulnerability-header">
                <h2>{vuln.owasp_id}: {vuln.name}</h2>
                {f'<span class="severity-badge {severity_class}">{vuln.severity}</span>' if vuln.severity else ''}
            </div>
            
            <div class="vulnerability-description">
                <p>{vuln.description}</p>
            </div>
            
            <div class="vulnerability-stats">
                <div class="stat">
                    <span class="stat-label">Total Tests:</span>
                    <span class="stat-value">{vuln.total_tests}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Passed:</span>
                    <span class="stat-value passed">{vuln.passed_tests}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Failed:</span>
                    <span class="stat-value failed">{vuln.failed_tests}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Injection Success Rate:</span>
                    <span class="stat-value injection-rate">{vuln.injection_success_rate:.1f}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Successful Injections:</span>
                    <span class="stat-value injections">{len(vuln.successful_injections)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Execution Time:</span>
                    <span class="stat-value">{vuln.execution_time:.2f}s</span>
                </div>
            </div>
            
            {successful_injections_html}
            {effective_prompts_html}
            
            <div class="test-cases">
                <h3>Test Cases</h3>
                {test_cases_html}
            </div>
            
            {recommendations_html}
        </section>
        """
    
    def _generate_test_cases_html(self, test_cases) -> str:
        """Generate HTML for test cases"""
        html_parts = []
        
        for i, test_case in enumerate(test_cases):
            status_class = "passed" if test_case.passed else "failed"
            vulnerability_class = "vulnerable" if test_case.vulnerability_detected else ""
            severity_info = f"<span class='test-severity {test_case.severity.value.lower()}'>{test_case.severity.value}</span>" if test_case.severity else ""
            
            # Show vulnerability indicator
            vulnerability_indicator = ""
            if test_case.vulnerability_detected:
                vulnerability_indicator = f"<span class='vulnerability-indicator'>🚨 VULNERABLE</span>"
            
            html_parts.append(f"""
            <div class="test-case {status_class} {vulnerability_class}">
                <div class="test-case-header" onclick="toggleTestCase({i})">
                    <h4>{test_case.name}</h4>
                    <div class="test-case-status">
                        <span class="status-badge {status_class}">
                            {'✅ PASS' if test_case.passed else '❌ FAIL'}
                        </span>
                        {severity_info}
                        {vulnerability_indicator}
                    </div>
                </div>
                <div class="test-case-content" id="test-case-{i}">
                    <div class="test-case-details">
                        <div class="test-detail">
                            <strong>Description:</strong>
                            <p>{test_case.description}</p>
                        </div>
                        <div class="test-detail">
                            <strong>Input Prompt:</strong>
                            <pre class="code-block">{self._escape_html(test_case.input_prompt)}</pre>
                        </div>
                        <div class="test-detail">
                            <strong>Expected Behavior:</strong>
                            <p>{test_case.expected_behavior}</p>
                        </div>
                        <div class="test-detail">
                            <strong>Actual Response:</strong>
                            <pre class="code-block">{self._escape_html(test_case.actual_response)}</pre>
                        </div>
                        
                        {self._generate_tester_analysis_html(test_case)}
                        
                        <div class="test-detail">
                            <strong>Execution Time:</strong>
                            <span>{test_case.execution_time:.2f}s</span>
                        </div>
                        {f'<div class="test-detail"><strong>Error:</strong><p class="error">{test_case.error_message}</p></div>' if test_case.error_message else ''}
                    </div>
                </div>
            </div>
            """)
        
        return "\n".join(html_parts)
    
    def _generate_tester_analysis_html(self, test_case) -> str:
        """Generate HTML for tester model analysis"""
        if not test_case.tester_analysis_prompt and not test_case.tester_analysis_response:
            return ""
        
        vulnerability_status = ""
        if test_case.vulnerability_detected:
            vulnerability_status = """
            <div class="vulnerability-status detected">
                <h5>🚨 Vulnerability Detected</h5>
                <p><strong>Explanation:</strong> {}</p>
                <p><strong>Evidence:</strong> {}</p>
            </div>
            """.format(
                test_case.vulnerability_explanation,
                test_case.vulnerability_evidence
            )
        else:
            vulnerability_status = """
            <div class="vulnerability-status safe">
                <h5>✅ No Vulnerability Detected</h5>
                <p>The tester model determined this response was safe.</p>
            </div>
            """
        
        return f"""
        <div class="tester-analysis">
            <h5>🔍 Tester Model Analysis</h5>
            
            {vulnerability_status}
            
            <div class="analysis-details">
                <div class="analysis-prompt">
                    <strong>Analysis Prompt (sent to tester model):</strong>
                    <pre class="code-block analysis-prompt-content">{self._escape_html(test_case.tester_analysis_prompt[:500])}{'...' if len(test_case.tester_analysis_prompt) > 500 else ''}</pre>
                </div>
                <div class="analysis-response">
                    <strong>Tester Model Response:</strong>
                    <pre class="code-block analysis-response-content">{self._escape_html(test_case.tester_analysis_response)}</pre>
                </div>
            </div>
        </div>
        """
    
    def _generate_successful_injections_html(self, successful_injections) -> str:
        """Generate HTML for successful injections"""
        if not successful_injections:
            return ""
        
        injection_items = []
        for i, injection in enumerate(successful_injections[:10]):  # Show top 10
            severity_class = injection.severity.value.lower() if injection.severity else "info"
            injection_items.append(f"""
            <div class="injection-item">
                <div class="injection-header">
                    <h5>{injection.name}</h5>
                    <span class="injection-severity {severity_class}">{injection.severity.value if injection.severity else 'INFO'}</span>
                </div>
                <div class="injection-details">
                    <div class="injection-explanation">
                        <strong>Vulnerability:</strong> {injection.vulnerability_explanation}
                    </div>
                    <div class="injection-evidence">
                        <strong>Evidence:</strong> {injection.vulnerability_evidence}
                    </div>
                    <div class="injection-prompt">
                        <strong>Attack Prompt:</strong>
                        <pre class="code-block">{self._escape_html(injection.input_prompt[:200])}{'...' if len(injection.input_prompt) > 200 else ''}</pre>
                    </div>
                </div>
            </div>
            """)
        
        return f"""
        <div class="successful-injections">
            <h3>💥 Successful Injections ({len(successful_injections)} found)</h3>
            <div class="injection-grid">
                {''.join(injection_items)}
            </div>
        </div>
        """
    
    def _generate_effective_prompts_html(self, effective_prompts) -> str:
        """Generate HTML for most effective prompts"""
        if not effective_prompts:
            return ""
        
        prompt_items = []
        for i, prompt in enumerate(effective_prompts, 1):
            prompt_items.append(f"""
            <div class="effective-prompt">
                <div class="prompt-number">{i}</div>
                <div class="prompt-content">
                    <pre class="code-block">{self._escape_html(prompt)}</pre>
                </div>
            </div>
            """)
        
        return f"""
        <div class="effective-prompts">
            <h3>🔥 Most Effective Attack Prompts</h3>
            <div class="prompt-list">
                {''.join(prompt_items)}
            </div>
        </div>
        """
    
    def _generate_recommendations_html(self, recommendations) -> str:
        """Generate HTML for recommendations"""
        if not recommendations:
            return ""
        
        recommendations_list = "\n".join([f"<li>{rec}</li>" for rec in recommendations])
        
        return f"""
        <div class="recommendations">
            <h3>🔧 Recommendations</h3>
            <ul>
                {recommendations_list}
            </ul>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""
        <footer class="report-footer">
            <p>Generated by LLM Penetration Testing Tool v1.0.0</p>
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
        """
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#39;"))
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the report"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .report-header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        
        .report-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .meta-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
        }
        
        .summary {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .summary h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .summary-card h3 {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .risk-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .risk-high { background: #dc3545; color: white; }
        .risk-medium { background: #fd7e14; color: white; }
        .risk-low { background: #28a745; color: white; }
        .risk-info { background: #17a2b8; color: white; }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .stat-number.passed { color: #28a745; }
        .stat-number.failed { color: #dc3545; }
        
        .severity-breakdown {
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        
        .severity-stats {
            display: flex;
            gap: 20px;
            justify-content: space-around;
            margin-top: 15px;
        }
        
        .severity-item {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            min-width: 100px;
        }
        
        .severity-item.high { background: #f8d7da; }
        .severity-item.medium { background: #ffeaa7; }
        .severity-item.low { background: #d4edda; }
        .severity-item.info { background: #cce5ff; }
        
        .severity-label {
            display: block;
            font-size: 0.9em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .severity-count {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .vulnerability {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .vulnerability-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .vulnerability-header h2 {
            color: #2c3e50;
            font-size: 1.6em;
        }
        
        .severity-badge {
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .severity-high { background: #dc3545; color: white; }
        .severity-medium { background: #fd7e14; color: white; }
        .severity-low { background: #28a745; color: white; }
        .severity-info { background: #17a2b8; color: white; }
        
        .vulnerability-description {
            margin-bottom: 20px;
            color: #6c757d;
        }
        
        .vulnerability-stats {
            display: flex;
            gap: 30px;
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .stat {
            display: flex;
            flex-direction: column;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .stat-value.passed { color: #28a745; }
        .stat-value.failed { color: #dc3545; }
        
        .test-cases h3 {
            color: #2c3e50;
            margin-bottom: 20px;
        }
        
        .test-case {
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        
        .test-case.passed {
            border-left: 4px solid #28a745;
        }
        
        .test-case.failed {
            border-left: 4px solid #dc3545;
        }
        
        .test-case-header {
            padding: 15px;
            background: #f8f9fa;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .test-case-header:hover {
            background: #e9ecef;
        }
        
        .test-case-header h4 {
            color: #2c3e50;
            margin: 0;
        }
        
        .test-case-status {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .status-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-badge.passed {
            background: #28a745;
            color: white;
        }
        
        .status-badge.failed {
            background: #dc3545;
            color: white;
        }
        
        .test-severity {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            font-weight: bold;
        }
        
        .test-severity.high { background: #dc3545; color: white; }
        .test-severity.medium { background: #fd7e14; color: white; }
        .test-severity.low { background: #28a745; color: white; }
        .test-severity.info { background: #17a2b8; color: white; }
        
        .test-case-content {
            display: none;
            padding: 20px;
            background: white;
        }
        
        .test-case-content.active {
            display: block;
        }
        
        .test-detail {
            margin-bottom: 20px;
        }
        
        .test-detail strong {
            color: #2c3e50;
            display: block;
            margin-bottom: 8px;
        }
        
        .code-block {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .error {
            color: #dc3545;
            background: #f8d7da;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #f5c6cb;
        }
        
        .recommendations {
            margin-top: 25px;
            padding: 20px;
            background: #e8f5e8;
            border-radius: 8px;
            border: 1px solid #c3e6cb;
        }
        
        .recommendations h3 {
            color: #155724;
            margin-bottom: 15px;
        }
        
        .recommendations ul {
            list-style: none;
            padding: 0;
        }
        
        .recommendations li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }
        
        .recommendations li:before {
            content: '🔧';
            position: absolute;
            left: 0;
        }
        
        .report-footer {
            text-align: center;
            padding: 30px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
            margin-top: 30px;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .report-header {
                padding: 20px;
            }
            
            .report-header h1 {
                font-size: 2em;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .vulnerability-stats {
                flex-direction: column;
                gap: 10px;
            }
            
            .severity-stats {
                flex-direction: column;
                gap: 10px;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features"""
        return """
        function toggleTestCase(index) {
            const content = document.getElementById('test-case-' + index);
            content.classList.toggle('active');
        }
        
        // Add smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // Add collapsible functionality to all test cases
        document.addEventListener('DOMContentLoaded', function() {
            const headers = document.querySelectorAll('.test-case-header');
            headers.forEach(header => {
                header.addEventListener('click', function() {
                    const content = this.nextElementSibling;
                    content.classList.toggle('active');
                    
                    // Add visual feedback
                    if (content.classList.contains('active')) {
                        this.style.backgroundColor = '#e9ecef';
                    } else {
                        this.style.backgroundColor = '#f8f9fa';
                    }
                });
            });
        });
        """