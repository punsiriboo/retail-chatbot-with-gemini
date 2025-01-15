import base64
import json
import re
from google.protobuf.json_format import MessageToDict

def ocr_handler(request):
    """
    Cloud Function to handle Datastore actions: insert, get, update.
    Includes CORS headers to allow cross-origin requests.
    """
    # Handle preflight (OPTIONS) requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        return ('', 204, headers)

    # Initialize response headers for CORS
    headers = {
        'Access-Control-Allow-Origin': '*',  # Allow all origins
        'Content-Type': 'application/json'
    }

    try:
        # Parse incoming JSON request
        request_json = request.get_json(silent=True)
        if not request_json:
            return ("Invalid request: JSON body required", 400, headers)

        response_dict = gemini_ocr(request_json)
        print(str(response_dict))
        return (json.dumps({"message": "Success", "data": response_dict}), 200, headers)
    
    except Exception as e:
        print(str(e))
        return (json.dumps({"message": "Error"}), 500, headers)
    
def cloud_vision_ocr(request_json):
    from google.cloud import vision 
    image_base64 = request_json.get("image_base64")
    image_bytes = base64.b64decode(image_base64)
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)

    response = client.text_detection(image=image)
    response_dict = MessageToDict(response._pb)
    return response_dict

def gemini_ocr(request_json):
    import vertexai
    import vertexai.generative_models as genai
    import uuid

    image_base64 = request_json.get("image_base64")
    image_bytes = base64.b64decode(image_base64)

    session_id = str(uuid.uuid4())
    gsc_image_path = upload_blob_from_memory(image_bytes, session_id)

    image_file = genai.Part.from_uri(
        gsc_image_path,
        mime_type="image/jpg",
    )
    
    vertexai.init(project="dataaibootcamp", location="us-central1")
    
    text_prompt = """จงตรวจสอบว่ารูปนี้เป็นรูปบัตรประชาชนหรือไม่ หากใช่ ให้ส่งข้อมูลที่อยู่ในบัตรประชาชนกลับมาในรูปแบบ JSON 
            is_nid: ให้ใส่ค่า True หากเป็นรูปบัตรประชาชน (Thai National ID Card) หรือ False หากไม่ใช่ รูปบัตรประชาชน ให้ใส่ค่า False
            nid: หมายเลขบัตรประชาชน 13 หลัก หากไม่ใช่ให้ใส่เป็น None
            first_name_th: ชื่อจริงภาษาไทย
            first_name_en: ชื่อจริงภาษาอังกฤษ
            last_name_th: นามสกุลภาษาไทย
            last_name_en: นามสกุลภาษาอังกฤษ   
            dob: โดยให้แปลงวันเกิดให้อยู่ในรูปแบบ yyyy-MM-dd และวันที่ออกบัตร และวันที่หมดอายุให้อยู่ในรูปแบบ yyyy-MM-dd
            genger: สำหรับเพศให้เดาจากคำนำหน้าชื่อ เช่น นาย เป็น Male และ น.ส., นางสาว เด็กหญิง เป็น Female หากไม่มีให้ใส่เป็น None
            address: ที่อยู่ภาษาไทย
            failed_reson: หากไม่สามารถอ่านข้อมูลจากรูปได้ให้ใส่เหตุผลที่ไม่สามารถอ่านได้ หากสามารถอ่านได้ให้ใส่เป็น None เช่น รูปเบลอ ไม่ใช่รูปบัตรประชาชน แต่เป็นใบขับขี่
            Example: {'is_nid': True, nid:'1000000000000' ,'first_name_th': 'สมใจ', 'first_name_en': 'Somjai', 'last_name_th': 'ศรีสดใส', 'last_name_en': 'Srisodsai', 'dob': '22/05/2534', 'address': '3/1 หมู่ที่ 8 ต.ช้างกลาง อ.ช้างกลาง จ.นครศรีธรรมราช', 'address_en': None, 'issue_date': '16 สิงหาคม 2016', 'expire_date': '21/05/2025', gender: 'Female'}
            Language = ภาษาไทย
            Recipe = {'is_nid': bool, nid: str, 'first_name_th': str, first_name_en: str, 'last_name_th': str, 'last_name_en': str, 'dob': str, 'address': str, 'address_en': str, 'issue_date': str, 'expire_date': str, gender:str, failed_reson: str}]}
            Return: Recipe
            """

    model = genai.GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content([image_file, text_prompt])

    pattern = r"(json)\s*(\{.*?\})\s*"
    match = re.search(pattern, response.text, re.DOTALL)
    if match:
        data_dict = json.loads(match.group(2))
    else:
        data_dict = None

    return data_dict

    

def upload_blob_from_memory(contents, session_id):
    from google.cloud import storage
    
    """Uploads a file to the bucket."""
    bucket_name = "line-cj-demo-chatboot"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    destination_blob_name = f"LINE_USERS_NID/image/{session_id}.jpg"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(contents)

    gsc_image_path = "gs://{}/{}".format(bucket_name, destination_blob_name)
    return gsc_image_path
    


