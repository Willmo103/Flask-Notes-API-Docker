// main.js

function handleFileSelect(evt) {
  evt.stopPropagation();
  evt.preventDefault();

  let files = evt.dataTransfer.files; // FileList object.

  // Only process the first file
  let file = files[0];

  // Render the file in the drop zone
  let dropZone = document.getElementById("dropZone");
  dropZone.textContent = file.name;
  dropZone.classList.remove("drag-over");

  // Add the file to the input field
  let inputFile = document.getElementById("file");
  inputFile.files = files;
}

function handleDragOver(evt) {
  evt.stopPropagation();
  evt.preventDefault();
  evt.dataTransfer.dropEffect = "copy"; // Explicitly show this is a copy.
  let dropZone = document.getElementById("dropZone");
  dropZone.classList.add("drag-over");
}

function handleDragLeave(evt) {
  evt.stopPropagation();
  evt.preventDefault();
  let dropZone = document.getElementById("dropZone");
  dropZone.classList.remove("drag-over");
}

// Setup the drag and drop listeners
document.addEventListener("DOMContentLoaded", function () {
  let dropZone = document.getElementById("dropZone");
  if (dropZone) {
    dropZone.addEventListener("dragover", handleDragOver, false);
    dropZone.addEventListener("dragleave", handleDragLeave, false);
    dropZone.addEventListener("drop", handleFileSelect, false);
  }
});
