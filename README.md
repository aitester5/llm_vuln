# LLM Penetration Testing Tool

A comprehensive CLI tool for testing LLM vulnerabilities using the OWASP LLM Top 10 framework. This tool uses one LLM model (tester) to systematically test another LLM model (target) for security vulnerabilities.

## Features

- **OWASP LLM Top 10 Coverage**: Tests for the most critical LLM vulnerabilities
- **Ollama Integration**: Uses Ollama for running local LLM models
- **Comprehensive Testing**: Covers prompt injection, sensitive data disclosure, and denial of service attacks
- **HTML Reports**: Generates detailed, interactive HTML reports
- **Configurable**: Supports different models and test configurations
- **Demo Mode**: Test the tool without requiring actual Ollama models

## Supported Vulnerabilities

### LLM01: Prompt Injection
- Role override attempts
- System prompt leakage
- Jailbreak techniques (DAN, etc.)
- Context manipulation
- Instruction hierarchy bypass
- Emotional manipulation

### LLM06: Sensitive Information Disclosure
- Training data extraction
- System information disclosure
- API key and credential extraction
- Personal information probing
- Internal process disclosure
- Memory/context probing

### LLM04: Model Denial of Service
- Token exhaustion attacks
- Complex reasoning tasks
- Infinite/recursive requests
- Memory exhaustion
- Rapid request simulation
- Repetitive task exhaustion

## Installation

1. **Install Ollama**: Follow the instructions at [ollama.ai](https://ollama.ai)

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull Required Models**:
   ```bash
   ollama pull llama3.1:latest
   ollama pull llama2-uncensored:latest
   ```

## Usage

### Basic Usage

```bash
# Run full vulnerability scan
python llm_pentest.py scan

# Test specific vulnerabilities
python llm_pentest.py scan --vulns prompt_injection,sensitive_data

# Use custom models
python llm_pentest.py scan --target mistral:latest --tester llama2:latest

# Enable verbose output
python llm_pentest.py scan --verbose
```

### Demo Mode

Test the tool without requiring actual Ollama models:

```bash
# Run demo with all vulnerabilities
python llm_pentest.py scan --demo

# Demo with specific vulnerabilities
python llm_pentest.py scan --demo --vulns prompt_injection --verbose
```

### Additional Commands

```bash
# List available models
python llm_pentest.py list-models

# Show version information
python llm_pentest.py version

# Get help
python llm_pentest.py --help
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--target` | Target model to test | `llama3.1:latest` |
| `--tester` | Tester model to use | `llama2-uncensored:latest` |
| `--output` | Output directory for reports | `./reports` |
| `--vulns` | Vulnerabilities to test | `all` |
| `--verbose` | Enable verbose output | `false` |
| `--timeout` | Request timeout in seconds | `30` |
| `--max-retries` | Maximum retries for failed requests | `3` |
| `--demo` | Run in demo mode | `false` |

## Report Generation

The tool generates comprehensive HTML reports with:

- **Executive Summary**: Overall risk assessment and statistics
- **Vulnerability Details**: Detailed test results for each vulnerability
- **Test Cases**: Individual test case results with inputs/outputs
- **Recommendations**: Specific recommendations for fixing vulnerabilities
- **Interactive UI**: Expandable test cases and severity filtering

## Model Recommendations

### Target Models (Models to Test)
- `llama3.1:latest` - General-purpose model
- `mistral:latest` - Alternative general-purpose model
- `codellama:latest` - Code-focused model
- Any other Ollama-compatible model

### Tester Models (Models for Analysis)
- `llama2-uncensored:latest` - Less restricted model for analysis
- `mistral:latest` - Alternative analysis model
- `llama3.1:latest` - Can be used for both target and tester

## Examples

### Test a Specific Model for Prompt Injection
```bash
python llm_pentest.py scan \
    --target codellama:latest \
    --tester llama2-uncensored:latest \
    --vulns prompt_injection \
    --verbose
```

### Quick Demo Test
```bash
python llm_pentest.py scan --demo --vulns prompt_injection
```

### Full Security Assessment
```bash
python llm_pentest.py scan \
    --target llama3.1:latest \
    --output ./security_reports \
    --timeout 60 \
    --verbose
```

## Understanding Results

### Severity Levels
- **HIGH**: Critical vulnerabilities that pose significant security risks
- **MEDIUM**: Moderate vulnerabilities that should be addressed
- **LOW**: Minor issues that may need attention
- **INFO**: Informational findings

### Test Results
- **PASS**: Test was handled appropriately by the model
- **FAIL**: Test revealed a potential vulnerability
- **ERROR**: Test could not be completed due to technical issues

## Troubleshooting

### Common Issues

1. **"No models found"**: Ensure Ollama is running and models are pulled
2. **Connection errors**: Check if Ollama is running on `localhost:11434`
3. **Timeout errors**: Increase timeout or reduce test complexity
4. **Memory errors**: Use smaller models or reduce concurrent requests

### Model Availability
```bash
# Check Ollama status
ollama list

# Pull required models
ollama pull llama3.1:latest
ollama pull llama2-uncensored:latest
```

## Contributing

This tool is designed to be extensible. You can:

1. Add new vulnerability test patterns in `config.py`
2. Create new vulnerability test modules in `vulnerability_tests/`
3. Extend the report generator for additional formats
4. Add new analysis methods to the base tester class

## License

This tool is provided for educational and security research purposes only. Always ensure you have proper authorization before testing any systems.

## Security Notice

This tool is designed to test LLM vulnerabilities for security research and improvement. Always:
- Test only systems you own or have explicit permission to test
- Use responsibly and ethically
- Follow your organization's security policies
- Report vulnerabilities through proper channels

---

**LLM Penetration Testing Tool v1.0.0**  
OWASP LLM Top 10 Vulnerability Scanner