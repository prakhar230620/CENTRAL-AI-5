from ai_manager import get_ai, list_ais
import importlib
import requests
import subprocess


def select_and_process(analyzed_input):
    selected_ai = select_ai(analyzed_input)

    if selected_ai:
        return process_with_ai(selected_ai, analyzed_input)
    else:
        return "No suitable AI found to process the input."


def select_ai(analyzed_input):
    ais = list_ais()
    # This is a simple selection method. You may want to implement a more sophisticated one.
    for ai in ais:
        if any(token in ai['details'].get('description', '').lower() for token in analyzed_input['tokens']):
            return ai
    return None


def process_with_ai(ai_info, analyzed_input):
    if ai_info['type'] == 'API':
        return process_with_api(ai_info, analyzed_input)
    elif ai_info['type'] == 'Bot':
        return process_with_bot(ai_info, analyzed_input)
    elif ai_info['type'] == 'Local AI':
        return process_with_local_ai(ai_info, analyzed_input)
    elif ai_info['type'] == 'Custom AI':
        return process_with_custom_ai(ai_info, analyzed_input)
    else:
        return "Unsupported AI type"


def process_with_api(ai_info, analyzed_input):
    api_key = ai_info['details']['api_key']
    endpoint = ai_info['details']['endpoint']
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'input': analyzed_input['original_input']}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json().get('output', 'No output from API')
    except requests.RequestException as e:
        return f"Error from API: {str(e)}"


def process_with_bot(ai_info, analyzed_input):
    bot_file = ai_info['details']['file_path']
    try:
        spec = importlib.util.spec_from_file_location("bot_module", bot_file)
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)

        if hasattr(bot_module, 'process'):
            return bot_module.process(analyzed_input['original_input'])
        else:
            return "Error: Bot file does not have a 'process' function"
    except Exception as e:
        return f"Error processing with bot: {str(e)}"


def process_with_local_ai(ai_info, analyzed_input):
    command = ai_info['details']['command']
    full_command = f"{command} '{analyzed_input['original_input']}'"

    try:
        result = subprocess.run(full_command, shell=True, check=True, capture_output=True, text=True, timeout=30)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running local AI: {e.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Local AI process timed out"


def process_with_custom_ai(ai_info, analyzed_input):
    custom_ai_file = ai_info['details']['file_path']
    try:
        spec = importlib.util.spec_from_file_location("custom_ai_module", custom_ai_file)
        custom_ai_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_ai_module)

        if hasattr(custom_ai_module, 'process'):
            return custom_ai_module.process(analyzed_input['original_input'])
        else:
            return "Error: Custom AI file does not have a 'process' function"
    except Exception as e:
        return f"Error processing with custom AI: {str(e)}"