#!/usr/bin/python3
#coding=utf-8

import queue
from random import randint as rand

class Char():
  """Common PRED profile for character"""

  def __init__(self,randum = 0):
    self.P = 100 #Power, ability to inflict damage
    self.R = 100 #Rate, ablity to make multiple strikes
    self.E = 100 #Endurance, ability to suffer, max Health
    self.D = 100 #Defence, ability to block shit
    self.H = 100 #Health, current Endurance potence
    self.Name = 'Sennoma'   #Tis Warruir hath no name
    self.I = 20             #Initiative
    self.armor = Armor()    #Armor of a Warrior
    self.weapon = Weapon()  #Weapon of Warrior
    
    self.mods = []          #Listo de modificacion

    self.statusoj = []      #Listo de Statusoj de Warrior

    self.pos_x = 0  #X Cord in a Cell
    self.pos_y = 0  #Y Cord in a Cell
    self.cell = None
 
    if randum > 0:
      a_part = rand(25, 75) * randum // 100
      v_part = randum - a_part
      r_part = rand(0, 50) * a_part // 100
      p_part = a_part - r_part
      d_part = rand(0, 50) * v_part // 100
      e_part = v_part - d_part
      self.R = self.c_par(0,r_part)[0]
      self.P = int(self.c_par(0,r_part)[1])+p_part
      self.D = self.c_par(0,d_part)[0]
      self.E = int(self.c_par(0,d_part)[1])+e_part
      self.H = self.E

  def get_pts(self,val):
    if val <= 100:
      return val
    return val*val/100 - val + 100

  def get_dpts(self,base,val):
    if val <= 100:
      return val-base
    return self.get_pts(val) - self.get_pts(base)

  def c_par(self,base,amount):
    ret = [0,0]
    next = base+1
    while self.get_dpts(base, next) <= amount:
      next+=1
      ret[0]+=1
    ret[1] = round(amount - self.get_dpts(base, next-1),2)
    return ret


  def modu(self, parnam, parval):
    for mod in self.mods:
      if mod['TYPE'] == parnam+'_MUL':
        parval*= mod['VAL']
      if mod['TYPE'] == parnam+'_ADD':
        parval+= mod['VAL']
      if mod['TYPE'] == parnam+'_SET':
        parval = mod['VAL']
    return int(parval)

  def getA(self):
    """Attack: Ability attack potential of a char"""
    return self.P*self.R

  def getV(self):
    """Vitality: Ability to overcome damage"""
    return self.E*self.D
  

  def getH(self):
    """return H, even if it's modificated, like a shit!"""
    return self.modu('H',self.H)

  def getE(self):
    """return E, even if it's modificated, like a shit!"""
    return self.modu('E',self.E)

  def getP(self):
    """return P, even if it's modificated, like a shit!"""
    return self.modu('P',self.P)

  def getR(self):
    """return R, even if it's modificated, like a shit!"""
    return self.modu('R',self.R)

  def getD(self):
    """return D, even if it's modificated, like a shit!"""
    return self.modu('D',self.D)

  def getI(self):
    """return I, even if it's modificated, like a shit!"""
    return self.modu('I',self.I)

  def getStrikes(self):
    R = self.getR()
    if R % self.weapon.AR==0:
      return R // self.weapon.AR
    return R // self.weapon.AR + 1
  
  def getS_Chance(self):
    R = self.getR()
    if R % self.weapon.AR==0:
      return self.weapon.AC
    return (self.weapon.AC*(self.getStrikes()-1) + self.weapon.AC * ((R % self.weapon.AR) / self.weapon.AR)) // self.getStrikes()

  def getDodges(self):
    D = self.getD()
    if D % self.armor.DP==0:
      return D // self.armor.DP
    return D // self.armor.DP + 1
  
  def getD_Chance(self):
    D = self.getD()
    if D % self.armor.DP==0:
      return self.armor.DC
    return (self.armor.DC*(self.getDodges()-1) + self.armor.DC * ((D % self.armor.DP) / self.armor.DP)) // self.getDodges()
 
  def move(self,dir):
    """Change the position of a warrior in his excellent square"""
    nx = self.pos[0]+dir[0]
    ny = self.pos[1]+dir[1]
    if nx >= 0 and nx <= 2 and ny >= 0 and ny <=2:
      print('Dauras moving!')
      if self.cell.isfree(nx,ny):
        self.cell.free(self.pos[0],self.pos[1])
        self.cell.add(self,nx,ny)

  def flush_mods(self,type):
    """Option to destroy all modifiers of selected type, ekzemple, to use them unufoje!"""
    for mod in self.mods:
      if mod['T']==type:
         self.mods.remove(mod)
   
