"""Commercial Agent - L-FDS
Agent autonome pour la gestion CRM HubSpot et les emails de prospection.
"""

import os
import json

import anthropic
from dotenv import load_dotenv

from config.system_prompt import get_system_prompt
from tools import ALL_TOOLS, execute_tool

load_dotenv()


def run_agent(user_message: str) -> str:
    """Run the commercial agent with a user message.

    The agent loops automatically: it calls tools, processes results,
    and continues until it has a final answer.
    """
    client = anthropic.Anthropic()
    system_prompt = get_system_prompt()

    messages = [{"role": "user", "content": user_message}]

    print(f"\n{'='*60}")
    print(f"AGENT COMMERCIAL - Traitement de la demande...")
    print(f"{'='*60}\n")

    max_iterations = 15
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
            system=system_prompt,
            tools=ALL_TOOLS,
            messages=messages,
        )

        # If Claude is done (no more tool calls), return the text
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            return final_text

        # Process tool calls
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        # Show intermediate text
        for block in text_blocks:
            if block.text.strip():
                print(f"[Agent] {block.text[:200]}")

        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        # Execute tools and collect results
        tool_results = []
        for tool in tool_use_blocks:
            print(f"  -> Tool: {tool.name}({json.dumps(tool.input, ensure_ascii=False)[:100]})")

            result = execute_tool(tool.name, tool.input)

            # Truncate very long results
            if len(result) > 5000:
                result = result[:5000] + "... (truncated)"

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    return "Agent stopped: maximum iterations reached."


def interactive_mode():
    """Run the agent in interactive mode (chat loop)."""
    print("\n" + "=" * 60)
    print("  AGENT COMMERCIAL L-FDS")
    print("  Tape 'quit' pour quitter")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n[Baptiste] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Au revoir!")
            break

        result = run_agent(user_input)
        print(f"\n[Agent Commercial]\n{result}")


if __name__ == "__main__":
    interactive_mode()
