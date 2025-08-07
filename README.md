# Lightspeed Providers

Custom provider implementations for Llama Stack that extend the capabilities of AI applications with specialized safety and content filtering features.

## Overview

This repository contains custom providers for Llama Stack, including:

- **Question Validity Shield**: Ensures queries are related to OpenShift/Kubernetes topics
- **Redaction Shield**: Automatically detects and redacts sensitive information from user messages
- **Additional safety and content filtering providers**

## Features

### 🛡️ Redaction Shield
- **Pattern-based redaction**: YAML-configurable regex patterns for flexible content filtering
- **Automatic detection**: Detects credit card numbers, API keys, tokens, passwords, and custom patterns
- **Logging support**: Configurable logging of redaction events for monitoring
- **Framework integration**: Follows Llama Stack shield architecture patterns

### ✅ Question Validity Shield
- **Topic validation**: Ensures queries are related to specified topics (OpenShift/Kubernetes)
- **LLM-powered classification**: Uses AI to determine query relevance
- **Customizable responses**: Configure custom messages for invalid queries

## Quick Start

### Prerequisites

- Python 3.9+
- Llama Stack server
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lightspeed-core/lightspeed-providers.git
   cd lightspeed-providers
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Install Llama Stack** (if not already installed)
   ```bash
   pip install llama-stack
   ```

### Local Setup

#### Method 1: Using with Existing Llama Stack

1. **Copy providers to your Llama Stack configuration**
   ```bash
   # Copy providers.d directory to your project
   cp -r lightspeed-providers/resources/external_providers /path/to/your/project/providers.d
   ```

2. **Install the Python package**
   ```bash
   pip install lightspeed_stack_providers
   ```

3. **Configure your run.yaml** (see Configuration section below)

#### Method 2: Docker Setup

1. **Build with providers included**
   ```dockerfile
   FROM your-base-llama-stack-image
   
   # Copy providers
   COPY providers.d /opt/lightspeed-providers/
   
   # Install Python dependencies
   RUN pip install lightspeed_stack_providers
   ```

2. **Update your run.yaml configuration**

## Configuration

### 1. Register External Providers

Add to your `run.yaml` file:

```yaml
# External providers configuration
external_providers_dir: /path/to/providers.d

providers:
  safety:
    # Question Validity Shield
    - provider_id: lightspeed-question-validity
      provider_type: external::lightspeed_question_validity
      config:
        model_id: ${env.INFERENCE_MODEL}
        invalid_question_response: "Please ask questions related to OpenShift or Kubernetes."
    
    # Redaction Shield
    - provider_id: lightspeed-redaction
      provider_type: external::lightspeed_redaction
      config:
        config_file: "config/redaction_config.yaml"
        log_redactions: true

# Register shields
shields:
  - shield_id: question-validity-shield
    provider_id: lightspeed-question-validity
    provider_shield_id: lightspeed_question_validity-shield
    
  - shield_id: redaction-shield
    provider_id: lightspeed-redaction
    provider_shield_id: lightspeed-redaction-shield
```

### 2. Create Redaction Configuration

Create `config/redaction_config.yaml`:

```yaml
redaction_patterns:
  # Passwords and secrets
  - pattern: "(?i)(password|passwd)[\\s:=]+[^\\s]+"
    replacement: "[REDACTED_PASSWORD]"
  
  # API keys and tokens
  - pattern: "(?i)(api_key|secret)[\\s:=]+[a-zA-Z0-9\\-_]{16,}"
    replacement: "[REDACTED_SECRET]"
  
  # Container registries and images
  - pattern: "(?i)(registry|image):\\s*([\\w\\d\\.-]+)(:[\\w\\d\\.-]+)?"
    replacement: "\\1: [REDACTED_IMAGE]"
  
  # URLs and endpoints
  - pattern: "(?i)(url|endpoint):\\s*https?://[\\w\\.-]+(:\\d+)?(/[\\w\\d\\.-]*)*"
    replacement: "\\1: [REDACTED_URL]"
  
  # IP addresses
  - pattern: "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b"
    replacement: "[REDACTED_IP]"
  
  # SSH keys
  - pattern: "(?i)(ssh-rsa|ssh-ed25519)\\s+[A-Za-z0-9+/=]+"
    replacement: "[REDACTED_SSH_KEY]"
  
  # Credit card numbers
  - pattern: "\\b(?:\\d[ -]*?){13,16}\\b"
    replacement: "[REDACTED_CARD]"
```

### 3. Agent Configuration

Configure your agent to use the shields:

```yaml
agents:
  - agent_id: lightspeed-agent
    provider_id: meta-reference
    agent_config:
      model: ${env.INFERENCE_MODEL}
      instructions: "You are a helpful OpenShift assistant."
      input_shields:
        - redaction-shield
        - question-validity-shield
```

## Usage Examples

### Basic Query with Shields

