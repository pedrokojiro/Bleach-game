"""Local, versioned settings with validation and atomic replacement."""
import json
import os
import sys
from pathlib import Path
from input_manager import MAPS

# A one-file executable extracts modules into a temporary directory. Persist
# preferences beside the executable instead of losing them when it closes.
DEFAULT_PATH = (Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent) / 'settings.json'

def defaults():
    return {'version':1, 'volume':.35, 'muted':False, 'shake':True, 'keys':[dict(m) for m in MAPS]}

def load(path=DEFAULT_PATH):
    result=defaults()
    try:
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        if not isinstance(data,dict):return result
        volume=data.get('volume')
        if isinstance(volume,(int,float)) and 0<=volume<=1:result['volume']=volume
        for key in ('muted','shake'):
            if isinstance(data.get(key),bool):result[key]=data[key]
        keys=data.get('keys')
        if isinstance(keys,list) and len(keys)==2:
            for i,m in enumerate(keys):
                if isinstance(m,dict) and set(m)==set(MAPS[i]) and all(isinstance(k,int) and 0<k<2**31 for k in m.values()) and len(set(m.values()))==len(m):
                    result['keys'][i]=m
    except (OSError,ValueError,TypeError):pass
    return result

def save(data,path=DEFAULT_PATH):
    path=Path(path)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temp,path)
