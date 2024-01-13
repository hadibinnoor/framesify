import mimetypes,requests,base64,cv2,numpy as np
from flask import request

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

def image_frame_rendering(user_details):
        edit_frame=user_details['edit_frame']
        contour_details=user_details['contour_details']
        text_field=user_details['text']
        aspect_ratio_yellow=contour_details['aspect_ratio_yellow']
        x=contour_details['x']
        y=contour_details['y']
        h=contour_details['h']
        w=contour_details['w']
        contour_mask=contour_details['contour_mask']
        text_data = (request.form.get('textData'))
        if text_data!=None:
            parts = text_data.split(',')

    # Create an array and append the parts
            text_values = []
            text_values.extend(parts)
            print(text_values)
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
            
            return {'mime_image':result_base64_with_mime,'base64_image':result_base64}
