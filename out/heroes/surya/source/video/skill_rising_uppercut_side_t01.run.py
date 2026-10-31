import sys, json, pathlib, subprocess
sys.path.insert(0,'scripts')
import fal_video; fal_video.load_dotenv(pathlib.Path('.env'))
import fal_client
D=pathlib.Path('out/heroes/surya/.work/ref_uppercut')
img=fal_client.upload_file('out/heroes/surya/source/design/master_v02.png')
vid=fal_client.upload_file('ref/sprite/uppercut/ref_uppercut.mp4')
args={"prompt":(D/'prompt.txt').read_text(encoding='utf-8'),"prompt_expansion_mode":"disabled",
 "reference_image_urls":[img],"reference_video_urls":[vid],"duration":5,"resolution":"480P","aspect_ratio":"1:1"}
r=fal_client.subscribe("minimax/h3-max/reference-to-video",arguments=args)
(D/'result.json').write_text(json.dumps({k:v for k,v in r.items() if k!='expanded_prompt'},indent=1),encoding='utf-8')
subprocess.run(['curl','-sSL','-o',str(D/'out_t01.mp4'),r['video']['url']],check=True)
print(json.dumps({k:r.get(k) for k in ('seed','reference_tokens')}))
