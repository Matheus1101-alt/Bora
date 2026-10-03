---
name: montagem-colagem-papel
description: Monta um vídeo documental curto a partir de N clipes de animação em colagem de papel (cada um termina no frame final da composição) e uma narração, sincronizando cada clipe a um beat do roteiro. Use quando o usuário entregar clipes gerados (ex. "Paper collage animation") + áudio de narração + roteiro e pedir montagem, sincronia, edição ou "encaixar os clipes na narração"; também para recomendar texto/duração de narração que caiba nos clipes.
---

# Montagem de documentário em colagem de papel

**Caminhos:** `scripts/` e `exemplos/` são relativos à pasta desta skill. Instalada globalmente, ela fica em
`~/.claude/skills/montagem-colagem-papel/`. Use o caminho absoluto ao chamar os scripts a partir de outro projeto.

Pipeline: transcrição com timestamps → beats → análise dos clipes → montagem → verificação visual → relatório.
Execute sem pedir confirmação a cada etapa; pare só nos pontos marcados **[decisão]**.

## Entradas
- Clipes `.mp4` (qualquer resolução/fps; descarta o áudio deles).
- Narração (`.wav`/`.mp3`).
- Roteiro: uma linha por beat, na ordem. Grave em `roteiro.txt`. Cada linha = um clipe.
- Opcional: trilha sonora de fundo (`.mp3`/`.wav`).

## Saída padrão
1920x1080, 30 fps, H.264 High **yuv420p** + AAC, -16 LUFS / -1,5 dBTP. Vertical: `largura:1080, altura:1920` no config (crop central).
Ao escolher vertical, avise que 16:9→9:16 descarta ~68% da largura em TODOS os beats.

## Referência aprovada
Leia `exemplos/yamaguchi/README.md` antes de começar. É a **referência de qualidade** do usuário, **não um molde**:
- Transfira os princípios (ritmo de 1x a 2x, texto dimensionado pelos clipes, gancho concreto, detalhes que preparam
  o visual, checagem factual).
- **Não copie** a estrutura, as frases, a duração, a quantidade de beats nem os motivos visuais. Cada tema pede
  forma própria.
- No resumo de cada vídeo novo, compare-o com a referência em **qualidade** (ritmo, clareza, sincronia) e aponte se
  ele está parecido demais com o exemplo na forma.

## Etapas

0. **Ferramentas**: `ffmpeg`, `ffprobe`, `pip install faster-whisper numpy`.

1. **Beats a partir do áudio**
   `python3 scripts/transcrever_beats.py narracao.wav roteiro.txt trabalho/`
   - Alinha o roteiro às palavras transcritas por similaridade (tolera erros do Whisper em nomes próprios e números falados como "oito e quinze").
   - Início do beat = 1ª palavra − 0,1 s (imagem entra antes da voz); beat 1 começa em 0; último termina no fim do áudio.
   - Leia `AVISOS` e confira `palavras.tsv` quando houver. Se uma palavra-chave aparecer transcrita errada (ex. "Nagasaki" → "na Gazaque"), avise o usuário: pode ser erro de pronúncia do TTS.

2. **Análise dos clipes**
   `python3 scripts/analisar_clipes.py clipes/ trabalho/`
   - `cut` = fim do **pré-roll**: geradores de colagem costumam abrir mostrando a composição final por alguns frames antes de esvaziar a página. Isso tem que sair, senão o beat "pisca" o resultado.
   - `settle` = frame em que a montagem para de mudar. O que vem depois é cauda estática.
   - **Olhe `clipes_folha_*.png`** e mapeie cada beat ao clipe pelo **conteúdo**. Não confie na ordem dos arquivos (nomes por horário de geração costumam vir fora de ordem). Se a detecção do pré-roll errar, corrija com `ajuste_cut`.

3. **Viabilidade [decisão]**: velocidade do beat ≈ `util_s / (duração do beat − 0,2)`.
   - ≤ 2x natural; 2–3x aceitável; > 3x parece acelerado; > 4x ilegível.
   - Se algum beat passar de 3x, **antes de montar** recomende: reescrever a linha da narração com mais sílabas naquele beat (≈ 5,5–5,7 sílabas/s em TTS pt-BR), fundir beats ou regenerar o clipe mais simples. Alongar o áudio inteiro raramente é a resposta: o problema costuma ser um beat curto.

