#!/usr/bin/env python3
"""Transcreve a narração (faster-whisper, pt) e alinha cada beat do roteiro às palavras.

Uso: transcrever_beats.py NARRACAO ROTEIRO.txt SAIDA_DIR [--antecipa 0.1]
ROTEIRO.txt: uma linha por beat, na ordem. Gera SAIDA_DIR/palavras.tsv e SAIDA_DIR/beats.json.
"""
import argparse, difflib, json, re, subprocess, unicodedata, os

def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if not unicodedata.combining(c)))

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("roteiro"); ap.add_argument("saida")
ap.add_argument("--antecipa", type=float, default=0.1)
ap.add_argument("--modelo", default="small")
a = ap.parse_args(); os.makedirs(a.saida, exist_ok=True)

dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",a.audio],capture_output=True,text=True).stdout)
beats = [l.strip() for l in open(a.roteiro, encoding="utf-8") if l.strip()]

from faster_whisper import WhisperModel
nomes = " ".join(w for w in " ".join(beats).split() if w[:1].isupper())
segs, _ = WhisperModel(a.modelo, device="cpu", compute_type="int8").transcribe(
    a.audio, language="pt", word_timestamps=True, initial_prompt=nomes)
words = [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]
with open(f"{a.saida}/palavras.tsv", "w") as f:
    for s, e, w in words: f.write(f"{s:.2f}\t{e:.2f}\t{w}\n")

# alinhamento roteiro -> transcrição
sw, owner = [], []
for i, b in enumerate(beats):
    for w in b.split():
        if norm(w): sw.append(norm(w)); owner.append(i)
tw = [norm(w) for *_, w in words]
mapped = {}
for blk in difflib.SequenceMatcher(None, sw, tw, autojunk=False).get_matching_blocks():
    for k in range(blk.size): mapped[blk.a + k] = blk.b + k

out, avisos, prev_last = [], [], -1
for i in range(len(beats)):
    idx = [j for j in range(len(sw)) if owner[j] == i]
    hits = [(j, mapped[j]) for j in idx if j in mapped]
    if not hits:
        avisos.append(f"beat {i+1}: nenhuma palavra reconhecida"); first = prev_last + 1
    else:
        j0, t0 = hits[0]
        first = max(prev_last + 1, t0 - (j0 - idx[0]))  # recua pelas palavras não reconhecidas no início
        if j0 != idx[0]: avisos.append(f"beat {i+1}: início inferido ('{words[first][2]}')")
        prev_last = hits[-1][1]
    first = min(first, len(words) - 1)
    ws = words[first][0]
    ini = 0.0 if i == 0 else round(max(0.0, ws - a.antecipa), 2)
    out.append(dict(beat=i+1, texto=beats[i], primeira_palavra=words[first][2], palavra_ini=round(ws,2), ini=ini))
for i, b in enumerate(out):
    b["fim"] = out[i+1]["ini"] if i + 1 < len(out) else round(dur, 2)
    b["dur"] = round(b["fim"] - b["ini"], 2)
json.dump(dict(audio=a.audio, duracao=round(dur,2), beats=out, avisos=avisos), open(f"{a.saida}/beats.json","w"), ensure_ascii=False, indent=1)
for b in out: print(f"{b['beat']:02d} {b['ini']:6.2f}-{b['fim']:6.2f} ({b['dur']:.2f}s) [{b['primeira_palavra']}] {b['texto']}")
for w in avisos: print("AVISO:", w)
