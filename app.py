from flask import Flask, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore,initialize_app, storage
from common_functions import get_user_details,image_frame_rendering
import re,base64,uuid,datetime
import qrcode


# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()
bucket = storage.bucket('framesify.appspot.com')


app = Flask(__name__)
CORS(app,resources={r"/campaign/*": {"origins": "*"}},methods=['POST'],allow_headers=["Access-Control-Allow-Origin"],origins="*",supports_credentials=True)
@app.route('/campaign/<user_id>')

def campaign(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        display_frame_url=user_details['display_frame_url']
        client_title=user_details['client_title']
        aspect_ratio_yellow=user_details['contour_details']['aspect_ratio_yellow']
        text_field=user_details['text']

        return jsonify({
                "user_id": user_id,
                "frame_image": display_frame_url,
                "client_title": client_title,
                "aspect_ratio":aspect_ratio_yellow,
                "text_field":text_field
            })
    return jsonify(frame_image="Error")
    
@app.route('/campaign/<string:user_id>/download',methods=['POST'])

def image_rendering(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        image_details=image_frame_rendering(user_details)
        image_data=image_details['base64_image']
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        # Decode the base64 image data
        image_bytes = base64.b64decode(image_data)
        user_id_fb = str(uuid.uuid4())

        # Save the image to Firebase Storage
        filename = f'{user_id_fb}.jpg'  # Adjust the file extension as needed
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type='image/jpeg')  # Adjust the MIME type as needed

        # Get the URL of the uploaded image
        # Set the expiration time for the URL
        expiration_time = datetime.timedelta(minutes=60)
        image_url = blob.generate_signed_url(expiration_time)

        # Create a new document in Firestore with the user ID and image URL
        doc_ref = db.collection(f'users/{user_id}/user_images').document()
        doc_ref.set({
            'user_id': user_id_fb,
            'image_url': image_url,
        })

        return jsonify(image_details['mime_image'])
    else:
    # Handle the error accordingly, e.g., return an error response
            return jsonify({'error': 'Image processing failed'})

@app.route('/campaign/<string:user_id>/qr',methods=['POST'])
def qr_code_generation(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        image_details=image_frame_rendering(user_details)
        image_data=image_details['base64_image']
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        # Decode the base64 image data
        image_bytes = base64.b64decode(image_data)
        user_id_fb = str(uuid.uuid4())

        # Save the image to Firebase Storage
        filename = f'{user_id_fb}.jpg'  # Adjust the file extension as needed
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type='image/jpeg')  # Adjust the MIME type as needed

        # Get the URL of the uploaded image
        # Set the expiration time for the URL
        expiration_time = datetime.timedelta(minutes=60)
        image_url = blob.generate_signed_url(expiration_time)
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
        qr.add_data(image_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        # Create a new document in Firestore with the user ID and image URL
        doc_ref = db.collection(f'users/{user_id}/user_images').document()
        doc_ref.set({
            'user_id': user_id_fb,
            'image_url': image_url,
        })

        return jsonify(qr_img)
    else:
    # Handle the error accordingly, e.g., return an error response
            return jsonify({'error': 'Image processing failed'})

if __name__ == '__main__':
    app.run(debug=True)