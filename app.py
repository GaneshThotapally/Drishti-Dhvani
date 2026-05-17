import os
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import speech_recognition as sr
import threading

# =========================
# FOLDERS
# =========================

WORD_FOLDER = "dataset/words"
LETTER_FOLDER = "dataset/letters"

os.makedirs(WORD_FOLDER, exist_ok=True)
os.makedirs(LETTER_FOLDER, exist_ok=True)

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Text → Gesture Converter")
root.geometry("900x650")
root.configure(bg="black")

title = tk.Label(root,
                 text="TEXT → HAND GESTURE SYSTEM",
                 font=("Arial", 20, "bold"),
                 fg="white", bg="black")
title.pack(pady=10)

entry_text = tk.Entry(root, font=("Arial", 16), width=40)
entry_text.pack(pady=10)

image_label = tk.Label(root, bg="black")
image_label.pack(pady=20)

status_label = tk.Label(root, text="", fg="yellow",
                        bg="black", font=("Arial", 12))
status_label.pack()

# =========================
# IMAGE QUEUE SYSTEM
# =========================

image_queue = []
is_displaying = False


def display_next():
    global is_displaying

    if not image_queue:
        is_displaying = False
        image_label.config(image="")
        return

    path = image_queue.pop(0)

    if path and os.path.exists(path):
        img = Image.open(path)
        img = img.resize((300, 300))
        img = ImageTk.PhotoImage(img)

        image_label.config(image=img)
        image_label.image = img

    root.after(1000, display_next)


# =========================
# CONVERT TEXT
# =========================

def convert_text():
    global image_queue, is_displaying

    text = entry_text.get().strip().lower()

    if text == "":
        messagebox.showerror("Error", "Enter text first")
        return

    image_queue.clear()

    words = text.split()

    for word in words:

        word_path = os.path.join(WORD_FOLDER, word + ".jpg")

        if os.path.exists(word_path):
            image_queue.append(word_path)
        else:
            for letter in word:
                if letter.isalpha():
                    letter_path = os.path.join(
                        LETTER_FOLDER,
                        letter.upper() + ".jpg"
                    )
                    if os.path.exists(letter_path):
                        image_queue.append(letter_path)

        image_queue.append(None)

    if not is_displaying:
        is_displaying = True
        display_next()


# =========================
# VOICE INPUT
# =========================

def listen_voice():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8
    recognizer.dynamic_energy_threshold = True

    mic = sr.Microphone()

    with mic as source:
        status_label.config(text="Adjusting for noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        status_label.config(text="Listening...")
        audio = recognizer.listen(
            source,
            timeout=5,
            phrase_time_limit=6
        )

    try:
        status_label.config(text="Recognizing...")
        text = recognizer.recognize_google(
            audio,
            language="en-IN"  # change to your accent
        )

        entry_text.delete(0, tk.END)
        entry_text.insert(0, text.lower())
        status_label.config(text="Speech Recognized ✔")

    except sr.UnknownValueError:
        status_label.config(text="Could not understand audio")
    except sr.RequestError:
        status_label.config(text="Internet required")


def start_listening():
    threading.Thread(target=listen_voice).start()


# =========================
# REGISTER WORD
# =========================

def register_word():
    word = entry_text.get().strip().lower()

    if word == "":
        messagebox.showerror("Error", "Enter word name first")
        return

    cap = cv2.VideoCapture(0)

    messagebox.showinfo("Instructions",
                        "Press SPACE to capture\nPress ESC to cancel")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, "Press SPACE to Capture",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        cv2.imshow("Capture Gesture", frame)

        key = cv2.waitKey(1)

        if key == 27:
            break

        elif key == 32:
            save_path = os.path.join(WORD_FOLDER, word + ".jpg")
            cv2.imwrite(save_path, frame)
            messagebox.showinfo("Success",
                                f"Gesture for '{word}' saved!")
            break

    cap.release()
    cv2.destroyAllWindows()


# =========================
# BUTTONS
# =========================

btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=20)

register_btn = tk.Button(btn_frame,
                         text="Register Text",
                         font=("Arial", 14),
                         bg="green", fg="white",
                         command=register_word)
register_btn.grid(row=0, column=0, padx=15)

convert_btn = tk.Button(btn_frame,
                        text="Convert Text",
                        font=("Arial", 14),
                        bg="blue", fg="white",
                        command=convert_text)
convert_btn.grid(row=0, column=1, padx=15)

voice_btn = tk.Button(btn_frame,
                      text="🎤 Speak",
                      font=("Arial", 14),
                      bg="orange", fg="black",
                      command=start_listening)
voice_btn.grid(row=0, column=2, padx=15)

root.mainloop()
