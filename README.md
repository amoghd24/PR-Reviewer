# MCP Enterprise PR Reviewer

An enterprise-grade AI-powered Pull Request reviewer built with Model Context Protocol (MCP), integrating GitHub, Slack, and Asana for comprehensive developer workflow automation.

## 🏗️ Architecture Overview

This system demonstrates production-ready MCP architecture with:
- **Modular MCP Servers**: Individual servers for GitHub, Slack, Asana, and Agent Scope
- **Global Server Registry**: Centralized tool discovery and routing
- **Custom MCP Host**: FastAPI application orchestrating the entire workflow
- **Enterprise Observability**: Comprehensive tracing with Opik
- **Production Security**: OAuth 2.0, rate limiting, and access control

## 🎯 What This System Does

1. **Listens** for GitHub PR events via webhooks
2. **Analyzes** PR content and linked Asana tasks
3. **Generates** intelligent reviews using Gemini LLM
4. **Delivers** actionable feedback directly to Slack channels
5. **Tracks** everything with full observability and prompt versioning

## 📋 Development Roadmap

This project follows a structured 18-PR development roadmap across 5 phases:

### Phase 1: Foundation (PR-1 to PR-4)
Individual MCP servers using FastMCP

### Phase 2: Integration (PR-5 to PR-6)  
Global server and tool registry

### Phase 3: Host Implementation (PR-7 to PR-10)
FastAPI wrapper client and workflow orchestration

### Phase 4: Observability (PR-11 to PR-13)
Opik integration and production monitoring

### Phase 5: Security (PR-14 to PR-18)
OAuth 2.0, access control, and compliance

👉 **See [ROADMAP.md](./ROADMAP.md) for detailed implementation plan**

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- GitHub account with repository access
- Slack workspace with admin permissions
- Asana workspace access
- Opik account for observability

### Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd pr-reviewer

# Create virtual environment
python -m venv pr-reviewer-env
source pr-reviewer-env/bin/activate  # On Windows: pr-reviewer-env\Scripts\activate

# Install dependencies (when available)
pip install -r requirements.txt
```

### Configuration
Create `.env` file with required credentials:
```env
# GitHub Integration
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_ACCESS_TOKEN=your_github_access_token

# Slack Integration  
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=your_target_channel_id

# Asana Integration
ASANA_PERSONAL_ACCESS_TOKEN=your_asana_token
ASANA_WORKSPACE_ID=your_workspace_id
ASANA_PROJECT_GID=your_project_id

# LLM & Observability
GEMINI_API_KEY=your_gemini_api_key
OPIK_API_TOKEN=your_opik_api_token
OPIK_PROJECT=pr_reviewer_project
```

## 🏛️ Project Structure

```
pr-reviewer/
├── ROADMAP.md                 # Detailed development roadmap
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── servers/                  # Individual MCP servers
│   ├── asana_mcp/           # Asana integration server
│   ├── slack_mcp/           # Slack messaging server  
│   ├── agent_scope_mcp/     # Prompt management server
│   └── github_mcp/          # GitHub proxy server
├── global_server/           # MCP Global Server & Registry
│   ├── registry.py          # Tool registry implementation
│   └── server.py           # Global server main
├── host/                   # MCP Host (FastAPI application)
│   ├── webhook.py          # GitHub webhook handler
│   ├── mcp_client.py       # MCP client implementation
│   └── main.py            # FastAPI application
├── clients/                # API clients (e.g., Asana, Slack)
│   ├── asana.py            # Asana API client
│   └── slack.py            # Slack API client
├── observability/          # Opik integration
│   ├── tracing.py         # Trace configuration
│   └── metrics.py         # Custom metrics
├── security/              # Security implementations
│   ├── oauth.py          # OAuth 2.0 flows
│   ├── auth.py           # Authentication middleware
│   └── permissions.py    # Access control
└── tests/                # Comprehensive test suite
    ├── unit/            # Unit tests for each component
    ├── integration/     # Integration tests
    └── e2e/            # End-to-end workflow tests
```

## 🔧 Development Workflow

### For Contributors
1. **Pick a PR**: Choose the next PR from the roadmap
2. **Create Branch**: `git checkout -b feature/pr-{number}-{description}`
3. **Implement**: Follow the PR specification in ROADMAP.md
4. **Test**: Run comprehensive tests for your component
5. **Document**: Update relevant documentation
6. **Submit**: Create PR with detailed description and testing evidence

### For Each PR Implementation
- Read the ROADMAP.md specification carefully
- Understand the "Future Considerations" for forward-compatible design
- Implement with production quality (error handling, logging, validation)
- Write comprehensive tests
- Update documentation

## 🎓 Learning Outcomes

By following this roadmap, you'll learn:
- **MCP Architecture**: How to design scalable, modular AI systems
- **Enterprise Integration**: Real-world API integration patterns
- **Production Engineering**: Observability, security, and reliability practices
- **AI Orchestration**: How to coordinate LLMs with external tools effectively

## 📚 References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Opik Observability Platform](https://www.comet.com/opik)
- [Decoding ML Course](https://github.com/decodingml/enterprise-mcp-series)

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

We welcome contributions! Please read the ROADMAP.md for current priorities and implementation guidelines.

---

**Built with ❤️ following the Decoding ML Enterprise MCP Systems course**

