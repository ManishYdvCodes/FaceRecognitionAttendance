import cv2
import os
import numpy as np
from PIL import Image

path = 'dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
ids = []

for imagePath in os.listdir(path):

    img_path = os.path.join(path, imagePath)

    faceImg = Image.open(img_path).convert('L')

    faceNp = np.array(faceImg,'uint8')

    id = int(imagePath.split(".")[1])

    faces.append(faceNp)
    ids.append(id)

recognizer.train(
    faces,
    np.array(ids)
)

recognizer.save(
    'trainer/trainer.yml'
)

print("Training Complete")