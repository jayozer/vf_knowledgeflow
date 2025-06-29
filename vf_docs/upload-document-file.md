# Voiceflow Knowledge Base - Upload Document (File)

> **Source:** [Voiceflow API Reference - Upload Document (File)](https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload)

## Overview

The Upload Document (File) endpoint allows you to upload local files to the Voiceflow Knowledge Base. This API accepts PDF, text, and DOCX files, with a limit of one file per call.

## Endpoint

```
POST https://api.voiceflow.com/v1/knowledge-base/docs/upload
```

## Authentication

Requires valid Voiceflow API key in the Authorization header.

## Supported File Types

- **PDF** (.pdf)
- **Text** (.txt)
- **DOCX** (.docx)

## Request Parameters

### Headers
- **Content-Type** (required): `multipart/form-data`
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

### Form Data Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | The document file to upload (PDF, text, or DOCX). One file per call. |
| `metadata` | string | No | Custom key-value pairs in JSON format: `{"key":"value"}` |

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

### Basic File Upload

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?maxChunkSize=1000' \
  --header 'accept: application/json' \
  --header 'content-type: multipart/form-data' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --form 'file=@/path/to/your/document.pdf'
```

### File Upload with Metadata

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?overwrite=true&maxChunkSize=800' \
  --header 'accept: application/json' \
  --header 'content-type: multipart/form-data' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --form 'file=@/path/to/your/document.pdf' \
  --form 'metadata={"category": "manual", "priority": "high", "version": "1.2"}'
```

### File Upload with Beta Features

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?markdownConversion=true&llmGeneratedQ=true&llmBasedChunking=true' \
  --header 'accept: application/json' \
  --header 'content-type: multipart/form-data' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --form 'file=@/path/to/your/document.docx'
```

### Text File Upload with Complex Metadata

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?maxChunkSize=1200' \
  --header 'accept: application/json' \
  --header 'content-type: multipart/form-data' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --form 'file=@/path/to/your/notes.txt' \
  --form 'metadata={"inner": {"text": "research notes", "price": 5, "tags": ["research", "ai", "nlp"]}}'
```

## Response Format

### Successful Response (200)

```json
{
  "data": [
    {
      "status": "PENDING",
      "data": {
        "type": "file",
        "name": "document.pdf",
        "url": null
      },
      "updatedAt": "2023-09-28T20:06:34.049Z",
      "documentID": "6515dccab4bc5400060fbc6a",
      "metadata": {
        "category": "manual",
        "priority": "high",
        "version": "1.2"
      }
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `data[]` | array | Array of uploaded document objects |
| `data[].status` | string | Processing status: `PENDING`, `SUCCESS`, `ERROR`, `INITIALIZED` |
| `data[].data.type` | string | Document type (`"file"`) |
| `data[].data.name` | string | Original filename |
| `data[].data.url` | string | Always `null` for file uploads |
| `data[].updatedAt` | datetime | Timestamp of last update |
| `data[].documentID` | string | Unique identifier for the uploaded document |
| `data[].metadata` | object | Associated metadata as provided during upload |

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

## Metadata Usage

Metadata can be used for filtering and organizing your documents. Common use cases:

### Simple Metadata
```json
{
  "category": "tutorial",
  "difficulty": "beginner",
  "language": "english"
}
```

### Nested Metadata (for complex filtering)
```json
{
  "inner": {
    "text": "product documentation",
    "price": 99,
    "tags": ["product", "guide", "v2"],
    "author": {
      "name": "John Doe",
      "department": "engineering"
    }
  }
}
```

## Example Usage

```python
import requests

url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload?maxChunkSize=1000"

headers = {
    "accept": "application/json",
    "content-type": "multipart/form-data"
}

response = requests.post(url, headers=headers)

print(response.text)
```

For advanced filtering capabilities, see the [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) documentation.

## Best Practices

1. **File Size**: Keep files reasonably sized for better processing performance
2. **File Format**: Use text-searchable PDFs rather than image-only PDFs
3. **Chunk Size Optimization**: Test different chunk sizes based on your content type
4. **Metadata Strategy**: Use consistent metadata schemas across similar documents
5. **Status Monitoring**: Check document status after upload to ensure successful processing
6. **Overwrite Carefully**: Use the `overwrite` parameter carefully to avoid data loss

## Error Handling

Monitor the `status` field in the response:
- If `ERROR`, check file format, size, and accessibility
- If `PENDING`, the document is still processing
- Use the Document Chunk Retrieval API to verify successful processing

Common issues:
- **Unsupported file type**: Ensure file is PDF, TXT, or DOCX
- **File too large**: Consider splitting large documents
- **Invalid metadata format**: Ensure metadata is valid JSON

## File Type Specific Considerations

### PDF Files
- Text-searchable PDFs work best
- Image-heavy PDFs may have reduced accuracy
- Password-protected PDFs are not supported

### Text Files
- UTF-8 encoding recommended
- Plain text provides most reliable processing
- Consider line breaks and formatting

### DOCX Files
- Modern Word format (.docx) only
- Tables and complex formatting may affect chunking
- Images and embedded objects are ignored

## Related APIs

- [Document Chunk Retrieval](https://docs.voiceflow.com/reference/document-chunk-retrieval) - View processed chunks
- [Filtering with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata) - Query documents with filters
- [Upload Document (URL)](https://docs.voiceflow.com/reference/upload-document-url) - Upload from URLs
- [Upload Table Data](https://docs.voiceflow.com/reference/upload-table-data) - Upload structured data

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/post_v1-knowledge-base-docs-upload* 