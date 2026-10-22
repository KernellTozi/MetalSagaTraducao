"""Evidence-based GFI glyph access and experimental PT-BR mapping.

The engine's existing SJIS-shaped reader maps these pairs to blank JIS row 0x23
cells. They are a project extension, NOT standard CP932 or UTF-8 characters.
"""
from pathlib import Path
import hashlib,math,struct,unicodedata

POINTS=(0xe7,0xe1,0xe0,0xe3,0xe2,0xe9,0xea,0xed,0xf3,0xf4,0xf5,0xfa,0xfc,0xc7,0xc1,0xc9,0xc3,0xd5)
TRAILS=tuple(range(0x40,0x4f))+tuple(range(0x59,0x5c))
CHAR_TO_BYTES={chr(point):bytes((0x82,trail)) for point,trail in zip(POINTS,TRAILS)}
BYTES_TO_CHAR={value:key for key,value in CHAR_TO_BYTES.items()}

def sjis_to_jis(code):
    """Equivalent arithmetic to ELF file 0x197EE8..0x197F70, for valid pairs."""
    lead,trail=code>>8,code&255
    if not (0x81<=lead<=0x9f or 0xe0<=lead<=0xef) or not (0x40<=trail<=0xfc and trail!=0x7f):
        raise ValueError('Invalid two-byte SJIS-shaped code')
    row=(lead-0x81 if lead<0xa0 else lead-0xc1)*2+0x21
    if trail>=0x9f:row+=1;column=trail-0x7e
    else:column=trail-(0x1f if trail<0x7f else 0x20)
    return row<<8|column

def encode(text):
    result=bytearray()
    for char in text:
        if char in CHAR_TO_BYTES:result.extend(CHAR_TO_BYTES[char])
        elif char in '\n\t' or 0x20<=ord(char)<=0x7e:result.append(ord(char))
        else:raise ValueError(f'Unsupported project glyph U+{ord(char):04X}')
    return bytes(result)

def decode(raw):
    result=[];i=0
    while i<len(raw):
        pair=raw[i:i+2]
        if pair in BYTES_TO_CHAR:result.append(BYTES_TO_CHAR[pair]);i+=2
        elif raw[i] in (9,10) or 0x20<=raw[i]<=0x7e:result.append(chr(raw[i]));i+=1
        else:raise ValueError('Unknown byte sequence, not project PT-BR encoding')
    return ''.join(result)

class Gfi:
    def __init__(self,data):
        if len(data)<0x2ec:raise ValueError('Short GFI')
        self.data=data
        self.stride,self.data_start,self.extra_codes,self.extra_start,self.kana_start,self.fallback,self.extra_count,self.kana_count=struct.unpack_from('<8I',data,0x10)
        self.side=math.isqrt(self.stride*2)
        if self.side not in (22,26) or self.side*self.side!=self.stride*2:
            raise ValueError('Unsupported GFI dimensions')
        self.rows=list(struct.unpack_from('<94I',data,0x30))
        if self.data_start!=0x2ec or self.extra_codes!=0x1a8 or self.extra_count!=161 or self.kana_count!=63:
            raise ValueError('Unexpected GFI layout')
        if self.extra_start-self.data_start!=3384*self.stride or self.kana_start-self.extra_start!=161*self.stride or self.fallback-self.kana_start!=63*self.stride or len(data)!=self.fallback+self.stride:
            raise ValueError('Unexpected GFI bank lengths')
        for row in self.rows:
            if row and not self.data_start<=row<=self.extra_start-94*self.stride:
                raise ValueError('Row outside full-glyph bank')

    def glyph_offset(self,jis):
        row,column=jis>>8,jis&255
        if not (0x21<=row<=0x7e and 0x21<=column<=0x7e):raise ValueError('JIS index out of range')
        base=self.rows[row-0x21]
        if not base:raise ValueError('Row not directly allocated')
        return base+(column-0x21)*self.stride

    def ascii_offset(self,char):
        if not 0x21<=ord(char)<=0x7e:raise ValueError('ASCII bitmap not in font row')
        return self.rows[0x7a-0x21]+(ord(char)-0x21)*self.stride

    def pixels(self,offset):
        result=[]
        for value in self.data[offset:offset+self.stride]:result.extend((value&15,value>>4))
        return result

    def blank_columns(self,row=0x23):
        return [column for column in range(0x21,0x7f) if not any(self.data[self.glyph_offset(row<<8|column):self.glyph_offset(row<<8|column)+self.stride])]

