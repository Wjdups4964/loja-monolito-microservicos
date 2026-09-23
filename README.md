# Laboratório — a mesma loja, duas arquiteturas

Estilos Arquiteturais V · Microsserviços 

Nomes: ____________________________________ 

Vocês vão rodar a **mesma loja** de dois jeitos: como um **monolito** (um processo, um banco) e como **microsserviços** (quatro processos, um banco por serviço). As duas versões têm as mesmas rotas. Ninguém precisa programar — só um experimento pede para mudar um número no código. 

Requisito: Python 3.8 ou superior. Nada para instalar. No macOS/Linux use `python3`.

| Versão | Como subir | Endereço |
|---|---|---|
| Monolito | `python monolito.py` | http://localhost:8000 |
| Microsserviços | `python iniciar_microsservicos.py` | http://localhost:9000 |

O objetivo é descobrir, na prática, **onde os microsserviços ganham e onde eles cobram** . 

|**Versão**|**Endereço**|**Onde ficam os dados**|
|---|---|---|
|Monolito|http://localhost:8000|dados/monolito.json|
|Microsserviços|http://localhost:9000 (Vitrine)|dados/estoque.json e<br>dados/pedidos.json|
|Rotas nas duas| `/produto/1`, `/comprar/1`, `/relatorio`, `/bug/estoque`||
|Derrubar um serviço|http://localhost:<porta>/desligar|Catálogo 9001 · Estoque 9002 ·<br>Pedidos 9003|

**Faça** Abra dois terminais na pasta laboratorio. 

<mark># terminal 1 — leva 10 s para subir</mark> `python monolito.py` 

<mark># terminal 2 — sobe 4 processos</mark> `python iniciar_microsservicos.py` 

**Faça** Abra duas abas no navegador, lado a lado: 

http://localhost:8000/produto/1,  http://localhost:9000/produto/1 

**Deve aparecer** O mesmo produto nas duas: Teclado mecânico, R$ 250, 5 em estoque. 

### **Experimento 1 · Deploy de uma promoção** 

O time de vendas quer 10% de desconto. Vocês vão "publicar" essa mudança nas duas versões e observar **o que sai do ar enquanto isso**. 

**Faça — monolito a)** Em monolito.py, mude DESCONTO = 0 para DESCONTO = 10. **b)** No terminal 1, Ctrl+C e rode `python monolito.py` de novo. **c)** Durante os 10s de subida, tente abrir <localhost:8000/relatorio>. 

**Faça — microsserviços a)** Em catalogo.py, mude DESCONTO = 0 para DESCONTO = 10. **b)** Abra <localhost:9001/desligar> para derrubar só o Catálogo. **c)** Num terceiro terminal, rode `python catalogo.py`. **d)** Durante os 4s de subida, tente <localhost:9000/relatorio> e <localhost:9000/produto/1>.   

**Deve aparecer** Depois da subida, o preço é R$ 225 nas duas. 

||**Monolito**|**Microsserviços**|
|---|---|---|
|Quanto tempo ficou fora do ar?|~10s (todo o sistema, enquanto o processo reiniciava)|~4-15s, mas só a parte que depende do Catálogo|
|O que parou de funcionar?|Tudo — inclusive /relatorio, que não tinha nada a ver com o desconto|Só /produto/1 (precisa do preço do Catálogo)|
|O que continuou funcionando?|Nada|/relatorio e /comprar/1, que dependem de Pedidos e Estoque, não do Catálogo|

**Responda** Poder ou problema dos microsserviços? Por quê? 

É um poder, mas com uma condição. Nos microsserviços, o Catálogo caiu e a loja continuou operando: quem só queria ver o relatório ou finalizar uma compra nem percebeu o problema. No monolito, como tudo é um processo só, um reinício derruba a aplicação inteira — mesmo que a mudança fosse só no módulo de Catálogo, ninguém conseguia acessar nada, nem função que não tinha relação com o desconto.

Essa independência de deploy é justamente a promessa central dos microsserviços: cada serviço pode subir, cair ou ser atualizado sem tirar o sistema inteiro do ar. O preço que se paga por isso é complexidade — agora existem 4 processos, 4 portas e a necessidade de cada serviço saber lidar com a possibilidade de outro estar fora do ar (é o que a Vitrine faz ao tratar Indisponivel e mostrar "estoque desconhecido" em vez de quebrar).

### **Experimento 2 · Latência** 

**Faça** Num terminal livre, rode: 

`python comparar.py</mark>` 

**Faça** Abra de novo /produto/1 nas duas abas e compare o campo tempo_interno_ms. 

||**Monolito**|**Microsserviços**|
|---|---|---|
|Tempo médio por página (comparar.py)|11.36 ms|19.64 ms|
|tempo_interno_ms|0.011|42.086|

