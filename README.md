
# Pokémon Battle Simulator

## Descrição

Este projeto é um simulador de batalhas Pokémon. Ele permite a criação de times de Pokémon com base em dados aleatórios e configurações de regras específicas, bem como a realização de batalhas automáticas entre treinadores. O projeto utiliza dados da API PokéBase e o Firestore como banco de dados.

## Estrutura do Projeto

O projeto está dividido nos seguintes módulos:

1. `battleRules.py`: Define as regras das batalhas.
2. `data_fetching.py`: Seleciona Pokémon aleatórios e monta os times dos treinadores.
3. `fetch_functions.py`: Funções para buscar dados no Firestore.
4. `utils.py`: Funções utilitárias.
5. `trainer.py`: Define a classe do treinador e suas ações.
6. `pokemon.py`: Define a classe do Pokémon e suas ações.

## battleRules.py

### Classe `BattleRules`

Define as regras das batalhas, como o nível máximo permitido e o tamanho do time.

- `apply_rules(trainer1, trainer2)`: Aplica as regras aos times dos treinadores, ajustando o nível dos Pokémon e verificando restrições.

## data_fetching.py

### Funções Principais

- `select_random_pokemon(num_pokemon, battle_rules)`: Seleciona Pokémon aleatórios com base nas regras da batalha.
- `select_team(trainer, battle_rules)`: Seleciona o time do treinador aleatoriamente, garantindo que os Pokémon selecionados não sejam banidos.

## fetch_functions.py

### Funções de Busca

- `fetch_banned_pokemon()`: Busca a lista de Pokémon banidos no Firestore.
- `fetch_type_chart()`: Busca a tabela de tipos no Firestore.
- `fetch_stat_multipliers()`: Busca os multiplicadores de estágios de stats no Firestore.
- `fetch_natures()`: Busca as naturezas dos Pokémon no Firestore.
- `fetch_type_to_int()`: Busca o mapeamento de tipos para inteiros no Firestore.

## utils.py

### Funções Utilitárias

- `get_random_nature(natures_ref)`: Retorna uma natureza aleatória do banco de dados.
- `get_stat_multipliers()`: Retorna os multiplicadores de estágios de stats.

## trainer.py

### Classe `Trainer`

Define o treinador e suas ações, como adicionar Pokémon ao time, selecionar o Pokémon ativo e realizar turnos de batalha.

- `add_pokemon(pokemon)`: Adiciona um Pokémon ao time do treinador.
- `switch_active_pokemon(index)`: Troca o Pokémon ativo do treinador.
- `choose_active_pokemon()`: Escolhe um Pokémon ativo aleatoriamente dentre os disponíveis.
- `battle_turn(opponent_trainer)`: Realiza o turno de batalha do treinador.
- `handle_fainted_pokemon()`: Lida com o Pokémon desmaiado do treinador.
- `all_pokemons_fainted()`: Verifica se todos os Pokémon do treinador estão desmaiados.

## pokemon.py

### Classe `Pokemon`

Define o Pokémon e suas ações, incluindo a seleção de movimentos, cálculo de danos e treinamento do modelo de aprendizado por reforço.

- `__init__(...)`: Inicializa os atributos do Pokémon, como stats, naturezas e nível.
- `train_step(X, y)`: Realiza um passo de treinamento do modelo.
- `build_model(input_dim, output_dim)`: Constrói o modelo de aprendizado por reforço.
- `train_model()`: Treina o modelo de aprendizado por reforço.
- `prepare_data()`: Prepara os dados para o treinamento do modelo.
- `save_model(filepath)`: Salva o modelo no caminho especificado.
- `load_model(filepath)`: Carrega o modelo do caminho especificado.
- `generate_random_ivs()`: Gera IVs aleatórios para o Pokémon.
- `generate_random_evs()`: Gera EVs aleatórios para o Pokémon.
- `load_stat_multipliers()`: Carrega os multiplicadores de estágios de stats do Firestore.
- `apply_buff(stat, stages)`: Aplica um buff ao stat do Pokémon.
- `apply_debuff(stat, stages)`: Aplica um debuff ao stat do Pokémon.
- `apply_nature_effects(stat_name)`: Aplica os efeitos da natureza ao stat do Pokémon.
- `calculate_stat(base, iv, evs, level)`: Calcula o stat do Pokémon.
- `calculate_hp_stat(base, iv, evs, level)`: Calcula o stat de HP do Pokémon.
- `calculate_final_stats()`: Calcula os stats finais do Pokémon.
- `apply_stat_change(base_value, stage)`: Aplica a mudança de estágio ao stat do Pokémon.
- `get_type_effectiveness(move_type, defender_types)`: Calcula a eficácia do tipo do movimento.
- `is_banned()`: Verifica se o Pokémon é banido.
- `auto_level()`: Ajusta o nível do Pokémon automaticamente.
- `check_play_restrictions(team)`: Verifica as restrições de uso do Pokémon.
- `get_pokemon_info(pokemon_id)`: Obtém as informações do Pokémon pela API PokéBase.
- `select_move(opponent)`: Seleciona o movimento do Pokémon.
- `select_move_automatically(opponent)`: Seleciona automaticamente o movimento do Pokémon.
- `select_random_move(opponent)`: Seleciona um movimento aleatório para o Pokémon.
- `use_move(opponent)`: Usa o movimento selecionado contra o oponente.
- `calculate_damage(attacker, defender, move_info)`: Calcula o dano do movimento.
- `confirm_attack(opponent)`: Confirma o ataque do Pokémon.
- `get_move_info(move)`: Obtém as informações do movimento pela API PokéBase.
- `show_move_info(move)`: Mostra as informações do movimento.

## Como Executar

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure o Firestore**:
   - Adicione suas credenciais do Firebase em `pokemonbattleia-firebase-adminsdk-rjtw2-7c11d2875b.json`.

3. **Execute o simulador**:
   ```bash
   python main.py
   ```

## Contribuição

Sinta-se à vontade para abrir issues e pull requests para melhorias no projeto.

## Licença

Esse produto foi feito apenas para ser apresentado como um TCC e como uma ferramenta para auxiliar jogadores competitivos do VGC, produto feito sem qualquer visão de lucro que possa prejudicar de alguma forma as empresas: **The Pokémon Company**; **Game Freak**; **Nintendo**.