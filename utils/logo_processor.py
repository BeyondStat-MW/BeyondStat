
from PIL import Image
import numpy as np

def remove_white_background(input_path, output_path, tolerance=30):
    try:
        img = Image.open(input_path).convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            # item is (R, G, B, A)
            # Check if pixel is close to white
            if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
                new_data.append((255, 255, 255, 0)) # Transparent
            else:
                new_data.append(item)

        img.putdata(new_data)
        
        # Crop (Trim whitespace)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        img.save(output_path, "PNG")
        print(f"Successfully processed logo to {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    remove_white_background("assets/logo_center.png", "assets/logo_center_transparent.png")
