const textInput = document.getElementById("textInput");
const generateButton = document.getElementById("generateButton");
const resultImage = document.getElementById("resultImage");
const previewFrame = document.getElementById("previewFrame");
const previewEmpty = document.getElementById("previewEmpty");
const downloadLink = document.getElementById("downloadLink");
const statusText = document.getElementById("status");
const backgroundColor = document.getElementById("backgroundColor");
const width = document.getElementById("width");
const height = document.getElementById("height");
const maskDropZone = document.getElementById("maskDropZone");
const maskDropPrompt = document.getElementById("maskDropPrompt");
const maskInput = document.getElementById("maskInput");
const selectedMask = document.getElementById("selectedMask");
const maskFileInfo = document.getElementById("maskFileInfo");
const removeMaskButton = document.getElementById("removeMaskButton");

const MAX_MASK_BYTES = 5 * 1024 * 1024;
const MAX_MASK_DIMENSION = 3000;
const PNG_SIGNATURE = [137, 80, 78, 71, 13, 10, 26, 10];
const GENERIC_ERROR_MESSAGE =
  "Something went wrong while generating the WordCloud.";

let selectedMaskFile = null;

function setStatus(message, state = "") {
  statusText.textContent = message;

  if (state) {
    statusText.dataset.state = state;
  } else {
    delete statusText.dataset.state;
  }
}

function parseDimension(input, label) {
  const value = Number(input.value);

  if (!Number.isInteger(value) || value < 100 || value > 3000) {
    throw new Error(`${label} must be a whole number between 100 and 3000.`);
  }

  return value;
}

async function getResponseErrorMessage(response) {
  try {
    const data = await response.json();

    if (typeof data.detail === "string" && data.detail.trim()) {
      return data.detail;
    }

    if (Array.isArray(data.detail)) {
      const messages = data.detail
        .map((error) => error.msg)
        .filter((message) => typeof message === "string" && message.trim());

      if (messages.length) {
        return messages.join(" ");
      }
    }
  } catch (error) {
    console.error("Unable to read the error response.", error);
  }

  return GENERIC_ERROR_MESSAGE;
}

function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getImageDimensions(file) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    const imageUrl = URL.createObjectURL(file);

    image.onload = () => {
      URL.revokeObjectURL(imageUrl);
      resolve({ width: image.naturalWidth, height: image.naturalHeight });
    };

    image.onerror = () => {
      URL.revokeObjectURL(imageUrl);
      reject(new Error("The selected file is not a valid PNG image."));
    };

    image.src = imageUrl;
  });
}

async function validateMaskFile(file) {
  if (file.size > MAX_MASK_BYTES) {
    throw new Error("The mask image must be 5 MB or smaller.");
  }

  const header = new Uint8Array(await file.slice(0, 8).arrayBuffer());
  const isPng = PNG_SIGNATURE.every((byte, index) => header[index] === byte);

  if (!isPng) {
    throw new Error("The mask image must be a PNG file.");
  }

  const dimensions = await getImageDimensions(file);

  if (
    dimensions.width > MAX_MASK_DIMENSION ||
    dimensions.height > MAX_MASK_DIMENSION
  ) {
    throw new Error("The mask dimensions must not exceed 3000×3000 pixels.");
  }
}

function clearMaskSelection() {
  selectedMaskFile = null;
  maskInput.value = "";
  maskFileInfo.textContent = "";
  selectedMask.hidden = true;
  maskDropZone.classList.remove("has-file");
  maskDropPrompt.textContent = "Drop a PNG mask here or click to browse.";
}

async function selectMaskFile(file) {
  try {
    await validateMaskFile(file);

    selectedMaskFile = file;
    maskFileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
    selectedMask.hidden = false;
    maskDropZone.classList.add("has-file");
    maskDropPrompt.textContent = "Drop another PNG here or click to replace.";
    setStatus("Mask selected.", "success");
  } catch (error) {
    clearMaskSelection();
    const message =
      error instanceof Error
        ? error.message
        : "The selected mask could not be validated.";
    setStatus(message, "error");
  }
}

maskDropZone.addEventListener("click", () => maskInput.click());

maskDropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    maskInput.click();
  }
});

maskInput.addEventListener("change", () => {
  const [file] = maskInput.files;

  if (file) {
    selectMaskFile(file);
  }
});

maskDropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  maskDropZone.classList.add("is-dragover");
});

maskDropZone.addEventListener("dragleave", () => {
  maskDropZone.classList.remove("is-dragover");
});

maskDropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  maskDropZone.classList.remove("is-dragover");

  const [file] = event.dataTransfer.files;

  if (file) {
    selectMaskFile(file);
  }
});

removeMaskButton.addEventListener("click", () => {
  clearMaskSelection();
  setStatus("Mask removed.");
});

generateButton.addEventListener("click", async () => {
  const text = textInput.value.trim();

  if (!text) {
    setStatus("Please enter some text.", "error");
    return;
  }

  let outputWidth;
  let outputHeight;

  try {
    outputWidth = parseDimension(width, "Width");
    outputHeight = parseDimension(height, "Height");
  } catch (error) {
    setStatus(error.message, "error");
    return;
  }

  generateButton.disabled = true;
  setStatus("Generating...", "loading");

  let errorMessage = GENERIC_ERROR_MESSAGE;

  try {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("background_color", backgroundColor.value);
    formData.append("width", String(outputWidth));
    formData.append("height", String(outputHeight));

    if (selectedMaskFile) {
      formData.append("mask", selectedMaskFile, selectedMaskFile.name);
    }

    const response = await fetch("/api/wordcloud", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      errorMessage = await getResponseErrorMessage(response);
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    const imageUrl = `${data.image_url}?t=${Date.now()}`;

    resultImage.src = imageUrl;
    resultImage.hidden = false;
    previewEmpty.hidden = true;
    previewFrame.classList.add("has-result");
    downloadLink.href = imageUrl;
    downloadLink.hidden = false;
    setStatus("Done.", "success");
  } catch (error) {
    console.error(error);
    setStatus(errorMessage, "error");
  } finally {
    generateButton.disabled = false;
  }
});
