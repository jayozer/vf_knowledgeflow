# Voiceflow Knowledge Base - Update Chunk Metadata

> **Source:** [Voiceflow API Reference - Update Chunk Metadata](https://docs.voiceflow.com/reference/patch_v1-knowledge-base-docs-documentid-chunk-chunkid)

## Overview

The Update Chunk Metadata endpoint allows you to update metadata for a specific chunk within a document while leaving all other chunks unchanged. This endpoint works with all document types (file, URL, and table uploads) and provides granular control over individual chunk metadata.

## Endpoint

```
PATCH https://api.voiceflow.com/v1/knowledge-base/docs/{documentID}/chunk/{chunkID}
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `documentID` | string | Yes | A unique identifier of the document object |
| `chunkID` | string | Yes | A unique identifier of the chunk to update |

### Headers

- **Authorization** (required): `YOUR_DM_API_KEY`
- **Content-Type** (required): `application/json`
- **Accept**: `application/json`

### Request Body

The request body should contain a `data` object with the metadata to update:

```json
{
  "data": {
    "metadata": {
      "key1": "value1",
      "key2": "value2",
      "nested": {
        "property": "value"
      }
    }
  }
}
```

## Example Usage

### Basic Python Example

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/documentID/chunk/chunkID"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "YOUR_DM_API_KEY"
}

response = requests.patch(url, headers=headers)
print(response.text)
```

### Complete Metadata Update Example

```bash
curl --request PATCH \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/6515dccab4bc5400060fbc6a/chunk/chunk_12345' \
  --header 'accept: application/json' \
  --header 'content-type: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "metadata": {
        "category": "updated_category",
        "priority": "high",
        "tags": ["updated", "important"],
        "last_modified": "2024-01-15T10:30:00Z"
      }
    }
  }'
```

### Python Implementation with Metadata

```python
import requests
import json

def update_chunk_metadata(api_key, document_id, chunk_id, metadata):
    """Update metadata for a specific chunk"""
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/chunk/{chunk_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    payload = {
        "data": {
            "metadata": metadata
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    return response.json()

# Example usage
api_key = "YOUR_DM_API_KEY"
document_id = "6515dccab4bc5400060fbc6a"
chunk_id = "chunk_12345"

new_metadata = {
    "category": "technical_documentation",
    "difficulty": "intermediate",
    "tags": ["api", "reference", "updated"],
    "version": "2.0",
    "reviewer": {
        "name": "John Doe",
        "date": "2024-01-15"
    }
}

result = update_chunk_metadata(api_key, document_id, chunk_id, new_metadata)
print(json.dumps(result, indent=2))
```

### Batch Chunk Updates

```python
import requests
import time

def batch_update_chunk_metadata(api_key, document_id, chunk_updates, delay=0.5):
    """Update metadata for multiple chunks with rate limiting"""
    results = []
    
    for chunk_id, metadata in chunk_updates.items():
        url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/chunk/{chunk_id}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": api_key
        }
        
        payload = {
            "data": {
                "metadata": metadata
            }
        }
        
        try:
            response = requests.patch(url, headers=headers, json=payload)
            results.append({
                "chunk_id": chunk_id,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            })
            
            # Rate limiting delay
            if delay > 0:
                time.sleep(delay)
                
        except requests.exceptions.RequestException as e:
            results.append({
                "chunk_id": chunk_id,
                "success": False,
                "error": str(e)
            })
    
    return results

# Example batch update
chunk_updates = {
    "chunk_001": {
        "category": "introduction",
        "priority": "high"
    },
    "chunk_002": {
        "category": "advanced",
        "priority": "medium"
    },
    "chunk_003": {
        "category": "reference",
        "priority": "low"
    }
}

batch_results = batch_update_chunk_metadata(api_key, document_id, chunk_updates)
```

## Response Format

### Successful Response (200)

```json
{
  "data": {
    "status": "SUCCESS",
    "data": {
      "type": "file",
      "name": "user-manual.pdf",
      "url": null
    },
    "updatedAt": "2024-01-15T10:30:00.000Z",
    "documentID": "6515dccab4bc5400060fbc6a",
    "metadata": {
      "category": "updated_category",
      "priority": "high",
      "tags": ["updated", "important"],
      "last_modified": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data.status` | string | Processing status: `SUCCESS`, `ERROR`, `PENDING`, `INITIALIZED` |
| `data.data.type` | string | Document type: `file`, `url`, or `table` |
| `data.data.name` | string | Document name |
| `data.data.url` | string | Original URL (for URL documents) |
| `data.updatedAt` | datetime | Timestamp of the last update |
| `data.documentID` | string | Unique identifier of the document |
| `data.metadata` | object | Updated metadata for the chunk |

## Status Types

- **SUCCESS**: Chunk metadata successfully updated
- **ERROR**: An error occurred during the update
- **PENDING**: Update is being processed
- **INITIALIZED**: Update process initiated

## Metadata Update Strategies

### Incremental Updates
Update specific metadata fields while preserving existing ones:

```python
def incremental_metadata_update(api_key, document_id, chunk_id, new_fields):
    """Add or update specific metadata fields without removing existing ones"""
    # First, get current chunk metadata (requires Document Chunk Retrieval API)
    # Then merge with new fields
    
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/chunk/{chunk_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    # Merge existing metadata with new fields
    # Note: You'll need to retrieve current metadata first using the chunk retrieval API
    updated_metadata = {
        **existing_metadata,  # Existing metadata from chunk retrieval
        **new_fields          # New fields to add/update
    }
    
    payload = {
        "data": {
            "metadata": updated_metadata
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    return response.json()
```

### Complete Replacement
Replace all metadata for a chunk:

```python
def replace_chunk_metadata(api_key, document_id, chunk_id, new_metadata):
    """Completely replace chunk metadata"""
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/chunk/{chunk_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    payload = {
        "data": {
            "metadata": new_metadata
        }
    }
    
    response = requests.patch(url, headers=headers, json=payload)
    return response.json()
```

## Common Use Cases

### Content Classification

```python
def classify_chunk_content(api_key, document_id, chunk_id, classification):
    """Add classification metadata to a chunk"""
    metadata = {
        "content_type": classification["type"],
        "confidence": classification["confidence"],
        "categories": classification["categories"],
        "keywords": classification["keywords"],
        "classified_at": "2024-01-15T10:30:00Z",
        "classifier_version": "1.0"
    }
    
    return update_chunk_metadata(api_key, document_id, chunk_id, metadata)
```

### Quality Scoring

```python
def update_chunk_quality_score(api_key, document_id, chunk_id, quality_metrics):
    """Update chunk with quality assessment metadata"""
    metadata = {
        "quality_score": quality_metrics["overall_score"],
        "readability": quality_metrics["readability"],
        "completeness": quality_metrics["completeness"],
        "accuracy": quality_metrics["accuracy"],
        "last_reviewed": "2024-01-15T10:30:00Z",
        "reviewer_id": quality_metrics["reviewer_id"]
    }
    
    return update_chunk_metadata(api_key, document_id, chunk_id, metadata)
```

### Access Control

```python
def set_chunk_permissions(api_key, document_id, chunk_id, permissions):
    """Set access control metadata for a chunk"""
    metadata = {
        "access_level": permissions["level"],
        "allowed_roles": permissions["roles"],
        "department": permissions["department"],
        "expires_at": permissions.get("expires_at"),
        "created_by": permissions["created_by"]
    }
    
    return update_chunk_metadata(api_key, document_id, chunk_id, metadata)
```

## Error Handling

```python
import requests
import json

def safe_update_chunk_metadata(api_key, document_id, chunk_id, metadata):
    """Safely update chunk metadata with comprehensive error handling"""
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/chunk/{chunk_id}"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    payload = {
        "data": {
            "metadata": metadata
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 404:
            return {"success": False, "error": "Document or chunk not found"}
        elif response.status_code == 401:
            return {"success": False, "error": "Unauthorized - Check API key"}
        elif response.status_code == 400:
            return {"success": False, "error": "Bad request - Check metadata format"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON response"}

# Usage with error handling
result = safe_update_chunk_metadata(api_key, document_id, chunk_id, new_metadata)
if result["success"]:
    print("Chunk metadata updated successfully!")
    print(f"Document ID: {result['data']['data']['documentID']}")
else:
    print(f"Update failed: {result['error']}")
```

## Best Practices

### Metadata Design
1. **Consistent Schema**: Use consistent metadata schemas across similar chunks
2. **Meaningful Keys**: Use descriptive, standardized metadata keys
3. **Data Types**: Maintain consistent data types for metadata values
4. **Versioning**: Include version information in metadata for tracking changes

### Performance Optimization
1. **Batch Operations**: Group multiple chunk updates to minimize API calls
2. **Rate Limiting**: Implement delays between requests to avoid rate limits
3. **Error Recovery**: Implement retry logic for failed updates
4. **Validation**: Validate metadata before sending to avoid errors

### Workflow Integration
1. **Audit Trail**: Maintain logs of metadata changes
2. **Backup Strategy**: Consider backing up original metadata before updates
3. **Testing**: Test metadata updates on non-production data first
4. **Monitoring**: Monitor update success rates and performance

## Metadata Validation

```python
def validate_metadata(metadata):
    """Validate metadata structure before updating"""
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")
    
    # Check for reserved keys (if any)
    reserved_keys = ["_id", "_type", "_internal"]
    for key in metadata.keys():
        if key.startswith("_") and key in reserved_keys:
            raise ValueError(f"Reserved metadata key: {key}")
    
    # Validate data types
    def validate_value(value):
        if isinstance(value, (str, int, float, bool, list)):
            return True
        elif isinstance(value, dict):
            return all(validate_value(v) for v in value.values())
        else:
            return False
    
    for key, value in metadata.items():
        if not validate_value(value):
            raise ValueError(f"Invalid metadata value type for key: {key}")
    
    return True

# Example usage
try:
    validate_metadata(new_metadata)
    result = update_chunk_metadata(api_key, document_id, chunk_id, new_metadata)
except ValueError as e:
    print(f"Metadata validation error: {e}")
```

## Related APIs

- [Document Chunk Retrieval](https://docs.voiceflow.com/reference/document-chunk-retrieval) - Get current chunk metadata
- [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) - Query chunks by metadata
- [Update Document Metadata](https://docs.voiceflow.com/reference/update-document-metadata) - Update document-level metadata
- [Document List](https://docs.voiceflow.com/reference/document-list) - List documents and their chunks
- [Upload Table Data](https://docs.voiceflow.com/reference/upload-table-data) - Upload structured data with metadata

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/patch_v1-knowledge-base-docs-documentid-chunk-chunkid* 