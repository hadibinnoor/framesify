from flask import Flask, jsonify, request
from flask_cors import CORS
from firebase_admin import credentials, firestore,initialize_app, storage
from modules.image_handling import image_frame_rendering,text_placing
from modules.testimonial import testimonial_rendering
from modules.page_rendering import page_rendering
from modules.details_fetching import get_user_details
import re,base64,uuid,datetime
import http
from modules.reviews import review_handler


# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()
bucket = storage.bucket('framesify.appspot.com')


app = Flask(__name__)
CORS(app,resources={r"/campaign/*": {"origins": "*"},r"/testimonial/*": {"origins": "*"},r"/rates/*":{"origins":"*"},r"/reviews/*":{"origins":"*"}},methods=['POST','GET'],allow_headers=["Access-Control-Allow-Origin"],origins="*")
@app.route('/campaign/<user_id>')

def campaign(user_id):
    return page_rendering(user_id,db)
    
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
        if user_id=="P6hGi":
            return jsonify(image_url)
        else:
            return jsonify(image_details['mime_image'])
   
    else:
    # Handle the error accordingly, e.g., return an error response
        return jsonify({'error': 'Image processing failed'})

@app.route('/testimonial/<string:user_id>',methods=['GET','POST'])
def testimonial(user_id):
    return page_rendering(user_id,db)

@app.route('/testimonial/<string:user_id>/download', methods=['POST'])
def testimonial_generation(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        image_details=testimonial_rendering(user_details)
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
@app.route('/rates/<string:user_id>',methods=['GET','POST'])
def daily_rate_display(user_id):
    return page_rendering(user_id,db)
@app.route('/rates/<string:user_id>/download',methods=['POST'])
def daily_rate(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        image_details=text_placing(user_details)
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
@app.route('/reviews/<string:user_id>',methods=['POST'])
def makeMoreReviews(user_id):
    if request.is_json:
        data=request.get_json()
        poster=review_handler(user_id,db,data)
        return jsonify(poster)
        
if __name__ == '__main__':
    app.run(debug=True)