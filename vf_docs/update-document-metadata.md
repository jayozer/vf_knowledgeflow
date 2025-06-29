# Update Document Metadata

Updates metadata for an entire document (all chunks) in the Voiceflow Knowledge Base.

## Overview

This endpoint allows you to update metadata for all chunks within a specific document. The metadata update applies to the entire document rather than individual chunks.

**Important Note**: This endpoint does not work for document type 'table'. Use the Upload Table Data endpoint for table documents.

## Endpoint

```
PATCH https://api.voiceflow.com/v1/knowledge-base/docs/{documentID}
```

## Authentication

Include your Voiceflow API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `documentID` | string | Yes | A unique identifier of the document object |

## Request Body

The request body should contain the metadata object you want to apply to the document:

```json
{
  "metadata": {
    "category": "support",
    "priority": "high",
    "department": "customer-service",
    "tags": ["faq", "billing", "account"]
  }
}
```

## Response Format

### Success Response (200)

```json
{
  "data": {
    "status": "SUCCESS",
    "data": {
      "type": "url",
      "name": "string",
      "url": "string"
    },
    "updatedAt": "2025-06-27T15:59:52.299Z",
    "documentID": "string",
    "metadata": {
      "category": "support",
      "priority": "high",
      "department": "customer-service",
      "tags": ["faq", "billing", "account"]
    }
  }
}
```

### Error Response (400)

```json
{
  "error": "Bad request - Table documents are not supported for whole document metadata update"
}
```

## Status Values

| Status | Description |
|--------|-------------|
| `SUCCESS` | Document metadata updated successfully |
| `ERROR` | Update failed due to an error |
| `PENDING` | Update is in progress |
| `INITIALIZED` | Update process has been initialized |

## Python Example

```python
import requests

def update_document_metadata(api_key, document_id, metadata):
    """
    Update metadata for an entire document in Voiceflow Knowledge Base
    
    Args:
        api_key (str): Your Voiceflow API key
        document_id (str): The document ID to update
        metadata (dict): Metadata to apply to the document
    
    Returns:
        dict: API response containing update status and document info
    """
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "metadata": metadata
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()

# Basic usage example
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/documentID"

headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.patch(url, headers=headers)

print(response.text)

# Example with metadata update
api_key = "your_api_key_here"
document_id = "your_document_id_here"

metadata = {
    "category": "product-docs",
    "version": "2.1",
    "author": "technical-writing-team",
    "last_reviewed": "2024-01-15",
    "tags": ["api", "documentation", "v2"]
}

try:
    result = update_document_metadata(api_key, document_id, metadata)
    print(f"Update Status: {result['data']['status']}")
    print(f"Document ID: {result['data']['documentID']}")
    print(f"Updated At: {result['data']['updatedAt']}")
    print(f"Applied Metadata: {result['data']['metadata']}")
except requests.exceptions.HTTPError as e:
    print(f"Error updating document metadata: {e}")
    print(f"Response: {e.response.text}")
```

## cURL Example

```bash
curl --request PATCH \
     --url https://api.voiceflow.com/v1/knowledge-base/docs/your_document_id \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --header 'Authorization: Bearer YOUR_API_KEY' \
     --data '{
       "metadata": {
         "category": "support",
         "priority": "high",
         "department": "customer-service"
       }
     }'
```

## Use Cases

### Content Classification
```python
# Classify documents by content type
metadata = {
    "content_type": "tutorial",
    "difficulty": "beginner",
    "estimated_reading_time": "5 minutes"
}
```

### Version Management
```python
# Track document versions and updates
metadata = {
    "version": "1.2.0",
    "changelog": "Updated API endpoints and examples",
    "compatibility": ["v1", "v2"]
}
```

### Access Control
```python
# Set access permissions and visibility
metadata = {
    "visibility": "internal",
    "department": "engineering",
    "security_level": "confidential"
}
```

## Important Limitations

1. **Table Documents**: This endpoint does not work with table-type documents
2. **Bulk Updates**: Updates apply to all chunks within the document
3. **Metadata Structure**: Ensure metadata follows your knowledge base schema

## Error Handling

```python
def safe_update_document_metadata(api_key, document_id, metadata):
    """
    Safely update document metadata with comprehensive error handling
    """
    try:
        result = update_document_metadata(api_key, document_id, metadata)
        
        if result['data']['status'] == 'SUCCESS':
            return {
                'success': True,
                'document_id': result['data']['documentID'],
                'updated_at': result['data']['updatedAt'],
                'metadata': result['data']['metadata']
            }
        else:
            return {
                'success': False,
                'status': result['data']['status'],
                'message': 'Update pending or failed'
            }
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return {
                'success': False,
                'error': 'Table documents not supported for metadata updates'
            }
        else:
            return {
                'success': False,
                'error': f'HTTP {e.response.status_code}: {e.response.text}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }
```

## Best Practices

1. **Validate Document Type**: Ensure the document is not a table type before updating
2. **Consistent Schema**: Use consistent metadata keys across your knowledge base
3. **Status Monitoring**: Check the status field in responses for update confirmation
4. **Error Recovery**: Implement retry logic for pending or failed updates
5. **Metadata Standards**: Establish metadata standards for your organization

## Related APIs

- [Update Chunk Metadata](./update-chunk-metadata.md) - Update metadata for specific chunks
- [Upload Document (File)](./upload-document-file.md) - Upload documents with initial metadata
- [Upload Document (URL)](./upload-document-url.md) - Upload from URL with metadata
- [Document List](./document-list.md) - List documents and their metadata
- [Upload Table Data](./upload-table-data.md) - Alternative for table documents 