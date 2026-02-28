// WebUI automatically injects a socket connection
const socket = window.socket;

// Listen for temperature updates
socket.on("temperature", (data) => {
  document.getElementById("temperature").innerText =
    data.value.toFixed(2) + " °C";
});

// Listen for heat index updates
socket.on("heat_index", (data) => {
  document.getElementById("heatIndex").innerText =
    data.value.toFixed(2) + " °C";
});

// Listen for object detections
socket.on("classifications", (message) => {
  const list = document.getElementById("detections");
  list.innerHTML = "";

  const data = JSON.parse(message);

  data.forEach(entry => {
    const li = document.createElement("li");
    li.innerText = `${entry.content} (${(entry.confidence * 100).toFixed(1)}%)`;
    list.appendChild(li);
  });
});

// Send threshold override to backend
function sendThreshold() {
  const value = parseFloat(document.getElementById("thresholdInput").value);
  socket.emit("override_th", value);
}