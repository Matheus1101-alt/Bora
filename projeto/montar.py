import json,subprocess
cuts={int(k):v for k,v in json.load(open("cortes_clipes.json")).items()}
cuts[5]["cut"]=1; cuts[9]["cut"]=0
AUD=44.76
starts=[0.00,4.30,7.48,10.12,13.54,16.38,19.46,22.04,25.36,29.12,32.10,35.40,38.28,40.30]
clip=[7,3,2,4,8,9,10,5,11,14,1,13,6,12]
xf_after={1,2,5,6,8,10,11,12}
XF=0.15;H=XF/2;HOLD=0.2;FPS=30
ends=starts[1:]+[AUD]
rows=[];segs=[]
for i in range(14):
    b=i+1; pre=H if (b-1) in xf_after else 0; post=H if b in xf_after else 0
    L=ends[i]-starts[i]+pre+post
    c=cuts[clip[i]]; src=(c["settle"]-c["cut"]+1)/24
    avail=L-pre-post-HOLD - (0 if post==0 else 0)
    sp=max(1.0,src/avail); capped=sp>4; sp=min(sp,4)
    build=src/sp; freeze=L-build
    rows.append(dict(beat=b,clip=clip[i],ini=starts[i],fim=ends[i],dur=ends[i]-starts[i],orig=6.016,util=src,pre=c["cut"]/24,tail=(143-c["settle"])/24,speed=sp,freeze=freeze,cap=capped,xf="crossfade 0.15" if b in xf_after else ("fim" if b==14 else "corte seco"),L=L))
    segs.append((clip[i],c["cut"],c["settle"],sp,L))
inp=[];fc=[]
for k,(cl,a,z,sp,L) in enumerate(segs):
    inp+=["-i",f"clipes/{cl:02d}.mp4"]
    fc.append(f"[{k}:v]trim=start_frame={a}:end_frame={z+1},setpts=(PTS-STARTPTS)/{sp:.5f},scale=1920:1080:flags=lanczos,fps={FPS},tpad=stop_mode=clone:stop_duration=10,trim=duration={L:.4f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1,settb=1/30[v{k}]")
cur="v0";acc=segs[0][4]
for k in range(1,14):
    b=k  # boundary after beat b
    if b in xf_after:
        off=acc-XF; fc.append(f"[{cur}][v{k}]xfade=transition=fade:duration={XF}:offset={off:.4f}[x{k}]"); acc=acc-XF+segs[k][4]
    else:
        fc.append(f"[{cur}][v{k}]concat=n=2:v=1:a=0,settb=1/30[x{k}]"); acc+=segs[k][4]
    cur=f"x{k}"
fc.append(f"[14:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]")
cmd=["ffmpeg","-v","error","-y"]+inp+["-i","narracao.wav","-filter_complex",";".join(fc),"-map",f"[{cur}]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-profile:v","high","-preset","slow","-crf","18","-r",str(FPS),"-c:a","aac","-b:a","192k","-t",str(AUD),"-movflags","+faststart","saida/video_final.mp4"]
subprocess.run(cmd,check=True)
json.dump(rows,open("saida/beats.json","w"))
print("total timeline",round(acc,3))
for r in rows: print(r["beat"],r["clip"],f'{r["dur"]:.2f}',f'util {r["util"]:.2f}',f'x{r["speed"]:.2f}',f'freeze {r["freeze"]:.2f}',r["cap"],r["xf"])
