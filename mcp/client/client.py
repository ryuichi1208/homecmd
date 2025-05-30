from pydantic_ai import Agent

agent = Agent(
    'gemini-1.5-flash',
    system_prompt='Be concise, reply with one sentence.'  # システムプロンプト例
)

result = agent.run_sync('Where does "hello world" come from?')

print(result.output)
