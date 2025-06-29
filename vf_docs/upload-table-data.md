# Voiceflow Knowledge Base - Upload Table Data

> **Source:** [Voiceflow API Reference - Upload Table Data](https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload-table-1)

## Overview

The Upload Table Data endpoint allows you to upload structured table data to the Voiceflow Knowledge Base. This endpoint supports completely custom fields in the table data, including various data types such as string, number, array, or object. It's ideal for uploading structured datasets, product catalogs, FAQ databases, and other tabular information.

## Endpoint

```
POST https://api.voiceflow.com/v1/knowledge-base/docs/upload/table
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Request Parameters

### Headers

- **Authorization** (required): `YOUR_DM_API_KEY`
- **Content-Type** (required): `application/json`
- **Accept**: `application/json`

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `overwrite` | boolean | No | false | If set to true, existing table with the same name will be overwritten |
| `markdownConversion` | boolean | No | false | **Beta feature** - Automatic HTML to markdown conversion for better chunks |
| `llmGeneratedQ` | boolean | No | false | **Beta feature** - Generate questions for each chunk to enhance retrieval |
| `llmPrependContext` | boolean | No | false | **Beta feature** - Prepend context summary to each chunk |
| `llmContentSummarization` | boolean | No | false | **Beta feature** - Summarize content (limited to 15 rows per table) |

### Request Body

The request body must contain a `data` object with the following structure:

```json
{
  "data": {
    "name": "table_name",
    "schema": {
      "searchableFields": ["field1", "field2"],
      "metadataFields": ["metadata_field1", "metadata_field2"]
    },
    "items": [
      {
        "field1": "value1",
        "field2": "value2",
        "metadata_field1": "metadata_value"
      }
    ]
  }
}
```

#### Required Fields
- **name** (string): Unique name for the table
- **schema** (object): Defines the table structure
  - **searchableFields** (array): Fields that can be searched
  - **metadataFields** (array): Fields used for filtering and metadata
- **items** (array): Array of data objects

## Example Usage

### Basic Python Example

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "YOUR_DM_API_KEY"
}

response = requests.post(url, headers=headers)
print(response.text)
```

### Complete Table Upload Example

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload/table' \
  --header 'accept: application/json' \
  --header 'content-type: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "name": "products",
      "schema": {
        "searchableFields": ["name", "description"],
        "metadataFields": ["category", "price", "tags"]
      },
      "items": [
        {
          "name": "Laptop Pro",
          "description": "High-performance laptop for professionals",
          "category": "electronics",
          "price": 1299,
          "tags": ["laptop", "professional", "high-performance"]
        },
        {
          "name": "Wireless Mouse",
          "description": "Ergonomic wireless mouse with precision tracking",
          "category": "accessories",
          "price": 49,
          "tags": ["mouse", "wireless", "ergonomic"]
        }
      ]
    }
  }'
```

### Complex Data Types Example

```python
import requests
import json

url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": "YOUR_DM_API_KEY"
}

