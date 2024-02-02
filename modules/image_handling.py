import mimetypes,requests,base64,cv2,numpy as np,os
from flask import request
from PIL import ImageFont,Image,ImageDraw

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
        result=placing_details['result']
        if user_details['text']:
                return text_placing(user_details,result)
        else:
                retval, buffer = cv2.imencode('.jpg', result)
                result_base64 = base64.b64encode(buffer).decode('utf-8')
                file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
                mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'


                # Prepend the MIME type to the base64 encoded image data
                result_base64_with_mime = f"{mime_type}{result_base64}"
                
                return {'mime_image':result_base64_with_mime,'base64_image':result_base64}
        

def text_placing(user_details,image=None):
        if image is None:
                image=user_details['edit_frame']
        text_field=user_details['text']
        text_data = (request.form.get('textData'))
        font_color=tuple(user_details['text_color'])
        if text_data!=None:
                text_coordinates=user_details['text_coordinates']
                text_coordinates_array=[]
                if len(text_field)>=2:
        # Create an array and append the parts
                        parts = text_data.split(',')
                        text_values = []
                        text_values.extend(parts)
                else:
                        text_values=[text_data]
                for field in text_field:
                        text_coordinates_array.append(text_coordinates[field])
        if text_field:
                current_dir = os.path.dirname(os.path.realpath(__file__))
                font_path = os.path.join(current_dir,'../assets/fonts/Manjari-Regular.ttf')
                malayalam_font = ImageFont.truetype(font_path, size=user_details['text_size'])
                

                # text_size_1 = malayalam_font.getsize(text_values[0])
                # text_size_2 = malayalam_font.getsize(text_values[1])
                text_size=[]

                array_length=len(text_values)
                for i in range(array_length):
                       text_size.append(malayalam_font.getsize(text_values[i]))
            

 

# Calculate the x-coordinate of the center of the text
                width,height,_=image.shape
                # center_x,center_y=int(width*0.347),int(height*1.10)

                x_coordinates=[]
                y_coordinates=[]
                for i in range(array_length):
                        x_coordinates.append(int(text_coordinates_array[i][0]*width))
                        y_coordinates.append(int(text_coordinates_array[i][1]*height))
                

                # Calculate the x-coordinate of the starting point for each tex

                # Calculate the starting points for the text based on the center
                # text_position_1 = (center_x - int(text_size_1[0] / 2), center_y)
                # text_position_2 = (center_x - int(text_size_2[0] / 2), center_y + 50)
                text_positions=[]

                for i in range(array_length):
                       text_positions.append((x_coordinates[i]-int(text_size[i][0]/2), y_coordinates[i]))
                
                result_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(result_pil)

                # Use malayalam_font to draw text on the image
                # draw.text(text_position_1, text_values[0], font=malayalam_font, fill=font_color)
                # draw.text(text_position_2, text_values[1], font=malayalam_font, fill=font_color)

                for i in range(array_length):
                        draw.text(text_positions[i],text_values[i], font=malayalam_font,fill=font_color)
                # Convert the result back to OpenCV format
                result = cv2.cvtColor(np.array(result_pil), cv2.COLOR_RGB2BGR)
                retval, buffer = cv2.imencode('.jpg', result)
                result_base64 = base64.b64encode(buffer).decode('utf-8')
                file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
                mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'


                # Prepend the MIME type to the base64 encoded image data
                result_base64_with_mime = f"{mime_type}{result_base64}"
                
                return {'mime_image':result_base64_with_mime,'base64_image':result_base64}