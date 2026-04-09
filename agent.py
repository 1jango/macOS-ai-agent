#!/usr/bin/env python3
import ollama
import subprocess
import os


# Setup environment variables
HOME = os.path.expanduser("~")
MODEL = "llama3"


def get_ai_command(user_query):
    # System prompt to define behavior and safety
    system_prompt = f"""
  - OUTPUT ONLY THE COMMAND. 
    - DO NOT provide explanations, notes, or commentary.
    - DO NOT use markdown formatting (no backticks, no code blocks).
    - If you provide multiple lines, they must all be valid shell commands.
    - If the user provides a filename without an extension, append an asterisk (*).
    - NEVER use 'rm', always use 'trash'.
    - Use absolute paths starting from {HOME}
    - Prioritize simple, readable commands (like 'ls', 'grep', 'du -sh').
    - Avoid complex '-exec' chains unless absolutely necessary.
    - For "largest files", prefer 'ls -lSh' or 'du -sh * | sort -h'.
    - Ensure commands are compatible with macOS (BSD) utilities, not GNU/Linux.
    - Use the SHORTEST and SIMPLEST modern macOS command possible.
"""
    try:
        response = ollama.generate(model=MODEL, system=system_prompt, prompt=user_query, stream=False)
        return response['response'].strip()
    except Exception as e:
        return f"ERROR: Connection failed ({e})"


def execute_command(command):
    # Hardcoded safety filter to block destructive strings
    forbidden = ['rm ', 'rm-', 'delete', 'truncate', '> /dev/']
    if any(term in command.lower() for term in forbidden) or "ERROR" in command:
        print(f"Safety Block: Command rejected. ({command})")
        return

    print(f"Suggested Command: {command}")
    confirm = input("Execute? (y/n): ").lower()

    if confirm == 'y':
        try:
            # Execute command using system shell
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print("Success")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Execution Error: {e.stderr}")
    else:
        print("Skipped")


if __name__ == "__main__":
    print(r"""
         __
 _(\    |@@|
(__/\__ \--/ __
   \___|----|  |   __
       \ }{ /\ )_ / _\
       /\__/\ \__O (__
      (--/\--)    \__/
      _)(  )(_
     `---''---`
            """)
    print("--- macOS AI Agent active (Type 'exit' to stop) ---")


    while True:
        try:
            query = input("Prompt > ")

            if query.lower() in ['exit', 'quit', 'q']:
                print("Exiting...")
                break

            if not query.strip():
                continue

            generated_cmd = get_ai_command(query)
            execute_command(generated_cmd)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
            break