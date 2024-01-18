import mimetypes,requests,base64,cv2,numpy as np
from flask import request,jsonify
import textwrap

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
                if 'text_field' in user_data.keys():
                      text_field=user_data['text_field']
                contour_details=contour_id(edit_frame,color_lower_bound,color_upper_bound)
                client_title=user_data['user_title']
                return {'client_title':client_title,'contour_details':contour_details,'display_frame_url':display_frame_url,'edit_frame':edit_frame,'text':text_field}

def contour_id(image_data,color_lower_bound,color_upper_bound):
        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        # Define range for color in HSV
        lower_bound = np.array(color_lower_bound)
        upper_bound = np.array(color_upper_bound)

                # Threshold the HSV image to get only yellow colors
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

                # Find contours in the mask image
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Assuming the frame is the largest yellow area, find the largest contour
        frame_contour = max(contours, key=cv2.contourArea)

                # Create an empty mask to draw the contour
        contour_mask = np.zeros_like(mask)

                # Draw the largest contour onto the mask
        cv2.drawContours(contour_mask, [frame_contour], -1, (255), thickness=cv2.FILLED)

                # Get the bounding rectangle for the largest contour
        x, y, w, h = cv2.boundingRect(frame_contour)

        aspect_ratio_yellow = w / h
        
        return {'x':x,'y':y,'w':w,'h':h,'aspect_ratio_yellow':aspect_ratio_yellow,'contour_mask':contour_mask}
def image_placing(user_details):
        edit_frame=user_details['edit_frame']
        contour_details=user_details['contour_details']
        aspect_ratio_yellow=contour_details['aspect_ratio_yellow']
        x=contour_details['x']
        y=contour_details['y']
        h=contour_details['h']
        w=contour_details['w']
        contour_mask=contour_details['contour_mask']
        cropped_image_base64 = request.files.get('croppedImage')
        if cropped_image_base64:
            cropped_image_data=cropped_image_base64.read()
            cropped_image=bytes(cropped_image_data)
            # Convert bytes to numpy array
            nparr = np.frombuffer(cropped_image, np.uint8)
              # Decode the image using OpenCV
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Convert the image from RGB to BGR
            if len(img.shape) == 3:  # Check if it's a color image
                new_image = img
            else:
                new_image = img
                # Convert the frame_image to HSV color space

            new_w = min(w, h * aspect_ratio_yellow)
            new_h = new_w / aspect_ratio_yellow

                # Resize the new image to fit within the frame while maintaining aspect ratio
            new_image_resized = cv2.resize(new_image, (int(new_w), int(new_h)))

                # Create a mask of the resized new image with the contour mask
            new_image_mask = np.zeros_like(edit_frame)
            new_image_mask[y:y + new_image_resized.shape[0], x:x + new_image_resized.shape[1]] = new_image_resized

                # Apply the contour mask to the new image mask
            new_image_mask = cv2.bitwise_and(new_image_mask, new_image_mask, mask=contour_mask)

                # Create an inverse mask of the frame_image
            poster_mask = cv2.bitwise_and(edit_frame, edit_frame, mask=cv2.bitwise_not(contour_mask))

                # Combine the new image with the frame_image
            result = cv2.add(poster_mask, new_image_mask)

            return {'new_w':new_w,'new_h':new_h,'result':result}

def image_frame_rendering(user_details):
        placing_details=image_placing(user_details)
        text_field=user_details['text']
        contour_details=user_details['contour_details']
        x=contour_details['x']
        y=contour_details['y']
        new_w=placing_details['new_w']
        new_h=placing_details['new_h']
        result=placing_details['result']
        text_data = (request.form.get('textData'))
        if text_data!=None:
         if len(text_field)>=2:
                parts = text_data.split(',')

        # Create an array and append the parts
                text_values = []
                text_values.extend(parts)
         else:
              text_values=[text_data]
        if text_field:
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 1.3
                font_color = (0,0,0)  # yellow color
                line_type = 2
                text_size, _ = cv2.getTextSize(text_data, font, font_scale, line_type)

    # Calculate the x-coordinate of the center of the text
 # Calculate the x-coordinate of the center of the text
                # ... (previous code remains unchanged)

