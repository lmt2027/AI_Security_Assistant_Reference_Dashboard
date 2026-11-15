import unittest
from unittest.mock import patch, MagicMock
import sys
import types
import ai_assistant

class OpenAITests(unittest.TestCase):
    def test_default_model(self):
        self.assertEqual(ai_assistant.DEFAULT_MODEL, "gpt-4o-mini")

    def test_request_uses_openai(self):
        response = MagicMock()
        response.choices[0].message.content = "Demo answer"
        with patch.object(ai_assistant, "get_api_key", return_value="test-key"), \
             patch.object(ai_assistant, "build_database_context", return_value="Synthetic login event"), \
             patch.dict(sys.modules, {"openai": types.SimpleNamespace(OpenAI=MagicMock())}):
            client_type = sys.modules["openai"].OpenAI
            client_type.return_value.chat.completions.create.return_value = response
            self.assertEqual(ai_assistant.ask_ai("What happened?"), "Demo answer")
            self.assertNotIn("base_url", client_type.call_args.kwargs)
            kwargs = client_type.return_value.chat.completions.create.call_args.kwargs
            self.assertEqual(kwargs["model"], "gpt-4o-mini")
            self.assertEqual(kwargs["messages"][0]["role"], "system")

if __name__ == "__main__":
    unittest.main()
