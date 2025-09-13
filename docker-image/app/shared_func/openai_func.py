import config
from openai import OpenAI
import re

# Initialize OpenAI client with your API key
client = OpenAI(api_key = config.openai_api_key)


def sentiment_analysis(transcription):
    transcription = ", ".join(transcription)
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": f"As an AI with expertise in sentiment analysis, your task is to analyze the sentiment of the following text. Please evaluate the overall sentiment conveyed by the language used and provide a numerical sentiment score between 0 and 1, where 0 represents a very negative sentiment and 1 represents a very positive sentiment. The text to analyze is: '{transcription}'"
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )

    # Extract the content from the response
    completion = response.choices[0].message.content.strip()

    # Use regex to find the first float in the response
    match = re.search(r"[-+]?\d*\.\d+|\d+", completion)
    if match:
        sentiment_score = float(match.group())
    else:
        raise ValueError("No numeric sentiment score found in the response")

    return sentiment_score
