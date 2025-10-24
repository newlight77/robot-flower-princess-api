# Documentation Index

Welcome to the **Robot Flower Princess API** documentation! This comprehensive guide covers everything from architecture to deployment.

## 📚 Documentation Overview

| Document | Description | Size |
|----------|-------------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture, DDD patterns, design decisions | 38KB |
| [API.md](API.md) | Complete API reference with examples | 24KB |
| [TESTING_STRATEGY.md](TESTING_STRATEGY.md) | Testing best practices and examples | 28KB |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment guide for various platforms | 20KB |
| [CI_CD.md](CI_CD.md) | GitHub Actions workflow and pipeline | 27KB |
| [COVERAGE.md](COVERAGE.md) | Code coverage strategy and tools | 19KB |

**Total Documentation**: ~156KB of comprehensive guides

---

## 🚀 Quick Links by Role

### For Developers

**Getting Started**:
1. [Architecture Overview](ARCHITECTURE.md#overview) - Understand the system design
2. [Local Development](DEPLOYMENT.md#local-development) - Set up your dev environment
3. [Testing Strategy](TESTING_STRATEGY.md#overview) - Learn how to write tests
4. [API Reference](API.md#api-endpoints) - Explore available endpoints

**Development Workflow**:
1. [Running Tests](TESTING_STRATEGY.md#running-tests) - How to run tests locally
2. [Code Coverage](COVERAGE.md#running-coverage-locally) - Measure test coverage
3. [Pull Request Workflow](CI_CD.md#pull-request-workflow) - Submit changes

### For DevOps/SRE

**Infrastructure**:
1. [Docker Deployment](DEPLOYMENT.md#docker-deployment) - Containerization guide
2. [Production Deployment](DEPLOYMENT.md#production-deployment) - Cloud platforms
3. [CI/CD Pipeline](CI_CD.md#pipeline-stages) - Automated workflows
4. [Monitoring](DEPLOYMENT.md#monitoring--observability) - Observability setup

**Operations**:
1. [Environment Configuration](DEPLOYMENT.md#environment-configuration) - Config management
2. [Security Best Practices](DEPLOYMENT.md#security) - Secure your deployment
3. [Troubleshooting](DEPLOYMENT.md#troubleshooting) - Common issues and solutions

### For QA/Testers

**Testing**:
1. [Testing Types](TESTING_STRATEGY.md#test-types) - Unit, integration, feature-component
2. [Test Examples](TESTING_STRATEGY.md#examples) - Real test examples
3. [Coverage Reports](COVERAGE.md#coverage-reports) - Understanding coverage
4. [CI Testing](CI_CD.md#pipeline-stages) - Automated test execution

### For API Consumers

**API Usage**:
1. [API Overview](API.md#overview) - Getting started with the API
2. [Endpoints](API.md#api-endpoints) - Available endpoints
3. [Request/Response Schemas](API.md#requestresponse-schemas) - Data formats
4. [Examples](API.md#examples) - Code examples (Python, JavaScript, cURL)
5. [Error Handling](API.md#error-handling) - Error codes and messages

---

## 📖 Documentation by Topic

### Architecture & Design

- [System Architecture](ARCHITECTURE.md#system-architecture) - High-level overview
- [Hexagonal Architecture](ARCHITECTURE.md#architectural-patterns) - Ports and Adapters
- [Domain-Driven Design](ARCHITECTURE.md#domain-driven-design) - DDD patterns
- [Project Structure](ARCHITECTURE.md#project-structure) - Code organization
- [Core Components](ARCHITECTURE.md#core-components) - Key classes and modules
- [Design Patterns](ARCHITECTURE.md#design-patterns) - Patterns used
- [Data Flow](ARCHITECTURE.md#data-flow) - Request/response flow
- [Design Decisions](ARCHITECTURE.md#key-design-decisions) - Why we chose X

### API Documentation

- [Base URL & Authentication](API.md#base-url) - API basics
- [Health Endpoints](API.md#health--status) - Health checks
- [Game Management](API.md#game-management) - CRUD operations
- [Game Actions](API.md#game-actions) - Robot actions
- [AI Autoplay](API.md#ai-autoplay) - Auto-solve games
- [Schemas](API.md#requestresponse-schemas) - Request/response formats
- [Error Handling](API.md#error-handling) - Error codes
- [Code Examples](API.md#examples) - Python, JS, cURL examples

### Testing

- [Test Strategy Overview](TESTING_STRATEGY.md#overview) - Testing approach
- [Unit Tests](TESTING_STRATEGY.md#unit-tests) - Testing domain logic
- [Integration Tests](TESTING_STRATEGY.md#integration-tests) - Testing API
- [Feature-Component Tests](TESTING_STRATEGY.md#feature-component-tests) - E2E tests
- [Best Practices](TESTING_STRATEGY.md#best-practices) - Writing good tests
- [Running Tests](TESTING_STRATEGY.md#running-tests) - Commands and options
- [Troubleshooting Tests](TESTING_STRATEGY.md#troubleshooting) - Common issues

### Deployment

- [Local Development](DEPLOYMENT.md#local-development) - Poetry setup
- [Docker Deployment](DEPLOYMENT.md#docker-deployment) - Containerization
- [Cloud Deployment](DEPLOYMENT.md#production-deployment) - AWS, GCP, Azure, Heroku
- [Reverse Proxy](DEPLOYMENT.md#reverse-proxy-nginx) - Nginx configuration
- [SSL/TLS](DEPLOYMENT.md#ssltls-certificates-lets-encrypt) - HTTPS setup
- [Process Manager](DEPLOYMENT.md#process-manager-systemd) - systemd service
- [Environment Config](DEPLOYMENT.md#environment-configuration) - Env vars
- [Monitoring](DEPLOYMENT.md#monitoring--observability) - Logging, metrics
- [Security](DEPLOYMENT.md#security) - Best practices
- [Troubleshooting](DEPLOYMENT.md#troubleshooting) - Common issues

### CI/CD

- [Workflow Overview](CI_CD.md#github-actions-workflow) - Pipeline structure
- [Pipeline Stages](CI_CD.md#pipeline-stages) - Unit, integration, lint, docker
- [Coverage Workflow](CI_CD.md#coverage-workflow) - Coverage in CI
- [Docker Build](CI_CD.md#docker-build--deploy) - Building images
- [Secrets Management](CI_CD.md#environment-variables--secrets) - GitHub secrets
- [Branch Strategy](CI_CD.md#branch-strategy) - Git workflow
- [Pull Request Flow](CI_CD.md#pull-request-workflow) - PR process
- [Troubleshooting CI](CI_CD.md#troubleshooting-ci-issues) - CI issues

### Code Coverage

- [Coverage Strategy](COVERAGE.md#coverage-strategy) - Three-tier approach
- [Running Coverage](COVERAGE.md#running-coverage-locally) - Local commands
- [Coverage Reports](COVERAGE.md#coverage-reports) - HTML, XML, LCOV
- [CI Coverage](COVERAGE.md#cicd-coverage-workflow) - Coverage in CI
- [Coverage Metrics](COVERAGE.md#coverage-metrics) - Current status
- [Improving Coverage](COVERAGE.md#improving-coverage) - Raising coverage
- [Troubleshooting](COVERAGE.md#troubleshooting) - Coverage issues

---

## 🎯 Common Tasks

### Setup & Installation

```bash
# Clone repository
git clone https://github.com/yourusername/robot-flower-princess-api.git
cd robot-flower-princess-api

# Install dependencies
pyenv install 3.13.0
pyenv local 3.13.0
poetry install

# Run development server
make run
```

👉 [Full Setup Guide](DEPLOYMENT.md#local-development)

### Running Tests

```bash
# Run all tests
make test-all

# Run with coverage
make coverage
make coverage-combine

# View coverage report
open .coverage/coverage_html/index.html
```

👉 [Testing Guide](TESTING_STRATEGY.md#running-tests)

### Docker Deployment

```bash
# Build image
docker build -t robot-flower-princess:latest .

# Run container
docker run -d -p 8000:8000 robot-flower-princess:latest

# Test health
curl http://localhost:8000/health
```

👉 [Docker Guide](DEPLOYMENT.md#docker-deployment)

### Contributing

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and test
make test-all
make coverage-combine

# Commit and push
git commit -m "feat: add my feature"
git push origin feature/my-feature

# Open PR on GitHub
```

👉 [PR Workflow](CI_CD.md#pull-request-workflow)

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Documentation Files** | 6 |
| **Total Doc Size** | ~156KB |
| **Test Coverage** | 90%+ |
| **API Endpoints** | 8 |
| **Test Suites** | 3 (unit, integration, feature-component) |
| **CI Pipeline Time** | ~5 minutes |
| **Docker Image Size** | ~150MB |

---

## 🔗 External Resources

### Python & FastAPI

- [Python 3.13 Documentation](https://docs.python.org/3.13/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)

### Testing

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

### DevOps

- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Architecture

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## 🤝 Contributing to Documentation

Found an error or want to improve the docs?

1. **Report Issues**: Open a GitHub issue
2. **Submit PRs**: Fork, edit, and submit a pull request
3. **Ask Questions**: Open a discussion on GitHub

### Documentation Standards

- Use **clear, concise language**
- Include **code examples** where applicable
- Add **diagrams** for complex concepts
- Keep **table of contents** updated
- Test all **code examples**
- Update **documentation index** when adding new docs

---

## 📝 License

This documentation is licensed under the same license as the project (MIT License).

---

## 📞 Support

- **GitHub Issues**: https://github.com/yourusername/robot-flower-princess/issues
- **Discussions**: https://github.com/yourusername/robot-flower-princess/discussions
- **Email**: support@your-domain.com

---

**Last Updated**: October 24, 2025

**Documentation Version**: 1.0.0
