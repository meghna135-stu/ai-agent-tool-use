import os
import json
import requests
from groq import Groq


def get_client():
    """Create and return a Groq client using the API key from environment variables."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Did you set it with setx/export?")
    return Groq(api_key=api_key)


def calculate(expression):
    """Safely evaluate a basic math expression."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"


def get_weather(city):
    """Look up current weather for a given city name."""
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_response = requests.get(geo_url, params={"name": city, "count": 1}, timeout=5)
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"Could not find location: {city}"

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_response = requests.get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        }, timeout=5)
        weather_data = weather_response.json()

        current = weather_data.get("current_weather", {})
        temp = current.get("temperature")
        windspeed = current.get("windspeed")

        return f"In {city}: {temp}°C, wind speed {windspeed} km/h."

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather: {e}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a basic arithmetic expression, e.g. '12*7' or '(4+5)/3'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a given city name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name, e.g. 'Bengaluru' or 'Paris'.",
                    }
                },
                "required": ["city"],
            },
        },
    },
]


def ask_with_tools(prompt, messages, model="openai/gpt-oss-120b"):
    """Send a prompt (with full conversation history) and return the reply."""
    client = get_client()
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
    )
    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        print(f"[Model wants to call: {tool_call.function.name}]")
        print(f"[With arguments: {tool_call.function.arguments}]")

        args = None
        result = None
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            result = "Error: model returned invalid arguments."

        available_functions = {
            "calculate": calculate,
            "get_weather": get_weather,
        }

        if args is not None:
            func_name = tool_call.function.name
            func = available_functions.get(func_name)
            if func:
                result = func(**args)
            else:
                result = "Unknown tool"

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        final_message = second_response.choices[0].message
        messages.append(final_message)
        return final_message.content

    messages.append(message)
    return message.content


if __name__ == "__main__":
    print("Agent ready. Type 'quit' to exit.\n")
    conversation = []

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        reply = ask_with_tools(user_input, conversation)
        print(f"Agent: {reply}\n")