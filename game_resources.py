"""Runtime resources come exclusively from the extracted local TTR installation."""
from pathlib import Path
import re
from panda3d.core import getModelPath,Filename,loadPrcFileData
loadPrcFileData('', 'model-cache-models false\nmodel-cache-textures false')
ROOT=Path(__file__).resolve().parent
TTR=ROOT/'assets/ttr'
getModelPath().prependDirectory(Filename.fromOsSpecific(str(TTR)))
FILES={str(p.relative_to(TTR)):p for p in TTR.rglob('*') if p.is_file()}
BY_NAME={p.name:p for p in FILES.values()}
def resource(name):
 name=str(name)
 base=Path(name).name
 match=re.fullmatch(r'tt_a_chr_dgm_shorts_(legs|torso|head)_(.+)\.bam',base)
 if match:
  part,anim=match.groups()
  if anim=='1000':base='ttr_r_chr_avt_dog.bam' if part=='head' else f'ttr_r_chr_dgm_{part}.bam'
  else:base=f'ttr_a_chr_avt_dog_{anim}.bam' if part=='head' else f'ttr_a_chr_dgm_{part}_{anim}.bam'
 match=re.fullmatch(r'suit([ABC])-(.+)\.bam',base)
 if match:
  body,suffix=match.groups();prefix=f'ene_cg{body.lower()}'
  base=f'ttr_r_{prefix}_'+('suit' if suffix in ('mod','lose-mod') else 'heads')+'.bam' if suffix in ('mod','lose-mod','heads') else f'ttr_a_{prefix}_{suffix}.bam'
 match=re.fullmatch(r'cog([ABC])_robot-(zero|lose-mod)\.bam',base)
 if match:base=f'ttr_r_ene_cg{match[1].lower()}_skelecog.bam'
 match=re.fullmatch(r'(cat|rabbit|mouse|duck|horse|pig|bear|monkey)-heads-1000.bam',base)
 if match:base=f'ttr_r_chr_avt_{match[1]}.bam'
 if base=='tart.bam':base='ttr_m_prp_bat_pie.bam'
 if base=='MickeyFont.bam':base='MickeyFontClassic.bam'
 if base==Path(name).name and name in FILES:return FILES[name]
 if base in BY_NAME:return BY_NAME[base]
 raise FileNotFoundError('No extracted TTR resource for '+name)
class ResourceLibrary:
 def __truediv__(self,name):return resource(name)
SOURCE=ResourceLibrary()
