import sys, json, pathlib, subprocess
sys.path.insert(0,'scripts')
import fal_video; fal_video.load_dotenv(pathlib.Path('.env'))
import fal_client
V=pathlib.Path('out/heroes/moon_crane/source/video')
img=fal_client.upload_file('out/heroes/moon_crane/source/design/master_v08.png')
vid=fal_client.upload_file('ref/sprite/hero_skill_3_sweep/ref_skill_3_sweep.mp4')
args={"prompt":(V/'skill_sweep_ref_t01.prompt.txt').read_text(encoding='utf-8'),"prompt_expansion_mode":"disabled",
 "reference_image_urls":[img],"reference_video_urls":[vid],"duration":3,"resolution":"480P","aspect_ratio":"16:9"}
r=fal_client.subscribe("minimax/h3-max/reference-to-video",arguments=args)
(V/'skill_sweep_ref_t01.json').write_text(json.dumps({'model':'minimax/h3-max/reference-to-video','duration':3,'resolution':'480P','price_usd':0.15,**{k:v for k,v in r.items() if k!='expanded_prompt'}},indent=1),encoding='utf-8')
subprocess.run(['curl','-sSL','-o',str(V/'skill_sweep_ref_t01.mp4'),r['video']['url']],check=True)
print(json.dumps({k:r.get(k) for k in ('seed','reference_tokens')}))
