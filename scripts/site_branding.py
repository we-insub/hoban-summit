"""Generate original geometric icons using one shape definition for SVG and PNG."""
from pathlib import Path
from PIL import Image, ImageDraw
COLORS=[('#23473d','#f6f1e6'),('#102b43','#e8d9bd'),('#3b3a36','#ffffff'),('#735b4a','#eee9df'),('#13283c','#ba9369'),('#766e64','#ffffff'),('#50695a','#f4f0e4'),('#9c7c60','#fbf2e7'),('#4e6a7e','#ffffff'),('#30362f','#dedcc7')]
def build_branding(ident,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    bg,fg=COLORS[int(ident)-1];shapes=[]
    def line(points): shapes.append(('line',points))
    def box(x1,y1,x2,y2): line([(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)])
    n=int(ident)
    if n in [1,2,4]:
        box(18,36,44,79);box(54,20,80,79)
        if n==1:
            for y in [46,59]:line([(25,y),(37,y)])
        elif n==2:line([(60,31),(73,31)])
        else:line([(13,84),(85,84)])
    elif n in [3,6,8]:
        box(19,19,79,79)
        if n==3:line([(49,19),(49,79)]);line([(19,49),(79,49)])
        elif n==6:line([(19,44),(79,44)]);line([(43,44),(43,79)]);line([(62,19),(62,44)])
        else:box(35,35,63,63);line([(49,63),(49,79)])
    else:
        line([(16,45),(49,18),(82,45)]);line([(24,39),(24,80),(74,80),(74,39)])
        if n==5:
            for x,y in [(38,63),(49,54),(60,46)]:line([(x,y),(x,71)])
        elif n==7:line([(45,65),(65,43),(65,60),(45,65),(45,46),(57,46)])
        elif n==9:shapes.append(('circle',(49,54,8)))
        else:line([(37,58),(47,68),(65,46)])
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">',f'<rect width="96" height="96" rx="16" fill="{bg}"/>',f'<g fill="none" stroke="{fg}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">']
    im=Image.new('RGB',(384,384),bg);draw=ImageDraw.Draw(im)
    for kind,pts in shapes:
        if kind=='line':
            svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+'"/>')
            draw.line([(x*4,y*4) for x,y in pts],fill=fg,width=16,joint='curve')
        else:
            x,y,r=pts;svg.append(f'<circle cx="{x}" cy="{y}" r="{r}"/>');draw.ellipse(((x-r)*4,(y-r)*4,(x+r)*4,(y+r)*4),outline=fg,width=16)
    svg.append('</g></svg>');(folder/'favicon.svg').write_text(''.join(svg))
    im.resize((96,96),Image.Resampling.LANCZOS).save(folder/'favicon-96.png')
    im.resize((180,180),Image.Resampling.LANCZOS).save(folder/'apple-touch-icon.png')
    im.save(folder/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
