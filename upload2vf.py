import requests

def upload_to_voiceflow(vf_api_key, content, filename, overwrite=False, max_chunk_size=1000):
    base_url = "https://api.voiceflow.com/v1/knowledge-base/docs/upload"
    params = {
        "overwrite": str(overwrite).lower(),
        "maxChunkSize": max_chunk_size
    }
    
    headers = {
        "accept": "application/json",
        "Authorization": vf_api_key
    }

    # Ensure the filename ends with .txt
    if not filename.lower().endswith('.txt'):
        filename += '.txt'

    # Remove summary tags from content
    content = content.replace("---START_SUMMARY---", "").replace("---END_SUMMARY---", "").strip()

    files = {'file': (filename, content.encode('utf-8'), 'text/plain')}
    
    response = requests.post(base_url, params=params, headers=headers, files=files)

    return response.json()

def check_voiceflow_status(vf_api_key, document_id):
    url = f"https://api.voiceflow.com/v1/knowledge-base/docs/{document_id}/status"
    headers = {
        "Authorization": f"Bearer {vf_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()