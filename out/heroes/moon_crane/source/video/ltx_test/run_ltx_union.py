import os, sys, json, fal_client, subprocess
S='/tmp/claude-0/-home-user-fal-lab/0d4327dc-c403-51b7-8868-48c89542b69c/scratchpad/ltx/'
mode=sys.argv[1]; strength=float(sys.argv[2]); tag=sys.argv[3]
ref=fal_client.upload_file(S+'ref.mp4'); img=fal_client.upload_file(S+'first.png')
prompt=("Stylized flat 2D vector cartoon game animation, thick dark outlines, flat solid colours, no 3D, no realistic lighting. The stocky heroic warrior of the first frame (slate-blue armour with a gold crane emblem, a giant cream crane-wing shoulder guard, a black topknot, an oversized spear with a silver leaf-shaped spearhead) performs the MOTION of the reference video: he winds up, drops low, turns with his back to the camera and holds. "
        "Keep his design, proportions and colours exactly as in the first frame; do not copy the reference character's body, costume or weapon; the weapon is his spear. The camera is fixed. No slash trails, no glow, no effects. Solid flat pure magenta background.")
args={"prompt":prompt,"video_url":ref,"image_url":img,"video_strength":strength,"match_video_length":True,"ic_lora_type":mode}
try:
    res=fal_client.subscribe("fal-ai/ltx-2.3-22b/distilled/reference-video-to-video",arguments=args)
except Exception as e:
    print("ERR",str(e)[:1500]); sys.exit(1)
print(json.dumps({k:(v if k!='video' else v) for k,v in res.items()})[:600])
url=res['video']['url']
subprocess.run(['curl','-sS','-o',S+f'out_{tag}.mp4',url],check=True)
json.dump({"args":{k:v for k,v in args.items() if k not in('video_url','image_url')},"result":res},open(S+f'out_{tag}.json','w'))