def pack(pixels):
    if len(pixels)%2 or any(not 0<=p<=15 for p in pixels):raise ValueError('Invalid 4bpp pixels')
    return bytes(pixels[i]|pixels[i+1]<<4 for i in range(0,len(pixels),2))

def accented_pixels(font,char):
    # Pillow is installed locally under work/python-deps for the research toolchain.
    from PIL import Image,ImageDraw
    decomposed=unicodedata.normalize('NFD',char);base,mark=decomposed
    source=Image.new('L',(font.side,font.side));source.putdata([p*17 for p in font.pixels(font.ascii_offset(base))])
    # Remove the original dot before composing acute i.
    if base=='i':source.paste(0,(0,0,font.side,5 if font.side==22 else 6))
    bbox=source.getbbox()
    if not bbox:raise ValueError('Missing base letter')
    body=source.crop(bbox)
    head=5 if font.side==22 else 6;tail=4 if mark=='\u0327' else 0
    y_start=bbox[1] if tail else max(bbox[1],head)
    height=min(body.height,font.side-y_start-tail)
    if height<1:raise ValueError('No room for accent')
    if height!=body.height:body=body.resize((body.width,height),Image.Resampling.LANCZOS)
    canvas=Image.new('L',(font.side,font.side));x=(font.side-body.width)//2
    canvas.paste(body,(x,y_start))
    # Compose a small antialiased mark above/below the native body, inside its cell.
    scale=4;marks=Image.new('L',(font.side*scale,font.side*scale));draw=ImageDraw.Draw(marks)
    center=font.side/2;top=1;bottom=head-2
    def line(points,width=1.3):draw.line([(round(a*scale),round(b*scale)) for a,b in points],fill=255,width=round(width*scale))
    if mark=='\u0301':line([(center-2,bottom),(center+2,top)])
    elif mark=='\u0300':line([(center+2,bottom),(center-2,top)])
    elif mark=='\u0302':line([(center-3,bottom),(center,top),(center+3,bottom)])
    elif mark=='\u0303':line([(center-4,top+2),(center-2,top+1),(center+1,top+3),(center+4,top+2)])
    elif mark=='\u0308':
        for dx in (-3,2):draw.ellipse(((center+dx)*scale,top*scale,(center+dx+1.4)*scale,(top+1.4)*scale),fill=255)
    elif mark=='\u0327':
        y=y_start+height;line([(center,y-0.7),(center+1,y+1),(center-1,y+2),(center-2,y+2)],width=1.2)
    else:raise ValueError('Unsupported diacritic')
    accent=marks.resize(canvas.size,Image.Resampling.LANCZOS)
    pixels=[max(a,b) for a,b in zip(canvas.getdata(),accent.getdata())]
    return [min(15,max(0,round(p/17))) for p in pixels]

def font_patches(data):
    font=Gfi(data);patches=[]
    for char,pair in CHAR_TO_BYTES.items():
        jis=sjis_to_jis(int.from_bytes(pair,'big'));offset=font.glyph_offset(jis)
        before=data[offset:offset+font.stride]
        if any(before):raise ValueError('Reserved PT-BR cell is not blank')
        after=pack(accented_pixels(font,char))
        patches.append({'offset':offset,'before':before,'after':after,'character':char,'bytes':pair.hex(),'jis':f'{jis:04x}'})
    return patches
