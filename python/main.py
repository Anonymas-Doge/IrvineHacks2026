# SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
#
# SPDX-License-Identifier: MPL-2.0

import math
import datetime
from arduino.app_utils import App, Bridge
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.dbstorage_tsstore import TimeSeriesStore
from arduino.app_bricks.video_imageclassification import VideoImageClassification
from datetime import datetime, UTC
import json

ui = WebUI()
detection_stream = VideoImageClassification(confidence=0.5, debounce_sec=0.0)

ui.on_message("override_th", lambda sid, threshold: detection_stream.override_threshold(threshold))

# Example usage: Register a callback for when a specific object is detected
def person_detected():
  pass  # Implement your logic here, e.g., send a notification

detection_stream.on_detect("person", person_detected)

def record_sensor_samples(celsius: float):
    """Callback invoked by the board sketch via Bridge.notify to send sensor samples.
    Forwards temperature samples to the Web UI.
    """
    if celsius is None or not isinstance(celsius, (int, float)):
        print("Received invalid sensor samples: celsius=%s" % celsius)
        return

    ts = int(datetime.datetime.now().timestamp() * 1000)

    # Push realtime updates to the UI
    ui.send_message('temperature', {"value": float(celsius), "ts": ts})

    # --- Derived metrics ---
    T = float(celsius)

    # Heat Index (using Rothfusz regression). Convert to Fahrenheit and back to Celsius.
    T_f = T * 9.0 / 5.0 + 32.0
    R = max(min(RH, 100.0), 0.0)
    HI_f = (-42.379 + 2.04901523 * T_f + 10.14333127 * R - 0.22475541 * T_f * R
            - 0.00683783 * T_f * T_f - 0.05481717 * R * R
            + 0.00122874 * T_f * T_f * R + 0.00085282 * T_f * R * R
            - 0.00000199 * T_f * T_f * R * R)
    heat_index = (HI_f - 32.0) * 5.0 / 9.0

    if heat_index is not None:
        ui.send_message('heat_index', {"value": float(heat_index), "ts": ts})


# Example usage: Register a callback for when all objects are detected
def send_detections_to_ui(classifications: dict):
  if len(classifications) == 0:
      return
      
  entries = []
  for key, value in classifications.items():
    entry = {
      "content": key,
      "confidence": value,
      "timestamp": datetime.now(UTC).isoformat()
    }
    entries.append(entry)    
  
  if len(entries) > 0:
    msg = json.dumps(entries)
    ui.send_message("classifications", message=msg)

detection_stream.on_detect_all(send_detections_to_ui)

App.run()
