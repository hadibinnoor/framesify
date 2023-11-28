from flask import Flask, request, jsonify, render_template
from PIL import Image
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge_images', methods=['POST'])
def merge_images():
    if 'background' not in request.files or 'overlay' not in request.files:
        return jsonify({'error': 'Missing input files'}), 400

    img1 = request.files['background']
    img2 = request.files['overlay']
    
    from PIL import Image, ImageDraw, ImageOps

    # Open your images
    fp = Image.open(img1)
    fc = Image.open(img2)

    # Resize the second image
    r = fc.resize((150, 200))

    # Create a new image for the mask
    mask = Image.new('L', r.size, 0)

    # Create a draw object
    draw = ImageDraw.Draw(mask)

    # Draw a white ellipse on the mask
    draw.ellipse((0, 0, 150, 200), fill=255)

    # Create a composite image using the resized image and the mask
    result = ImageOps.fit(r, mask.size, method=0, bleed=0.0, centering=(0.5, 0.5))
    result.putalpha(mask)
    
    # Paste the result image onto the first image
    fp.paste(result, (200, 150), result)

    # fp.show()

    # Ensure the files are PNG images
    # if fp.mimetype != 'image/png' or fc.mimetype != 'image/png':
    #     return jsonify({'error': 'Please provide PNG images only'}), 400

    # background = Image.open(fp)
    # overlay = Image.open(fc)

    # # Resize overlay image to fit within the background
    # overlay = overlay.resize((200, 200))  # Adjust the size as needed

    # # Paste the overlay image onto the background
    # background.paste(overlay, (50, 50))  # Adjust the position as needed

    # Save the modified image to a BytesIO object
    # output = io.BytesIO()
    # fp.save(output, format='PNG')
    # output.seek(0)

    # # Encode the image as base64
    # encoded_img = base64.b64encode(output.read()).decode('utf-8')

    # return jsonify({'image': encoded_img})
    fp.save('merged_image.png')  # Save the merged image as 'merged_image.png'

    # Read the saved image file and encode it as base64
    with open('merged_image.png', 'rb') as image_file:
        encoded_img = base64.b64encode(image_file.read()).decode('utf-8')

    return jsonify({'image': encoded_img})

if __name__ == '__main__':
    app.run(debug=True)
