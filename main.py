import base64
import io
import os
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.cloud import texttospeech
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/process', methods=['POST'])
def procesar_solicitud():
    datos = request.get_json()['image']
    bytes = base64.b64decode(datos.encode("utf8"))
    audio_base64 = obtener_audio(etiquetar_imagen(bytes))
    return jsonify({"audio": audio_base64})

def etiquetar_imagen(imagen):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'token.json'
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.content = imagen
    features = [
        types.Feature(type=vision.Feature.Type.LABEL_DETECTION),
        types.Feature(type=vision.Feature.Type.WEB_DETECTION)
    ]
    request = types.AnnotateImageRequest(image=image, features=features)
    response = client.annotate_image(request=request)
    labels = response.label_annotations
    web_detection = response.web_detection
    print("Labels:")
    label_description = "No object detected"
    if labels:
        label_description = labels[0].description
    entity_description = ""
    if web_detection.web_entities:
        entity_description = web_detection.web_entities[0].description
    result = f"{entity_description} {label_description}"
    return result

def obtener_audio(text):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
    with open("output.mp3", "rb") as mp3_file:
        mp3_bytes = mp3_file.read()
    audio_base64 = base64.b64encode(mp3_bytes).decode('utf-8')
    return audio_base64

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("8080"), debug=True)