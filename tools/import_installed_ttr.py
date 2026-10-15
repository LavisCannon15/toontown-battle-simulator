"""Copy public phase resources from the local TTR installation, read-only at source."""
from pathlib import Path,PurePosixPath
from panda3d.core import Multifile
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/laviscannon/.var/app/com.toontownrewritten.Launcher/data')
DEST=ROOT/'assets/ttr'
def main():
 DEST.mkdir(parents=True,exist_ok=True)
 result={'source':str(SOURCE),'archives':{},'files':{},'skipped':[]}
 for archive in sorted(SOURCE.glob('phase_*.mf')):
  mf=Multifile()
  if not mf.openRead(str(archive)):raise RuntimeError('Cannot read '+str(archive))
  count=0
  for i in range(mf.getNumSubfiles()):
   name=mf.getSubfileName(i);path=PurePosixPath(name)
   if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!=archive.stem:
    result['skipped'].append({'archive':archive.name,'entry':name});continue
   data=mf.readSubfile(i);dest=DEST/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
   result['files'][name]={'archive':archive.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};count+=1
  mf.close();result['archives'][archive.name]={'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':count}
  print(archive.name,count,flush=True)
 (ROOT/'assets/ttr_resource_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Imported',len(result['files']),'resources into',DEST,flush=True)
if __name__=='__main__':main()
