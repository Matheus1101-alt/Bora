# Exemplo de referência: Tsutomu Yamaguchi (aprovado)

Vídeo aprovado pelo usuário. Serve **apenas como referência** de qualidade para projetos futuros e não é um molde.

> **Use como régua, não como forma.** Cada vídeo novo deve atingir o mesmo nível (ritmo, clareza,
> precisão, sincronia), mas com estrutura, frases e visual próprios do tema. Se o vídeo novo puder ser
> descrito como "o Yamaguchi com outro personagem", ele falhou.

## O que transferir × o que NÃO copiar

| Transferir (princípio) | Não copiar (escolha específica deste vídeo) |
|---|---|
| Ritmo: montagens entre 1x e 2x, nenhum beat > 3x | A duração de 44,8 s e os 14 beats |
| Dimensionar o texto pelo tempo de montagem dos clipes | O texto, as frases e a ordem dos fatos |
| Abrir com um gancho concreto nos primeiros 3–4 s | "Data. Lugar." como abertura |
| Ancorar em uma pessoa ou um detalhe humano | Nome + cargo no 2º beat |
| Responder perguntas implícitas do espectador | "está em viagem de trabalho" |
| Detalhes concretos (número, hora, distância) | O espelhamento "Às Xh, a bomba explode" |
| Fechar com um dado que reenquadra a história | Ironia + data + idade no fim |
| Cada beat = uma imagem clara; o texto prepara o visual | Tarja nos olhos, barbante vermelho, etiquetas datilografadas |
| Voz clara, música 10 a 18 dB abaixo, com ducking | A faixa musical específica |
| Checagem factual antes de gerar a voz | — |

A estrutura narrativa e a linguagem visual abaixo **descrevem** o que funcionou aqui. Elas explicam *por que*
funcionou e não servem de roteiro para o próximo. Outro tema pede outra abertura, outra progressão e outro desfecho.
Master: `projeto/saida/video_final.mp4` (raiz do repositório). Clipes e narração originais não estão versionados.

## Métricas de qualidade atingidas (régua de ritmo, não meta de duração)

| Métrica | Referência | Faixa aceitável |
|---|---|---|
| Duração total | 44,8 s | 35–50 s |
| Beats / clipes | 14 / 14 (6 s cada) | 1 clipe por beat |
| Duração por beat | 1,9–4,5 s (média 3,2 s) | ≥ 2,5 s ideal; < 2 s só se o clipe montar rápido |
| Velocidade da montagem | 1,0–2,4x (12 de 14 entre 1,0x e 1,8x) | ≤ 2x ideal; > 3x refazer |
| Congelamento do frame final | 0,2–0,6 s | ≤ 1 s |
| Fala do TTS | ~5,3 sílabas/s + pausas de 0,6–1,4 s entre frases | — |
| Áudio | -16 LUFS, true peak -1,5 dBTP | — |
| Trilha (teste) | -30 LUFS antes do mix + ducking; pausas 8–17 dB abaixo da fala | 10–18 dB abaixo |
| Trilha (teste) | -30 LUFS antes do mix + ducking; pausas 8–17 dB abaixo da fala | 10–18 dB abaixo |

A v1 (34,4 s, mesmo conteúdo com texto mais enxuto) foi **reprovada no ritmo**: beat 03 a 4x e beats a 3,3x.
A lição: dimensionar o **texto** por beat a partir do tempo de montagem dos clipes, não o contrário.

## Estrutura narrativa deste vídeo (descrição, não modelo)

1. **Gancho de data + lugar**, frase nominal curta ("6 de agosto de 1945. Hiroshima.")
2. **Personagem com nome e função**, para dar uma âncora humana.
3. **Contexto que responde a pergunta implícita** ("está em viagem de trabalho": por que ele estava lá?).
4. **Proximidade concreta**, com um número ("a apenas três quilômetros…").
5. **Evento com hora exata** ("Às 8h15, a bomba explode."), frase curta e seca.
6. Consequência imediata → deslocamento → chegada ("No dia seguinte, ferido…", "de volta a Nagasaki…").
7. **Repetição espelhada do evento** ("Às 11h02, a segunda bomba explode.") com a mesma construção do item 5.
8. **Desfecho com ironia + dado final** ("só o reconheceu oficialmente… em 2009, aos 93 anos.").

Princípios de texto que valem para qualquer tema:
- Uma linha do roteiro = um clipe = uma imagem clara. Quebre frases longas em dois beats no ponto em que a imagem muda.
- Detalhes que preparam o visual seguinte ("enfaixado" antes do clipe com curativos).
- Números por extenso no TTS ("oito e quinze"); nomes estrangeiros com acento de pronúncia se o TTS errar ("Nagasáki").
- Checar fatos antes de gerar a voz (a v1 tinha "dois dias depois", quando foi no dia seguinte).

## Linguagem visual deste vídeo (descrição, não modelo)

Colagem de papel sobre fundo de papel envelhecido e jornal; recortes P&B de pessoas com tarja nos olhos;
acentos em vermelho (círculos, carimbos, linhas de barbante ligando elementos); etiquetas datilografadas com
data/hora/lugar ("6 AGO 1945", "8H15", "3 KM", "11H02"). Cada clipe: página vazia → peças entram → composição
assenta por volta de 3,5–5 s. Os clipes que montam em ~3–4 s são os que mais folgam no tempo.
Princípio transferível: elementos gráficos com dado (data, hora, distância) reforçam a narração; o estilo em si
deve vir do tema e do pedido do usuário.

## Arquivos

- `roteiro.txt`: narração aprovada, uma linha por beat.
- `beats.json`: tempos extraídos do áudio aprovado.
- `clipes.json`: pré-roll e assentamento de cada clipe.
- `config.json`: mapeamento beat → arquivo usado (note que os arquivos chegaram **fora de ordem**).
- `relatorio.md` / `contact_sheet.png`: resultado aprovado; compare a folha de contato de um vídeo novo com esta.
