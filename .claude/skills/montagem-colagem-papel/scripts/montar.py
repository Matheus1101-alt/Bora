#!/usr/bin/env python3
"""Monta o vídeo: cada beat recebe seu clipe (sem pré-roll), acelerado para a montagem terminar dentro do beat,
com congelamento do frame final no resto. Cortes secos dentro da frase, crossfade entre frases.

Uso: montar.py CONFIG.json
CONFIG: {
  "narracao": "...", "beats": "trabalho/beats.json", "clipes_json": "trabalho/clipes.json", "clipes_dir": "...",
  "ordem": ["07.mp4", ...]          # arquivo de cada beat, na ordem dos beats
  "crossfade_apos": [1,2,5,...],    # opcional: beats seguidos de crossfade (padrão: texto termina em . ! ?)
  "ajuste_cut": {"05.mp4": 1},      # opcional: corrige pré-roll detectado
  "saida": "saida/video_final.mp4", "largura":1920, "altura":1080, "fps":30,
  "crossfade":0.15, "hold":0.2, "vel_max":4.0, "lufs":-16,
  "trilha": "trilha.mp3",           # opcional: música de fundo
  "trilha_inicio": 1.0,             # s a pular no início da música (silêncio/intro)
  "trilha_lufs": -30,               # nível da música antes do mix (voz em -16)
  "trilha_fade_in": 0.5, "trilha_fade_out": 2.5, "ducking": true }
"""
import json, subprocess, sys, os
C = json.load(open(sys.argv[1]))
B = json.load(open(C["beats"])); beats = B["beats"]; AUD = B["duracao"]
CL = json.load(open(C["clipes_json"]))
W, H_, FPS = C.get("largura",1920), C.get("altura",1080), C.get("fps",30)
XF, HOLD, VMAX = C.get("crossfade",0.15), C.get("hold",0.2), C.get("vel_max",4.0)
# padrão: crossfade depois de beats cujo texto termina frase (. ! ?); corte seco no resto
xf_after = set(C["crossfade_apos"]) if "crossfade_apos" in C else {b["beat"] for b in beats[:-1] if b["texto"].rstrip()[-1:] in ".!?"}; half = XF/2
ordem = C["ordem"]; assert len(ordem) == len(beats), "ordem precisa ter um clipe por beat"
rows, segs = [], []
for i, b in enumerate(beats):
    n = i + 1; f = ordem[i]; c = CL[f]
    cut = C.get("ajuste_cut", {}).get(f, c["cut"]); settle = c["settle"]; fps_in = c["fps"]
    pre = half if (n-1) in xf_after else 0; post = half if n in xf_after else 0
    L = b["fim"] - b["ini"] + pre + post
    util = (settle - cut + 1) / fps_in
    avail = L - pre - post - HOLD
    sp = max(1.0, util / avail); cap = sp > VMAX
    if cap:  # apara o início do trecho útil (nunca o final) até caber em vel_max
        need = util - VMAX * avail; cut += int(round(need * fps_in)); util = (settle - cut + 1) / fps_in; sp = VMAX
    freeze = L - util / sp
    rows.append(dict(beat=n, arquivo=f, ini=b["ini"], fim=b["fim"], dur=round(b["fim"]-b["ini"],2), orig=round(c["frames"]/fps_in,2),
        preroll=round(cut/fps_in,2), util=round(util,2), vel=round(sp,2), congelado=round(freeze,2), aparado_extra=cap,
        transicao="crossfade %.2f" % XF if n in xf_after else ("fim" if n == len(beats) else "corte seco")))
    segs.append((f, cut, settle, sp, L))
inp, fc = [], []
for k, (f, a, z, sp, L) in enumerate(segs):
    inp += ["-i", os.path.join(C["clipes_dir"], f)]
    fc.append(f"[{k}:v]trim=start_frame={a}:end_frame={z+1},setpts=(PTS-STARTPTS)/{sp:.5f},"
              f"scale={W}:{H_}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H_},fps={FPS},"
              f"tpad=stop_mode=clone:stop_duration=30,trim=duration={L:.4f},setpts=PTS-STARTPTS,format=yuv420p,setsar=1,settb=1/{FPS}[v{k}]")
