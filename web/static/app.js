const textInput = document.getElementById("textInput");
const generateButton = document.getElementById("generateButton");
const resultImage = document.getElementById("resultImage");
const statusText = document.getElementById("status");
const backgroundColor = document.getElementById("backgroundColor");
const width = document.getElementById("width");
const height = document.getElementById("height");

generateButton.addEventListener("click", async () => {
  const text = textInput.value.trim();

  if (!text) {
    statusText.textContent = "Please enter some text.";
    return;
  }

  generateButton.disabled = true;
  statusText.textContent = "Generating...";

  try {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("background_color", backgroundColor.value);
    formData.append("width", width.value);
    formData.append("height", height.value);

    const response = await fetch("/api/wordcloud", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();

    resultImage.src = `${data.image_url}?t=${Date.now()}`;
    statusText.textContent = "Done.";
  } catch (error) {
    console.error(error);

    statusText.textContent =
      "Something went wrong while generating the WordCloud.";
  } finally {
    generateButton.disabled = false;
  }
});
