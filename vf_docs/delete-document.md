# Voiceflow Knowledge Base - Delete Document

> **Source:** [Voiceflow API Reference - Delete Document](https://docs.voiceflow.com/reference/delete_v1-knowledge-base-docs-documentid)

## Overview

The Delete Document endpoint allows you to permanently remove a specific document from the Voiceflow Knowledge Base using its document ID. This operation is irreversible and will delete the document along with all its associated chunks and metadata.

## Endpoint

```
DELETE https://api.voiceflow.com/v1/knowledge-base/docs/{documentID}
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Request Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `documentID` | string | Yes | The unique identifier of the document to delete |

### Headers

- **Authorization** (required): `YOUR_DM_API_KEY`
- **Content-Type**: `application/json` (optional)

## Example Usage

### Basic Delete Request

```bash
curl --request DELETE \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/6515dccab4bc5400060fbc6a' \
  --header 'Authorization: YOUR_DM_API_KEY'
```

### Python Example

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/documentID"
headers = {
    "Authorization": "YOUR_DM_API_KEY"
}

response = requests.delete(url, headers=headers)
print(response.text)
```

### Node.js Example

```javascript
const axios = require('axios');

const documentID = 'your-document-id';
const url = `https://api.voiceflow.com/v1/knowledge-base/docs/${documentID}`;

const config = {
  method: 'delete',
  url: url,
  headers: {
    'Authorization': 'YOUR_DM_API_KEY'
  }
};

axios(config)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error(error);
  });
```

## Response Format

### Successful Response (200)

```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### Error Responses

#### Document Not Found (404)
```json
{
  "error": "Document not found",
  "code": 404,
  "message": "The specified document ID does not exist"
}
```

#### Unauthorized (401)
```json
{
  "error": "Unauthorized",
  "code": 401,
  "message": "Invalid or missing API key"
}
```

#### Internal Server Error (500)
```json
{
  "error": "Internal Server Error",
  "code": 500,
  "message": "An error occurred while processing the request"
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Document successfully deleted |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Document not found |
| 500 | Internal server error |

## Important Considerations

### ⚠️ Irreversible Operation
- **Permanent deletion**: Once deleted, the document cannot be recovered
- **Associated data**: All chunks and metadata are permanently removed
- **No backup**: Voiceflow does not maintain backups of deleted documents

### Data Impact
- **Chunks removed**: All text chunks associated with the document are deleted
- **Metadata cleared**: All associated metadata is permanently removed
- **Search impact**: The document will no longer appear in knowledge base queries
- **References broken**: Any external references to this document will become invalid

## Best Practices

1. **Verify Document ID**: Always confirm the correct document ID before deletion
2. **Backup Important Data**: Export or backup important documents before deletion
3. **Check Dependencies**: Ensure no critical workflows depend on the document
4. **Use Document List API**: Verify document exists before attempting deletion
5. **Error Handling**: Implement proper error handling for failed deletions

## Pre-deletion Workflow

Before deleting a document, consider this workflow:

1. **List Documents**: Use the Document List API to verify the document exists
2. **Retrieve Chunks**: Use Document Chunk Retrieval to backup content if needed
3. **Check Metadata**: Review associated metadata that will be lost
4. **Confirm Deletion**: Ensure this is the intended document to delete
5. **Execute Delete**: Perform the deletion operation

## Error Handling

```python
import requests

def delete_document(api_key, document_id):
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}"
    headers = {"Authorization": api_key}
    
    try:
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Document {document_id} deleted successfully")
            return True
        elif response.status_code == 404:
            print(f"Document {document_id} not found")
            return False
        elif response.status_code == 401:
            print("Unauthorized: Check your API key")
            return False
        else:
            print(f"Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

# Usage
api_key = "YOUR_DM_API_KEY"
document_id = "6515dccab4bc5400060fbc6a"
delete_document(api_key, document_id)
```

## Bulk Deletion

For deleting multiple documents, you'll need to make individual API calls:

```python
import requests
import time

def bulk_delete_documents(api_key, document_ids, delay=1):
    """
    Delete multiple documents with optional delay between requests
    """
    results = []
    
    for doc_id in document_ids:
        url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{doc_id}"
        headers = {"Authorization": api_key}
        
        try:
            response = requests.delete(url, headers=headers)
            results.append({
                "document_id": doc_id,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
            # Add delay to avoid rate limiting
            if delay > 0:
                time.sleep(delay)
                
        except requests.exceptions.RequestException as e:
            results.append({
                "document_id": doc_id,
                "error": str(e),
                "success": False
            })
    
    return results
```

## Related APIs

- [Document List](https://docs.voiceflow.com/reference/document-list) - List all documents before deletion
- [Document Chunk Retrieval](https://docs.voiceflow.com/reference/document-chunk-retrieval) - Backup content before deletion
- [Upload Document (File)](https://docs.voiceflow.com/reference/upload-document-file) - Re-upload documents if needed
- [Upload Document (URL)](https://docs.voiceflow.com/reference/upload-document-url) - Re-upload from URLs if needed

## Security Notes

- **API Key Protection**: Never expose your API key in client-side code
- **Rate Limiting**: Be mindful of API rate limits when performing bulk deletions
- **Audit Trail**: Consider maintaining your own audit trail of deletions
- **Access Control**: Ensure only authorized users can perform delete operations

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/delete_v1-knowledge-base-docs-documentid* 