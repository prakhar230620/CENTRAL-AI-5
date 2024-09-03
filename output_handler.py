import pyttsx3


def process_output(raw_output):
    processed_output = f"Processed: {raw_output}"

    # Text-to-speech conversion
    try:
        engine = pyttsx3.init()
        engine.say(processed_output)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech conversion: {str(e)}")

    return processed_output