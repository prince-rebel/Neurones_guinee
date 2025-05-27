#-*- encoding: utf-8 -*-
#Version 1 2009/09/27
#Conversion des Nombres en Caracteres
#langage de programmation Python

#-------------------------------------------------------------
# French
#-------------------------------------------------------------
import pdb
import string
import re

Number_1 = {'fr':{0:'',
     1:'un', 2:'deux', 3:'trois', 4:'quatre', 5:'cinq', 6:'six', 7:'sept', 8:'huit', 9:'neuf'
},'en':{0:'',
     1:'one', 2:'two', 3:'three', 4:'four', 5:'five', 6:'six', 7:'seven', 8:'eight', 9:'nine'
}}

Number_10={'fr':{
    10: 'dix', 20:'vingt', 30:'trente',40:'quarante', 50:'cinquante', 60:'soixante', 70:'soixante-dix', 80:'quatre-vingt', 90:'quatre-vingt-dix'
},'en':{
    10: 'ten', 20:'twenty', 30:'thirty',40:'forty', 50:'fifty', 60:'sixty', 70:'seventy', 80:'eighty', 90:'ninety'
}}

Number_A_10={'fr':{
    11:'onze', 12:'douze', 13:'treize', 14:'quatorze', 15:'quinze', 16:'seize'
},'en':{
    11:'eleven', 12:'twelve', 13:'thirteen', 14:'fourteen', 15:'fifteen', 16:'sixteen',17:'seventeen',18:'eighteen',19:'nineteen'
}}

Number_B_10={'fr':{
    71:'soixante-onze', 72:'soixante-douze', 73:'soixante-treize', 74:'soixante-quatorze', 75:'soixante-quinze', 76:'soixante-seize'
}}

Number_C_10={'fr':{
    91:'quatre-vingt-onze', 92:'quatre-vingt-douze', 93:'quatre-vingt-treize', 94:'quatre-vingt-quatorze', 95:'quatre-vingt-quinze', 96:'quatre-vingt-seize'
}}

Number_100={'fr':{ 1:'Cent' ,2:'Cent'},'en':{1:'hundred'}}

Number_Mille= {'fr':{1:'Mille'},'en':{1:'thousand'}}

Number_Million={'fr':{1:'Million' },'en':{1:'million'}}
Number_Millions={'fr':{1:'Millions' },'en':{1:'millions'}}

#Lang= ['fr','en']

#-------------------------------------------------------------
# Function Number_To_Word_10
#argument: Number (integer)
#return Word (String)
#-------------------------------------------------------------

def _Number_To_Word_10(Number,langue) :
    #division
    Reste=int(Number/10)
    Modulo=Number%10
    Word=''
    if(Reste==0 and Modulo==0):
       Word=Number_1[langue][Modulo]
    elif(Reste==0 and Modulo):
       Word=Number_1[langue][Modulo]
    elif(Reste ==1 and Modulo < 7):
     if(Modulo ==0):
       Word=Number_10[langue][Number]
     else:
       Word=Number_A_10[langue][Number]
    
    elif(Reste == 1 and Modulo >=7) :
       Word=Number_10[langue][10]+' '+Number_1[langue][Modulo]
    
    elif(Reste > 1 and Reste < 7) :
       if(Modulo ==0):
        Word=Number_10[langue][Number]
       else:
        Word=Number_10[langue][Reste*10] +' '+Number_1[langue][Modulo]
    elif(Reste >=7 and langue=="fr"):
        if(Modulo ==0):
          Word=Number_10[langue][Number]
        elif(Reste==7):
          if(Modulo  < 7):
            Word=Number_B_10[langue][Number]
          else:
             Word=Number_10[langue][Reste*10]+' '+Number_1[langue][Modulo]
        elif(Reste==8):
          Word=Number_10[langue][Reste*10] +' '+Number_1[langue][Modulo]
        elif(Reste==9):
          if(Modulo  < 7):
            Word=Number_C_10[langue][Number]
          else:
            Word=Number_10[langue][Reste*10]+' '+Number_1[langue][Modulo]
        else:
          pass
    else:
       if(Modulo ==0):
          Word=Number_10[langue][Number]
       else:
          Word=Number_10[langue][Reste*10] +' '+Number_1[langue][Modulo]

    return Word 

