from Chatbot.llm.chatollama import ChatOllamaBot

_bot = ChatOllamaBot(username="tester")

def chatbot_reply(question: str) -> str:
    return _bot.chat(question)