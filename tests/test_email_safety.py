import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
from gtm_agent.gtm_agent import SYSTEM_PROMPT, send_prospect_email


class SendProspectEmailSafetyTests(unittest.TestCase):
    def call_tool(self, prospect_id, **kwargs):
        return send_prospect_email.func(
            {"prospect_id": prospect_id, "name": "Test Prospect", "email": "test@example.com"},
            "Subject",
            "Body",
            runtime=None,
            from_rep={"name": "Test Rep", "email": "rep@example.com"},
            **kwargs,
        )

    def test_disqualified_prospect_is_blocked(self):
        result = self.call_tool("LEAD-50002")

        self.assertEqual(result, {"status": "blocked", "reason": "prospect disqualified"})

    def test_disqualified_prospect_can_be_overridden(self):
        result = self.call_tool("LEAD-50002", rep_confirmed_override=True)

        self.assertEqual(result["status"], "sent")

    def test_qualified_prospect_is_sent(self):
        result = self.call_tool("LEAD-12853")

        self.assertEqual(result["status"], "sent")

    def test_prompt_requires_disqualification_check_and_notice(self):
        self.assertIn("check its disqualified flag", SYSTEM_PROMPT)
        self.assertIn("tell the rep the prospect is disqualified", SYSTEM_PROMPT)
        self.assertNotIn("always carry the request through", SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