class Armor():
  """Armor of a Warrior"""

  def __init__(self):
    self.DC = 80 # Defence Chance, DC
    self.DP = 80 # Defence Potence, DP
    self.AV = 0 # Armor Value, AV
    self.EC = 100 # Evasion Chance
    pass

  def getEC(self):
    """Evasion Chance - Chance to halve incoming damage after sucessfull block"""
    return self.DP/self.DC * 100
   
class Weapon():
  """Weapon of a Warrior"""

  def __init__(self):
    self.AC = 80 #Attack Chance, AC
    self.AR = 80 #Attack Rate, AR
    self.AP = 0 #Armor Piercing
    self.AD = 0 #Additional Damage
    self.PM = 1 #Power Modifier
    pass

  def getAM(self):
    """Atack Modifier - Power Modifier of each sucesfull strike"""
    return self.AR / self.AC

class BQueue():
  """Battle Queue of events"""

  def __init__(self):
    #print ('BQueue created!')
    self.que = []
    self.curt = 0
    self.nque = queue.Queue()
    for i in range(20):
      self.que.append(queue.Queue())
    self.que[0].put({'TYPE':'BATTLE_START','TTL':0})
    self.que[0].put({'TYPE':'PLEN_TURN_START', 'TTL':-1})
    for i in range(20):
      self.que[0].put({'TYPE':'TURN_START', 'TTL':-1, 'NUM':i+1})
      self.que[0].put({'TYPE':'TURN_END', 'TTL':-1, 'NUM':i+1})

  
  def add(self, kio, kien):
    """Add event or turn to a que"""
    if kien+self.curt >= 20:
      self.nque.put([kio,kien+self.curt-20])
    else:
      end = self.que[kien].get()
      self.que[kien].put(kio)
      self.que[kien].put(end)

  def getnext(self):
    """return next event or event"""
    while self.que[self.curt].qsize()==0:
      self.curt += 1
      if self.curt == 20:
        self.curt = 0 
        for i in range(self.nque.qsize()):
          c = self.nque.get()
          if c[1]>=20:
            c[1] = c[1]-20
            self.nque.put(c)
          else:
            self.que[c[1]].put(c[0])
    event = self.que[self.curt].get()
    if event['TTL'] < 0:
      self.nque.put([event,self.curt])
    if event['TTL'] > 0:
      event['TTL'] -= 1
      self.nque.put([event,self.curt])
    return event

class Cell():
  """Cell sur batalkampo"""
  
  def __init__(self,x,y):
    self.x = x
    self.y = y
    self.kamp = [[None,None,None],[None,None,None],[None,None,None]]
    self.ckamp = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]

  def add(self, kio,x,y):
    """adds a mistvieho in a cell"""
    self.kamp[x][y] = kio
    self.ckamp[x][y] = kio.Name[0]
    kio.pos = [x,y]
    kio.cell = self
    
  def draw(self,bord):
    """return an array of strings, that can be drawed like symbold"""
    ret = ['','','']
    n = 0
    if 'n' in bord:
      ret.append('')
      if 'w' in bord:
        ret[0] = ret[0]+'╔'
      ret[0] = ret[0]+'═══'
      if 'e' in bord:
        ret[0] =ret[0]+'╗'
      n = 1
    if 'w' in bord:
      ret[0+n] += '║'
      ret[1+n] += '║'
      ret[2+n] += '║'
    for i in range(3):
      for j in range(3):
        ret[j+n] = ret[j+n]+self.ckamp[i][j]
    if 'e' in bord:
      ret[0+n] += '║'
      ret[1+n] += '║'
      ret[2+n] += '║'
    if 's' in bord:
      ret.append('')
      if 'w' in bord:
        ret[3+n] = '╚'
      ret[3+n] += '═══'
      if 'e' in bord:
        ret[3+n] += '╝'
    return ret
  
  def isfree(self, x, y):
    """Check whether cell is free or not"""
    return self.kamp[x][y]==None
  
  def free(self, x, y):
    """Make the cell free!"""
    self.kamp[x][y] = None
    self.ckamp[x][y] = ' '
 
 

