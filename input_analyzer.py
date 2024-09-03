import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


def analyze_input(user_input):
    tokens = word_tokenize(user_input.lower())

    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]

    intents = {
        'question': ['what', 'why', 'how', 'when', 'where', 'who'],
        'command': ['do', 'please', 'can', 'could', 'would'],
        'statement': ['is', 'are', 'was', 'were']
    }

    detected_intent = 'unknown'
    for intent, keywords in intents.items():
        if any(word in filtered_tokens for word in keywords):
            detected_intent = intent
            break

    return {
        'original_input': user_input,
        'tokens': filtered_tokens,
        'intent': detected_intent
    }