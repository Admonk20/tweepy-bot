import tweepy
import time
import requests
import json

# Twitter API credentials
api_key = "bLQ7BQ4yJaVNWZNLUYywTyWyy"
api_secret = "E2pBhW19zKglxsXyPbh506Sjzem77mvXDkkV21YETmVVoHPz4a"
bearer_token = r"AAAAAAAAAAAAAAAAAAAAAHN%2ByQEAAAAAEoD17VawewNd3JLUOnCRI4o9sFY%3DTL3ujWQwqRbbPGMcusLALcmfBRUrvqZeBGbsQZzBTLLhHfhB6X"
access_token = "1881434884427976705-7WSV9yFujefAqr1pv7c8xffvuJRATH"
access_token_secret = "OD2Xstk3o8vLXGqzBywawTSxHKeKdSTTDVi8sHzTDfzbj"

# Gemini API Key
gemini_api_key = "AIzaSyC3gHLCPrhLLGe8HKw_9votWzeUagEnHbM"

# Initialize Tweepy client & API object
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Get Twitter user ID
client_id = client.get_me().data.id

# Fetch latest mention ID to avoid duplicate replies
start_id = 1
while True:
    try:
        initial_mentions = client.get_users_mentions(client_id)
        break  # Exit the loop if successful
    except tweepy.errors.TooManyRequests:
        print("Too many requests while fetching initial mentions. Waiting for 15 minutes before retrying...")
        time.sleep(900)  # Wait for 15 minutes
if initial_mentions.data:
    start_id = initial_mentions.data[0].id


def get_gemini_response(user_message):
    """Generate AI response using Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText?key={gemini_api_key}"
    
    payload = {
        "prompt": {"text": f"Reply to this tweet: \"{user_message}\""},
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response_data = response.json()
        
        return response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Thanks for mentioning me!")
    except Exception as e:
        print("Error calling Gemini API:", e)
        return "I'm unable to provide a response right now."


# Main loop to check mentions and reply
while True:
    try:
        response = client.get_users_mentions(client_id, since_id=start_id)
    except tweepy.errors.TooManyRequests:
        print("Too many requests. Waiting for 15 minutes before retrying...")
        time.sleep(900)  # Wait for 15 minutes
        continue

    if response.data:
        for tweet in response.data:
            try:
                print(f"Processing tweet: {tweet.text}")

                # Generate AI response
                reply_text = get_gemini_response(tweet.text)

                # Reply to the mention
                client.create_tweet(in_reply_to_tweet_id=tweet.id, text=reply_text)
                print(f"Replied: {reply_text}")

                # Update last processed tweet ID
                start_id = tweet.id

            except Exception as error:
                print("Error processing tweet:", error)

    # Wait 10 minutes to avoid rate limits
    time.sleep(1020)
