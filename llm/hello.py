from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

def chat(agent: Agent, message: str, message_history) -> str:
    result = agent.run_sync(message, message_history=message_history)
    return result


def main():
    ollama_model = OpenAIModel(
        model_name='dsasai/llama3-elyza-jp-8b',
        provider=OpenAIProvider(base_url='http://localhost:11434/v1')

    )
    agent1 = Agent(ollama_model, name='agent1', system_prompt="あなたは過激なvim派のエンジニアです。回答は端的に口語でお願いします。")
    agent2 = Agent(ollama_model, name='agent2', system_prompt="あなたは過激なemacs派のエンジニアです。回答は端的に口語でお願いします。")

    input_txt = str(input('Enter your message: '))
    response = chat(agent1, input_txt, message_history=None)
    message_history = []
    message_history.append(response.new_messages())
    while True:
        response = chat(agent2, response.output, message_history=message_history[-1])
        print(">>>")
        print(response.output)
        message_history.append(response.new_messages())
        response = chat(agent1, response.output, message_history=message_history[-1])
        print(">>>")
        print(response.output)
        message_history.append(response.new_messages())


if __name__ == '__main__':
    main()
