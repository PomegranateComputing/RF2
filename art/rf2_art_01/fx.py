"""Native supersampled RF01 droplet sprites. Restrained dark blood; no IWAD pixels."""
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'enemies/_pipeline'))
import sdfrig as S
from PIL import Image
def main():
    out=ROOT/'src/sprites/fx';out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(25901);particles=[(rng.normal(0,14),rng.normal(0,17),rng.uniform(1.6,4.8)) for _ in range(18)]
    yy,xx=np.mgrid[:384,:384]/4
    for frame,letter in enumerate('ABC'):
        canvas=np.zeros((384,384,4),float)
        for x,y,size in particles:
            cx=48+x*(.65+.2*frame);cy=43+y*(.6+.22*frame)+frame*4
            d=((xx-cx)/(size*(1-.14*frame)))**2+((yy-cy)/(size*(1.25+.2*frame)))**2
            a=np.clip((1-d)*2.5,0,1)*(.93-.17*frame)
            rgb=np.stack([72+42*np.clip(1-d,0,1),21+13*np.clip(1-d,0,1),24+12*np.clip(1-d,0,1)],axis=-1)
            prev=canvas[:,:,3]/255;alpha=a+prev*(1-a)
            canvas[:,:,:3]=np.divide(rgb*a[:,:,None]+canvas[:,:,:3]*prev[:,:,None]*(1-a[:,:,None]),np.maximum(alpha[:,:,None],1e-8))
            canvas[:,:,3]=alpha*255
        im=Image.fromarray(np.clip(canvas,0,255).astype('uint8')).resize((96,96),Image.Resampling.LANCZOS)
        S.save_sprite(np.array(im),out/f'RFBX{letter}0.png',48,48)
    print('3 original RGBA droplet frames exported')
if __name__=='__main__':main()
