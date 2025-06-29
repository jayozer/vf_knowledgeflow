# Voiceflow Knowledge Base - Filtering with Metadata

> **Source:** [Voiceflow API Reference - Filter with Metadata](https://docs.voiceflow.com/reference/filter-with-metadata)

## Overview

Voiceflow's Knowledge Base API provides advanced query filtering capabilities that enable precise searches within your data using a robust set of operators. This documentation covers how to implement metadata filtering for enhanced knowledge base queries.

## Advanced Query Filtering

The filtering system supports various operators for complex data retrieval:

### Supported Operators

- **Equality and Comparison:** `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`
- **Array Operations**: `$in`, `$nin`, `$all`
- **Logical Operators**: `$and`, `$or`

These operators enable you to create complex queries for precise data retrieval, such as:
- Finding products under a certain price
- Filtering by multiple tags
- Combining multiple conditions

## How to Use

### Adding Metadata to Data Sources

Voiceflow supports three methods for adding metadata to your data sources:

#### 1. FILE Upload

Upload files with associated metadata using the multipart/form-data format:

```bash
curl --request POST \
--url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload?overwrite=true' \
--header 'Authorization: YOUR_DM_API_KEY' \
--header 'Content-Type: multipart/form-data' \
--header 'User-Agent: insomnia/8.0.0' \
--form 'file=@/path/to/your/file.pdf' \
--form 'metadata={"inner": {"text": "some test value", "price": 5, "tags": ["t1", "t2", "t3", "t4"]}}'
```

#### 2. URL Upload

Upload documents from URLs with metadata:

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "data": {
        "type": "url",
        "url": "https://example.com/",
        "metadata": {"test": 5}
    }
}'
```

#### 3. TABLE Upload

Upload structured table data with searchable and metadata fields:

```bash
curl --request POST \
  --url 'https://api.voiceflow.com/v1/knowledge-base/docs/upload/table' \
  --header 'Authorization: YOUR_DM_API_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "data": {
        "name": "products",
        "schema": {
            "searchableFields": ["name", "description"],
            "metadataFields": ["developer", "project"]
        },
        "items": [
            {
                "name": "example_name",
                "description": "example_description",
                "developer": {
                    "name": "Jane Doe",
                    "level": "senior",
                    "skills": ["Python", "JavaScript"],
                    "languages": [
                        {
                            "name": "Russian"
                        },
                        {
                            "name": "German"
                        }
                    ]
                },
                "project": {
                    "name": "AI Development",
                    "deadline": "2024-12-31"
                }
            }
        ]
    }
}'
```

## Practical Query Examples

### Match All Specific Tags (`$all` operator)

Identify chunks that include every specified tag in the list:

```json
{
    "filters": {
        "inner.tags": {
            "$all": ["t1", "t2"]
        }
    }
}
```

### Match Any of the Specified Tags (`$in` operator)

Find chunks containing any of the tags listed:

```json
{
    "filters": {
        "inner.tags": {
            "$in": ["t1", "t2"]
        }
    }
}
```

### Exclude Chunks With Certain Metadata (`$nin` operator)

Filter out chunks that include any of the specified values:

```json
{
    "filters": {
        "developer.skills": {
            "$nin": ["Python", "Rust"]
        }
    }
}
```

### Combination of Conditions (`$or` operator)

Search for chunks that match multiple conditions using logical OR:

```json
{
    "filters": {
        "$or": [
            {
                "inner.tags": {
                    "$in": ["t1"]
                }
            },
            {
                "inner.price": {
                    "$eq": 5
                }
            }
        ]
    }
}
```

## Complete Query Request Example

Here's a comprehensive example showing how to structure a complete query request with filters:

```json
{
  "chunkLimit": 2,
  "synthesis": true,
  "settings": {
    "model": "claude-instant-v1",
    "temperature": 0.1,
    "system": "You are an AI FAQ assistant. Information will be provided to help answer the user's questions. Always summarize your response to be as brief as possible and be extremely concise. Your responses should be fewer than a couple of sentences. Do not reference the material provided in your response."
  },
  "question": "what are some museums I can visit",
  "filters": {
    "Price": {
      "$eq": 5
    }
  }
}
```

## Key Parameters

- **chunkLimit**: Maximum number of chunks to return
- **synthesis**: Whether to synthesize the response
- **settings**: Configuration for the AI model response
- **question**: The user's query
- **filters**: Metadata filtering conditions

## Best Practices

1. **Nested Metadata**: Use dot notation to access nested metadata fields (e.g., `"developer.skills"`)
2. **Array Operations**: Use `$all` for exact matches and `$in` for partial matches
3. **Logical Combinations**: Leverage `$and` and `$or` for complex filtering logic
4. **Performance**: Consider chunk limits to optimize response times

---

*Last updated: About 1 month ago*
*Documentation scraped from: https://docs.voiceflow.com/reference/filter-with-metadata* 