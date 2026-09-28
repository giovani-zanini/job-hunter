### Bloco 1: Métricas e Impacto de Negócio

Muitos tópicos estão descritivos ("Desenvolvimento de microsserviços"), mas recrutadores amam números.

1. **Sobre a Afya (Core Squad):** Você mencionou a redução de boilerplate com "Base Repositories". Você consegue estimar quanto tempo de desenvolvimento (ou esforço de setup) foi economizado para os outros times com essa padronização?
- Eu trouxe para reflexão a redução de DTO's (tinhamos o uso excessivo de BaseModel uma implementação custoza do pydantic para realizar validações) e a implementação de entidades de dominio. Como resultado da discução, foi considerado um ponto muito importante de melhoria, entretanto o time não aderiu ao uso de entidades de dominio pelo aumento da complexidade induzida. Mas a idéia da redução dos DTO's e padronização do seu uso somente nos pontos de entrada e saida da aplicação foi amplamente usada, assim sendo utilizado estruturas mais simples como dataclasses e namedtuples na comunicação de camadas internas da aplicação. Também levei para discução o uso de data mappers, mas novamente iria aumentar a complexidade induzida e o time nao aderiu...
- Sobre o base repository, eles seriam o proximo passo e a evolução natural sobre as discuções entre DTO's; Entidades e Data Mappers. A idéia evoluiu a um ponto onde nós iriamos encapsular operações comuns a todos os bouded contexts em funções, utilizando dataclasses como output de cada repository. A idéia seria basicamente uma coleção de funções que encapsulam operações com o banco sem ter depencia entre serviços de dominio e usecases "controllers"


2. **Sobre a Infoglobo (Eleições 2022):** A arquitetura Serverless suportou picos de tráfego. Você lembra de algum número de requisições por segundo (RPS) ou volume de acessos simultâneos que o sistema aguentou sem cair?
- A idéia das soluções serverless na editora nunca foi focada em levar um hit no lambda por uma ação do usuario (que estava logado no site) e sim através de eventos internos, tanto da infra (trigger de s3, evento em fila sqs, e etc...) quanto da parte de negocios (triggers em planilhas, sistemas internos, etc...). O que o usuario consumia era o resultado final do processamento e distribuido através de um bucket publico do S3 (acesso sempre por uma cdn com ttl de 5 a 10 minutos), isso era o que viabilizava a entrega de conteudo estatistico como relatorios. Ou seja, quem levava o pico de trafico era a cdn e nao a infra serverless. Obs.: Lembro que nas eleições a quantidade de acessos contabilizou em torno de 580 milhoes [referência](https://oglobo.globo.com/politica/noticia/2022/11/o-globo-bate-recorde-historico-e-supera-meio-bilhao-de-paginas-vistas-no-mes-da-eleicao.ghtml)

3. **Sobre a Noana (IoT):** Ao atingir 85% de cobertura de testes e automatizar regressões, houve uma queda perceptível no número de bugs que chegavam em produção ou no tempo de "Hotfix"?
- Ouve uma queda de bugs em produção do ponto de vista de novas features (elas nao quebravam dependencias, etc....)


### Bloco 2: Liderança e "Soft Skills" Técnicas

Agora que ajustamos a parte de infra, vamos focar em como você influencia pessoas e processos.

4. **Mentoria e Cultura:** Na Afya ou Infoglobo, você participou da criação de guias de estilo, documentação de arquitetura (ADRs) ou ajudou a estruturar o processo de *Code Review*? Como isso impactou a velocidade ou a qualidade do que o time entregava?
- Minha atuação sempre foi com um olhar socratico e em casos raros uma imposição técnica séria (quando o design/padrões do projeto acaba sendo projudicado), sempre foco em manter os padrões da casa (sem me enviesar para as minhas escolhas) e sujerir alterações focadas em performance e simplicidades....

5. **Tomada de Decisão (Pragmatismo):** Você mencionou que o time não aderiu a Entidades de Domínio por causa da complexidade. Como foi esse processo de negociação? Você apresentou uma PoC ou fez um "post-mortem" de design para chegar à solução das `dataclasses`? Isso demonstra sua capacidade de liderança técnica.
- Eu realizeri uma poc demonstrando os conceitos de entidades de dominio, redução e simplificação de DTO's, data mapper's e algumas simplificações e correções....

### Bloco 3: IA e Projetos de Inovação

Você tem uma veia forte de IA com o **Plantii** e o **The Architect**.

6. **Arquitetura RAG no Plantii:** Como você lidou com a precisão dos diagnósticos? Você usou alguma técnica de *Prompt Engineering* específica ou refinamento de busca vetorial (ex: *Self-Querying* ou *Re-ranking*)?
- Nós focamos em um mvp realmente enchuto, sem diagnosticos de doenças. Nós levamos a identificação, programaas de cuidado e dicas.... tanto para o historico do chat como para o cache das respostas nós utilizamos bancos RAG e técnicas com llms mais baratas com o intuito de gerar menssagens personalizadas mas com um menor custo (faz o hit no modelo maior quando realmente precisa)

7. **The Architect:** Sendo uma ferramenta de brainstorming arquitetural, qual o maior desafio técnico que você está enfrentando no desenvolvimento? (Ex: Alucinação da IA em padrões de design ou integração do grafo de dependências).
- Ainda nao dei muita atenção nesse projeto, eu estou em uma faze muito inicial testando a viabilidade e entendendo se vale a pena seguir com esse projeto. A idéia é basicamente eu criar projetos, cada projeto é um chat com uma llm no mdoo socratico e em um tela no lado direito eu tenho um mini agente que organiza os idéias da nossa discução em um markdown
