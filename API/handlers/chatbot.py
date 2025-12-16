import flask
from Chatbot.llm.chatbot_for_Collection import chatbot_reply

class ChatbotHandler:
    def getChatbotReply(self, payload):
        if not payload or "message" not in payload:
            return flask.jsonify({"error": "BAD REQUEST: Missing field 'message'"}), 400
        message = payload["message"]

        if not isinstance(message, str) or message.strip() == "":
            return flask.jsonify({"error": "BAD REQUEST: 'message' must be a non-empty string"}), 400
        reply = chatbot_reply(message)
        return flask.jsonify({"question":message, "reply": reply}), 200