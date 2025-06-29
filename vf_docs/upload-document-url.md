# Voiceflow Knowledge Base - Upload Document (URL)

> **Source:** [Voiceflow API Reference - Upload Document (URL)](https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload-url)

## Overview

The Upload Document (URL) endpoint allows you to upload documents from web URLs to the Voiceflow Knowledge Base. This API accepts one URL per call and processes the content for use in your knowledge base.

## Endpoint

```
POST https://api.voiceflow.com/v1/knowledge-base/docs/upload
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Request Parameters

### Headers
- **Content-Type** (required): `application/json; charset=utf-8`
- **Authorization** (required): `YOUR_DM_API_KEY`

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `overwrite` | boolean | No | false | Specify whether to overwrite existing data. Set to "true" to overwrite. |
| `maxChunkSize` | integer | No | 1000 | Determines document chunking granularity. Range: 500-1500 tokens. |
| `markdownConversion` | boolean | No | false | **Beta feature** - Automatic HTML to markdown conversion for better chunks. |
| `llmGeneratedQ` | boolean | No | false | **Beta feature** - Generate questions for each chunk to enhance retrieval. |
| `llmPrependContext` | boolean | No | false | **Beta feature** - Prepend context summary to each chunk. |
| `llmBasedChunking` | boolean | No | false | **Beta feature** - Use LLM for optimal semantic chunking. |
| `llmContentSummarization` | boolean | No | false | **Beta feature** - Summarize and optimize content for retrieval. |

### Request Body

The request body must contain a `data` object with the following structure:

```json
{
  "data": {
    "type": "url",
    "url": "https://example.com/document",
    "metadata": {
      "key": "value"
    }
  }
}
```

#### Required Fields
- **type** (string): Must be set to `"url"`
- **url** (string): The URL of the document to upload

#### Optional Fields
- **metadata** (object): Additional metadata to associate with the document

## Chunk Size Considerations

The `maxChunkSize` parameter affects how your document is processed:

### Smaller Chunk Size (500-800 tokens)
- ✅ Narrower, more focused context
- ✅ Faster response times
- ✅ Lower token consumption
- ⚠️ Higher risk of less accurate answers

### Larger Chunk Size (1200-1500 tokens)
- ✅ More comprehensive context
- ✅ Better answer accuracy
- ⚠️ Slower response times
- ⚠️ Higher token consumption

## Example Usage

### Basic URL Upload

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?maxChunkSize=1000' \
  --header 'accept: application/json' \
  --header 'content-type: application/json; charset=utf-8' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "type": "url",
      "url": "https://www.familyhandyman.com/article/simple-step-stool/"
    }
  }'
```

### URL Upload with Metadata

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?overwrite=true&maxChunkSize=800' \
  --header 'accept: application/json' \
  --header 'content-type: application/json; charset=utf-8' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "type": "url",
      "url": "https://example.com/product-guide",
      "metadata": {
        "category": "product",
        "priority": "high",
        "tags": ["guide", "tutorial"]
      }
    }
  }'
```

### URL Upload with Beta Features

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?markdownConversion=true&llmGeneratedQ=true' \
  --header 'accept: application/json' \
  --header 'content-type: application/json; charset=utf-8' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --data '{
    "data": {
      "type": "url",
      "url": "https://docs.example.com/api-reference"
    }
  }'
```

## Response Format

### Successful Response (200)

```json
{
  "data": {
    "documentID": "6515dccab4bc5400060fbc6a",
    "data": {
      "type": "url",
      "name": "familyhandyman.com/article/simple-step-stool/",
      "url": "https://www.familyhandyman.com/article/simple-step-stool/",
      "metadata": {
        "additionalProp": {}
      }
    },
    "updatedAt": "2023-09-28T20:06:34.049Z",
    "status": {
      "type": "PENDING"
    },
    "tags": [
      "beginner",
      "small_scale"
    ]
  }
}
```

## Example Usage

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload?maxChunkSize=1000"

payload = "{\"data\":{\"type\":\"url\"}}"
headers = {
    "accept": "application/json",
    "content-type": "application/json; charset=utf-8"
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)

```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `documentID` | string | Unique identifier for the uploaded document |
| `data.type` | string | Document type (`"url"`) |
| `data.name` | string | Auto-generated name from URL |
| `data.url` | string | The original URL |
| `data.metadata` | object | Associated metadata |
| `updatedAt` | datetime | Timestamp of last update |
| `status.type` | string | Processing status: `PENDING`, `SUCCESS`, `ERROR`, `INITIALIZED` |
| `tags` | array | Auto-generated or assigned tags |

## Status Types

- **PENDING**: Document is being processed
- **SUCCESS**: Document successfully uploaded and processed
- **ERROR**: An error occurred during processing
- **INITIALIZED**: Document upload initiated

## Beta Features

Voiceflow offers several beta features for enhanced document processing:

### Smart Chunking Beta
- **markdownConversion**: Converts HTML to markdown for better chunk generation
- **llmGeneratedQ**: Generates questions for each chunk to improve retrieval alignment
- **llmPrependContext**: Adds context summaries to chunks
- **llmBasedChunking**: Uses AI for optimal semantic chunking
- **llmContentSummarization**: Summarizes and optimizes content

> **Note**: To access beta features, [join the waiting list](https://beta.proxy-voiceflow.com/?beta=smartchunking)

## Best Practices

1. **URL Validation**: Ensure URLs are publicly accessible and return valid content
2. **Chunk Size Optimization**: Test different chunk sizes based on your use case
3. **Metadata Usage**: Add relevant metadata for better filtering and organization
4. **Status Monitoring**: Check document status after upload to ensure successful processing
5. **Overwrite Strategy**: Use the `overwrite` parameter carefully to avoid data loss

## Error Handling

Monitor the `status.type` field in the response:
- If `ERROR`, check the URL accessibility and format
- If `PENDING`, the document is still processing
- Use the Document Chunk Retrieval API to verify successful processing

## Related APIs

- [Document Chunk Retrieval](https://docs.voiceflow.com/reference/document-chunk-retrieval) - View processed chunks
- [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) - Query documents with filters
- [Upload Document (File)](https://docs.voiceflow.com/reference/upload-document-file) - Upload local files

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload-url* 