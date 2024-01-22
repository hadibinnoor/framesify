import mimetypes,base64,cv2
from flask import request
import textwrap
from modules.image_handling import image_placing


def testimonial_rendering(user_details):
    placing_details = image_placing(user_details)
    contour_details = user_details['contour_details']
    result = placing_details['result']
    text_data = request.form.get('textData')

    # Create an array and append the parts
    text_values = text_data.split(',')

    

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    font_color = (255,255,255) 
    line_type = cv2.LINE_AA
    height, width, _ = result.shape

# Calculate coordinates based on image dimensions
    x1 = int(width * 0.65)  # 10% from the left
    y1 = int(height * 0.77)  # 50% from the top

    x2= int(width * 0.13)
    y2= int(height * 0.5)
    wrapped_text=textwrap.wrap(text_values[2],width=55)
    for i,line in enumerate(wrapped_text):
          text_size_n=cv2.getTextSize(line,font,6,2)
          gap=text_size_n[1]+40
          y=(y2+i*gap)+130
        #   x=int((result.shape[1]-text_size_n[0])/2)
          cv2.putText(result, line, (x2,y), font, font_scale, font_color, 4, line_type)
    

        #   x=int((result.shape[1]-text_size_n[0])/2)
          
    cv2.putText(result,text_values[0],(x1,y1),font,font_scale,font_color,3,line_type)
 

    # Convert the resulting image to base64
    retval, buffer = cv2.imencode('.jpg', result)
    result_base64 = base64.b64encode(buffer).decode('utf-8')
    file_extension = mimetypes.guess_extension(mimetypes.types_map['.jpg'])
    mime_type = f"data:image/{file_extension[1:]};base64,"  # Extracting the extension without '.'

    # Prepend the MIME type to the base64 encoded image data
    result_base64_with_mime = f"{mime_type}{result_base64}"
    print(result_base64_with_mime[:30])

    return {'mime_image': result_base64_with_mime, 'base64_image': result_base64}

