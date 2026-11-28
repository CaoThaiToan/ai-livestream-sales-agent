import json
import unittest
from unittest.mock import patch

from agent.catalog import default_catalog
from agent.query import select_products
from agent.service import answer_question
from llm import llm_response


class ProductLookupTests(unittest.TestCase):
    def product_ids(self, question):
        products, _ = select_products(default_catalog, question)
        return [product["id"] for product in products]

    def test_strict_and_inclusive_price_boundaries(self):
        self.assertEqual(self.product_ids("Chuột dưới 299 nghìn"), [])
        self.assertEqual(self.product_ids("Chuột tối đa 299 nghìn"), ["SP001"])
        self.assertEqual(self.product_ids("Chuột dưới 300.000 đồng"), ["SP001"])
        self.assertEqual(
            self.product_ids("Bàn phím tối đa 1,5 triệu"),
            ["SP004", "SP005", "SP006"],
        )

    def test_recommendations_exclude_sold_out_products(self):
        self.assertEqual(self.product_ids("Chuột dưới 600k"), ["SP001", "SP002"])

    def test_named_sold_out_products_remain_available_for_lookup(self):
        self.assertEqual(self.product_ids("Delux M618 Mini còn hàng không?"), ["SP003"])
        self.assertEqual(
            self.product_ids("Hub Ugreen 70411 giá bao nhiêu, muốn mua một chiếc?"),
            ["SP012"],
        )

    def test_named_product_retains_failed_budget_verdict(self):
        products, instruction = select_products(default_catalog, "M220 dưới 200 nghìn?")
        self.assertEqual([product["id"] for product in products], ["SP001"])
        self.assertIn("không đáp ứng", instruction)
        self.assertIn("299000", instruction)
        self.assertIn("200000", instruction)

    def test_comparisons_keep_both_named_products(self):
        self.assertEqual(
            self.product_ids("So sánh Havit H2002D và Sony WH-CH720N"),
            ["SP007", "SP009"],
        )

    def test_mouse_pad_does_not_select_mice(self):
        self.assertEqual(self.product_ids("Lót chuột dưới 100k"), ["SP014"])
        self.assertEqual(
            self.product_ids("Phụ kiện dưới 100k để di chuột mượt mà"), ["SP014"]
        )

    def test_unknown_product_does_not_select_an_alternative(self):
        self.assertEqual(self.product_ids("SP999 còn hàng không?"), [])
        self.assertEqual(self.product_ids("Chuột Logitech M999 còn không?"), [])

    def test_context_keeps_full_product_and_policy_data(self):
        product = default_catalog.get_product("SP001")
        context = default_catalog.format_context_for_prompt([product])
        for feature in product["features"]:
            self.assertIn(feature, context)
        self.assertIn(product["description"], context)
        self.assertIn(default_catalog.policy_text, context)
        self.assertNotIn('"SP002"', context)


class AgentLookupIntegrationTests(unittest.TestCase):
    def test_normal_avatar_entry_point_uses_selected_context(self):
        class Avatar:
            sessionid = "lookup-test"

            def __init__(self):
                self.messages = []

            def put_msg_txt(self, text, metadata):
                self.messages.append((text, metadata))

        expected_answer = "Chuột Delux M618 Mini hiện đã hết hàng."
        avatar = Avatar()
        with patch("openai.OpenAI") as client_class:
            completion = client_class.return_value.chat.completions.create
            completion.return_value.choices[0].message.content = json.dumps({
                "answer": expected_answer,
                "product_ids": ["SP003"],
                "status": "ok",
            })
            llm_response("Delux M618 Mini còn hàng không?", avatar, {"case": "W5"})

        prompt = completion.call_args.kwargs["messages"][1]["content"]
        self.assertIn('"SP003"', prompt)
        self.assertNotIn('"SP001"', prompt)
        self.assertEqual(avatar.messages, [(expected_answer, {"case": "W5"})])

    def test_response_with_unselected_product_returns_error(self):
        with patch("openai.OpenAI") as client_class:
            completion = client_class.return_value.chat.completions.create
            completion.return_value.choices[0].message.content = json.dumps({
                "answer": "Mẫu Razer còn hàng.",
                "product_ids": ["SP002"],
                "status": "ok",
            })
            response = answer_question("lookup-test", "M220 giá bao nhiêu?")
        self.assertEqual(response["status"], "error")


if __name__ == "__main__":
    unittest.main()