**Responda** Aqui tudo roda no mesmo computador. O que aconteceria com essa diferença se cada serviço estivesse numa máquina diferente? 

A diferença de latência ficaria bem maior. Aqui, os 19,64 ms extras dos microsserviços vêm quase só do custo de processar duas chamadas HTTP localmente (na mesma máquina, sem atraso real de rede). Se Catálogo, Estoque, Pedidos e Vitrine estivessem em máquinas diferentes — em datacenters distintos, por exemplo —, cada uma dessas chamadas passaria a sofrer latência real de rede (alguns milissegundos a dezenas de milissegundos por salto, dependendo da distância e da infraestrutura), além do risco de perda de pacotes e variação de latência (jitter).

Como a Vitrine faz 2 saltos de rede para montar /produto/1 (Catálogo e Estoque), esse custo se multiplicaria a cada chamada. Num monolito, como tudo é uma chamada de função dentro do mesmo processo, esse custo não existe — a "comunicação" é só acesso à memória. É por isso que arquiteturas de microsserviços em produção real costumam investir em: reduzir o número de saltos por requisição, usar cache, processar em paralelo o que não depende um do outro, e posicionar serviços que se comunicam muito na mesma região/rede.

### - **Experimento 3 · Consistência** 

Na demonstração, o professor derrubou o Estoque e a loja em microsserviços **continuou vendendo** . Agora vocês vão ver o preço disso. 

**Faça a)** Abra <localhost:9000/relatorio> e anote os números. **b)** Derrube só o Estoque: <localhost:9002/desligar>. **c)** Compre duas vezes: <localhost:9000/comprar/1>. **d)** Religue o Estoque: `python estoque.py`. **e)** Abra <localhost:9000/relatorio> de novo. 

**Deve aparecer** Em (c): "aviso": "Estoque fora do ar: pedido registrado SEM baixa de estoque". Em (e): "pedidos_pendentes": 2 e "consistente": false. 

|**/relatorio (microsserviços)**|**Antes**|**Depois**|
|---|---|---|
|pedidos_confirmados|5|5|
|pedidos_pendentes|3|5|
|baixas_de_estoque|5|5|
|consistente|false|false|


**Faça** Abra a pasta dados/. Compare pedidos.json e estoque.json: cada banco conta uma história diferente. 

**Responda** No monolito, o bug do Estoque derrubou a loja inteira: nenhuma venda, mas nenhum dado errado. Nos microsserviços, a loja vendeu, mas os bancos discordam. **Qual dos dois a loja prefere? Quem decide isso?** 

Não existe resposta técnica certa — é uma decisão de negócio. O monolito escolhe consistência: prefere não vender a vender errado, porque estoque e pedido moram na mesma transação. Os microsserviços, como implementados aqui, escolhem disponibilidade: prioridade é não perder a venda, mesmo que isso signifique reconciliar os dados depois (ou até vender um produto que já tinha acabado o estoque).

Essa é a essência do trade-off descrito no teorema CAP: com uma falha de rede/serviço, você não pode ter os dois ao mesmo tempo — precisa escolher entre Consistência e Disponibilidade. Quem decide isso não é o time técnico sozinho, é o negócio: para um e-commerce concorrido, perder uma venda pode custar mais caro do que lidar depois com uma reconciliação manual de estoque; já para um sistema financeiro (transferência bancária, por exemplo), vender "errado" é inaceitável, então vale a pena tirar o sistema do ar antes de arriscar inconsistência. A arquitetura de microsserviços aqui só torna essa escolha explícita — o código de pedidos.py até comenta isso: "Decisão de negócio: não perder a venda."

### **Experimento 4 · Operação** 

**Faça** Faça uma compra em cada versão (/comprar/2 nas duas) e olhe os terminais. 

|**Para uma compra…**|**Monolito**<br>**Microsserviços**|
|---|---|



|Quantos processos estão rodando?|1|4 (Catálogo, Estoque, Pedidos, Vitrine)|
|Quantas portas?|1 (8000)|4 (9000, 9001, 9002, 9003)|
|Quantos arquivos de banco?|1 (monolito.json)|2 (estoque.json, pedidos.json)|
|Quantas linhas de log apareceram?|||
|Em quantos serviços?|


**Responda** Se a compra desse errado, onde vocês procurariam o erro em cada versão? 

## **Placar da dupla** 

|**Experimento**|**Quem saiu melhor?**|**Para microsserviços, é poder ou**<br>**problema?**|
|---|---|---|
|Bug fatal (demonstração)|||
|1 · Deploy|||
|2 · Latência|||
|3 · Consistência|||
|4 · Operação|||


**Para fechar** Uma loja com **3 desenvolvedores** deveria usar qual das duas versões? E uma com **300** ? Usem o placar como argumento. 

Para recomeçar do zero: desliguem tudo (Ctrl+C nos terminais) e rodem `python resetar.py`. 


