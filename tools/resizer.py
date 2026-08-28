import os
from PIL import Image

# ==========================================
# CONFIGURATION
# ==========================================
MAX_SIZE = 300  # Change this value to adjust the maximum allowed dimension
TARGET_DIRECTORY = "."  # Folder to process ('.' means current directory)
# ==========================================


def resize_png_images(directory, max_dimension):
    # Ensure the directory path exists
    if not os.path.exists(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # Loop through all files in the given directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(".png"):
            file_path = os.path.join(directory, filename)

            try:
                with Image.open(file_path) as img:
                    width, height = img.size

                    # Check if either dimension is larger than the max allowed size
                    if width > max_dimension or height > max_dimension:
                        # Calculate new dimensions while maintaining aspect ratio
                        if width > height:
                            new_width = max_dimension
                            new_height = int((max_dimension / width) * height)
                        else:
                            new_height = max_dimension
                            new_width = int((max_dimension / height) * width)

                        # Resize the image using high-quality resampling
                        resized_img = img.resize(
                            (new_width, new_height), Image.Resampling.LANCZOS
                        )

                        # Generate the new filename: originalname-XxY.png
                        name_without_ext, _ = os.path.splitext(filename)
                        new_filename = (
                            f"{name_without_ext}-{new_width}x{new_height}.png"
                        )
                        new_file_path = os.path.join(directory, new_filename)

                        # Save the resized image
                        resized_img.save(new_file_path)
                        print(f"Resized: '{filename}' -> '{new_filename}'")
                    else:
                        print(
                            f"Skipped: '{filename}' (Within bounds: {width}x{height})"
                        )

            except Exception as e:
                print(f"Could not process {filename}: {e}")


# Run the program
if __name__ == "__main__":
    resize_png_images(TARGET_DIRECTORY, MAX_SIZE)
