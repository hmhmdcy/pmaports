#!/usr/bin/env python3
"""Replay the complete camera patch queue from public source, with zero fuzz."""
from pathlib import Path
from urllib.request import urlopen,Request
import argparse,hashlib,json,re,subprocess,tarfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True)
a=p.parse_args();work=a.work.resolve();work.mkdir(parents=True)
repo=Path(__file__).resolve().parents[1];ports=repo/'temp/libcamera'
lock=json.loads((repo/'samurai/libcamera-source-lock.json').read_text())
version=lock['source_version'];name='libcamera-v'+version+'.tar.gz'
expected=re.search(r'^([0-9a-f]{128})  '+re.escape(name)+r'$',(ports/'APKBUILD').read_text(),re.M)[1]
url='https://gitlab.freedesktop.org/camera/libcamera/-/archive/v'+version+'/'+name
data=urlopen(Request(url,headers={'User-Agent':'samurai-source-replay'}),timeout=90).read()
assert hashlib.sha512(data).hexdigest()==expected
archive=work/name;archive.write_bytes(data)
with tarfile.open(archive) as t:t.extractall(work,filter='data')
tree=work/('libcamera-v'+version)
patches=sorted(ports.glob('00*.patch'));assert len(patches)==12
for patch in patches:
 result=subprocess.run(['patch','--fuzz=0','-p1','-i',str(patch)],cwd=tree,capture_output=True,text=True)
 (work/(patch.stem+'.log')).write_text(result.stdout+result.stderr)
 assert result.returncode==0,patch.name
for name,digest in lock['final_sources_sha256'].items():
 assert hashlib.sha256((tree/name).read_bytes()).hexdigest()==digest,name
report={'patch_count':len(patches),'zero_fuzz':True,'final_source_hashes_verified':len(lock['final_sources_sha256']),
 'source_sdk_used':False,'hardware_tested':False}
(work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
