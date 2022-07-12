# percepcion
Modulo 4 Robotics

El presente trabajo de proyecto de final de modulo describe el desarrollo de un algoritmo de control para un robot móvil diferencial
que sigue como trayectoria una línea en un plano cartesiano determinado por el usuario, aplicando técnicas de control clásica y técnicas de visión artificial. 

El sistema de control utiliza las técnicas de visión artificial para aplicar operaciones morfológicas y hallar las coordenadas en pixeles
de un punto de interes de la línea a seguir, esto como entrada de un sensor. 

La señal de entrada del punto de interés de la línea, es comparada con una señal de referencia que es el centro de la imagen, respecto al eje x unicamente, 
Por lo que a continuación se aplica una ley de control proporcional, es decir se tiene un sistema de control relimentado ON-OFF.   

