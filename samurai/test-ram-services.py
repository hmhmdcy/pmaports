#!/usr/bin/env python3
"""Run real RAM-storage/RPC regressions on a Linux host; never access a phone."""
from pathlib import Path
from urllib.request import urlopen,Request
import argparse,hashlib,json,os,re,shutil,subprocess,tarfile
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--work',type=Path,required=True)
a=p.parse_args();work=a.work.resolve();work.mkdir(parents=True)
repo=Path(__file__).resolve().parents[1];tests=repo/'samurai/tests'
radio=repo/'device/testing/samurai-radio-tools'
rpc=repo/'device/testing/samurai-hexagonrpcd'
def archive(recipe,name,url):
 table=(recipe/'APKBUILD').read_text()
 expected=re.search(r'^([0-9a-f]{128})  '+re.escape(name)+r'$',table,re.M)[1]
 data=urlopen(Request(url,headers={'User-Agent':'samurai-regression'}),timeout=90).read()
 assert hashlib.sha512(data).hexdigest()==expected,name
 path=work/name;path.write_bytes(data)
 with tarfile.open(path) as t:
  top=t.getnames()[0].split('/')[0]
  t.extractall(work,filter='data')
 return work/top
rmtfs=archive(radio,'rmtfs-b30a3eb.tar.gz','https://api.github.com/repos/linux-msm/rmtfs/tarball/b30a3eb')
qrtr=archive(radio,'qrtr-29e36ae.tar.gz','https://codeload.github.com/linux-msm/qrtr/tar.gz/29e36ae164389580a0f8ea7a7fdb728140ae978d')
h=archive(rpc,'hexagonrpc-v0.4.0.tar.gz','https://codeload.github.com/linux-msm/hexagonrpc/tar.gz/23a69640bf10dc498226c602c5b5db11d8cb3d8e')
records=[]
def command(args,label,env=None,cwd=None):
 result=subprocess.run(list(map(str,args)),capture_output=True,text=True,env=env,cwd=cwd)
 (work/(label+'.log')).write_text(result.stdout+result.stderr)
 if result.returncode:raise RuntimeError(label+' failed; see '+str(work/(label+'.log')))
 return result
flags=['cc','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Wall','-Wextra']
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0',UBSAN_OPTIONS='halt_on_error=1')
# Upstream's RPC builder has no destructor; exclude that known process-lifetime
# allocation from leak checking while retaining ASan/UBSan memory-error checks.
for name in ['storage-cow','sharedmem-bounded']:
 binary=work/('test-'+name)
 command(flags+['-I'+str(radio),'-I'+str(rmtfs),'-I'+str(qrtr/'include'),tests/('test-'+name+'.c'),'-o',binary],name+'-build')
 result=command([binary],name,env)
 records.append({'case':name,'result':result.stdout.strip().splitlines()[-1]})
binary=work/'test-tftp-ram'
command(flags+[tests/'test-tftp-ram.c',radio/'samurai-tftp-ram.c',radio/'ro-firmware.c','-o',binary],'tftp-build')
records.append({'case':'tftp','result':command([binary],'tftp',env).stdout.strip().splitlines()[-1]})
command(['patch','--fuzz=0','-p1','-i',rpc/'ram-registry-listener.patch'],'rpc-patch',cwd=h)
shutil.copyfile(rpc/'hexagonfs_ram_registry.c',h/'hexagonrpcd/hexagonfs_ram_registry.c')
shutil.copyfile(tests/'test-rpc-registry.c',h/'hexagonrpcd/test-rpc-registry.c')
sources=[h/'libhexagonrpc'/(x+'.c') for x in ['context','fastrpc','interfaces','session']]
sources += [h/'hexagonrpcd'/(x+'.c') for x in ['aee_error','apps_mem','interfaces','hexagonfs','hexagonfs_mapped',
 'hexagonfs_plat_subtype_name','hexagonfs_virt_dir','hexagonfs_ram_registry','iobuffer','localctl','rpcd_builder','test-rpc-registry']]
binary=work/'test-rpc-registry'
command(flags+['-Wno-unused-parameter','-I'+str(h/'include'),'-I'+str(h/'hexagonrpcd')]+sources+['-pthread','-o',binary],'rpc-build')
records.append({'case':'rpc-registry','result':command([binary],'rpc-registry',env).stdout.strip().splitlines()[-1]})
report={'cases':records,'asan_ubsan':True,'known_builder_process_lifetime_leaks_excluded':True,'hardware_tested':False}
(work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
