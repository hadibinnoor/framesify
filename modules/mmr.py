#makemorereviews
import requests,cv2,numpy as np
from modules.image_handling import contour_id
import mimetypes,requests,base64,cv2,numpy as np,os
from flask import request,jsonify
from PIL import ImageFont,Image,ImageDraw
import re,base64,uuid,datetime

def get_user_details(user_id,db):
        users_ref = db.collection('users').document(user_id)
        user = users_ref.get()
        if user.exists:
            user_data = user.to_dict()
            edit_frame_url=user_data['edit_frame']
            response = requests.get(edit_frame_url) 
            edit_frame_data = response.content
            edit_frame_np = np.frombuffer(edit_frame_data, np.uint8)
            edit_frame = cv2.imdecode(edit_frame_np, cv2.IMREAD_COLOR)
            text_coordinates=None
            if 'text_coordinates' in user_data.keys():
                  text_coordinates=user_data['text_coordinates']
            
            if 'text_color' in user_data.keys():
                  text_color=user_data['text_color']
            else:
                  text_color=(0,0,0)
            if 'text_size' in user_data.keys():
                  text_size=user_data['text_size']
            else:
                  text_size=40
            client_title=user_data['user_title']
            return {'client_title':client_title,'edit_frame':edit_frame,'text_coordinates':text_coordinates,'text_color':text_color,'text_size':text_size}

def text_placing(user_details,data,image=None):
        if image is None:
                image=user_details['edit_frame']
        text_field=user_details['text']
        font_color=tuple(user_details['text_color'])
        if data!=None:
                text_coordinates=user_details['text_coordinates']
                text_coordinates_dict={}
        # Create an array and append the parts

                for field in text_field:
                        text_coordinates_dict[field]=text_coordinates[field]
        if text_field:
                current_dir = os.path.dirname(os.path.realpath(__file__))
                font_path = os.path.join(current_dir,'../assets/fonts/Manjari-Bold.ttf')
                malayalam_font = ImageFont.truetype(font_path, size=user_details['text_size'])
                

                # text_size_1 = malayalam_font.getsize(text_values[0])
                # text_size_2 = malayalam_font.getsize(text_values[1])
                text_size={}

                array_length=len(data)
                for key in data.keys():
                       text_size[key]=malayalam_font.getsize(data[key])
            

 

# Calculate the x-coordinate of the center of the text
                width,height,_=image.shape
                # center_x,center_y=int(width*0.347),int(height*1.10)

                x_coordinates=[]
                y_coordinates=[]
                for key in data.keys():
                        x_coordinates.append(int(text_coordinates_dict[key][0]*width))
                        y_coordinates.append(int(text_coordinates_dict[key][1]*height))
               
                text_positions={}

                for key in data.keys():
                       text_positions[key]=(x_coordinates[key]-int(text_size[key][0]/2), y_coordinates[key])
                
                result_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(result_pil)

               
                for key in data.keys():
                        draw.text(text_positions[key],data[key], font=malayalam_font,fill=font_color)
                # Convert the result back to OpenCV format
                result = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
                retval, buffer = cv2.imencode('.jpg', result)
                result_base64 = base64.b64encode(buffer).decode('utf-8')
                file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
                mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'


                # Prepend the MIME type to the base64 encoded image data
                result_base64_with_mime = f"{mime_type}{result_base64}"
                
                return {'mime_image':result_base64_with_mime,'base64_image':result_base64}
def review_handler(user_id,db,data):
        user_details=get_user_details(user_id,db)
        image_details=text_placing(user_details,data,image=user_details['edit_frame'])
        
        return jsonify(image_details['mime_image'])
