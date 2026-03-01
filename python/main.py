# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

import math
import datetime
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC
import json

ui = WebUI()
detection_stream = VideoObjectDetection(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))
# Example usage: Register a callback for when a specific object is detected
def person_detected():
  pass  # Implement your logic here, e.g., send a notification

# detection_stream.on_detect("person", person_detected)

def record_sensor_samples(celsius: float):
    if celsius is None or not isinstance(celsius, (int, float)):
        print("Received invalid sensor samples: celsius=%s" % celsius)
        return

    # Push realtime updates to the UI
    ui.send_message("temperature", message={"value": float(celsius), "timestamp": datetime.now(UTC).isoformat()})

def send_detections_to_ui(detections: dict):
  for key, values in detections.items():
    for value in values:
      entry = {
        "content": key,
        "confidence": value.get("confidence"),
        "timestamp": datetime.now(UTC).isoformat()
      }
      ui.send_message("detection", message=entry)

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
