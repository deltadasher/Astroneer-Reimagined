"""Compose original Blender renders into a labeled review sheet; requires Pillow."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
root=Path(__file__).resolve().parents[1]
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=lambda s,b=False:ImageFont.truetype(bold if b else font,s)
im=Image.new('RGB',(1800,2130),'#10212c');d=ImageDraw.Draw(im)
d.text((70,48),'RESONANCE',font=f(56,True),fill='#e7f0e8')
d.text((73,123),'Original low-poly assets  /  Astroneer Reimagined',font=f(26),fill='#78d2cd')
panels=[('01_TuningLens.png','01  TUNING LENS','1,144 triangles  /  26 × 19 × 36 cm'),('02_EchoGlass.png','02  ECHO GLASS','262 triangles  /  18 × 19 × 23 cm'),('03_SiteDormant.png','03  DORMANT SITE','1,076 triangles assembled  /  shared ground pivot'),('04_SiteActive.png','04  RESPONSIVE SITE','1,306 triangles assembled  /  same base, open crown')]
for i,(file,title,sub) in enumerate(panels):
 x=70+(i%2)*860;y=195+(i//2)*890
 img=Image.open(root/'renders'/file).convert('RGB').resize((800,800),Image.Resampling.LANCZOS)
 im.paste(img,(x,y))
 d.text((x,y+813),title,font=f(25,True),fill='#e7f0e8')
 d.text((x,y+847),sub,font=f(18),fill='#9cb6c4')
d.line((70,1990,1730,1990),fill='#47616d',width=2)
d.text((70,2015),'Provisional scale · Views individually framed · Opaque materials, no shader-dependent state cues',font=f(20),fill='#a9c2cb')
d.text((70,2055),'FBX + editable .blend + deterministic builder  |  Windows cooking and in-game fit UNTESTED',font=f(20),fill='#78d2cd')
im.save(root/'renders'/'Resonance_ContactSheet.png')
