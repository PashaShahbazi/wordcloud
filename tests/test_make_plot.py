import unittest
from unittest.mock import Mock, patch

import make_plot


class PlotTests(unittest.TestCase):
    @patch("make_plot.plt.axis")
    @patch("make_plot.plt.imshow")
    @patch("make_plot.plt.figure")
    def test_preview_uses_reasonable_figure_size(self, figure, imshow, axis):
        cloud = Mock()

        make_plot.plot_cloud(cloud)

        figure.assert_called_once_with(figsize=(12, 8))
        imshow.assert_called_once_with(cloud)
        axis.assert_called_once_with("off")


if __name__ == "__main__":
    unittest.main()
