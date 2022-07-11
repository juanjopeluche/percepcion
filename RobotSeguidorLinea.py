#------------------ Importar modulos --------------------------------#
from pyArduino import *        # modulo para el manejo de puerto serial
from tkinter import *           
from PIL import Image, ImageTk 
import cv2
import numpy as np
import sys
#------------------ Funcion para cambiar de texto -------------------#
def toggle():
    btn.config(text=btnVar.get())   # Se obtiene valor del boton
# Funcion para cerrar el programa   
def onClossing():
    arduino.sendData([0,0])         # Parar el Robot
    arduino.close()                 # Cerrar el puerto serial  
    root.quit()                     # Salir del bucle de eventos
    cap.release()                   # Cerrar camara
    print("Camara desconectada")
    root.destroy()                  # Destruye la ventana creada
# Funcion para establecer el nivel de umbralizacion 
def thresholdValue(int):
    umbralValue.set(slider.get())   # Establecer el valor numerico 
# Funcion para detectar un objeto     
def DeteccionObjecto(rawImage):
    kernel = np.ones((10,10),np.uint8)  # Nucleo o Kernel
    isObject = False                    # Verdadero si encuentra un objeto
    cx,cy = 0,0                         # Centroide (x), centroide (y)
    area_min = 500                      # Area minima para considerar que es un objeto
    
#------------------ Procesamiento de la imagen ----------------------#
    gray = cv2.cvtColor(rawImage, cv2.COLOR_BGR2GRAY)           # Conversion de grises
    t,binary = cv2.threshold(gray, umbralValue.get(), 255, cv2.THRESH_BINARY_INV) # obtenemos imagen binaria
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)  # Aplicamos operacion morfologica de apertura

#------------------ Hallar contornos de la imagen -------------------#
    contours,_ = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        momentos = cv2.moments(cnt)     # Calculo de los momentos
        area = momentos['m00']          # Calculo del area
        if (area > area_min):           # Condicion de area minima
            # Calculo de los centroides
            cx = int(momentos['m10']/momentos['m00'])     
            cy = int(momentos['m01']/momentos['m00'])
            isObject = True
    return isObject,binary,cx,cy        # Retornamos si hay objeto, imagen binaria, coordenadas 
    
def callback():
#------------------ Funcion para adquirir la imagen -----------------#
        cap.open(url)               # Abrimos la camara 
        ret, frame = cap.read()     # Leemos la imagen
        if ret:
            uRef = 0                # Velocidad lineal del robot
            wRef = 0                # Velocidad angular del robot
            isObject,binary,cx,cy = DeteccionObjecto(frame)     # llamamos a la funcion de deteccion de objeto
            cv2.circle(frame,(cx,cy),10, (0,0,255), -1)         # la idea principal es que el punto verde siga al rojo
            cv2.circle(frame,(cxd,cyd),10, (0,255,0), -1)       # Dibujamos el Punto Deseado en Color Verde
            if isObject:
                hx = frame.shape[1]/2-cx        # Cambio de coordenadas en el eje X
                hxe  = hxd-hx                   # Calculamos el error 
                print (hxe)
                K = 0.002                       # valor en pixeles alto , entonces el valor K deber ser bajo 0.003 1 
                uRef = 0.1                      # Velocidad lineal constante 0.2
                wRef = -K*hxe                   # Ley de control, Variamos velocidad angular       
            else:
                uRef = 0
                wRef = 0
            if btnVar.get() == 'Inicio':        # Si el boton esta iniciado (se hizo un click) 
                arduino.sendData([uRef,wRef])   # Enviar valores de velocidad al Robot
            else:
                arduino.sendData([0,0])         # Enviar 0, si se activo Pause
            
            # Mostramos la imagen original en pantalla 
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    
            img = Image.fromarray(img)
            img.thumbnail((400,400))
            tkimage = ImageTk.PhotoImage(img)
            label.configure(image = tkimage)
            label.image = tkimage
            # Mostramos imagen procesada en pantalla 
            img1 = Image.fromarray(binary)
            img1.thumbnail((400,400))
            tkimage1 = ImageTk.PhotoImage(img1) 
            label1.configure(image = tkimage1)
            label1.image = tkimage1
            root.after(10,callback)
        else:                                   # Si no recibimos exactamente un frame 
            onClossing()
            
#------------------ Camara inalambrica IP ---------------------------#
url='http://192.168.1.215:8080/shot.jpg'
cap = cv2.VideoCapture(url)             # Capturamos imagen externa 
if cap.isOpened():
    print("Camara IP iniciada")
else:
    sys.exit("Camara IP desconectada)
cap.open(url)    
ret, frame = cap.read()

#--------- Posicion deseada en pixeles, Centro de la imagen ---------#
cxd = int(frame.shape[1]/2)             # Centro en eje X         
cyd = int(frame.shape[0]/2)             # Centro en eje Y
# Valor X deseado es igual a 0, para mantener al robot en el origen 
hxd = 0                                 # Robot se mantiene centrado en la linea que va a seguir 

#------------------ Comunicacion serial con arduino -----------------#
port = '/dev/ttyACM0'                   # Numero de puerto serial de Ubuntu
arduino = serialArduino(port)           # Configuramos objeto serial de Arduino
arduino.readSerialStart()               # Se arranca la comunicacion de datos 

#------------------ Interfaz de usuario  ----------------------------#
root = Tk()
root.protocol("WM_DELETE_WINDOW",onClossing)
root.title("SEGUIDOR DE LINEA - PERCEPCION")    # titulo de la ventana que creamos
# Imagen original 
label=Label(root)
label.grid(row=0,padx=20,pady=20)               # 1ra ventana = fila 0, espacio de 20 en X y 20 en Y
# Imagen procesada
label1=Label(root)
label1.grid(row= 0,column=1,padx=20,pady=20)    # 2da ventana = fila 0, columna 1, espacio de 20 en X y 20 en Y
# Creamos el slider en 2da fila, para regular el Umbral de la imagen
umbralValue = IntVar()
slider = Scale(root,label = 'UMBRALIZACION', from_=0, to=255, orient=HORIZONTAL,command=thresholdValue,length=400)  
slider.grid(row = 1)
# Creamos un boton para iniciar o pausar el programa  
btnVar = StringVar(root, 'Pause')               
btn = Checkbutton(root, text=btnVar.get(), width=12, variable=btnVar, offvalue='Pause',
                  onvalue='Inicio', indicator=False, command=toggle)
 # Agregamos el boton a la ventana principal                   
btn.grid(row = 1,column = 1)                   
# inicializamos la funcion principal 
root.after(10,callback)                         # Llamar a callback despues de 10 ms 
root.mainloop()                                 