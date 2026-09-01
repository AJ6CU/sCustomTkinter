import os
from PIL import Image

# ==========================================
# CONFIGURATION
# ==========================================
MAX_SIZE = 325  # Change this value to adjust the maximum allowed dimension
TARGET_DIRECTORY = "../Docs/src/images/"  # Folder to process
# ==========================================


def resize_png_images(directory, max_dimension):
    # Ensure the directory path exists
    if not os.path.exists(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # Loop through all files in the given directory
    for filename in os.listdir(directory):
        # Process PNGs, but SKIP any previously saved backups to avoid loops
        if filename.lower().endswith(".png") and not filename.lower().endswith("_save.png"):
            file_path = os.path.join(directory, filename)

            try:
                # Open the image file
                with Image.open(file_path) as img:
                    width, height = img.size

                    # Check if either dimension is larger than the max allowed size
                    if width > max_dimension:
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

                        # Generate backup filename (e.g., foo.png -> foo_save.png)
                        name_without_ext, ext = os.path.splitext(filename)
                        backup_filename = f"{name_without_ext}_save{ext}"
                        backup_file_path = os.path.join(directory, backup_filename)

                        # Close the original image reference so OS can rename it
                        img.close()

                        # Rename original file to the backup name
                        os.rename(file_path, backup_file_path)

                        # Save the resized image as the original filename
                        resized_img.save(file_path)
                        print(f"Processed: Original backed up to '{backup_filename}', smaller image saved as '{filename}'")
                    else:
                        print(
                            f"Skipped: '{filename}' (Within bounds: {width}x{height})"
                        )

            except Exception as e:
                print(f"Could not process {filename}: {e}")


# Run the program
if __name__ == "__main__":
    resize_png_images(TARGET_DIRECTORY, MAX_SIZE)
