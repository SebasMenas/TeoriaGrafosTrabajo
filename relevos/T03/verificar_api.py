"""Comprobar una instancia Flask del proyecto. Ejecutar con Python 3."""
import json,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parent
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:5000').rstrip('/')
def pedir(method,path,data=None,raw=None):
    body=raw.encode() if raw is not None else json.dumps(data).encode() if data is not None else None
    req=Request(BASE+path,data=body,method=method,headers={'Content-Type':'application/json'})
    try:
        with urlopen(req,timeout=10) as res: return res.status,json.load(res)
    except HTTPError as e: return e.code,json.load(e)

def comprobar(g,r,dist,k):
    assert r['distancia']==dist and r['maximo']==k
    assert r['calculos_pendientes']==[] and len(r['caminos'])==k
    active={(a['origen'],a['destino']) for a in g['arcos'] if a.get('activo',True)}
    s,t=g['entrada'],g['salida']
    if dist is None: assert r['ruta'] is None
    else:
        p=r['ruta']; assert p[0]==s and p[-1]==t and len(p)-1==dist
        assert set(zip(p,p[1:]))<=active
    used=set()
    for p in r['caminos']:
        assert p[0]==s and p[-1]==t and len(p)==len(set(p))
        arcs=set(zip(p,p[1:])); assert arcs<=active and not arcs&used
        used|=arcs
    cut={tuple(a) for a in r['corte']}
    assert len(cut)==len(r['corte'])==k and cut<=active
    reached={s}
    while True:
        nxt=reached|{b for a,b in active-cut if a in reached}
        if nxt==reached: break
        reached=nxt
    assert t not in reached

def main():
    for name,dist,k in [('original',3,2),('bloqueo',4,1),('atajo',2,3),('manual',3,2),('sin-conexion',None,0)]:
        g=json.loads((ROOT/f'{name}-entrada.json').read_text(encoding='utf-8'))
        status,r=pedir('POST','/analizar',g);assert status==200
        comprobar(g,r,dist,k);print('PASA:',name)
    for case in json.loads((ROOT/'errores.json').read_text(encoding='utf-8')):
        status,r=pedir(case['metodo'],case['url'],case.get('entrada'),case.get('cuerpo'))
        assert status==case['status'] and isinstance(r.get('error'),str) and r['error']
        print('PASA:',case['nombre'])
    print('11 comprobaciones HTTP correctas. Registrar el commit del servidor y el revisor.')
if __name__=='__main__':
    try: main()
    except Exception as e:
        print('FALLA:',type(e).__name__,str(e));sys.exit(1)
