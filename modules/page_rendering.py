from flask import jsonify
from modules.details_fetching import get_user_details

def page_rendering(user_id,db):
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
      else:
        return jsonify(frame_image="Error")