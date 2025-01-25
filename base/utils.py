import face_recognition as fr
import numpy as np
from .models import Employee


def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces(email):
    try:
        qs = Employee.objects.get(emp_email=email)
    except Employee.DoesNotExist:
        return None


    if qs.emp_image:
        encoding = None

        face = fr.load_image_file(qs.emp_image.path)

        face_location = fr.face_locations(face)
        face_encodings = fr.face_encodings(face, face_location)
        encoding = face_encodings 

        return encoding
    return None 


def classify_face(img, email):
    faces = get_encoded_faces(email)

    img = fr.load_image_file(img)
    img2 = fr.face_locations(img)
    face_encoding = fr.face_encodings(img, img2)
 
    try:
        is_match = fr.compare_faces(faces, face_encoding[0])

        return is_match
    except:
        return False
    