import requests,cv2,numpy as np
from modules.image_handling import contour_id

def get_user_details(user_id,db):
        users_ref = db.collection('users').document(user_id)
        user = users_ref.get()
        if user.exists:
            user_data = user.to_dict()
            display_frame_url=user_data['display_frame']
            edit_frame_url=user_data['edit_frame']
            response = requests.get(edit_frame_url) 
            edit_frame_data = response.content
            edit_frame_np = np.frombuffer(edit_frame_data, np.uint8)
            edit_frame = cv2.imdecode(edit_frame_np, cv2.IMREAD_COLOR)
            if 'color_lower_bound' in user_data.keys() and 'color_upper_bound' in user_data.keys():
                  color_lower_bound=user_data['color_lower_bound']
                  color_upper_bound=user_data['color_upper_bound']
            else:
                  color_lower_bound=[100,50,50]
                  color_upper_bound=[130,255,255]
            text_field=None
            text_coordinates=None
            if 'text_field' in user_data.keys():
                  text_field=user_data['text_field']
                  text_coordinates=user_data['text_coordinates']
            
            if 'rate_poster' not in user_data.keys(): 
                  contour_details=contour_id(edit_frame,color_lower_bound,color_upper_bound)
            if 'text_color' in user_data.keys():
                  text_color=user_data['text_color']
            else:
                  text_color=(0,0,0)
            if 'text_size' in user_data.keys():
                  text_size=user_data['text_size']
            else:
                  text_size=40
            client_title=user_data['user_title']
            return {'client_title':client_title,'contour_details':contour_details,'display_frame_url':display_frame_url,'edit_frame':edit_frame,'text':text_field,'text_coordinates':text_coordinates,'text_color':text_color,'text_size':text_size}
