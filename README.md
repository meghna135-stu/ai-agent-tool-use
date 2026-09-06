# AI Agent with Tool Use

A simple Python AI agent built with the Groq API that can decide when to call tools — a calculator and a live weather lookup — and remembers conversation context across turns.

## How it works

The model can't act on its own. It reads your prompt and either answers directly, or requests a tool call (e.g. `get_weather(city="Bengaluru")`). Your code executes the tool and sends the result back so the model can give a final answer.

```
Prompt → Model decides → Tool call? → Your code runs it → Result → Model's final answer
```

## Tools

- 🧮 `calculate` — evaluates basic math expressions (sandboxed)
- 🌦️ `get_weather` — fetches live weather for any city (via Open-Meteo, chained geocoding + forecast calls)

## Setup

1. Get a free API key from [console.groq.com](https://console.groq.com/)
2. Set it as an environment variable:
   ```
   setx GROQ_API_KEY "your-key-here"   # Windows
   export GROQ_API_KEY="your-key-here" # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install groq requests
   ```
4. Run it:
   ```
   python agent.py
   ```

## Example

```
You: What's the weather in Mumbai?
Agent: The current weather in Mumbai is 28.3°C with a wind speed of 10.5 km/h.

You: Compare it with Bengaluru's weather
Agent: Bengaluru is about 2°C warmer and slightly windier than Mumbai right now.
```

## Next up

- More tools + chaining multiple tool calls in one turn
- Basic web search tool
