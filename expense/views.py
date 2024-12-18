import os
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from deepface import DeepFace  # Import DeepFace for face recognition
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings

def load_image(img_url):
    try:
        response = requests.get(img_url)
        image = Image.open(BytesIO(response.content))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return np.array(image)
    except Exception as e:
        print(f"Error loading image from {img_url}: {str(e)}")
        return None
    
def index(request):
    return HttpResponse("Welcome to Django Project")

class FaceCheckAPI(APIView):
    def get(self, request):
        url = "https://devanthosting.cloud/icare_v2/icare_api/public/api/getStudents/2"
        headers = {
            "Authorization": "Bearer 29|iUmTLVUyinZ3SUmCbcTkxTu6mKcwvaleD97es9Jwd20395cf"
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return Response({"status": "success", "data": data})
            else:
                return Response({"status": "error", "message": response.text},status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return Response({"status": "error", "message": str(e)},status=500)
    
    def post(self, request):
        data = request.data
        user_img_url = data.get('img_url')
        # return Response({"message": user_img_url},status=200)

        # Load the user face image
        user_face = load_image(user_img_url)
        if user_face is None:
            return Response({"error": "Failed to load user image."}, status=400)

        url = "https://devanthosting.cloud/icare_v2/icare_api/public/api/getStudents/2"
        headers = {
            "Authorization": "Bearer 29|iUmTLVUyinZ3SUmCbcTkxTu6mKcwvaleD97es9Jwd20395cf"
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                res_data = response.json()
                reference_img_list = res_data.get("data", [])
            else:
                return Response({"status": "error", "message": response.text},status=response.status_code)
            
        except requests.exceptions.RequestException as e:
            return Response({"status": "error", "message": str(e)},status=500)
        
        # reference_img_list = [
        #     {
        #         "id": 54564,
        #         "name": "Ayan",
        #         "image": os.path.join(settings.MEDIA_URL, 'user1.jpg')
        #     },
        #     {
        #         "id": 54565,
        #         "name": "Krishna",
        #         "image": os.path.join(settings.MEDIA_URL, 'user2.jpg')
        #     },
        #     {
        #         "id": 54566,
        #         "name": "Soumen",
        #         "image": os.path.join(settings.MEDIA_URL, 'user3.jpg')
        #     }
        # ]

        # Track match result and matching reference details
        match_found = False
        matched_reference = None

        for reference in reference_img_list:
            # Load each reference face image
            reference_face = load_image(reference["img_url"])
            if reference_face is None:
                continue  # Skip if reference image fails to load

            try:
                # Verify the user face against the current reference face
                result = DeepFace.verify(
                    img1_path=user_face,
                    img2_path=reference_face,
                    model_name='VGG-Face',
                    enforce_detection=False
                )
                # If match found, update status and save reference details
                if result["verified"]:
                    match_found = True
                    matched_reference = reference
                    break  # Stop further checks once a match is found
            except Exception as e:
                print(f"Error processing faces for {reference['first_name']}: {str(e)}")
                continue  # Skip to the next reference if an error occurs

        # Prepare response data
        if match_found:
            response_data = {
                "match_found": True,
                "matched_reference": matched_reference
            }
        else:
            response_data = {"match_found": False}

        # Return JSON response with the match result
        return Response(response_data)