def atako(anto,ato):
  """Default attack of a mistvieho"""
  ret = {}
  strajkoj = anto.getStrikes()
  prec = anto.getS_Chance()
  dodgoj = ato.getDodges()
  dodge = ato.getD_Chance()
  armor= ato.armor.AV - anto.weapon.AP
  if armor < 0:
    armor = 0
  damage = anto.P * anto.weapon.getAM() - armor
  fin_damage = 0
  ret['DAMAGE'] = damage
  ret['STRIKE_COUNT'] = strajkoj
  ret['DODGE_COUNT'] = dodgoj
  ret['DODGE_CHANCE'] = dodge
  ret['ATTACK_CHANCE'] = prec
  ret['STRIKES'] = []
  ret['DODGES'] = []
  for s in range(strajkoj):
    r = rand(0,100)
    ret['STRIKES'].append({'roll':r})
    if r < prec:
      """Hit!"""
      dodge_st = []
      for d in range(dodgoj):
        r = rand(0,100)
        dodge_st.append({'roll':r})
        if r < dodge:
          """Dodge!"""
          damage -= armor
          e = ato.armor.getEC()
          mul=0
          while e >= 100:
            e-=100
            mul+=1
            damage = damage // 2
          if e > 0 and rand(0,100)<e:
            mul+=1
            damage = damage // 2
          dodge_st[-1]['mul'] = mul
      ret['DODGES'].append(dodge_st[:])
      fin_damage+=damage
      ret['STRIKES'][-1]['dmg'] = damage
  ret['ALL_DAMAGE'] = fin_damage
  return ret
           
def Agu(agaro):
  ret = 0
  for ago in agaro:
    if ago["TYPE"] == 'ATTACK':
      k_list = [0.5,1,2]
      anto = ago['ANTO']
      ato = ago['ATO']
      if anto.cell.x > ato.cell.x:
        # print ('right to left!')
        # 'B' is special battle mod. it works only during one attack! It is the mods for range, ekzemple, mifrendo!
        anto.mods.append({'TYPE':"R_MUL",'VAL':k_list[2-anto.pos[0]],'T':'B'})
        anto.mods.append({'TYPE':"D_MUL",'VAL':k_list[anto.pos[0]],'T':'B'})
        ato.mods.append({'TYPE':"R_MUL",'VAL':k_list[ato.pos[0]],'T':'B'})
        ato.mods.append({'TYPE':"D_MUL",'VAL':k_list[2-ato.pos[0]],'T':'B'})
      if anto.cell.x < ato.cell.x:
        #print ('left to right!')
        anto.mods.append({'TYPE':"R_MUL",'VAL':k_list[anto.pos[0]],'T':'B'})
        anto.mods.append({'TYPE':"D_MUL",'VAL':k_list[2-anto.pos[0]],'T':'B'})
        ato.mods.append({'TYPE':"R_MUL",'VAL':k_list[2-ato.pos[0]],'T':'B'})
        ato.mods.append({'TYPE':"D_MUL",'VAL':k_list[ato.pos[0]],'T':'B'})
      stat =  atako(anto,ato)
      print (stat)
      anto.flush_mods('B')
      bq.add({'TYPE':'GET_DAMAGE', 'TTL':0, 'ID':ago['ATO'].Name, 'SRC':ago['ANTO'].Name,'VAL':stat['ALL_DAMAGE']},0)
      ret = stat
    if ago["TYPE"] == 'SUFFER':
      dmg = ago["VAL"]
      for mod in ago["CEL"].mods:
        if mod["TYPE"] == "DEFENSE":
          dmg = dmg // 2
      ago["CEL"].H -= dmg
      ret = dmg
    if ago["TYPE"] == 'DEFENSE':
      ago["ANTO"].mods.append({"TYPE":"DEFENSE","TTL":0,"T":"A"})
    return ret

