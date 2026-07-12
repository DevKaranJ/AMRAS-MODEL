# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.0 | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in AMRAS, please report it responsibly.

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email security concerns to: security@example.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 1 week
- **Fix timeline:** Depends on severity

### What to Expect

- We will acknowledge receipt of your report
- We will provide an estimated timeline for a fix
- We will credit you in the security advisory (unless you prefer anonymity)

## Security Best Practices

### For Users

- Keep AMRAS updated to the latest version
- Use environment variables for sensitive configuration
- Never commit API keys or secrets to version control
- Use strong database credentials in production
- Enable HTTPS in production deployments

### For Developers

- Never log secrets or API keys
- Validate all user input
- Use parameterized queries (SQLAlchemy handles this)
- Follow the principle of least privilege
- Run the application as a non-root user in Docker

## Configuration Security

### Environment Variables

Sensitive configuration should be stored in `.env` files:

```env
# AI Provider API Keys
AI__API_KEY=your-api-key-here

# Database Credentials (production)
DB__URL=postgresql+asyncpg://user:password@host:port/dbname

# Never commit .env files
```

### Docker Security

The Dockerfile runs as a non-root user:

```dockerfile
RUN useradd -m -s /bin/bash amras
USER amras
```

### API Security

- Settings endpoint redacts secrets
- Health endpoints do not expose sensitive information
- Consider adding authentication for production use

## Dependency Security

We use Poetry for dependency management with locked versions in `poetry.lock`.

To check for vulnerabilities:

```bash
pip install safety
safety check -r requirements.txt
```

## Data Privacy

AMRAS processes manga content locally. No data is sent to external services unless:

1. You configure cloud AI providers (OpenAI, Anthropic, etc.)
2. You explicitly publish content to YouTube

Local AI models (default configuration) process all data on your machine.
