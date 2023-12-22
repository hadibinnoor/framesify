import mimetypes,requests,firebase_admin,base64,cv2,numpy as np
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
                contour_details=yellow_contour_id(edit_frame)
                client_title=user_data['user_title']

                return {'client_title':client_title,'contour_details':contour_details,'display_frame_url':display_frame_url,'edit_frame':edit_frame}




def yellow_contour_id(image_data):
        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)

                # Define range for yellow color in HSV
                lower_yellow = np.array([0, 0, 200])  # Lower bound for white
                upper_yellow = np.array([180, 255, 255])  # Upper bound for white




                # Threshold the HSV image to get only yellow colors
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

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
        aspect_ratio_yellow=contour_details['aspect_ratio_yellow']
        x=contour_details['x']
        y=contour_details['y']
        h=contour_details['h']
        w=contour_details['w']
        contour_mask=contour_details['contour_mask']
        text_data = (request.form.get('textData'))
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

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (0,0,0)  # yellow color
            line_type = 2
            text_size, _ = cv2.getTextSize(text_data, font, font_scale, line_type)

# Calculate the x-coordinate of the center of the text
            center_x = int(x + (new_w - text_size[0]) / 2)

        #     cv2.putText(result, text_data, (center_x, int(y + new_h + 30)), font, font_scale, font_color, line_type)
            # Convert the resulting image to base64
            retval, buffer = cv2.imencode('.jpg', result)
            result_base64 = base64.b64encode(buffer).decode('utf-8')
            print("success")
            file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
            mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'

        # Prepend the MIME type to the base64 encoded image data
            result_base64_with_mime = f"{mime_type}{result_base64}"

            return result_base64_with_mime