# Calculate the x-coordinate of the center of the text
                center_x = int(x + new_w / 2 + 520)

                # Calculate the y-coordinate of the center of the text
                center_y = int(y + new_h / 2)

                # Calculate the x-coordinate of the starting point for each text
                text_size_1, _ = cv2.getTextSize(text_values[0], font, font_scale, line_type)
                text_start_x_1 = center_x - int(text_size_1[0] / 2)

                text_size_2, _ = cv2.getTextSize(text_values[1], font, font_scale, line_type)
                text_start_x_2 = center_x - int(text_size_2[0] / 2)

                # Calculate the starting points for the text based on the center
                text_position_1 = (text_start_x_1-95, center_y - 15)
                text_position_2 = (text_start_x_2-95, center_y + 95)
                cv2.putText(result, text_values[0], text_position_1, font, font_scale, font_color, 2, line_type)
                cv2.putText(result, text_values[1], text_position_2, font, font_scale, font_color, 2, line_type)

# ... (remaining code remains unchanged)

                
            # Convert the resulting image to base64
        retval, buffer = cv2.imencode('.jpg', result)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
        mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'


        # Prepend the MIME type to the base64 encoded image data
        result_base64_with_mime = f"{mime_type}{result_base64}"
        print(result_base64_with_mime[:30])
            
        return {'mime_image':result_base64_with_mime,'base64_image':result_base64}


def testimonial_rendering(user_details):
    placing_details = image_placing(user_details)
    contour_details = user_details['contour_details']
    x = contour_details['x']
    y = contour_details['y']
    new_w = placing_details['new_w']
    new_h = placing_details['new_h']
    result = placing_details['result']
    text_data = request.form.get('textData')

    # Create an array and append the parts
    text_values = text_data.split(',')

    # Convert the result image to HSV color space
#     hsv_result = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

    # Define range for color in HSV for the text area
#     text_area_lower_bound = np.array(text_area_color_lower_bound)
#     text_area_upper_bound = np.array(text_area_color_upper_bound)

#     # Threshold the HSV image to get only the text area color
#     text_area_mask = cv2.inRange(hsv_result, text_area_lower_bound, text_area_upper_bound)

#     # Find contours in the text area mask
#     text_area_contours, _ = cv2.findContours(text_area_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     # Assuming the text area is the largest colored region, find the largest contour
#     text_area_contour = max(text_area_contours, key=cv2.contourArea)

#     # Get the bounding rectangle for the text area
#     text_area_x, text_area_y, text_area_w, text_area_h = cv2.boundingRect(text_area_contour)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3.2
    font_color = (255,255,255) 
    line_type = cv2.LINE_AA
    wrapped_text=textwrap.wrap(text_values[1],width=55)
    for i,line in enumerate(wrapped_text):
          text_size_n=cv2.getTextSize(line,font,6,2)
          gap=text_size_n[1]+40
          y=(1500+i*gap)+130
        #   x=int((result.shape[1]-text_size_n[0])/2)
          cv2.putText(result, line, (310,y), font, font_scale, font_color, 4, line_type)
    

        #   x=int((result.shape[1]-text_size_n[0])/2)
          
    cv2.putText(result,text_values[0],(2200,2480),font,font_scale,font_color,3,line_type)
    # Calculate the x-coordinate of the center of the text area
#     text_area_center_x = int(text_area_x + text_area_w / 2)

#     # Calculate the y-coordinate of the center of the text area
#     text_area_center_y = int(text_area_y + text_area_h / 2)

#     # Calculate the starting points for the text based on the center of the text area
#     text_size, _ = cv2.getTextSize(text_values[1], font, font_scale, line_type)
#     text_start_x = text_area_center_x - int(text_size[0] / 2)
#     text_position = (text_start_x, text_area_center_y)

#     # Draw the text on the result image within the identified text area
#     cv2.putText(result, text_values[1], text_position, font, font_scale, font_color, 2, line_type)

    # Convert the resulting image to base64
    retval, buffer = cv2.imencode('.jpg', result)
    result_base64 = base64.b64encode(buffer).decode('utf-8')
    file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
    mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'

    # Prepend the MIME type to the base64 encoded image data
    result_base64_with_mime = f"{mime_type}{result_base64}"
    print(result_base64_with_mime[:30])

    return {'mime_image': result_base64_with_mime, 'base64_image': result_base64}