4. **Montagem**: escreva `trabalho/config.json` e rode `python3 scripts/montar.py trabalho/config.json`.
   ```json
   {"narracao":"narracao.wav","beats":"trabalho/beats.json","clipes_json":"trabalho/clipes.json",
    "clipes_dir":"clipes","ordem":["07.mp4","03.mp4", "..."],"saida":"saida/video_final.mp4"}
   ```
   Opcionais: `crossfade_apos`, `ajuste_cut`, `largura`, `altura`, `fps`, `crossfade` (0.15), `hold` (0.2), `vel_max` (4), `lufs` (-16).
   Trilha: `trilha`, `trilha_inicio` (s a pular), `trilha_lufs` (-30), `trilha_fade_in` (0.5), `trilha_fade_out` (2.5), `ducking` (true).

   Regras que o script aplica:
   - Usa só o trecho `cut → settle`, acelerado com `setpts` para terminar `hold` s antes da troca; o frame final fica congelado (`tpad clone`) até o fim do beat. O **frame final completo sempre aparece**; o que se descarta é pré-roll e cauda parada.
   - Acima de `vel_max`: apara o **início** do trecho útil, nunca o final, e sinaliza no relatório.
   - Corte seco dentro da frase; crossfade de 0,15 s centrado na troca depois de beats que terminam em `. ! ?`. Os segmentos ganham 0,075 s de cada lado, então a duração total = duração do áudio.
   - **Trilha de fundo**, quando houver:
     - Antes de montar, rode `ffprobe` e `silencedetect -40dB` na música e use `trilha_inicio` para pular o silêncio
       ou intro inicial.
     - A voz é normalizada em -16 LUFS. A música entra em -30 LUFS, com fade in, fade out no fim do vídeo e
       *ducking* (sidechain) sob a voz. O mix final volta a -16 LUFS / -1,5 dBTP.
     - Faixas comerciais costumam vir saturadas (a referência veio em -6,9 LUFS e +0,6 dBTP). O `loudnorm` antes do
       mix resolve isso, então não use a faixa crua.
     - Música mais curta que o vídeo: avise. O script completa com silêncio; não faz loop.
     - Ajuste fino: música alta demais → `trilha_lufs` -33; sumindo → -27. Confira medindo o volume numa pausa
       e numa fala: a música deve ficar 10 a 18 dB abaixo da voz.
   - Força `yuv420p` na saída: o `xfade` pode promover para yuv444p (High 4:4:4), que **não abre em celular nem na maioria dos players**.

5. **Verificação** (obrigatória antes de entregar): `bash scripts/verificar.sh saida/`
   - Abra `contact_sheet.png` e confira: cada beat mostra a cena certa no início e a composição completa no fim.
   - Duração = áudio (±0,1 s), sem frames pretos, loudness ≈ -16 LUFS, `pix_fmt=yuv420p`.
   - Com trilha: meça o volume numa pausa e numa fala, por exemplo
     `ffmpeg -ss T -t 0.6 -i video.mp4 -af volumedetect -vn -f null -`. A música deve ficar 10 a 18 dB abaixo da voz
     e não pode mascarar palavras. Escute o início e o fim.

6. **Entrega**
   - `saida/video_final.mp4` + `saida/relatorio.md` (tabela por beat: início, fim, duração, clipe original, pré-roll, trecho útil, velocidade, congelado, transição).
   - Para enviar ao usuário, gere também uma prévia leve (720p, H.264 Main, CRF 24). Arquivos acima de ~40 MB podem falhar no envio.
   - No resumo: o mapeamento beat → arquivo (destaque encaixes interpretativos), beats acima de 3x ou congelados acima de 1 s (candidatos a regenerar), e upscale quando a fonte for menor que a saída.

## Armadilhas já vistas
- Os clipes chegaram fora da ordem dos beats; só a folha de contato revelou isso.
- Pré-roll de 1 a 21 frames com a composição final, diferente em cada clipe.
- Saída em yuv444p que o usuário não conseguia abrir.
- O TTS saiu ~10% mais lento que a estimativa por sílabas: refaça a conta com o áudio real.
- Erros factuais no roteiro (ex. datas de deslocamento): confira antes de gerar a narração.
