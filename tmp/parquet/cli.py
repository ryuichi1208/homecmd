import ollama
import time

# ================== グローバル設定 =================
MODEL_NAME_A = "gemma3:1b"
MODEL_NAME_B = "gemma3:1b"

MAX_HISTORY = 8
conversation_history = []

ROLE_PROMPT_A = "あなたは新人ソフトウェアエンジニアです。なりきってたくさん先輩に質問してください。質問は具体的で、専門用語を使わず、わかりやすく説明してください。"
ROLE_PROMPT_B = "あなたは優秀なソフトウェアエンジニアです。公開からの質問に対して、丁寧に答えてください。専門用語を使わず、わかりやすく説明してください。"


def generate_llm_response(assistant_role):

    global conversation_history

    if assistant_role == "assistant_A":
        system_prompt = ROLE_PROMPT_A
        model_name = MODEL_NAME_A
    elif assistant_role == "assistant_B":
        system_prompt = ROLE_PROMPT_B
        model_name = MODEL_NAME_B
    else:
        raise ValueError("assistant_role は 'assistant_A' または 'assistant_B' で指定してください。")

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    conversation_text = ""
    for turn in conversation_history:
        if turn["role"] == "assistant_A":
            conversation_text += f"イエス(A): {turn['content']}\n"
        elif turn["role"] == "assistant_B":
            conversation_text += f"釈迦(B): {turn['content']}\n"

    # もし会話履歴があれば、userロールとしてまとめて追加
    if conversation_text.strip():
        messages.append({"role": "user", "content": conversation_text})

    response = ollama.chat(model=model_name, messages=messages)

    response_text = ""
    if response and "message" in response:
        response_text = response["message"].get("content", "").strip()

    # ▼ 5) 会話履歴に今回の発話を追加
    conversation_history.append({
        "role": assistant_role,
        "content": response_text
    })
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    return response_text

if __name__ == "__main__":
    conversation_round = 0
    try:
        while True:
            conversation_round += 1
            print(f"--- {conversation_round} ---")

            # Aが発話
            response_A = generate_llm_response("assistant_A")
            print("LLM_Aの発話:", response_A)

            # Bが発話
            response_B = generate_llm_response("assistant_B")
            print("LLM_Bの発話:", response_B)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nキーボード割り込みにより終了します。")