# Complex table with nested objects and arrays
table_data = {
    "data": {
        "name": "employees",
        "schema": {
            "searchableFields": ["name", "department", "skills"],
            "metadataFields": ["level", "location", "projects"]
        },
        "items": [
            {
                "name": "Jane Doe",
                "department": "Engineering",
                "skills": ["Python", "JavaScript", "React"],
                "level": "senior",
                "location": {
                    "city": "San Francisco",
                    "country": "USA",
                    "timezone": "PST"
                },
                "projects": [
                    {
                        "name": "AI Development",
                        "status": "active",
                        "deadline": "2024-12-31"
                    }
                ]
            },
            {
                "name": "John Smith",
                "department": "Design",
                "skills": ["Figma", "Sketch", "UI/UX"],
                "level": "mid",
                "location": {
                    "city": "New York",
                    "country": "USA",
                    "timezone": "EST"
                },
                "projects": [
                    {
                        "name": "Mobile App Redesign",
                        "status": "completed",
                        "deadline": "2024-06-30"
                    }
                ]
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=table_data)
print(json.dumps(response.json(), indent=2))
```

### Table Upload with Beta Features

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload/table?overwrite=true&llmGeneratedQ=true&markdownConversion=true' \
  --header 'accept: application/json' \
  --header 'content-type: application/json' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "name": "faq_database",
      "schema": {
        "searchableFields": ["question", "answer"],
        "metadataFields": ["category", "priority", "last_updated"]
      },
      "items": [
        {
          "question": "How do I reset my password?",
          "answer": "Click on the forgot password link on the login page and follow the instructions.",
          "category": "account",
          "priority": "high",
          "last_updated": "2024-01-15"
        }
      ]
    }
  }'
```

## Response Format

### Successful Response (200)

```json
{
  "data": {
    "data": {
      "name": "products",
      "type": "table",
      "rowsCount": 4
    },
    "documentID": "66821ba553dbbb191a23b21c",
    "updatedAt": "2024-07-02T13:52:15.809Z",
    "status": {
      "type": "PENDING"
    },
    "tags": []
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data.data.name` | string | Name of the uploaded table |
| `data.data.type` | string | Always "table" for table uploads |
| `data.data.rowsCount` | integer | Number of rows in the uploaded table |
| `data.documentID` | string | Unique identifier for the uploaded table |
| `data.updatedAt` | datetime | Timestamp of the upload |
| `data.status.type` | string | Processing status: `PENDING`, `SUCCESS`, `ERROR` |
| `data.tags` | array | Associated tags (initially empty) |

## Error Responses

### Bad Request (400)
```json
{
  "error": {
    "code": 400,
    "message": "Bad Request",
    "details": "The request was invalid. Check request body format, required fields, or data types."
  }
}
```

### Forbidden (403)
```json
{
  "error": {
    "code": 403,
    "message": "Forbidden",
    "details": "The number of rows in the uploaded table exceeds the limit for your current plan."
  }
}
```

### Unprocessable Entity (422)
```json
{
  "error": {
    "code": 422,
    "message": "Unprocessable Entity",
    "details": "The metadata format is invalid."
  }
}
```

## Data Types Support

The table upload endpoint supports various data types:

### Primitive Types
- **String**: Text values
- **Number**: Integer and floating-point numbers
- **Boolean**: true/false values

### Complex Types
- **Array**: Lists of values `["item1", "item2", "item3"]`
- **Object**: Nested key-value pairs `{"key": "value", "nested": {"inner": "value"}}`

### Example with All Data Types

```json
{
  "data": {
    "name": "comprehensive_example",
    "schema": {
      "searchableFields": ["title", "description"],
      "metadataFields": ["price", "active", "tags", "details"]
    },
    "items": [
      {
        "title": "Sample Product",
        "description": "A comprehensive example product",
        "price": 99.99,
        "active": true,
        "tags": ["example", "sample", "demo"],
        "details": {
          "weight": 1.5,
          "dimensions": {
            "length": 10,
            "width": 5,
            "height": 3
          },
          "features": ["feature1", "feature2"]
        }
      }
    ]
  }
}
```

## Beta Features

### Smart Chunking Features

> **Note**: To access beta features, [join the waiting list](https://beta.proxy-voiceflow.com/?beta=smartchunking)

- **markdownConversion**: Converts HTML content to markdown for better chunk generation
- **llmGeneratedQ**: Generates questions for each chunk to improve retrieval alignment
- **llmPrependContext**: Adds context summaries to chunks (cannot be used with llmGeneratedQ)
- **llmContentSummarization**: Summarizes and optimizes content (limited to 15 rows per table)

## Best Practices

### Schema Design
1. **Searchable Fields**: Include fields users will commonly search for
2. **Metadata Fields**: Use for filtering, categorization, and additional context
3. **Field Naming**: Use clear, consistent naming conventions
4. **Data Types**: Ensure consistent data types within columns

### Data Organization
1. **Row Limits**: Be mindful of plan limits for number of rows
2. **Data Quality**: Ensure clean, consistent data before upload
3. **Overwrite Strategy**: Use `overwrite=true` carefully to avoid data loss
4. **Chunking**: Consider how data will be chunked for retrieval

### Performance Optimization
1. **Batch Uploads**: Upload related data together in single tables
2. **Metadata Strategy**: Use metadata for efficient filtering
3. **Search Fields**: Limit searchable fields to improve performance
4. **Data Size**: Keep individual field values reasonably sized

## Common Use Cases

### Product Catalog

```python
def upload_product_catalog(api_key, products):
    """Upload product catalog to Voiceflow"""
    url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    table_data = {
        "data": {
            "name": "product_catalog",
            "schema": {
                "searchableFields": ["name", "description", "brand"],
                "metadataFields": ["category", "price", "availability", "tags"]
            },
            "items": products
        }
    }
    
    response = requests.post(url, headers=headers, json=table_data)
    return response.json()
```

### FAQ Database

```python
def upload_faq_database(api_key, faqs):
    """Upload FAQ database to Voiceflow"""
    url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    table_data = {
        "data": {
            "name": "faq_database",
            "schema": {
                "searchableFields": ["question", "answer", "keywords"],
                "metadataFields": ["category", "priority", "last_updated"]
            },
            "items": faqs
        }
    }
    
    response = requests.post(url, headers=headers, json=table_data)
    return response.json()
```

## Error Handling

```python
import requests
import json

def safe_table_upload(api_key, table_data):
    """Safely upload table data with comprehensive error handling"""
    url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload/table"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": api_key
    }
    
    try:
        response = requests.post(url, headers=headers, json=table_data, timeout=60)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 400:
            return {"success": False, "error": "Bad Request - Check data format"}
        elif response.status_code == 403:
            return {"success": False, "error": "Forbidden - Row limit exceeded"}
        elif response.status_code == 422:
            return {"success": False, "error": "Invalid metadata format"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON response"}

# Usage
result = safe_table_upload(api_key, table_data)
if result["success"]:
    print("Table uploaded successfully!")
    print(f"Document ID: {result['data']['data']['documentID']}")
else:
    print(f"Upload failed: {result['error']}")
```

## Related APIs

- [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) - Query uploaded table data
- [Document List](https://docs.voiceflow.com/reference/document-list) - List uploaded tables
- [Delete Document](https://docs.voiceflow.com/reference/delete-document) - Remove tables
- [Upload Document (File)](https://docs.voiceflow.com/reference/upload-document-file) - Upload files
- [Upload Document (URL)](https://docs.voiceflow.com/reference/upload-document-url) - Upload from URLs

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload-table-1* 