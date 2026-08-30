# WordCloud Project

A small learning project that combines a reusable Python WordCloud core with a
FastAPI backend and a responsive Vanilla JavaScript interface. It can generate
a WordCloud from manually entered text or an English Wikipedia article, with
an optional PNG image mask.

The repository also retains its original terminal and Tkinter desktop workflow
as a legacy interface.

## Features

- Generate a WordCloud from manual text.
- Retrieve and normalize an English Wikipedia article by exact subject.
- Choose the background color and output dimensions.
- Optionally resize and apply a PNG mask.
- Preview and download the latest generated image.
- Use a responsive, accessible interface without a frontend framework.
- Run focused tests for the core, API, Wikipedia integration, and legacy flow.

## Requirements

- Python 3.12
- An internet connection when using Wikipedia mode
- A graphical desktop session and Tkinter only for the legacy desktop workflow

## Installation

From the repository root, create a virtual environment and install the project
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The virtual environment and generated application output are ignored by Git.

## Run the web interface

Start the FastAPI application from the repository root:

```bash
uvicorn web.app:app --reload
```

Open <http://127.0.0.1:8000> in a browser. The API health endpoint is available
at <http://127.0.0.1:8000/health>.

### Manual text mode

1. Leave **Manual text** selected.
2. Enter or paste source text.
3. Choose a background color and output dimensions.
4. Optionally select a PNG mask.
5. Select **Generate WordCloud**.

### Wikipedia mode

1. Select **Wikipedia** as the text source.
2. Enter an exact English Wikipedia article subject, up to 200 characters.
3. Configure the background, dimensions, and optional mask.
4. Select **Generate WordCloud**.

Wikipedia lookup uses exact matching with automatic suggestions disabled. Page
not found, ambiguous subject, and connection failures are shown in the web
interface. Retrieved article text is normalized in memory and is not displayed
or stored.

### PNG masks

The mask is optional. Drop a file onto the upload area or use it to open the
file picker.

- Only valid PNG images are accepted.
- The maximum upload size is 5 MB.
- Source dimensions must not exceed 3000×3000 pixels.
- The mask is converted to grayscale and resized to the selected output width
  and height.
- Uploaded masks are processed for the request and are not saved by the
  application.

High-contrast black-and-white masks generally produce the clearest shapes.

### Preview, download, and generated files

After successful generation, the preview appears in the output panel and a
**Download PNG** link downloads it as `wordcloud.png`.

The server stores only the latest result at `web/generated/wordcloud.png`.
Each successful request overwrites that file. The `web/generated/` directory
is ignored by Git; the project does not provide persistent or multi-user image
storage.

## Tests

Run the full test suite from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg python -m unittest discover -s tests -v
```

The tests cover text normalization, basic and masked WordCloud generation,
Wikipedia success and failure behavior through mocks, API validation and
generation paths, desktop import behavior, dialog cancellation, save ordering,
and plotting. Tests do not require live Wikipedia access or automated desktop
interaction.

## Legacy desktop workflow

The original interface remains available through `main.py`. It combines
terminal prompts with Tkinter file dialogs and a Matplotlib preview.

Tkinter is supplied by the operating system rather than PyPI. On Ubuntu,
Pop!_OS, and related distributions, install it if necessary:

```bash
sudo apt install python3-tk
```

Run the desktop workflow from the repository root:

```bash
python main.py
```

The desktop steps are:

1. Choose `f` for a local UTF-8 text file or `w` for a Wikipedia subject.
2. Choose whether to use a black-and-white PNG mask.
3. Enter a Matplotlib-compatible background color such as `white` or `black`.
4. Select an output filename in the save dialog.
5. View the saved image in the Matplotlib preview.

Canceling a file dialog exits the operation cleanly.

## Example output

![Cybersecurity WordCloud example](example-output/cybersecurity-wordcloud.png)

This example was generated from cybersecurity terminology. Its temporary mask
used the [Bootstrap Icons shield-lock-fill silhouette](https://icons.getbootstrap.com/icons/shield-lock-fill/),
which is provided under the project's
[MIT License](https://github.com/twbs/icons/blob/main/LICENSE). The source mask
is not stored in this repository.

## Dependencies

Direct dependencies are listed in `requirements.txt`:

- FastAPI and Uvicorn for the web application
- HTTPX for API tests
- python-multipart for form and file upload handling
- Matplotlib for the legacy preview
- NumPy and Pillow for mask processing
- wikipedia for article retrieval
- wordcloud for image generation

The `wikipedia` package is old and depends on Wikipedia's live service. Upstream
changes can affect live lookup even though expected failures are handled and
the automated tests use mocks.

## Project scope

This is intentionally a compact learning project rather than a production
service. It uses one generated output file, has no database or user accounts,
and favors straightforward FastAPI and Vanilla JavaScript code over additional
frameworks or infrastructure.
