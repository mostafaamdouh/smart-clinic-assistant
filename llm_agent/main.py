from agent.agent import run_agent

def main():
    print("🏥 Clinic Assistant — Type 'exit' to quit")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            continue
            
        try:
            result = run_agent(user_input)
            print(f"Assistant: {result}")
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()