import config
from openai import OpenAI

# Initialize OpenAI client with your API key
client = OpenAI(api_key = config.openai_api_key)

# Initialize OpenAI API with your API key

def sentiment_analysis(comment):
    transcription = " ".join(map(str,comment))
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text. Please consider the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. "
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return completion.choices[0].message.content

def analyze_sentiment(comment):
    if comment is not None:
        response = client.completions.create(
            model="text-davinci-003",  # Choose the model according to your preference
            prompt=f"Classify sentiment as a numeric score from 0 to 1:\n{comment}\n",
            max_tokens=1,
            stop=["\n"]
        )
        try:
            sentiment_score = float(response.choices[0].text.strip())
            if 0 <= sentiment_score <= 1:
                return sentiment_score
            else:
                return None  # Invalid sentiment score
        except ValueError:
            return None  # Unable to extract a valid numeric sentiment score
    else:
        return None  # No comment provided
