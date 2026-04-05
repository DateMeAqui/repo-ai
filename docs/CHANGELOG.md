# CHANGELOG

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-01-15

### Added

- **REST API**
  - `POST /api/v1/generate-lambda` - Generate Lambda from documentation
  - `POST /api/v1/deploy` - Deploy to AWS
  - `GET /api/v1/status/{job_id}` - Job status tracking
  - `POST /api/v1/docs/upload` - Document upload
  - `GET /api/v1/projects` - List projects
  - `GET /api/v1/projects/{name}` - Project details
  - `DELETE /api/v1/projects/{name}` - Delete project
  - `GET /api/v1/health` - Health check

- **WebSocket API**
  - `/ws/chat/{session_id}` - Chat interface for Lambda generation
  - Streaming responses
  - File upload support

- **Documentation Parsing**
  - OpenAPI 3.0/3.1 JSON support
  - OpenAPI YAML support
  - Postman Collection v2.1 support
  - Firecrawl URL fetching

- **AWS Services**
  - Lambda function generation
  - SNS topic configuration
  - SQS queue setup
  - EventBridge rules
  - DynamoDB table definitions

- **AI Integration**
  - OpenAI GPT-4 integration
  - Streaming chat responses
  - Context-aware code generation

### Documentation

- Quickstart guide
- Installation guide
- Configuration guide
- API REST reference
- WebSocket protocol reference
- Architecture overview
- AWS services explanation
- Troubleshooting guide
