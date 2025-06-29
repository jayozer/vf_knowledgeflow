# Voiceflow Knowledge Base - Document List

> **Source:** [Voiceflow API Reference - Document List](https://docs.voiceflow.com/reference/get_v1-knowledge-base-docs)

## Overview

The Document List endpoint retrieves a list of all documents within a given project's Knowledge Base. This API supports pagination and filtering to help you manage and navigate through your knowledge base documents efficiently.

## Endpoint

```
GET https://api.voiceflow.com/v1/knowledge-base/docs
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Request Parameters

### Headers

- **Authorization** (required): `YOUR_DM_API_KEY`
- **Accept**: `application/json`

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number for pagination |
| `limit` | integer | No | 10 | Number of documents per page (max recommended: 100) |
| `search` | string | No | - | Search term to filter documents by name or content |
| `type` | string | No | - | Filter by document type (`file`, `url`, `table`) |
| `status` | string | No | - | Filter by status (`PENDING`, `SUCCESS`, `ERROR`, `INITIALIZED`) |

## Example Usage

### Basic Document List Request

```bash
curl --request GET \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs' \
  --header 'accept: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY'
```

### Paginated Request

```bash
curl --request GET \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs?page=1&limit=10' \
  --header 'accept: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY'
```

### Python Example

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs?page=1&limit=10"
headers = {
    "accept": "application/json",
    "Authorization": "YOUR_DM_API_KEY"
}

response = requests.get(url, headers=headers)
print(response.text)
```

### Advanced Filtering

```bash
curl --request GET \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs?page=1&limit=20&type=file&status=SUCCESS' \
  --header 'accept: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY'
```

### Search Documents

```bash
curl --request GET \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs?search=user%20manual&limit=50' \
  --header 'accept: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY'
```

## Response Format

### Successful Response (200)

```json
{
  "data": [
    {
      "documentID": "6515dccab4bc5400060fbc6a",
      "data": {
        "type": "file",
        "name": "user-manual.pdf",
        "url": null
      },
      "status": {
        "type": "SUCCESS"
      },
      "updatedAt": "2023-09-28T20:06:34.049Z",
      "createdAt": "2023-09-28T19:45:12.123Z",
      "metadata": {
        "category": "documentation",
        "version": "1.0"
      },
      "tags": [
        "manual",
        "guide"
      ],
      "chunkCount": 45
    },
    {
      "documentID": "6515dccab4bc5400060fbc6b",
      "data": {
        "type": "url",
        "name": "example.com/api-docs",
        "url": "https://example.com/api-docs"
      },
      "status": {
        "type": "PENDING"
      },
      "updatedAt": "2023-09-28T20:10:15.321Z",
      "createdAt": "2023-09-28T20:10:15.321Z",
      "metadata": {
        "category": "api",
        "priority": "high"
      },
      "tags": [
        "api",
        "reference"
      ],
      "chunkCount": 0
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "totalPages": 3,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data[]` | array | Array of document objects |
| `data[].documentID` | string | Unique identifier for the document |
| `data[].data.type` | string | Document type: `file`, `url`, or `table` |
| `data[].data.name` | string | Document name or filename |
| `data[].data.url` | string | Original URL (for URL type documents) |
| `data[].status.type` | string | Processing status: `PENDING`, `SUCCESS`, `ERROR`, `INITIALIZED` |
| `data[].updatedAt` | datetime | Last update timestamp |
| `data[].createdAt` | datetime | Creation timestamp |
| `data[].metadata` | object | Associated metadata |
| `data[].tags` | array | Document tags |
| `data[].chunkCount` | integer | Number of processed chunks |
| `pagination` | object | Pagination information |
| `pagination.page` | integer | Current page number |
| `pagination.limit` | integer | Items per page |
| `pagination.total` | integer | Total number of documents |
| `pagination.totalPages` | integer | Total number of pages |
| `pagination.hasNext` | boolean | Whether there are more pages |
| `pagination.hasPrevious` | boolean | Whether there are previous pages |

## Status Types

- **SUCCESS**: Document successfully processed and ready for use
- **PENDING**: Document is being processed
- **ERROR**: An error occurred during processing
- **INITIALIZED**: Document upload initiated but not yet processed

## Practical Examples

### Get All Documents with Status Check

```python
import requests

def get_all_documents(api_key, page_size=50):
    """
    Retrieve all documents from knowledge base with pagination
    """
    all_documents = []
    page = 1
    
    while True:
        url = f"https://api.voiceflow.com/v1/knowledge-base/docs?page={page}&limit={page_size}"
        headers = {
            "accept": "application/json",
            "Authorization": api_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
            
        data = response.json()
        documents = data.get('data', [])
        
        if not documents:
            break
            
        all_documents.extend(documents)
        
        # Check if there are more pages
        pagination = data.get('pagination', {})
        if not pagination.get('hasNext', False):
            break
            
        page += 1
    
    return all_documents

# Usage
api_key = "YOUR_DM_API_KEY"
documents = get_all_documents(api_key)
print(f"Total documents: {len(documents)}")
```

### Filter Documents by Status

```python
import requests

def get_documents_by_status(api_key, status="SUCCESS"):
    """
    Get documents filtered by processing status
    """
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs?status={status}&limit=100"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Get only successfully processed documents
successful_docs = get_documents_by_status(api_key, "SUCCESS")
```

### Search and Filter Documents

```python
import requests
from urllib.parse import quote

def search_documents(api_key, search_term, doc_type=None):
    """
    Search documents by name/content and optionally filter by type
    """
    encoded_search = quote(search_term)
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs?search={encoded_search}&limit=50"
    
    if doc_type:
        url += f"&type={doc_type}"
    
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Search for PDF files containing "manual"
manual_pdfs = search_documents(api_key, "manual", "file")
```

## Error Handling

```python
import requests

def safe_get_documents(api_key, page=1, limit=10):
    """
    Safely retrieve documents with comprehensive error handling
    """
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs?page={page}&limit={limit}"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("Unauthorized: Check your API key")
            return None
        elif response.status_code == 429:
            print("Rate limit exceeded: Please wait before making more requests")
            return None
        else:
            print(f"HTTP Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage with error handling
result = safe_get_documents(api_key, page=1, limit=20)
if result:
    documents = result.get('data', [])
    pagination = result.get('pagination', {})
    print(f"Retrieved {len(documents)} documents")
```

## Best Practices

1. **Pagination**: Use appropriate page sizes (10-50 documents per request)
2. **Error Handling**: Always check response status codes and handle errors gracefully
3. **Rate Limiting**: Be mindful of API rate limits when making multiple requests
4. **Filtering**: Use status and type filters to get only the documents you need
5. **Caching**: Consider caching document lists if they don't change frequently

## Common Use Cases

### Document Management Dashboard

```python
def get_document_summary(api_key):
    """
    Get a summary of all documents organized by status
    """
    url = "https://api.voiceflow.com/v1/knowledge-base/docs?limit=100"
    headers = {
        "accept": "application/json",
        "Authorization": api_key
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('data', [])
        
        summary = {
            "total": len(documents),
            "by_status": {},
            "by_type": {},
            "total_chunks": 0
        }
        
        for doc in documents:
            status = doc.get('status', {}).get('type', 'UNKNOWN')
            doc_type = doc.get('data', {}).get('type', 'unknown')
            chunk_count = doc.get('chunkCount', 0)
            
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            summary['by_type'][doc_type] = summary['by_type'].get(doc_type, 0) + 1
            summary['total_chunks'] += chunk_count
        
        return summary
    
    return None
```

## Related APIs

- [Upload Document (File)](https://docs.voiceflow.com/reference/upload-document-file) - Upload new documents
- [Upload Document (URL)](https://docs.voiceflow.com/reference/upload-document-url) - Upload from URLs
- [Delete Document](https://docs.voiceflow.com/reference/delete-document) - Remove documents
- [Document Chunk Retrieval](https://docs.voiceflow.com/reference/document-chunk-retrieval) - Get document chunks
- [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) - Advanced filtering

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/get_v1-knowledge-base-docs* 