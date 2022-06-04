#potrebni library tkinter, PIL, cv2, numpy
#instalacija: u CMD upisati: py -m pip install 'naziv_biblioteke'
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import math
import wave

global direktorij_slika

image_display_size = 300, 300

#Učitavanje audio datoteke
def load_audio():
    global direktorij_audio
    direktorij_audio = filedialog.askopenfilename()
    global song
    song = wave.open(direktorij_audio, mode='rb')

#enkripcija audio datoteke
def encrypt_data_audio():
    slika_u_bajt = bytearray(list(song.readframes(song.getnframes()))) #čitanje datoteke

    poruka = txt.get(1.0, "end-1c") # tajna poruka
    poruka = poruka + int((len(slika_u_bajt)-(len(poruka)*8*8))/8) *'#' #lažni podaci koje će popuniti ostatak bajtova
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in poruka]))) #pretvaranje poruke u niz bitova

    # Mjenjanje zadnjeg bita svakog bajta datoteke s jednim bitom teksta iz našeg niza bitova
    for i, bit in enumerate(bits):
        slika_u_bajt[i] = (slika_u_bajt[i] & 254) | bit
    
    #dohvaćanje modifiniranih bajtova
    kodirana_slika = bytes(slika_u_bajt)

    # Upisivanje bajtova u novu wav datoteku
    with wave.open('Desktop\pjesma_kriptirana.wav', 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(kodirana_slika)
    song.close()

    tkinter.messagebox.showinfo("Poruka",  "Enkripcija uspješna")

# dekripcija audio datoteke
def decrypt_data_audio():
    slika_u_bajt = bytearray(list(song.readframes(song.getnframes())))

    # Ekstrakcija zadnjeg bita svakog bajta
    bajtovi_slike = [slika_u_bajt[i] & 1 for i in range(len(slika_u_bajt))]
    # Konverzija niza bajta u poruka
    poruka = "".join(chr(int("".join(map(str,bajtovi_slike[i:i + 8])), 2)) for i in range(0, len(bajtovi_slike), 8))
    # Makivanje nepotrebnih popunjenih bajtova
    decoded = poruka.split("###")[0]
    
    song.close()

    poruka_label = Label(app, text=decoded, bg='lavender', font=("Times New Roman", 10))
    poruka_label.place(x=350, y=400)

# Učitavanje slike
def load_image():
    global direktorij_slika
    
    direktorij_slika = filedialog.askopenfilename() # dohvaćanje puta do slike
    slika = Image.open(direktorij_slika) # učitavanje slike
    slika.thumbnail(image_display_size, Image.ANTIALIAS) # postavljanje slike u GUI

    # učitavanje slike kao numpy niz za efektivniju kompjutaciju i mnjanja tipa u unsigned integer
    np_slika = np.asarray(slika) 
    np_slika = Image.fromarray(np.uint8(np_slika))
    render = ImageTk.PhotoImage(np_slika)
    img = Label(app, image=render)
    img.image = render
    img.place(x=25, y=400)
    
def encrypt_data_image():
    global direktorij_slika
    data = txt.get(1.0, "end-1c") #tajna poruka
    img = cv2.imread(direktorij_slika) #učitavanje slike
    # slika se dijeli na ASCII znakove
    data = [format(ord(i), '08b') for i in data]
    _, width, _ = img.shape
    # algoritam za encode slike 
    PixReq = len(data) * 3

    RowReq = PixReq/width
    RowReq = math.ceil(RowReq)

    count = 0
    charCount = 0
    for i in range(RowReq + 1):
        while(count < width and charCount < len(data)):
            char = data[charCount]
            charCount += 1
            for index_k, k in enumerate(char):
                if((k == '1' and img[i][count][index_k % 3] % 2 == 0) or (k == '0' and img[i][count][index_k % 3] % 2 == 1)):
                    img[i][count][index_k % 3] -= 1
                if(index_k % 3 == 2):
                    count += 1
                if(index_k == 7):
                    if(charCount*3 < PixReq and img[i][count][2] % 2 == 1):
                        img[i][count][2] -= 1
                    if(charCount*3 >= PixReq and img[i][count][2] % 2 == 0):
                        img[i][count][2] -= 1
                    count += 1
        count = 0
    #Izrada nove slike
    cv2.imwrite("Desktop\kriptirana_slika.png", img)
    tkinter.messagebox.showinfo("Poruka",  "Enkripcija uspješna")

def decrypt_data_image():
    # algoritam za dekripciju slike
    img = cv2.imread(direktorij_slika)
    data = []
    stop = False
    for index_i, i in enumerate(img):
        i.tolist()
        for index_j, j in enumerate(i):
            if((index_j) % 3 == 2):
                data.append(bin(j[0])[-1])
                data.append(bin(j[1])[-1])
                if(bin(j[2])[-1] == '1'):
                    stop = True
                    break
            else:
                data.append(bin(j[0])[-1])
                data.append(bin(j[1])[-1])
                data.append(bin(j[2])[-1])
        if(stop):
            break

    poruka = []
    # spajanje bitova kako bi dobili slova
    for i in range(int((len(data) + 1) / 8)):
        poruka.append(data[i * 8 : (i * 8 + 8)])
    # spajanje slova kako bi dobili poruku
    poruka = [chr(int(''.join(i), 2)) for i in poruka]
    poruka = ''.join(poruka)
    poruka_label = Label(app, text=poruka, bg='lavender', font=("Times New Roman", 10))
    poruka_label.place(x=350, y=400)

def on_click():
    if kodiranje_var.get() == 'Encode' and tip_datoteke_var.get() == 'Slika - .png': 
        load_image()
        kriptiraj_button = ttk.Button(app, text="Kriptiraj", command=encrypt_data_image)
        kriptiraj_button.place(x=25, y=600)

    elif kodiranje_var.get() == 'Decode' and tip_datoteke_var.get() == 'Slika - .png': 
        load_image()
        dekriptiraj_button = ttk.Button(app, text="Dekriptiraj", command=decrypt_data_image)
        dekriptiraj_button.place(x=25, y=600)
    
    elif kodiranje_var.get() == 'Encode' and tip_datoteke_var.get() == 'Audio - .wav': 
        load_audio()
        kriptiraj_zvuk_button = ttk.Button(app, text="Kriptiraj", command=encrypt_data_audio)
        kriptiraj_zvuk_button.place(x=25, y=350)

    elif kodiranje_var.get() == 'Decode' and tip_datoteke_var.get() == 'Audio - .wav': 
        load_audio()
        kriptiraj_zvuk_button = ttk.Button(app, text="Dekriptiraj", command=decrypt_data_audio)
        kriptiraj_zvuk_button.place(x=25, y=350)

#Kreiranje GUI
app = Tk()
app.configure(background='lavender')
app.title("Steganografija")
app.geometry('700x700')

#Radio button za encode i decode
lf = LabelFrame(app, text='Encode/Decode')
lf.grid(column=0, row=0, padx=20, pady=20)
lf.place(x=25, y= 10)

kodiranje_var = StringVar()
kodiranje = ('Encode', 'Decode')

grid_column = 0
for alignment in kodiranje:
    radio1 = Radiobutton(lf, text=alignment, value=alignment, variable=kodiranje_var)
    radio1.grid(column=grid_column, row=0, ipadx=10, ipady=10)
    grid_column += 1

#Radio button za tip datoteke
lf2 = LabelFrame(app, text='Datoteka')
lf2.grid(column=0, row=0, padx=20, pady=20)
lf2.place(x=250, y= 10)

tip_datoteke_var = StringVar()
tip_datoteke = ('Slika - .png', 'Audio - .wav')

grid_column = 0
for alignment in tip_datoteke:
    radio2 = Radiobutton(lf2, text=alignment, value=alignment, variable=tip_datoteke_var)
    radio2.grid(column=grid_column, row=0, ipadx=10, ipady=10)
    grid_column += 1

txt = Text(app, wrap=WORD, width=30)
txt.place(x=25, y=125, height=145)
unesi_label = Label(app, text="Unesi kriptirani tekst:", bg='lavender', font=("Times New Roman", 10))
unesi_label.place (x=25, y=104)

#Gumb za pokretanje
pokreni = ttk.Button(app, text="Učitaj datoteku", command=on_click)
pokreni.place(x=25, y=300)

app.mainloop()
