import tkinter as tk
from tkinter.constants import S
from PIL import ImageTk, Image
import numpy as np
WIDTH = 800
HEIGHT = 500
BALLWITH=90

N_FIELDS=6




def create_image(imgfile,alpha=1,size=1.0):
    opacity_level=int(alpha*255)
    img=Image.open(imgfile)
    if size<1.0:
        s=img.size
        img=img.resize((int(s[0]*size), int(s[1]*size)), Image.ANTIALIAS)

    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[3] < opacity_level:
            newData.append(item)
        else:
            item=(item[0],item[1],item[2],opacity_level)
            newData.append(item)

    img.putdata(newData)
    img=ImageTk.PhotoImage(img)
    return img


class tanks:
    def __init__(self,master,imgfile,x=20,y=20,hidden=False):
        self.x=x
        self.y=y
        self.speedx = 5
        self.speedy = 5
        self.master=master
        self.img=create_image(imgfile,size=0.5)
        self.shape = master.create_image(self.x,self.y,anchor=tk.NW, image=self.img)
        if hidden:
            self.hide()


    def ball_update(self):
        self.x+=self.speedx
        self.y+=self.speedy
        self.master.moveto(self.shape, self.x, self.y)

        if self.x >= WIDTH-BALLWITH or self.x <= 0:
            self.speedx *= -1
        if self.y >= HEIGHT-BALLWITH or self.y <= 0:
            self.speedy *= -1

    def delete(self):
        self.master.delete(self.shape)

    def show(self):
        self.master.itemconfig(self.shape, state='normal')

    def hide(self):
        self.master.itemconfig(self.shape, state='hidden')




class battle_field(tk.Canvas):
    def __init__(self,master,n_battalions, win):
        tk.Canvas.__init__(self,master,bg='pink')
        self.master=master
        self.n_battalions=n_battalions
        self.battalion_objects_player=[]
        self.battalion_objects_computer=[]
        self.win=win
        


        #Adding fields:
        self.battalion_stand_computer=tk.Canvas(self,bg='grey', height=180)
        self.playing_field=tk.Canvas(self,bg='orange')
        self.battalion_stand_player=tk.Canvas(self,bg='grey', height=180)

        #Adding buttons
        self.button_pluss=tk.Button(self,text='+',font="Courier 20 bold",
            command=self.pluss_player
            )
        self.button_minus=tk.Button(self,text='-',font="Courier 20 bold",
            command=self.minus_player
            )

        #Information about number of battalions for player:
        self.info_txt_player=tk.StringVar(self)
        self.info_player=tk.Label(self,textvariable=self.info_txt_player,font="Courier 20 bold")
        self.info_txt_player.set(0)


        self.columnconfigure(0,weight=1)
        for i,w in [(0,1),(1,8), (2,1), (3,1), (4,1), (5,1)]:
            self.rowconfigure(i,weight=w)

        self.battalion_stand_computer.grid(column=0,    row=0,sticky=tk.NSEW)
        self.playing_field.grid(column=0,               row=1,sticky=tk.NSEW)
        self.battalion_stand_player.grid(column=0,      row=2,sticky=tk.NSEW)
        self.button_pluss.grid(column=0,                row=3,sticky=tk.NSEW)
        self.button_minus.grid(column=0,                row=4,sticky=tk.NSEW)
        self.info_player.grid(column=0,                 row=5,sticky=tk.NSEW)

        
        
    def pluss_player(self):
        if self.win.get_battalions_left()==0:
            self.win.message('You have no more battalions to deploy')
            return
        self.win.message('')
        self.pluss(self.battalion_objects_player, self.battalion_stand_player,self.info_txt_player)


    def minus_player(self):
        self.win.message('')
        self.minus(self.battalion_objects_player,self.info_txt_player)

    def set_player(self,n_battalions):
        self.set(n_battalions, self.battalion_objects_player, self.battalion_stand_player,self.info_txt_player)

    def pluss_computer(self, hidden=False):
        if self.win.get_battalions_left(False)==0:
            return
        self.pluss(self.battalion_objects_computer, self.battalion_stand_computer,self.info_txt_computer,hidden)

    def minus_computer(self):
        self.minus(self.battalion_objects_computer,self.info_txt_computer)

    def set_computer(self,n_battalions,hidden=False):
        self.set(n_battalions, self.battalion_objects_computer, self.battalion_stand_computer,hidden=hidden)

    def set(self,n_battalions,battalions,battalion_stand, info=None,hidden=False):
        while n_battalions>len(battalions) and self.win.get_battalions_left(False)>0:
            self.pluss(battalions,battalion_stand,info,hidden)
        while n_battalions<len(battalions):
            self.minus(battalions,info)



    def pluss(self,battalions,battalion_stand,info,hidden=False):
        CDIST=40
        RDIST=40
        NCOLS=6

        row=int(len(battalions)/NCOLS)
        x=(len(battalions)-row*NCOLS)*CDIST
        y=10+row*RDIST
        battalions.append(tanks(battalion_stand,'tanks.png',x,y,hidden))
        if not info is None:
            info.set(len(battalions))
        self.win.battalions_left.set(f'Remaining Battalions: {self.win.get_battalions_left()}')


    def minus(self,battalions,info):
        if len(battalions)==0:
            return
        battalions.pop().delete()
        self.info_txt_player.set(len(battalions))
        self.win.battalions_left.set(f'Remaining Battalions: {self.win.get_battalions_left()}')

    def clear(self):
        self.playing_field['bg']='orange'
        for i in self.battalion_objects_computer:
            i.delete()
        for i in self.battalion_objects_player:
            i.delete()
        self.battalion_objects_computer=[]
        self.battalion_objects_player=[]
        





