import cv2

def apply_gaussian_blur(filename, kernel_size=(77, 77)):
    # Open the video file
    video_capture = cv2.VideoCapture(f'tmp/{filename}')

    # Get video properties
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_filename = f'tmp/blur_{filename}'
    output_video = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        if not ret:
            break

        # Apply Gaussian blur to the frame
        blurred_frame = cv2.GaussianBlur(frame, kernel_size, 0)

        # Write the blurred frame to the output video file
        output_video.write(blurred_frame)

    # Release the VideoCapture and VideoWriter objects
    video_capture.release()
    output_video.release()
    return output_filename
