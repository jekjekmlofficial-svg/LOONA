import cv2
from ultralytics import YOLO

# Load the pre-trained YOLOv8 small model
model = YOLO('yolov8s.pt')

# Initialize the default laptop webcam (Index 0)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # Capture the video frame-by-frame
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame. Is the camera in use?")
        break

    # DITO DAPAT: Pass the raw frame array to the AI with 60% confidence filter
    results = model(frame, conf=0.6)

    # Automatically draw the bounding boxes and labels on the frame
    annotated_frame = results[0].plot()

    # Display the processed frame in a new window
    cv2.imshow("LOONA Vision Simulation", annotated_frame)

    # Listen for the 'q' key to cleanly exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera hardware and close the window
cap.release()
cv2.destroyAllWindows()