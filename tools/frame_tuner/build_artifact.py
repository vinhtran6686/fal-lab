"""Make data/artifact_index.html: the tuner page without the <html>/<head>/<body> wrappers (the Artifact tool adds its own skeleton).
Publish it with the sheets so other PCs can use the tuner without the repo:
  Artifact(file_path=<...>/data/artifact_index.html, files={'data/states.json': ..., 'data/<id>.png': ... for every state},
           capabilities={'db': {}, 'downloads': True})
In the artifact the recipes are saved in the page's db (Claude reads them back with ArtifactData) and can be downloaded or copied as JSON."""
import re, pathlib
HERE = pathlib.Path(__file__).resolve().parent
s = (HERE / 'index.html').read_text(encoding='utf-8')
style = re.search(r'<style>(.*?)</style>', s, re.S).group(1)
script = re.search(r'<script>(.*?)</script>', s, re.S).group(1)
body = re.search(r'<body>(.*?)<script>', s, re.S).group(1)
# side gutter for phones, as the artifact contract asks
style += "\nheader,main{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}\n"
out = ('<title>Frame Tuner</title>\n<style>' + style + '</style>\n' + body + '<script>' + script + '</script>\n')
(HERE / 'data').mkdir(exist_ok=True); (HERE / 'data' / 'artifact_index.html').write_text(out, encoding='utf-8')
print('wrote data/artifact_index.html', len(out) // 1024, 'KB')
