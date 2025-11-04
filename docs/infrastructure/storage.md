---
layout: default
title: Object Storage
description: MinIO object storage setup and usage
nav_order: 4
parent: Infrastructure
---

# Object Storage with MinIO

This document describes how the financial data extractor uses MinIO for object storage of PDF documents.

## Overview

The platform uses MinIO (S3-compatible object storage) for storing PDF files instead of local file system storage. This provides:

- **Scalability**: Object storage is designed for large-scale data
- **Reliability**: Built-in redundancy and data protection
- **Portability**: S3-compatible, can be migrated to AWS S3 or other providers
- **Development**: Easy local development with Docker

## Architecture

### Storage Service

The platform includes a unified storage service (`app.core.storage`) that supports:

1. **MinIOStorageService**: For object storage (S3-compatible)
2. **LegacyLocalStorageService**: Fallback for local file system
3. **StorageService**: Unified wrapper with automatic fallback

### Configuration

Storage is configured via environment variables in `.env`:

```bash
# MinIO (S3-compatible) object storage configuration
MINIO_ENABLED=true
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=financial-documents
MINIO_USE_SSL=false
```

### Object Key Structure

PDF files are stored using the following key structure:

```
company_{company_id}/{fiscal_year}/{filename}.pdf
```

Example:

```
company_1/2023/annual_report_2023.pdf
```

## Local Development

### Starting MinIO with Docker Compose

MinIO is included in the development docker-compose setup:

```bash
cd infrastructure/docker
docker-compose -f docker-compose.dev.yml up -d minio
```

MinIO web console: http://localhost:9001

- Username: `minioadmin`
- Password: `minioadmin`

MinIO S3 API: http://localhost:9000

### Accessing Files

You can access files via:

1. **MinIO Console**: http://localhost:9001
2. **Storage Service API**: Use the `IStorageService` interface in code
3. **Direct S3 API**: Compatible with any S3 client

### Bucket Creation

The bucket is automatically created on first use if it doesn't exist. This is handled by the `MinIOStorageService` initialization.

## Production Deployment

### Using AWS S3

To use AWS S3 instead of MinIO, update `.env`:

```bash
MINIO_ENABLED=true
MINIO_ENDPOINT=s3.amazonaws.com
MINIO_ACCESS_KEY=your_aws_access_key
MINIO_SECRET_KEY=your_aws_secret_key
MINIO_BUCKET_NAME=financial-documents-prod
MINIO_USE_SSL=true
```

### Using MinIO in Production

For production MinIO deployment, consider:

1. **High Availability**: Use distributed MinIO mode
2. **SSL/TLS**: Enable SSL for secure connections
3. **Backup**: Implement regular backups
4. **Monitoring**: Set up MinIO monitoring

## Migration from Local Storage

### Automatic Fallback

The storage service supports automatic fallback:

- If `MINIO_ENABLED=false`, files are stored locally
- Local storage uses the same object key structure
- All code is compatible with both storage types

### Data Migration

To migrate existing local PDFs to MinIO:

1. Keep `MINIO_ENABLED=false` initially
2. Download/process existing files
3. Set `MINIO_ENABLED=true` for new uploads
4. Optionally write a migration script to copy existing files

## Code Usage

### Basic Operations

```python
from app.core.storage import StorageServiceConfig, create_storage_service

# Create storage service
config = StorageServiceConfig(
    enabled=True,
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="financial-documents",
    use_ssl=False,
)
storage = create_storage_service(config)

# Save file
object_key = "company_1/2023/annual_report.pdf"
storage_path = await storage.save_file(
    file_content=pdf_bytes,
    object_key=object_key,
    content_type="application/pdf",
)

# Get file
pdf_content = await storage.get_file(object_key)

# Delete file
await storage.delete_file(object_key)

# Check existence
exists = await storage.file_exists(object_key)

# Calculate hash
file_hash = await storage.calculate_file_hash(object_key)

# Get URL
url = storage.get_file_url(object_key)
```

### In Workers

Workers automatically receive a storage service instance:

```python
def __init__(self, session, progress_callback, storage_service):
    self.storage_service = storage_service
```

## Monitoring

### Health Checks

MinIO includes built-in health checks:

```bash
curl http://localhost:9000/minio/health/live
```

### Metrics

Monitor MinIO using:

- MinIO Console dashboard
- Prometheus metrics endpoint
- S3-compatible API metrics

## Troubleshooting

### Connection Issues

1. Check MinIO is running: `docker ps | grep minio`
2. Verify endpoint: `curl http://localhost:9000/minio/health/live`
3. Check credentials in `.env`

### Bucket Not Found

- Buckets are auto-created on first use
- Check permissions on access keys
- Review MinIO logs

### File Not Found

- Verify object key format
- Check bucket name matches configuration
- Review MinIO console for file existence

## Security

### Development

Default credentials are fine for local development but should never be used in production.

### Production

1. Use strong access keys
2. Enable SSL/TLS
3. Implement bucket policies
4. Use IAM roles (AWS) or access policies (MinIO)
5. Enable encryption at rest

## References

- [MinIO Documentation](https://min.io/docs/minio/container/index.html)
- [MinIO Python SDK](https://min.io/docs/minio/linux/developers/python/API.html)
- [S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)
