from flask import Flask, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore,initialize_app

from common_functions import get_user_details,image_frame_rendering

# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
initialize_app(cred)
db = firestore.client()


app = Flask(__name__)
CORS(app,resources={r"/campaign/*": {"origins": "*"}},methods=['POST'],allow_headers=["Access-Control-Allow-Origin"],origins="*")
@app.route('/campaign/<user_id>')

def campaign(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        display_frame_url=user_details['display_frame_url']
        client_title=user_details['client_title']
        aspect_ratio_yellow=user_details['contour_details']['aspect_ratio_yellow']

        return jsonify({
                "user_id": user_id,
                "frame_image": display_frame_url,
                "client_title": client_title,
                "aspect_ratio":aspect_ratio_yellow
            })
    return jsonify(frame_image="Error")
    
@app.route('/campaign/<string:user_id>/download',methods=['POST'])

def image_rendering(user_id):
    user_details=get_user_details(user_id,db)
    if user_details:
        result_image=image_frame_rendering(user_details)
        return jsonify(result_image)
    else:
    # Handle the error accordingly, e.g., return an error response
            return jsonify({'error': 'Image processing failed'})
if __name__ == '__main__':
    app.run(debug=False)