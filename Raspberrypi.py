import cv2
from keras.models import model_from_json
import numpy as np
import pygame
import time
import paho.mqtt.client as mqtt

# Loading the emotion detection model
json_file = open("facialemotionmodel.json", "r")
model_json = json_file read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("facialemotionmodel.h5")

# Initializing pygame for audio playback
pygame.init()

# Defining music files for each emotion category
happy_music = "happy_song.mp3"
sad_music = "sad_song.mp3"
neutral_music = "neutral_song.mp3"

# Loading the face cascade classifier
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

# Initializing the webcam
webcam = cv2.VideoCapture(0)

# Initializing a flag to track whether music is playing
music_playing = False

# MQTT settings
mqtt_broker = "a32d056c843e4e16a70944e5f4eb65a6.s1.eu.hivemq.cloud"
mqtt_port = 8883
mqtt_topic = "/mood"

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set("username", "xxpasswordxx")  # Replace with your MQTT username and password
client.tls_set()  # Using TLS for secure communication
client.connect(mqtt_broker, mqtt_port, 60)  # Connecting to the MQTT broker

labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

# Adding an initial delay of 5 seconds before starting emotion detection
initial_delay = 5
start_time = time.time()

while True:
    i, im = webcam.read()
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(im, 1.3, 5)

    try:
        elapsed_time = time.time() - start_time

        if elapsed_time >= initial_delay:
            for (p, q, r, s) in faces:
                image = gray[q:q + s, p:p + r]
                cv2.rectangle(im, (p, q), (p + r, q + s), (255, 0, 0), 2)
                image = cv2.resize(image, (48, 48))
                img = extract_features(image)
                pred = model.predict(img)
                prediction_label = labels[pred.argmax()]

                # Publishing detected emotion to MQTT topic
                client.publish(mqtt_topic, prediction_label)

                # Playing music based on the detected emotion
                if not music_playing:
                    if prediction_label == 'happy':
                        pygame.mixer.music.load(happy_music)
                        pygame.mixer.music.play()
                    elif prediction_label == 'sad':
                        pygame.mixer.music load(sad_music)
                        pygame.mixer.music.play()
                    elif prediction_label == 'neutral':
                        pygame.mixer.music.load(neutral_music)
                        pygame.mixer.music.play()
                    else:
                        pygame.mixer.music.stop()  # Stop any playing music for unrecognized emotions
                    music_playing = True  # Setting the flag to indicate music is playing

                # Display the detected emotion on the image
                cv2.putText(im, prediction_label, (p - 10, q - 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255))

        cv2.imshow("Output", im)
        cv2.waitKey(27)
    except cv2.error:
        pass

# Releasing webcam, closing the pygame mixer, and disconnecting from MQTT when exiting
webcam.release()
pygame.mixer.quit()
cv2.destroyAllWindows()
client.disconnect()