```python
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:8321")

# Create agent with shields
agent = client.agents.create_agent({
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "instructions": "You are a helpful assistant.",
    "input_shields": ["redaction-shield", "question-validity-shield"]
})

# Send message - shields will automatically process
session = client.agents.create_agent_session(agent.agent_id, "test-session")
response = client.agents.create_agent_turn(
    agent_id=agent.agent_id,
    session_id=session.session_id,
    messages=[{"role": "user", "content": "My password is secret123. How do I deploy to OpenShift?"}]
)

# The password will be redacted automatically
```

### Testing Redaction

```bash
# Test the redaction shield
curl -X POST "http://localhost:8321/v1/safety/run_shield" \
  -H "Content-Type: application/json" \
  -d '{
    "shield_id": "redaction-shield",
    "messages": [
      {
        "role": "user", 
        "content": "My API key is abc123xyz and password is secret456"
      }
    ]
  }'
```

## Development

### Project Structure

```
lightspeed-providers/
├── lightspeed_stack_providers/
│   └── providers/
│       ├── inline/
│       │   └── safety/
│       │       ├── lightspeed_question_validity/
│       │       └── lightspeed_redaction/
│       └── remote/
├── resources/external_providers/
│   ├── lightspeed_question_validity.yaml
│   └── lightspeed_redaction.yaml
├── tests/
├── pyproject.toml
└── README.md
```

### Adding New Providers

1. **Create provider directory**
   ```bash
   mkdir -p lightspeed_stack_providers/providers/inline/safety/your_provider
   ```

2. **Implement provider files**
   - `__init__.py` - Provider registration
   - `config.py` - Configuration schema
   - `safety.py` - Shield implementation

3. **Add external provider definition**
   ```yaml
   # resources/external_providers/your_provider.yaml
   module: lightspeed_stack_providers.providers.inline.safety.your_provider
   config_class: lightspeed_stack_providers.providers.inline.safety.your_provider.config.YourProviderConfig
   pip_packages: ["lightspeed_stack_providers"]
   api_dependencies:
     - safety
   ```

### Running Tests

```bash
# Install test dependencies
pip install -e ".[test]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=lightspeed_stack_providers tests/
```

## Deployment

### Container Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM meta-llama/llama-stack:latest
   
   # Copy providers
   COPY providers.d /opt/lightspeed-providers/
   COPY config/ /app/config/
   
   # Install providers
   RUN pip install lightspeed_stack_providers
   
   # Copy configuration
   COPY run.yaml /app/run.yaml
   
   WORKDIR /app
   CMD ["llama", "stack", "run", "./run.yaml"]
   ```

2. **Build and run**
   ```bash
   docker build -t lightspeed-stack-with-providers .
   docker run -p 8321:8321 lightspeed-stack-with-providers
   ```

### Production Configuration

```yaml
# production-run.yaml
version: 1
external_providers_dir: /opt/lightspeed-providers

providers:
  safety:
    - provider_id: lightspeed-redaction
      provider_type: external::lightspeed_redaction
      config:
        config_file: "/app/config/redaction_config.yaml"
        log_redactions: true
        fail_on_pattern_error: false

shields:
  - shield_id: redaction-shield
    provider_id: lightspeed-redaction
    provider_shield_id: lightspeed-redaction-shield

# Configure logging
logging:
  level: INFO
  handlers:
    - type: file
      filename: /var/log/lightspeed-providers.log
```

## Troubleshooting

### Common Issues

1. **Provider not found**
   ```
   Error: Provider 'lightspeed-redaction' not found
   ```
   **Solution**: Ensure `external_providers_dir` points to the correct location and the YAML files are present.

2. **Configuration file not found**
   ```
   Error: Config file 'config/redaction_config.yaml' not found
   ```
   **Solution**: Create the configuration file or update the path in your run.yaml.

3. **Import errors**
   ```
   ModuleNotFoundError: No module named 'lightspeed_stack_providers'
   ```
   **Solution**: Install the package with `pip install lightspeed_stack_providers`.

### Debug Mode

Enable debug logging in your run.yaml:

```yaml
logging:
  level: DEBUG
  loggers:
    lightspeed_stack_providers: DEBUG
```

### Health Check

Test your providers:

```bash
# Check available shields
curl http://localhost:8321/v1/shields

# Test redaction shield
curl -X POST "http://localhost:8321/v1/safety/run_shield" \
  -H "Content-Type: application/json" \
  -d '{"shield_id": "redaction-shield", "messages": [{"role": "user", "content": "test message"}]}'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Documentation

- [Llama Stack Documentation](https://llama-stack.readthedocs.io/)
- [External Providers Guide](https://llama-stack.readthedocs.io/en/latest/providers/external.html)
- [Safety Providers](https://llama-stack.readthedocs.io/en/latest/providers/safety/index.html)
- [Building Applications](https://llama-stack.readthedocs.io/en/latest/building_applications/safety.html)

## Support

For questions and support:
- Create an issue in this repository
- Check the [Llama Stack documentation](https://llama-stack.readthedocs.io/)
- Join the community discussions
