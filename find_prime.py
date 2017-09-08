##
## Creates a prime of certain size form an image
##

from PIL import Image
import sys
import math
import random
import copy
import prime
import os

if len(sys.argv)<3:
    print "Usage:",sys.argv[0],"[Image path] {primesize}"
    print "    or",sys.argv[0],"[Image path] {width} {height}"
    exit()

#open image and get real size    
basefn = sys.argv[1]
img = Image.open(basefn)
w,h = img.size

if len(sys.argv) ==3:
    # exact prime size is given, find factors closest to the aspect ratio of the image
    SIZE = int(sys.argv[2])
    # makes wider
    W1 = min(filter(lambda x: x>=math.sqrt(SIZE * (w/float(h))),(reduce(list.__add__,  ([i, SIZE//i] for i in range(1, int(SIZE**0.5) + 1) if SIZE % i == 0)))))
    H1 = SIZE / W1
    #makes taller
    W2 = max(filter(lambda x: x<=math.sqrt(SIZE * (w/float(h))),(reduce(list.__add__,  ([i, SIZE//i] for i in range(1, int(SIZE**0.5) + 1) if SIZE % i == 0)))))
    H2 = SIZE / W2
    
    ratio1 = (float(W1)*h)/(H1*w)
    ratio2 = (float(W2)*h)/(H2*w)
    
    #prefere wider over taller, so the images is squished horezontally in the end and letters come out taller
    if ratio1< 1.1 / ratio2:
        W,H = W1,H1
    else:
        W,H = W2,H2
        
    print "Size:", W, H

elif len(sys.argv) >3:
    W,H = int(sys.argv[2]),int(sys.argv[3])

# how much distorion did we get from rounding to a divisor?
ratio = (float(W)*h)/(H*w)

    
def get_prime_string(img,W,H):
    # creates a string of 1 and 8 from an image
    w,h = img.size
    img = img.resize((W,H), Image.ANTIALIAS)
    
    img = img.convert('L')
    avr = sum(img.getdata()) / (W*H)
    bw = img.point(lambda x: 0 if x<avr else 255,'1')
    ps ="".join( map( lambda c: "1" if c>128 else "8",bw.getdata()))
    return ps[:-1]+"1"


def flip(ps):
    #changes a random position
    ran_pos = random.randrange(len(ps))
    c = ps[ran_pos]
    if c == "1":
       n = 7
    else:
       n = random.choice(["0","9","6","4","5","2","3"])      
    newps = ps[:ran_pos-1] + n + ps[ran_pos:]
    return newps

def print_prime(p,W,H):
    for i in range(H):
        print p[i*W: i*W+W]

def make_prime(ps):
    #try changes until a prime is found
    if prime.test_prime(int(ps),50):
        return ps
    i = 1
    while True:
        print "Try",i
        i+=1
        P = flip(ps)
        if prime.test_prime(int(P),50):
            return P
        

def make_pdf(ps,W,H,fn="output.pdf"):
    #use reportlab to generate a pdf with the prime in it
    end = " is a prime, with %i digits." % (W*H)
    rows = []
    for i in range(H):
        rows.append( ps[i*W: i*W+W])
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(fn)

    pdfmetrics.registerFont(TTFont('Square', 'square.ttf'))

    c.setPageSize((16*max(W,len(end)), 16*(2+H)))
    print (16*max(W,len(end)), 16*(2+H))
    c.setFont('Square', 16)

    TOP = 16*(1+H)
    for i,r in enumerate(rows):
        c.drawString(0, TOP - i*16, r)

    c.drawString(0, 8, end)
    c.save()
    

def to_scaled_image(ratio,fn="output.pdf",outfn = "tmp.png"):
    # convert a previously generated pdf to an image with the right proportions
    os.system("convert %s -density 300 -quality 100 -trim -flatten  -alpha off %s" % (fn,outfn) )
    if ratio == 1:
        return
    else:
        img = Image.open(outfn)
        w,h = img.size
        if ratio<1:
            res = img.resize((w,int(h*ratio+.5)), Image.ANTIALIAS)
            res.save(outfn)
        else:
            res = img.resize((int(w/ratio+.5),h), Image.ANTIALIAS)
            res.save(outfn)

if __name__ == "__main__":            
    ps = get_prime_string(img,W,H)
    print_prime(ps,W,H)
    res = make_prime(ps)
    make_pdf(res,W,H,basefn+".prime.pdf")
    to_scaled_image(ratio,basefn+".prime.pdf",basefn+".prime.png")
