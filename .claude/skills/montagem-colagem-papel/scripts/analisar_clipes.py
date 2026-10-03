#!/usr/bin/env python3
"""Mede, por clipe, o pré-roll (composição final exibida antes da montagem) e o frame em que a montagem assenta.
Gera folha de contato (1 frame/s) para conferir a ordem dos clipes pelo conteúdo.

Uso: analisar_clipes.py CLIPES_DIR SAIDA_DIR
Saída: SAIDA_DIR/clipes.json  {arquivo: {fps, frames, cut, settle, ...}} e SAIDA_DIR/clipes_folha_*.png
"""
import json, subprocess, sys, os, glob
import numpy as np
cdir, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(f"{cdir}/*.mp4"))
res = {}
for f in files:
    p = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate,width,height","-of","json",f],capture_output=True,text=True)
    st = json.loads(p.stdout)["streams"][0]; n, d = map(int, st["r_frame_rate"].split("/")); fps = n / d
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-vf","scale=64:36,format=gray","-f","rawvideo","-"],capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(float)
    fd = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    # pré-roll termina num pico isolado (troca brusca da prévia para a página vazia) no primeiro 1,5 s
    c, salto = 0, 0.0
    for k in range(min(len(fd) - 1, int(fps * 1.5))):
        if fd[k] >= 8 and fd[k+1] < fd[k] / 2:
            c, salto = k + 1, float(fd[k]); break
    else:
        if fd[0] >= 8:  # prévia se dissolvendo desde o frame 0: corta no pico da dissolução
            k = int(np.argmax(fd[:int(fps * 0.5)])); c, salto = k + 1, float(fd[k])
    settle = len(a) - 1
    while settle > c and np.abs(a[settle-1] - a[-1]).mean() < 2: settle -= 1
    res[os.path.basename(f)] = dict(fps=round(fps,3), frames=len(a), w=st["width"], h=st["height"], cut=c, settle=settle,
        preroll_s=round(c/fps,2), util_s=round((settle-c+1)/fps,2), salto=round(salto,1))
    print(os.path.basename(f), res[os.path.basename(f)])
    subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-vf",f"select='not(mod(n\\,{round(fps)}))',scale=240:-1,drawtext=text='{os.path.basename(f)}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1,tile=7x1","-frames:v","1",f"{out}/_th_{len(res):03d}.png"])
json.dump(res, open(f"{out}/clipes.json","w"), indent=1)
ths = sorted(glob.glob(f"{out}/_th_*.png"))
for k in range(0, len(ths), 7):
    grp = ths[k:k+7]
    subprocess.run(["ffmpeg","-v","error","-y"] + sum([["-i",t] for t in grp],[]) + ["-filter_complex",f"vstack={len(grp)}" if len(grp)>1 else "null", f"{out}/clipes_folha_{k//7+1}.png"])
for t in ths: os.remove(t)
