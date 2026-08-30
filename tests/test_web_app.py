import unittest
from unittest.mock import patch

import httpx

from web.app import GENERATED_DIR, app


class WebApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_reports_ok(self):
        response = await self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("web.app.create_cloud")
    async def test_wordcloud_generation_uses_request_data(self, create_cloud):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, "python learning word cloud"),
                "background_color": (None, "white"),
                "width": (None, "640"),
                "height": (None, "480"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "image_url": "/generated/wordcloud.png",
                "width": 640,
                "height": 480,
            },
        )
        create_cloud.assert_called_once_with(
            "python learning word cloud",
            "white",
            width=640,
            height=480,
        )
        create_cloud.return_value.to_file.assert_called_once_with(
            str(GENERATED_DIR / "wordcloud.png")
        )

    @patch("web.app.create_cloud")
    async def test_wordcloud_generation_rejects_empty_text(self, create_cloud):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, ""),
                "background_color": (None, "white"),
            },
        )

        self.assertEqual(response.status_code, 422)
        create_cloud.assert_not_called()


if __name__ == "__main__":
    unittest.main()
