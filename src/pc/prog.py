import Tkinter as tk
import math
from uart import *

WIDTH = 400
HEIGHT = 400

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=400, height=400)
        self.grid(sticky="WENS")

        self.parent = master;
        
        self.createWidgets()
        self.updateCanvas()

        self.stend = Stend(port = 'COM11')
        #self.after_idle(lambda: self.minsize(400, 500))
        

    def createWidgets(self):
        self.regulators = tk.LabelFrame(self, text="Regulator", padx=5, pady=5)
        self.regulators.grid(row = 1, column = 2, padx=10, pady=10, sticky="WEN")

        self.setParametrs = tk.LabelFrame(self, text="Set Parameter", padx=5, pady=5)
        self.setParametrs.grid(row = 2, column = 2, padx=10, pady=10, sticky="WENS")

        self.visCanvas = tk.LabelFrame(self, text="Stend visualization", padx=5, pady=5)
        self.visCanvas.grid(row = 1, column = 1,rowspan=3,  padx=10, pady=10, sticky="WENS")

        self.canvas = tk.Canvas(self.visCanvas, width=WIDTH, height=HEIGHT, bg = "white")
        self.canvas.pack()

        self.infoStend = tk.LabelFrame(self, text="Stend Info", padx=5, pady=5)
        self.infoStend.grid(row = 3, column = 2, padx=10, pady=10, sticky="WENS")

        #Regulator
        tk.Label(self.regulators, text="P:").grid(row=0, sticky="W")
        tk.Label(self.regulators, text="I:").grid(row=1, sticky="W")
        tk.Label(self.regulators, text="D:").grid(row=2, sticky="W")
        tk.Button(self.regulators, text="Upload", width=10, command=self.updatePID).grid(row=3, sticky="W")
        tk.Button(self.regulators, text="Load", width=10, command=self.loadPID).grid(column=1, row=3, sticky="E")

        self.pid_P = tk.StringVar()
        self.pid_I = tk.StringVar()
        self.pid_D = tk.StringVar()

        self.pid_P.set('1400')
        self.pid_I.set('400')
        self.pid_D.set('50')
        
        
        tk.Entry(self.regulators, textvariable=self.pid_P).grid(row=0, column=1)
        tk.Entry(self.regulators, textvariable=self.pid_I).grid(row=1, column=1)
        tk.Entry(self.regulators, textvariable=self.pid_D).grid(row=2, column=1)

        #Set parametrs
        tk.Label(self.setParametrs, text="Throttle:").grid(row=0, sticky="W")
        tk.Label(self.setParametrs, text="Angle:").grid(row=1, sticky="W")
        
        self.t = tk.Scale(self.setParametrs, from_=0, to=100, orient=tk.HORIZONTAL, command=self.updateThrott)
        self.t.set(40)
        self.t.grid(row=0, column=1)
        

        self.w = tk.Scale(self.setParametrs, from_=-100, to=100, orient=tk.HORIZONTAL, command=self.updateAngle)
        self.w.set(0)
        self.w.grid(row=1, column=1)
        

        tk.Label(self.infoStend, text="Angle:").grid(row=0, sticky="W")
        tk.Label(self.infoStend, text="M1:").grid(row=1, sticky="W")
        tk.Label(self.infoStend, text="M2:").grid(row=2, sticky="W")
        tk.Label(self.infoStend, text="Pwm:").grid(row=3, sticky="W")
        tk.Label(self.infoStend, text="Step time:").grid(row=4, sticky="W")

        self.viewAngle = tk.StringVar()
        self.viewAngle =  tk.StringVar()
        self.viewPwm1 =  tk.StringVar()
        self.viewPwm2 = tk.StringVar()
        self.viewPwm =  tk.StringVar()
        self.viewDelay =  tk.StringVar()
        
        tk.Label(self.infoStend, text="0", textvariable=self.viewAngle).grid(row=0, column=1, sticky="W")
        tk.Label(self.infoStend, text="0", textvariable=self.viewPwm1).grid(row=1, column=1, sticky="W")
        tk.Label(self.infoStend, text="0", textvariable=self.viewPwm2).grid(row=2, column=1, sticky="W")
        tk.Label(self.infoStend, text="0", textvariable=self.viewPwm).grid(row=3, column=1, sticky="W")
        tk.Label(self.infoStend, text="0", textvariable=self.viewDelay).grid(row=4, column=1, sticky="W")

        self.plank = Line(self.canvas, (200/2, 200/2), 45, 88)
        self.plankZad = Line(self.canvas, (200/2, 200/2), 45, 88)
        '''w = tk.Entry(self.setParametrs)
        w.pack()

        w = tk.Entry(self.infoStend)
        w.pack()'''
        
    def updateCanvas(self):
        self.canvas.delete("all")
        stendAngle = 0
        try:
            data = self.stend.get_data()
            #print data
            stendAngle = data['angles'][0]
            self.viewAngle.set(str(stendAngle))
            self.viewPwm1.set(str(data['pwm'][0]))
            self.viewPwm2.set(str(data['pwm'][1]))
            self.viewPwm.set(str(data['pwm'][1]))
            self.viewDelay.set(str(round(data['delay'], 5)))
        except:
            pass
        
        '''self.canvas.create_line(10, 200/2, 200-10, 100, width = 5) # plank
        self.canvas.create_line(200/2+20, 200/2+20, 200/2, 200/2, width = 5) #
        self.canvas.create_line(200/2-20, 200/2+20, 200/2, 200/2, width = 5) #
        self.canvas.create_line(200/2-20, 200/2+20, 200/2+20, 200/2+20, width = 5) #'''
        
        self.plank.draw(stendAngle)
        self.plankZad.draw(180-self.w.get(), fill="red", dash=(4, 4), width = 2)

        self.parent.after(100, self.updateCanvas)

    def updateThrott(self, e):
        th = int(self.t.get())
        self.stend.set_throttle(th)
        print th
        
    def updateAngle(self, e):
        angle = int(self.w.get())
        self.stend.set_angle(angle)
        print angle
        
    def updatePID(self):
        pid = (int(self.pid_P.get()), int(self.pid_I.get()), int(self.pid_D.get()))
        self.stend.set_pid(pid)
        print pid
        
    def loadPID(self):
        print 'load'
        print self.stend.get_pid()

class Line(tk.Frame):
    def __init__(self, parent, c, angle, lenght):
        self.cor = c
        self.parent = parent
        self.angle = angle
        self.lenght = lenght
    def nyak(self, cor, angle):
        return(cor[0] - self.lenght*math.cos(angle*math.pi/180),
               cor[1] - self.lenght*math.sin(angle*math.pi/180))
    def draw(self, angle, fill = 'black', dash=None, width=5):
        self.cor1 = self.nyak(self.cor, angle)
        self.cor2 = self.nyak(self.cor, angle-180)
        self.parent.create_line(int(self.cor[0]), int(self.cor[1]),
                                int(self.cor1[0]), int(self.cor1[1]), width=width, fill=fill, dash=dash)
        
        self.parent.create_line(int(self.cor[0]), int(self.cor[1]),
                                int(self.cor2[0]), int(self.cor2[1]), width=width, fill=fill, dash=dash)        
master = tk.Tk()
master.resizable(width=0, height=0)
app = Application(master)
app.master.title('Stend control')
app.mainloop()
