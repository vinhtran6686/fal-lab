import sys, numpy as np
from PIL import Image
from masks import *
from polar import *
from rebuild import build_layer, raster_union
from shapes import stroke_path
v,f,l,out=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
M={x:clean_mask(v,f,x) for x in LAYERS[v]}
U=np.zeros((700,700),bool)
for m in M.values(): U|=m
cx,cy,_=fit_centre(U); seam=seam_angle(U,(cx,cy))
sh=build_layer(M[l],(cx,cy),seam)
from rebuild import render; rm=render(sh,(cx,cy))
m=M[l]
img=np.zeros((700,700,3),np.uint8)+20
img[m&rm]=(200,200,200); img[m&~rm]=(0,255,0); img[rm&~m]=(255,0,0)
ys,xs=np.nonzero(m|rm); 
Image.fromarray(img[max(ys.min()-10,0):ys.max()+10, max(xs.min()-10,0):xs.max()+10]).save(out)
for p in sh: print(round(np.degrees(p['theta1']-p['theta0'])), 'Wmax',round(p['Wmax'],1),'rmsw',round(p['rms_w'],2),'rmss',round(p['rms_spine'],2),'npar',p['npar'], 'a,b',round(p['a'],2),round(p['b'],2))
