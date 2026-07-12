import os
from PIL import Image, ImageDraw, ImageFont
import collections

base_image_path = os.path.join(os.path.dirname(__file__), "base_medal.png")
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Assets", "Medals", "Progress"))

os.makedirs(output_dir, exist_ok=True)

def remove_background(img):
    img = img.convert("RGBA")
    data = img.load()
    width, height = img.size
    
    # BFS flood fill
    visited = set()
    queue = collections.deque([(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)])
    for start in queue:
        visited.add(start)
        
    while queue:
        x, y = queue.popleft()
        r, g, b, a = data[x, y]
        # Background in the generated image is typically white or very light gray
        if r > 230 and g > 230 and b > 230:
            data[x, y] = (255, 255, 255, 0)
            
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return img

base_img = Image.open(base_image_path).convert("RGBA")
# Remove the white background from the base image once
base_img = remove_background(base_img)
width, height = base_img.size

def get_font(size):
    try:
        return ImageFont.truetype(r"C:\Windows\Fonts\impact.ttf", size=size)
    except IOError:
        try:
            return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size=size)
        except IOError:
            return ImageFont.load_default()

milestones = [0, 1] + list(range(50, 1050, 50))

# Pre-calculate the font size based on the widest text ("1000")
global_font_size = int(height * 0.35)
temp_draw = ImageDraw.Draw(base_img)
temp_font = get_font(global_font_size)
bbox = temp_draw.textbbox((0, 0), "1000", font=temp_font)
while (bbox[2] - bbox[0]) > width * 0.40:
    global_font_size -= 5
    temp_font = get_font(global_font_size)
    bbox = temp_draw.textbbox((0, 0), "1000", font=temp_font)

global_font = temp_font
shadow_offset = max(3, int(height * 0.012))

for milestone in milestones:
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    text = str(milestone)
    
    bbox = draw.textbbox((0, 0), text, font=global_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) / 2
    # Adjust visual centering for '1' due to left serif in Impact font
    if text == "1":
        x -= width * 0.035
        
    y = (height - text_height) / 2 - bbox[1] + (height * 0.04)
    
    outline_color = (0, 0, 0, 255)
    text_color = (255, 255, 255, 255)
    
    draw.text((x, y), text, font=global_font, fill=text_color, stroke_width=shadow_offset, stroke_fill=outline_color)
    
    img_resized = img.resize((256, 256), Image.Resampling.LANCZOS)
    
    filename = f"{milestone:04d}.png"
    output_path = os.path.join(output_dir, filename)
    img_resized.save(output_path)
    print(f"Generated {filename}")
