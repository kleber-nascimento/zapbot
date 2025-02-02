import requests
import os
import json
import logging
import ollama
logger = logging.getLogger(__name__)
from datetime import datetime


# BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:1234') # LM studio
BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434') # ollama

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def get_models():
    return _get('v1/models')

def chat_completions(messages, model='default-model'):
    return _post('v1/chat/completions', messages=messages, model=model)

def chat_completions_ollama(messages, model='llama3.1'):
    r = _post('api/chat', messages=messages, model=model, stream=False)
    logger.info(f"PROMPTING {model}:\n{json.dumps(messages, indent=2)}\n\n\nREPLY_LLM\n{r['message']['content']}")
    return r['message']

def chat_completions_ollama_functions(messages, tools, tool_caller, model='llama3.1'):
    messages = messages[:]
    size_in = len(messages)
    client = ollama.Client()
    while True:
        response = client.chat(model=model, messages=messages, tools=tools)
        messages.append(response['message'])
        if not response['message'].get('tool_calls'):
            break
        for tool in response['message']['tool_calls']:
            fnresponse = tool_caller.call(tool)
            messages.append({'role': 'tool', 'content': json.dumps(fnresponse, default=json_serial)})
    return messages[size_in:]

def embeddings(input_text, model='default-model'):
    return _post('v1/embeddings', input=input_text, model=model)

def _post(command, expectCode=200, **kwargs):
    url = f"{BASE_URL}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=kwargs)
    if response.status_code == expectCode:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _get(command):
    url = f"{BASE_URL}/{command}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error. Status code: {response.status_code} {response.json()}")

def _dummy_test():
    try:
        imgbase64 = "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"
        messages = [
            #{"role": "user", "content": "Escreva uma descrição para esta imagem. Em português.", "images": [imgbase64]},
            # {
            #     "role": "assistant",
            #     "content": "I'm a large language model, so I don't have emotions or feelings like humans do. However, I're here to help and support you in any way I can. How about you? How's your day going?"
            # },
            # {"role": "user", "content": "Pretend you have."}
             {"role": "user", "content": "Tell me a joke"},
            # {"role": "assistant", "content": "Why did the chicken cross the street? To get to the other side! Haha"},
            # {"role": "user", "content": "Another"},
        ]
        response = chat_completions_ollama(messages, 'llama3.2')
        import json
        print(json.dumps(response, indent=2))
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    _dummy_test()
