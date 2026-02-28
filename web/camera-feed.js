class CameraFeed extends HTMLElement {
  constructor() {
    super();

    // Create video element
    this.video = document.createElement("video");
    this.video.autoplay = true;
    this.video.muted = true;
    this.video.playsInline = true;
    this.video.width = this.getAttribute("width") || 640;
    this.video.height = this.getAttribute("height") || 360;
    this.video.style.background = "#000"; // black background

    // Append video directly to the component
    this.appendChild(this.video);
  }

  connectedCallback() {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => { this.video.srcObject = stream; })
      .catch(err => {
        console.error("Camera access error:", err);
        this.textContent = "Cannot access camera. Make sure permissions are allowed.";
      });
  }
}

// Register custom element
customElements.define("camera-feed", CameraFeed);