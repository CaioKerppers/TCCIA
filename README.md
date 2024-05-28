# Pokémon Battle Simulator

Este projeto é um simulador de batalhas Pokémon em Python, utilizando a biblioteca Pokébase para obter informações detalhadas sobre Pokémon e seus movimentos. O objetivo é simular batalhas, aplicar regras de combate e utilizar aprendizado por reforço para melhorar a estratégia dos Pokémon ao longo do tempo.

## Requisitos

- Python 3.x
- Biblioteca `pokebase`
- Biblioteca `csv`

Você pode instalar a biblioteca `pokebase` utilizando o pip:

```bash
pip install pokebase
```

## Estrutura do Código

### Classe `Pokemon`

A classe `Pokemon` representa um Pokémon individual e contém informações detalhadas sobre o Pokémon, incluindo suas estatísticas, tipos, movimentos e natureza. Ela possui métodos para verificar se o Pokémon é banido, aplicar nível automático, selecionar e usar movimentos, aplicar efeitos da natureza e atualizar a tabela Q para aprendizado por reforço.

#### Métodos Principais

- `__init__`: Inicializa um novo Pokémon com suas características.
- `is_banned`: Verifica se o Pokémon é banido para batalhas.
- `auto_level`: Ajusta o nível do Pokémon para 50 durante batalhas.
- `check_play_restrictions`: Verifica restrições de jogo como cláusula de item e espécie.
- `get_pokemon_info`: Obtém informações do Pokémon utilizando a API Pokébase ou um arquivo CSV.
- `select_move`: Seleciona um movimento aleatório do conjunto de movimentos do Pokémon.
- `use_move`: Utiliza o movimento selecionado contra um oponente.
- `confirm_attack`: Confirma o uso do movimento selecionado.
- `get_move_info`: Obtém informações detalhadas sobre um movimento.
- `show_move_info`: Mostra informações sobre o movimento selecionado.
- `update_q_table`: Atualiza a tabela Q com o resultado da ação.
- `apply_nature`: Aplica os efeitos da natureza do Pokémon.
- `receive_status`: Aplica um status ao Pokémon.

### Classe `Trainer`

A classe `Trainer` representa um treinador de Pokémon e gerencia sua equipe de Pokémon. Ela permite adicionar novos Pokémon à equipe e selecionar o Pokémon ativo para batalha.

#### Métodos Principais

- `__init__`: Inicializa um novo treinador com as regras de batalha.
- `add_pokemon`: Adiciona um novo Pokémon à equipe do treinador.
- `switch_active_pokemon`: Troca o Pokémon ativo do treinador.
- `select_move`: Seleciona um movimento para o Pokémon ativo.
- `use_move`: Usa o movimento do Pokémon ativo contra um oponente.

### Classe `BattleRules`

A classe `BattleRules` define as regras de batalha, incluindo as vantagens e desvantagens de tipo para calcular o dano.

#### Métodos Principais

- `__init__`: Inicializa as regras de batalha com vantagens e desvantagens de tipo.

## Funções Auxiliares

- `get_state`: Obtém o estado atual do Pokémon do agente e do oponente.

## Como Usar

1. **Criação de Treinadores e Pokémon**:
    - Crie instâncias da classe `Trainer` para cada treinador.
    - Adicione Pokémon à equipe de cada treinador utilizando o método `add_pokemon`.

2. **Configuração da Batalha**:
    - Defina as regras de batalha utilizando a classe `BattleRules`.

3. **Simulação da Batalha**:
    - Utilize os métodos `select_move` e `use_move` para simular os turnos de batalha entre os Pokémon ativos dos treinadores.

4. **Aprendizado por Reforço**:
    - A tabela Q será atualizada com os resultados das ações para melhorar a estratégia dos Pokémon ao longo do tempo.

### Exemplo de Uso

```python
# Inicializar regras de batalha
battle_rules = BattleRules()

# Criar treinadores
trainer1 = Trainer(battle_rules)
trainer2 = Trainer(battle_rules)

# Adicionar Pokémon aos treinadores
trainer1.add_pokemon("Pikachu")
trainer2.add_pokemon("Charmander")

# Selecionar Pokémon ativo
trainer1.switch_active_pokemon(0)
trainer2.switch_active_pokemon(0)

# Simular turno de batalha
trainer1.select_move(trainer2.active_pokemon)
trainer1.use_move(trainer2.active_pokemon)

trainer2.select_move(trainer1.active_pokemon)
trainer2.use_move(trainer1.active_pokemon)
```


## Licença

Esse produto foi feito apenas para ser apresentado como um TCC e como uma ferramenta para auxiliar jogadores competitivos do VGC, produto feito sem qualquer visão de lucro que possa prejudicar de alguma forma as empresas: **The Pokémon Company**; **Game Freak**; **Nintendo**.