class run(tk.Tk):
    def __init__(self,n_fields,n_battalions, player_strategy=None, computer_strategy=None):
        tk.Tk.__init__(self)
        self.title("Blotto")
        self.geometry('%sx%s+%s+%s' %(self.winfo_screenwidth(),self.winfo_screenheight()-75,-5,0))
        self.n_fields=n_fields
        self.n_battalions=n_battalions
        self.mean_battalions=int(self.n_battalions/n_fields)
        self.battlefields=[]
        self.iterations=0
        self.tot_points=0

        #Defining strategies:
        if computer_strategy is None:
            self.computer_strategy=default_computer_strategy
        else:
            self.computer_strategy=computer_strategy
        if player_strategy is None:
            self.player_strategy=default_player_strategy
        else:
            self.player_strategy=player_strategy

        #Defining main areas:
        self.battlefields_canvas=tk.Canvas(self,bg="yellow")#this is the total screen area
        self.controls=tk.Canvas(self,bg="red")#This is the bottom area wtih buttons and output

        #Defining buttons:
        self.buttons=tk.Canvas(self.controls,bg="red")
        self.button_attack=tk.Button(self.buttons,command=self.attack, text="Attack",font="Courier 20 bold")
        self.button_restart=tk.Button(self.buttons,command=self.restart, text="Restart",font="Courier 20 bold")

        #Defining information text containers:
        outputfont="Courier 16 bold"
        self.output=tk.Canvas(self.controls,bg="blue")
        self.output_text=tk.StringVar(self)
        self.output_label=tk.Label(self.output,textvariable=self.output_text,font=outputfont,justify=tk.LEFT,anchor=tk.W,width=30,bg='light grey')
        self.message('')
        self.battalions_left=tk.StringVar(self)
        self.battalions_left_label=tk.Label(self.output,textvariable=self.battalions_left,font=outputfont,justify=tk.LEFT,anchor=tk.W,width=30)
        self.battalions_left.set(f'Remaining Battalions: {n_battalions}')
        self.points_txt=tk.StringVar(self)
        self.points=tk.Label(self.output,textvariable=self.points_txt,font=outputfont,justify=tk.LEFT,anchor=tk.W,width=30)
        self.points_txt.set(f'Points: 0 \t Total points: 0')
        

        #Defining battlefileds:
        for i in range(n_fields):
            bf=battle_field(self.battlefields_canvas,n_battalions,self)
            self.battlefields.append(bf)

        self.configure_layout()
        self.grid_all()
        self.initiate_game()

        self.mainloop()


    def initiate_game(self):
        #initiating players battalions:
        
        battalions=self.player_strategy(self.n_battalions, self.n_fields)
        assert sum(battalions)==self.n_battalions
        for i in range(len(self.battlefields)):
            self.battlefields[i].set_player(battalions[i])

        #setting computers battalions
        battalions=self.computer_strategy(self.n_battalions, self.n_fields)
        assert sum(battalions)==self.n_battalions
        for i in range(len(self.battlefields)):
            self.battlefields[i].set_computer(battalions[i],True)



    def configure_layout(self):
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1)
        self.columnconfigure(0,weight=1)
        self.battlefields_canvas.rowconfigure(0,weight=1)
        for i in range(self.n_fields):
            self.battlefields_canvas.columnconfigure(i,weight=1)

        self.controls.rowconfigure(0,weight=1)
        self.controls.rowconfigure(1,weight=1)
        self.controls.columnconfigure(0,weight=1)

        self.output.rowconfigure(0,weight=1)
        self.output.columnconfigure(0,weight=1)
        self.output.columnconfigure(1,weight=1)
        self.output.columnconfigure(2,weight=1)

        self.buttons.rowconfigure(0,weight=1)
        self.buttons.columnconfigure(0,weight=1)
        self.buttons.columnconfigure(1,weight=1)


    def grid_all(self):
        for i in range(self.n_fields):
            self.battlefields[i].grid(column=i,row=0,sticky=tk.NSEW)

        self.battlefields_canvas.grid(  row=0,  sticky=tk.NSEW)             #master: self
        self.controls.grid(             row=1,  column=0,sticky=tk.EW)      #master: battlefields_canvas

        self.buttons.grid(  row=0,  column=0,sticky=tk.EW)                  #master: controls
        self.output.grid(   row=1,  column=0,sticky=tk.EW)                  #master: controls

        self.button_attack.grid( row=0, column=0,   sticky=tk.EW)           #master: buttons
        self.button_restart.grid(row=0, column=1,   sticky=tk.EW)           #master: buttons
        
        self.battalions_left_label.grid(row=0,  column=0,   sticky=tk.EW)   #master: output
        self.output_label.grid(         row=0,  column=1,   sticky=tk.EW)   #master: output
        self.points.grid(               row=0,  column=2,   sticky=tk.EW)   #master: output


    def attack(self):
        player_battalions, computer_battalions=self.get_battalion_count()
        diff=(player_battalions-computer_battalions)
        points=np.sum(diff>0)-np.sum(diff<0)
        self.show_computer()
        self.set_colors()
        if points>0:
            self.message(f'YOU WON BY {points} POINTS')
        elif points==0:
            self.message('It was a draw')
        else:
            self.message(f'YOU LOST BY {-points} POINTS')
        
        data={'Iteration':self.iterations, 
                'Points':points
        }

        self.tot_points+=points
        self.points_txt.set(f'Points: {points} \t Total points: {self.tot_points}')


    def restart(self):
        for i in self.battlefields:
            i.clear()
        self.initiate_game()
        
    def show_computer(self):
        for i in self.battlefields:
            for j in i.battalion_objects_computer:
                j.show()

    def get_battalions_left(self,player=True):
        b=0
        for i in self.battlefields:
            if player:
                b+=len(i.battalion_objects_player)
            else:
                b+=len(i.battalion_objects_computer)
        return self.n_battalions-b

    def message(self,message):
        self.output_text.set(f'Message: {message}')

    def get_battalion_count(self):
        battalions_player=[]
        battalions_computer=[]
        for i in self.battlefields:
            battalions_player.append(len(i.battalion_objects_player))
            battalions_computer.append(len(i.battalion_objects_computer))
        return np.array(battalions_player, dtype=int), np.array(battalions_computer, dtype=int)


    def set_colors(self):
        for b in self.battlefields:
            diff=len(b.battalion_objects_player)-len(b.battalion_objects_computer)
            if diff>0:
                b.playing_field['bg']='green'
            elif diff==0:
                b.playing_field['bg']='orange'
            else:
                b.playing_field['bg']='red'





def default_computer_strategy(n_battalions,n_fields):
    #put your code here to change strategy
    #The function needs to return a vector with as many elements as there are battlefields (n_fields)
    #The total numner of battalions employed should equal n_battalions

    #random strategy:
    mean_battalions=int(n_battalions/n_fields)
    battalions=[np.random.randint(3)+1 for i in range(n_fields)]
    while True:
        for i in range(n_fields):
            if sum(battalions)==n_battalions:
                return battalions
            elif sum(battalions)<n_battalions:
                battalions[i]+=1
            elif sum(battalions)>n_battalions and battalions[i]>0:
                battalions[i]-=1


def default_player_strategy(n_battalions,n_fields):
        mean_battalions=int(n_battalions/n_fields)
        battalions=np.ones(n_fields,dtype=int)*mean_battalions
        #assigning the rest to random battlefields:
        rest=n_battalions-mean_battalions*n_fields
        rnd_sel=np.random.rand(n_fields).argsort()[:rest]
        battalions[rnd_sel]+=1
        assert sum(battalions)==n_battalions
        return battalions