cur, acc = "v0", segs[0][4]
for k in range(1, len(segs)):
    if k in xf_after:
        fc.append(f"[{cur}][v{k}]xfade=transition=fade:duration={XF}:offset={acc-XF:.4f}[x{k}]"); acc += segs[k][4] - XF
    else:
        fc.append(f"[{cur}][v{k}]concat=n=2:v=1:a=0,settb=1/{FPS}[x{k}]"); acc += segs[k][4]
    cur = f"x{k}"
fc.append(f"[{cur}]format=yuv420p[vout]")
NA = len(segs); LUFS = C.get("lufs", -16)
extra_in = ["-i", C["narracao"]]
T = C.get("trilha")
if not T:
    fc.append(f"[{NA}:a]loudnorm=I={LUFS}:TP=-1.5:LRA=11,aresample=48000[a]")
else:
    # trilha de fundo: recorta a partir de trilha_inicio, normaliza baixo, fades, ducking sob a voz, mix e normalização final
    extra_in += ["-i", T]
    ti, tl = C.get("trilha_inicio", 0.0), C.get("trilha_lufs", -30)
    fi, fo = C.get("trilha_fade_in", 0.5), C.get("trilha_fade_out", 2.5)
    fc.append(f"[{NA}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I={LUFS}:TP=-2:LRA=11,aresample=48000,asplit=2[voz][sc]")
    fc.append(f"[{NA+1}:a]atrim=start={ti},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
              f"loudnorm=I={tl}:TP=-6:LRA=11,aresample=48000,apad,atrim=duration={AUD},"
              f"afade=t=in:d={fi},afade=t=out:st={AUD-fo:.3f}:d={fo}[mus]")
    if C.get("ducking", True):
        fc.append("[mus][sc]sidechaincompress=threshold=0.02:ratio=4:attack=80:release=600:makeup=1[duck]")
    else:
        fc.append("[sc]anullsink;[mus]anull[duck]")
    fc.append(f"[voz][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I={LUFS}:TP=-1.5:LRA=11,aresample=48000[a]")
os.makedirs(os.path.dirname(C["saida"]) or ".", exist_ok=True)
subprocess.run(["ffmpeg","-v","error","-y"] + inp + extra_in + ["-filter_complex", ";".join(fc),
    "-map","[vout]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-profile:v","high","-preset","slow","-crf","18",
    "-r",str(FPS),"-c:a","aac","-b:a","192k","-t",str(AUD),"-movflags","+faststart", C["saida"]], check=True)
sd = os.path.dirname(C["saida"]) or "."
json.dump(dict(duracao=AUD, beats=rows), open(f"{sd}/montagem.json","w"), ensure_ascii=False, indent=1)
L = ["# Relatório de montagem","",f"Áudio: {AUD:.2f} s · {W}x{H_}, {FPS} fps, H.264 High yuv420p + AAC","",
     "| Beat | Arquivo | Início | Fim | Duração | Clipe orig. | Pré-roll removido | Trecho útil | Velocidade | Congelado | Transição |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['beat']:02d} | {r['arquivo']} | {r['ini']:.2f} | {r['fim']:.2f} | {r['dur']:.2f} | {r['orig']:.2f} | {r['preroll']:.2f} | {r['util']:.2f} | {r['vel']:.2f}x | {r['congelado']:.2f} | {r['transicao']} |")
alertas = [f"beat {r['beat']:02d}: {r['vel']}x" + (" (início aparado além do pré-roll)" if r['aparado_extra'] else "") for r in rows if r['vel'] > 3] + \
          [f"beat {r['beat']:02d}: congelado {r['congelado']} s" for r in rows if r['congelado'] > 1]
L += ["", "## Para decidir (regenerar clipe?)", ""] + ([f"- {x}" for x in alertas] or ["- nenhum beat acima de 3x nem congelado acima de 1 s"])
open(f"{sd}/relatorio.md","w").write("\n".join(L) + "\n")
for r in rows: print(r)
print("\n".join(alertas) or "sem alertas")
