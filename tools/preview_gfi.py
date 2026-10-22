"""Local comparison atlas; no installed system font or network required."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/python-deps'))
from PIL import Image,ImageDraw
from gfi import Gfi,CHAR_TO_BYTES,accented_pixels
from gfi_refined import accented_pixels as refined


def main():
    width=18*112
    atlas=Image.new('RGB',(width,2*3*150),(24,30,34))
    draw=ImageDraw.Draw(atlas)
    for bank,name in enumerate(('SUC20I22.GFI','SUC24I26.GFI')):
        font=Gfi((ROOT/'JOGO/Metal Saga/DATA/SYS'/name).read_bytes())
        for col,char in enumerate(CHAR_TO_BYTES):
            import unicodedata
            base=unicodedata.normalize('NFD',char)[0]
            for row,label in enumerate(('native base','v001','v002')):
                pixels=(font.pixels(font.ascii_offset(base)) if row==0 else
                        (accented_pixels if row==1 else refined)(font,char))
                im=Image.new('L',(font.side,font.side));im.putdata([p*17 for p in pixels])
                im=im.resize((font.side*4,font.side*4),Image.Resampling.NEAREST)
                x=col*112;y=(bank*3+row)*150
                draw.text((x+2,y+2),f'{font.side} {label}',fill='white')
                draw.text((x+2,y+16),f'U+{ord(char):04X}',fill='white')
                atlas.paste(im,(x,y+38))
    output=ROOT/'work/fontes-v002/comparacao.png'
    output.parent.mkdir(parents=True,exist_ok=True);atlas.save(output)
    print(output)


if __name__=='__main__':main()
