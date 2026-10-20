import sys, json, glob, os, pathlib
sys.path.insert(0,'/home/user/fal-lab/scripts')
from PIL import Image
ROOT=pathlib.Path('/home/user/fal-lab'); A=ROOT/'out/heroes/holy_commander'
SET=A/'.work/side_export'; SPR=ROOT/'tools/kr_compare/sprites/holy_commander'
S=120/268.0   # finish scale: the master body (268 px in the 480 px-high clip) -> 120 px @2x, as run_side
CW=CH=512; AX,AY=256,400
jobs={'attack':('attack_fast_frames','raw/attack_side_attack_t04.mp4',True),
      'death':('death_fast_frames','raw/death_side_death_t01.mp4',False),
      'skill':('charge_v4','raw/skill_side_skill_charge_v4_t01.mp4',False)}
state={'actions':{}}
for act,(src,clip,hit) in jobs.items():
    fr=sorted(glob.glob(str(SPR/src/'*.png'))); ims=[Image.open(f).convert('RGBA') for f in fr]
    b=ims[0].getchannel('A').point(lambda v:255 if v>24 else 0).getbbox()
    fx,fy=(b[0]+b[2])/2,b[3]
    d=SET/'fin'/act; d.mkdir(parents=True,exist_ok=True)
    for f in d.glob('*.png'): f.unlink()
    for n,im in enumerate(ims):
        sm=im.resize((round(im.width*S),round(im.height*S)),Image.LANCZOS)
        c=Image.new('RGBA',(CW,CH),(0,0,0,0)); c.paste(sm,(round(AX-fx*S),round(AY-fy*S))); c.save(d/f'f_{n:03d}.png')
    n=len(ims); sel={'start':0,'endExclusive':n,'durationsMs':[67]*n,'loopPolicy':'oneshot','fps':15}
    if hit: sel['impactMs']=round(0.4*67*n)
    (SET/f'sel_{act}.json').write_text(json.dumps(sel)); (SET/f'fin_{act}.json').write_text(json.dumps({'anchor':[AX,AY]}))
    state['actions'][act]={'status':'done','output':{'take':1},'takes':[{'take':1,'clip':{'path':'../../'+clip},'route':'supplied',
        'stages':{'finished':{'framesDir':f'fin/{act}','metadata':f'fin_{act}.json'},'selection':{'selection':f'sel_{act}.json'}}}]}
    print(act,src,n,'frames')
(SET/'set_state.json').write_text(json.dumps(state,indent=1))