def turno():
  """turnkontrolilo"""
 
  def getcel(dick,ink):
    k = 1
    for key in dick.keys():
      if ink == key.lower() or ink== str(k):
        return (dick[key])
      k+=1
    return None

  def spam_char(nomo,cell):
    heraro[nomo] = Char(randum=400)
    heraro[nomo].Name = nomo
    herlist.append(nomo)
    cell.add(heraro[nomo],1,1)

  
  w_cell = Cell(0,0)
  e_cell = Cell(1,0)
  herlist = []
  heraro = {}
  spam_char('Mistarch',w_cell)
  spam_char('Sterber',e_cell)
  
  global bq
  bq = BQueue()
 
  for c in herlist:
    bq.add({'TYPE':'HERO_TURN','TTL':0,'ID':c},0)
  
  ans = ''
  while ans!= 'q':
    ev = bq.getnext()
    print(ev)
    if ev['TYPE']=='HERO_TURN':
      cur = heraro[ev['ID']]
      for mod in cur.mods:
        if mod['T']=='A':
          if mod['TTL']== 0:
            cur.mods.remove(mod)
          if mod['TTL']>0:
            mod['TTL']-=1
      ret = True
      while ret:
        ans = input("Turno de " + cur.Name + "!What to do, mistvieh?\n")
        ans = ans.lower()
        arg = False
        args = []
        com = ans.split(' ')
        if len(com)>1:
          arg = True
          args = com[1:]
        if ans == 'q':
           ret = False
           break
        if com[0] == 'a' or com[0] =='attack':
          cel = None
          if arg:
            cel = getcel(heraro,args[0])
          if cel==None:
            cel = cur
          Agu([{'TYPE':'ATTACK','ANTO':heraro[cur.Name],'ATO':cel}])
          print ("%s attacks %s!" % (cur.Name, cel.Name))
          bq.add({'TYPE':'HERO_TURN', 'TTL':0, 'ID':cur.Name},cur.getI())
          ret = False
        elif ans == 'd' or ans == 'defense':
          Agu([{'TYPE':'DEFENSE','ANTO':heraro[cur.Name]}])
          print ("%s defences himself!" % (cur.Name))
          bq.add({'TYPE':'HERO_TURN', 'TTL':0, 'ID':cur.Name},cur.getI())
          ret = False
        elif ans == 'w' or ans == 'wait':
          print ("%s waits!" % (cur.Name))
          bq.add({'TYPE':'HERO_TURN', 'TTL':0, 'ID':cur.Name},cur.getI()//2)
          ret = False
        elif com[0] == 'l' or com[0] == 'list':
          print(arg)
          if arg:
            her = getcel(heraro,args[0])
            print ("%s:\nHealth: %d/%d\nPower: %d\nAttack Rate: %d\nDefense Rate: %d\n" % (her.Name,her.getH(),her.getE(),her.getP(),her.getR(),her.getD()))
          else:
            wcell = w_cell.draw(['n','w','s'])
            ecell = e_cell.draw(['n','e','s'])
            print(wcell[0]+'╦'+ecell[0])
            print(wcell[1]+'║'+ecell[1])
            print(wcell[2]+'║'+ecell[2])
            print(wcell[3]+'║'+ecell[3])
            print(wcell[4]+'╩'+ecell[4])
            i = 1
            for key in heraro.keys():
              print ("%d) %s" % (i,key))
              i+=1
        elif com[0] =='m' or com[0] == 'move':
          if arg:
            dir = [0,0]
            if 'n' in com[1]:
              print('North!')
              dir[1] -= 1
            if 'e' in com[1]:
              print('East!')
              dir[0] += 1
            if 's' in com[1]:
              print('South!')
              dir[1] += 1
            if 'w' in com[1]:
              print('West!')
              dir[0] -= 1
            bq.add({'TYPE':'HERO_MOVE', 'TTL':0, 'ID':cur.Name,'DIR':dir},0)
            bq.add({'TYPE':'HERO_TURN', 'TTL':0, 'ID':cur.Name},cur.getI())
            ret = False
    elif ev['TYPE'] == 'HERO_MOVE':
      print(ev['DIR'])
      heraro[ev['ID']].move(ev['DIR'])
      
    elif ev['TYPE'] == 'GET_DAMAGE':
      dmg = Agu([{'TYPE':'SUFFER','CEL':heraro[ev['ID']],'SRC':heraro[ev['SRC']],'VAL':ev['VAL']}])
      print ("%d damage dealed to %s by %s!" % (dmg,ev['ID'],ev['SRC']))


if __name__ == '__main__':
  turno() 
