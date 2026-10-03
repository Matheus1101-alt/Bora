#!/usr/bin/env bash
# Uso: verificar.sh SAIDA_DIR   (usa SAIDA_DIR/video_final.mp4 e SAIDA_DIR/montagem.json)
set -euo pipefail
D="$1"; V="$D/video_final.mp4"; T=$(mktemp -d)
echo "== stream"; ffprobe -v error -show_entries stream=codec_name,profile,pix_fmt:format=duration -of compact "$V"
python3 - "$D" "$V" "$T" <<'PY'
import json,subprocess,sys
d,v,t=sys.argv[1:]; m=json.load(open(f"{d}/montagem.json"))
for r in m["beats"]:
    for tag,ts in (("ini",r["ini"]+0.12),("fim",r["fim"]-0.12)):
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{ts:.3f}","-i",v,"-frames:v","1","-vf",
          f"scale=320:-1,drawtext=text='{r['beat']:02d} {tag}':x=5:y=5:fontsize=20:fontcolor=yellow:box=1",f"{t}/v_{r['beat']:02d}{tag[0]}.png"])
n=len(m["beats"]); subprocess.run(["ffmpeg","-v","error","-y","-pattern_type","glob","-i",f"{t}/v_*.png","-vf",f"tile=4x{(n*2+3)//4}","-frames:v","1",f"{d}/contact_sheet.png"])
print("duração áudio:",m["duracao"])
PY
echo "== frames pretos"; ffmpeg -v error -i "$V" -vf blackdetect=d=0.04:pix_th=0.1 -an -f null - 2>&1 | grep black || echo "nenhum"
echo "== loudness"; ffmpeg -i "$V" -af loudnorm=print_format=summary -f null - 2>&1 | grep -E "Input Integrated|Input True"
echo "contact sheet: $D/contact_sheet.png"; rm -rf "$T"