def _Number_To_Word_100(Number,lang):
    Reste=int(Number/100)
    Modulo=Number%100
    Word=''
      
    if(Modulo==0):
      if(Reste==1):
         Word=Number_100[lang][1] 
      elif(lang =="fr"):
         Word= Number_1[lang][Reste]+' '+Number_100[lang][2]
      else:
         Word= Number_1[lang][Reste]+' '+Number_100[lang][1]
    else:
       if(Reste==1):
         Word=Number_100[lang][1]+' '+_Number_To_Word_10(Modulo,lang)
       elif(lang=="fr"):
         Word=Number_1[lang][Reste]+' '+Number_100[lang][2]+' '+_Number_To_Word_10(Modulo,lang)   
       else:
         Word=Number_1[lang][Reste]+' '+Number_100[lang][1]+' '+_Number_To_Word_10(Modulo,lang) 
    return Word 

def _Number_To_Word_1000(Number,lang):
    Reste=int(Number/1000)
    Modulo=Number%1000
    Word=''
      
    if(Reste==1):
       if(Modulo ==0):
         Word=Number_Mille[lang][1] 
       elif(Modulo >=1 and Modulo< 10):
         Word=Number_Mille[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=Number_Mille[lang][1] +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=Number_Mille[lang][1] +' '+_Number_To_Word_100(Modulo,lang)
       else:
         pass

    elif(Reste< 10 and Reste >= 0) :
       if(Modulo ==0):
         Word=Number_1[lang][Reste]+' '+Number_Mille[lang][1] 
       elif(Modulo >=1 and Modulo< 10):
         Word=Number_1[lang][Reste]+' '+Number_Mille[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=Number_1[lang][Reste]+' '+Number_Mille[lang][1] +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         #   modif
         Word=Number_1[lang][Reste]+' '+Number_Mille[lang][1] +' '+_Number_To_Word_100(Modulo,lang)
       else:
         pass

    elif(Reste< 100 and Reste >= 10 ) :
       if(Modulo ==0):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Mille[lang][1] 
       elif(Modulo >=1 and Modulo< 10):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Mille[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Mille[lang][1] +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Mille[lang][1] +' '+_Number_To_Word_100(Modulo,lang)
       else:
         pass
            
    elif(Reste< 1000 and Reste >= 100 ) :
       if(Modulo ==0):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Mille[lang][1] 
       elif(Modulo >=1 and Modulo< 10):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Mille[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Mille[lang][1] +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Mille[lang][1] +' '+_Number_To_Word_100(Modulo,lang)
       else:
         pass

    return Word 

def _Number_To_Word_Million(Number,lang): 
    Reste=int(Number/1000000)
    Modulo=Number%1000000
    Word=''

    if(Reste==1):
       if(Modulo ==0):
         Word=Number_1[lang][1]+' '+Number_Million[lang][1] 
       elif(Modulo >=0 and Modulo< 10):
         Word=Number_1[lang][1]+' '+Number_Million[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=Number_1[lang][1]+' '+Number_Million[lang][1]+' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=Number_1[lang][1]+' '+Number_Million[lang][1]+' '+_Number_To_Word_100(Modulo,lang)
       elif(Modulo >=1000 and Modulo< 1000000):
         Word=Number_1[lang][1]+' '+Number_Million[lang][1] +' '+_Number_To_Word_1000(Modulo,lang)
       else:
         pass

    elif(Reste< 10 and Reste > 1) :
       if(Modulo ==0):
         Word=Number_1[lang][Reste]+' '+Number_Millions[lang][1]
       elif(Modulo >=1 and Modulo< 10):
         Word=Number_1[lang][Reste]+' '+Number_Millions[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=Number_1[lang][Reste]+' '+ Number_Millions[lang][1]+' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=Number_1[lang][Reste]+' '+ Number_Millions[lang][1]+' '+_Number_To_Word_100(Modulo,lang)
       elif(Modulo >=1000 and Modulo< 1000000):
         Word=Number_1[lang][Reste]+' '+Number_Millions[lang][1] +' '+_Number_To_Word_1000(Modulo,lang)
       else:
         pass

    elif(Reste< 100 and Reste >= 10 ) :
       if(Modulo ==0):
         Word=_Number_To_Word_10(Reste,lang)+' '+ Number_Millions[lang][1]
       elif(Modulo >=1 and Modulo< 10):
         Word=_Number_To_Word_10(Reste,lang)+' '+ Number_Millions[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Millions[lang][1]  +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=_Number_To_Word_10(Reste,lang)+' '+ Number_Millions[lang][1] +' '+_Number_To_Word_100(Modulo,lang)
       elif(Modulo >=1000 and Modulo< 1000000):
         Word=_Number_To_Word_10(Reste,lang)+' '+Number_Millions[lang][1] +' '+_Number_To_Word_1000(Modulo,lang)
       else:
         pass
            
    elif(Reste< 1000 and Reste >= 100 ) :
       if(Modulo ==0):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Millions[lang][1]
       elif(Modulo >=1 and Modulo< 10):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Millions[lang][1] +' '+Number_1[lang][Modulo]
       elif(Modulo >=10 and Modulo< 100):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Millions[lang][1] +' '+_Number_To_Word_10(Modulo,lang)
       elif(Modulo >=100 and Modulo< 1000):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Millions[lang][1]  +' '+_Number_To_Word_100(Modulo,lang)
       elif(Modulo >=1000 and Modulo< 1000000):
         Word=_Number_To_Word_100(Reste,lang)+' '+Number_Millions[lang][1] +' '+_Number_To_Word_1000(Modulo,lang)
       else:
         pass

    return Word 
  
def Number_To_Word(Number,lang,Devise,Devise2,Round=2):

    Round=Round
    Word=''
    dict_round={2:100,3:1000,4:10000,5:100000,6:1000000,7:10000000,8:10000000}
    if(isinstance(Number,int) or isinstance(Number,float)):
       Number =str(Number)
    else:
       pass
    if(isinstance(Number,str)):
      NoCaracter=re.compile('[^0-9]')
      findCaracter=NoCaracter.search(Number)
      if(findCaracter):
        isNumber=re.compile('^[0-9]{1,}'+findCaracter.group()+'[0-9]{0,}$')
        if(isNumber.match(Number)):
         index=findCaracter.start()
         firstNumber=int(Number[0:index])
         #endV=len(Number)
         endNumber=int(Number[index+1:index+Round+1])
         if(endNumber !=0):
          try:
            diviseur=dict_round[Round]
          except:
            diviseur=10
          
          endNumber=float(endNumber)/diviseur
          endNumber=round(endNumber,Round)
          endNumber=endNumber*diviseur
          endNumber=int(endNumber)
         else:
           pass
         
         if(firstNumber >= 0 and firstNumber < 10):
          if(firstNumber==0 and endNumber!=0):
            Word=_Number_To_Word_10(endNumber,lang) +' '+Devise2
          elif(endNumber==0):
            Word=''
          else:
           Word=Number_1[lang][firstNumber]+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) +' '+Devise2
         elif(firstNumber >= 10 and firstNumber < 100):
          if(endNumber!=0):
           Word=_Number_To_Word_10(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) +' '+Devise2
          else:
           Word=_Number_To_Word_10(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) 
         elif(firstNumber >= 100 and firstNumber < 1000):
          if(endNumber!=0):
           Word=_Number_To_Word_100(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) +' '+Devise2
          else:
           Word=_Number_To_Word_100(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) 
         elif(firstNumber >= 1000 and firstNumber < 1000000):
          if(endNumber!=0):
            Word=_Number_To_Word_1000(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) +' '+Devise2
          else:
            #   modif
            Word=_Number_To_Word_1000(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) 
         elif(firstNumber >= 1000000 and firstNumber < 1000000000):
          if(endNumber!=0):
            Word=_Number_To_Word_Million(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang) +' '+Devise2
          else:
            Word=_Number_To_Word_Million(firstNumber,lang)+' '+Devise+' '+_Number_To_Word_10(endNumber,lang)
        else:
          return '' 
      else:
        isNumber=re.compile('^[0-9]{1,}$')
        if(isNumber.match(Number)):
           firstNumber=int(Number)
           if(firstNumber >= 0 and firstNumber < 10):
              Word=Number_1[lang][firstNumber]+' '+Devise
           elif(firstNumber >= 10 and firstNumber < 100):
              Word=_Number_To_Word_10(firstNumber,lang)+' '+Devise
           elif(firstNumber >= 100 and firstNumber < 1000):
               Word=_Number_To_Word_100(firstNumber,lang)+' '+Devise
           elif(firstNumber >= 1000 and firstNumber < 1000000):
               Word=_Number_To_Word_1000(firstNumber,lang)+' '+Devise
           elif(firstNumber >= 1000000 and firstNumber < 1000000000):
               Word=_Number_To_Word_Million(firstNumber,lang)+' '+Devise

      Word=Word.upper()
      return Word
     
    else:
       return ''
      
