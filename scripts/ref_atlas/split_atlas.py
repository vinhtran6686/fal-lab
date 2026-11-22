"""Split a Cocos-style atlas (png + lua with size / trim / f_quad / alias) into one folder per sprite group.
usage: python scripts/ref_atlas/split_atlas.py <dir> <atlas.lua> <atlas.png>      (run from the repo root)
writes <dir>/out/<group>/{frames/NNNN.png, preview.gif, contact_sheet.png, frames.json} and <dir>/out/README.md (git-ignored, rebuilt on demand).
A frame = the f_quad crop pasted on a `size` canvas at (trim left, trim top); an alias is the same picture under another number."""
import sys, os
os.chdir(sys.argv[1]); LUA, PNG = sys.argv[2], sys.argv[3]
import re,json,collections
from PIL import Image
t=open(LUA,encoding='utf8').read()
atlas=Image.open(PNG).convert('RGBA')
ents={}
for m in re.finditer(r'^\t(\w+) = \{(.*?)^\t\}',t,re.M|re.S):
    b=m.group(2)
    def nums(k):
        mm=re.search(k+r' = \{(.*?)\}',b,re.S); return [int(x) for x in re.findall(r'-?\d+',mm.group(1))] if mm else []
    ents[m.group(1)]={'size':nums('size'),'trim':nums('trim'),'quad':nums('f_quad'),
        'alias':re.findall(r'"(\w+)"',re.search(r'alias = \{(.*?)\}',b,re.S).group(1))}
frames={}  # name -> (entry, src name)
for n,e in ents.items():
    frames[n]=(e,n)
    for a in e['alias']: frames[a]=(e,n)
groups=collections.defaultdict(list)
for n in frames:
    m=re.match(r'(.*)_(\d+)$',n); g,i=(m.group(1),int(m.group(2))) if m else (n,1); groups[g].append((i,n))
out='out'; summary=[]; md=['# go_hero_builder – frame detail\n','Source: `go_hero_builder-1.png` (2048x2048) + `go_hero_builder.lua`. Frame = crop `f_quad`, pasted on `size` canvas at (`trim` left, top). `alias` = same picture as another frame (atlas stores it once).\n']
for g,lst in sorted(groups.items()):
    lst.sort(); gd=f'{out}/{g}'; os.makedirs(gd+'/frames',exist_ok=True)
    W=max(frames[n][0]['size'][0] for _,n in lst); H=max(frames[n][0]['size'][1] for _,n in lst)
    ims=[]; rows=[]
    for i,n in lst:
        e,src=frames[n]; x,y,w,h=e['quad']; tl,tt,tr,tb=e['trim']; sw,sh=e['size']
        assert tl+w+tr==sw and tt+h+tb==sh,(n,e)
        im=Image.new('RGBA',(sw,sh),(0,0,0,0)); im.paste(atlas.crop((x,y,x+w,y+h)),(tl,tt))
        im.save(f'{gd}/frames/{i:04d}.png'); 
        c=Image.new('RGBA',(W,H),(0,0,0,0)); c.paste(im,((W-sw)//2,(H-sh)//2)); ims.append(c)
        rows.append((i,n,src,e))
    gif=[]
    for c in ims:
        bg=Image.new('RGBA',c.size,(90,90,100,255)); bg.alpha_composite(c); gif.append(bg.convert('P',palette=Image.ADAPTIVE))
    gif[0].save(f'{gd}/preview.gif',save_all=True,append_images=gif[1:],duration=40,loop=0,disposal=2)
    # contact sheet
    cols=min(10,len(ims)); rws=-(-len(ims)//cols); sh_=Image.new('RGBA',(cols*W,rws*H),(90,90,100,255))
    for k,c in enumerate(ims): sh_.alpha_composite(c,((k%cols)*W,(k//cols)*H))
    sh_.save(f'{gd}/contact_sheet.png')
    meta=[{'frame':n,'index':i,'alias_of':(src if src!=n else None),'size':e['size'],'trim_ltrb':e['trim'],'atlas_quad_xywh':e['quad']} for i,n,src,e in rows]
    json.dump({'group':g,'canvas':[W,H],'count':len(rows),'frames':meta},open(f'{gd}/frames.json','w'),indent=1)
    md.append(f'\n## {g}  ({len(rows)} frames, canvas {W}x{H})\n\n![gif]({g}/preview.gif)\n\n| # | frame | alias of | size | trim L,T,R,B | atlas x,y,w,h |\n|---|---|---|---|---|---|')
    for i,n,src,e in rows: md.append(f"| {i} | {i:04d}.png | {src.rsplit('_',1)[1] if src!=n else ''} | {e['size'][0]}x{e['size'][1]} | {','.join(map(str,e['trim']))} | {','.join(map(str,e['quad']))} |")
    summary.append((g,len(rows),W,H))
open(f'{out}/README.md','w',encoding='utf8').write('\n'.join(md)+'\n')
for s in summary:print(*s)
print(len(ents),'unique quads',len(frames),'frames')
