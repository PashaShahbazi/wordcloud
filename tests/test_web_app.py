import unittest
from io import BytesIO
from unittest.mock import AsyncMock, patch

import httpx
from PIL import Image

from get_wiki import WikipediaLookupError
from web.app import GENERATED_DIR, app


def image_bytes(image_format, size=(120, 120)):
    output = BytesIO()
    Image.new("L", size, color=0).save(output, format=image_format)
    return output.getvalue()


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

    @patch("web.app.create_cloud")
    @patch("web.app.create_cloud_mask")
    async def test_wordcloud_generation_resizes_png_mask(
        self,
        create_cloud_mask,
        create_cloud,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, "python learning word cloud"),
                "background_color": (None, "white"),
                "width": (None, "640"),
                "height": (None, "480"),
                "mask": ("mask.png", image_bytes("PNG"), "image/png"),
            },
        )

        self.assertEqual(response.status_code, 200)
        create_cloud.assert_not_called()

        text, background_color, mask = create_cloud_mask.call_args.args
        self.assertEqual(text, "python learning word cloud")
        self.assertEqual(background_color, "white")
        self.assertEqual(mask.shape, (480, 640))
        create_cloud_mask.return_value.to_file.assert_called_once_with(
            str(GENERATED_DIR / "wordcloud.png")
        )

    @patch("web.app.create_cloud_mask")
    async def test_wordcloud_generation_rejects_non_png_mask(
        self,
        create_cloud_mask,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, "python learning word cloud"),
                "mask": ("mask.jpg", image_bytes("JPEG"), "image/jpeg"),
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Mask image must be a PNG file.")
        create_cloud_mask.assert_not_called()

    @patch("web.app.MAX_MASK_BYTES", 10)
    @patch("web.app.create_cloud_mask")
    async def test_wordcloud_generation_rejects_oversized_mask_file(
        self,
        create_cloud_mask,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, "python learning word cloud"),
                "mask": ("mask.png", b"x" * 11, "image/png"),
            },
        )

        self.assertEqual(response.status_code, 413)
        create_cloud_mask.assert_not_called()

    @patch("web.app.create_cloud_mask")
    async def test_wordcloud_generation_rejects_oversized_mask_dimensions(
        self,
        create_cloud_mask,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "text": (None, "python learning word cloud"),
                "mask": ("mask.png", image_bytes("PNG", (3001, 1)), "image/png"),
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Mask dimensions must not exceed 3000x3000 pixels.",
        )
        create_cloud_mask.assert_not_called()

    @patch("web.app.create_cloud")
    @patch("web.app.run_in_threadpool", new_callable=AsyncMock)
    @patch("web.app.wiki_get")
    async def test_wordcloud_generation_uses_normalized_wikipedia_text(
        self,
        wiki_get,
        run_in_threadpool,
        create_cloud,
    ):
        run_in_threadpool.return_value = (
            "Python\n== History ==\nprogramming language"
        )

        response = await self.client.post(
            "/api/wordcloud",
            files={
                "source_mode": (None, "wikipedia"),
                "wikipedia_subject": (None, "  Python  "),
                "background_color": (None, "white"),
                "width": (None, "640"),
                "height": (None, "480"),
            },
        )

        self.assertEqual(response.status_code, 200)
        run_in_threadpool.assert_awaited_once_with(wiki_get, "Python")
        create_cloud.assert_called_once_with(
            "Python programming language",
            "white",
            width=640,
            height=480,
        )

    @patch("web.app.create_cloud")
    @patch("web.app.run_in_threadpool", new_callable=AsyncMock)
    @patch("web.app.wiki_get")
    async def test_wordcloud_generation_reports_wikipedia_lookup_error(
        self,
        wiki_get,
        run_in_threadpool,
        create_cloud,
    ):
        run_in_threadpool.side_effect = WikipediaLookupError(
            "No Wikipedia page was found for 'missing'."
        )

        response = await self.client.post(
            "/api/wordcloud",
            files={
                "source_mode": (None, "wikipedia"),
                "wikipedia_subject": (None, "missing"),
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "No Wikipedia page was found for 'missing'.",
        )
        run_in_threadpool.assert_awaited_once_with(wiki_get, "missing")
        create_cloud.assert_not_called()

    @patch("web.app.run_in_threadpool", new_callable=AsyncMock)
    async def test_wordcloud_generation_requires_wikipedia_subject(
        self,
        run_in_threadpool,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={"source_mode": (None, "wikipedia")},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json()["detail"],
            "Wikipedia subject cannot be empty.",
        )
        run_in_threadpool.assert_not_awaited()

    @patch("web.app.run_in_threadpool", new_callable=AsyncMock)
    async def test_wordcloud_generation_rejects_long_wikipedia_subject(
        self,
        run_in_threadpool,
    ):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "source_mode": (None, "wikipedia"),
                "wikipedia_subject": (None, "x" * 201),
            },
        )

        self.assertEqual(response.status_code, 422)
        run_in_threadpool.assert_not_awaited()

    async def test_wordcloud_generation_rejects_unknown_source_mode(self):
        response = await self.client.post(
            "/api/wordcloud",
            files={
                "source_mode": (None, "file"),
                "text": (None, "python learning word cloud"),
            },
        )

        self.assertEqual(response.status_code, 422)

    @patch("web.app.create_cloud")
    @patch("web.app.run_in_threadpool", new_callable=AsyncMock)
    async def test_wordcloud_generation_rejects_empty_wikipedia_article(
        self,
        run_in_threadpool,
        create_cloud,
    ):
        run_in_threadpool.return_value = "  \n== Empty ==\n"

        response = await self.client.post(
            "/api/wordcloud",
            files={
                "source_mode": (None, "wikipedia"),
                "wikipedia_subject": (None, "Empty article"),
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "The Wikipedia article did not contain any usable text.",
        )
        create_cloud.assert_not_called()


if __name__ == "__main__":
    unittest.main()
