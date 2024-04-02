import tkinter as tk
import random
import math

PLAYER_X = 'X'
PLAYER_O = 'O'
EMPTY = ' '
ROWS = 6
COLUMNS = 7
SIMULATION_COUNT = 1000

class CMTS:
    #constructor of CMTS class
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0

    #checks if it's full expended(all moves are explored)
    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_moves())

    #selects the child node to explore based on UCT
    def select_child(self, exploration_factor=1.414):
        best_child = None
        best_score = -float('inf')
        for child in self.children:
            if child.visits == 0:
                score = -float('inf')
            else:
                score = child.wins / child.visits + exploration_factor * math.sqrt(2 * math.log(self.visits) / child.visits)
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    #expands the current node by creating new child nodes for each possible move in the current state
    def expand(self):
        legal_moves = self.state.get_legal_moves()
        for move in legal_moves:
            new_state = self.state.copy()
            new_state.make_move(move)
            new_child = CMTS(new_state, parent=self)
            self.children.append(new_child)
        return random.choice(self.children) if self.children else None

    #backpropagates the result of a simulation up the tree search
    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

class GameState:
    #constructor of GameState class
    def __init__(self, board, current_player):
        self.board = board
        self.current_player = current_player

    #list of legal moves for the current player
    def get_legal_moves(self):
        legal_moves = []
        for col in range(COLUMNS):
            if self.board[0][col] == EMPTY:
                legal_moves.append(col)
        return legal_moves

    #makes a move for the current player at the specified column
    def make_move(self, col):
        for row in range(ROWS-1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = self.current_player
                break
        self.current_player = PLAYER_X if self.current_player == PLAYER_O else PLAYER_O

    #checks if there is a winner
    def check_winner(self):
        # Horizontal 
        for row in self.board:
            for i in range(COLUMNS - 3):
                if all(piece == self.current_player for piece in row[i:i+4]):
                    return True

        # Vertical 
        for col in range(COLUMNS):
            for i in range(ROWS - 3):
                if all(self.board[row][col] == self.current_player for row in range(i, i+4)):
                    return True

        # Diagonal (left to right) 
        for row in range(ROWS - 3):
            for col in range(COLUMNS - 3):
                if all(self.board[row+i][col+i] == self.current_player for i in range(4)):
                    return True

        # Diagonal (right to left) 
        for row in range(ROWS - 3):
            for col in range(3, COLUMNS):
                if all(self.board[row+i][col-i] == self.current_player for i in range(4)):
                    return True

        return False

    #checks if the board is full
    def is_board_full(self):
        return all(piece !=EMPTY for row in self.board for piece in row)

    #returns a copy of the current game
    def copy(self):
        return GameState([row[:] for row in self.board], self.current_player)

class AStar:
    #constructor of A* class
    def __init__(self, board):
        self.board = board
        self.current_player = PLAYER_X

    #returns the score of a given state
    def get_score(self, state):
        if state.check_winner():
            return 100 if state.current_player == self.current_player else -100
        elif state.is_board_full():
            return 0
        else:
            return 0

    #heuristic value of a given state
    def heuristic(self, state):
        score = 0
        # Horizontal 
        for row in state.board:
            for i in range(COLUMNS - 3):
                if all(piece == state.current_player for piece in row[i:i+4]):
                    score += 10

        # Vertical 
        for col in range(COLUMNS):
            for i in range(ROWS - 3):
                if all(state.board[row][col] == state.current_player for row in range(i, i+4)):
                    score += 10

        # Diagonal (left to right) 
        for row in range(ROWS - 3):
            for col in range(COLUMNS - 3):
                if all(state.board[row+i][col+i] == state.current_player for i in range(4)):
                    score += 10

        # Diagonal (right to left) 
        for row in range(ROWS - 3):
            for col in range(3, COLUMNS):
                if all(state.board[row+i][col-i] == state.current_player for i in range(4)):
                    score += 10

        return score
    #returns the best move for the current player in the given state
    def get_best_move(self, state):
        frontier = [(self.get_score(state) + self.heuristic(state), state)]
        explored = set()
        while frontier:
            _, current = min(frontier)
            explored.add(str(current.board))
            if current.check_winner():
                return current.get_legal_moves()[0]
            if not current.get_legal_moves():
                continue
            for move in current.get_legal_moves():
                new_state = current.copy()
                new_state.make_move(move)
                if str(new_state.board) not in explored:
                    frontier.append((self.get_score(new_state) + self.heuristic(new_state), new_state))

        return random.choice(current.get_legal_moves())

class ConnectFourGUI:
    #constructor of ConnectFourGUI class
    def __init__(self, master, ai_type='mcts'):
        self.master = master
        self.master.title("Connect Four")
        for i in range(ROWS + 3): 
            self.master.grid_rowconfigure(i, weight=1)
        for j in range(COLUMNS):
            self.master.grid_columnconfigure(j, weight=1)

        self.board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_player = PLAYER_X

        self.ai_type = ai_type

        self.create_board_buttons()
        self.create_labels()
        self.create_control_buttons() 

        # If current player is O, make move automatically
        if self.current_player == PLAYER_O:
            if self.ai_type == 'mcts':
                self.make_computer_move()
            else:
                self.make_computer_move_astar()

    #creates a frame for control buttons
    def create_control_buttons(self):
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=ROWS + 2, columnspan=COLUMNS, sticky="nsew")

        # AI type selection
        ai_type_label = tk.Label(control_frame, text="Choose AI:")
        ai_type_label.grid(row=0, column=0, padx=(10, 5))

        self.ai_type_var = tk.StringVar(control_frame)
        self.ai_type_var.set(self.ai_type)
        mcts_button = tk.Radiobutton(control_frame, text="MCTS", variable=self.ai_type_var, value='mcts')
        mcts_button.grid(row=0, column=1)

        astar_button = tk.Radiobutton(control_frame, text="A*", variable=self.ai_type_var, value='astar')
        astar_button.grid(row=0, column=2)

        # Restart button
        restart_button = tk.Button(control_frame, text='Restart Game', command=self.restart_game)
        restart_button.grid(row=0, column=3, padx=(20, 10))

    #enables all buttons in the board
    def enable_buttons(self):
        for button in self.buttons:
            button.config(state=tk.NORMAL)

    #restarts the game by resetting everything
    def restart_game(self):
        self.board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.current_player = PLAYER_X
        self.update_board()
        self.enable_buttons()
        self.status_label.config(text="Player X Turn")

    #creates a grid of buttons for the game board and a label for each button
    def create_board_buttons(self):
        self.buttons = []
        for col in range(COLUMNS):
            button = tk.Button(self.master, text=' ', width=4, height=2,
                               command=lambda col=col: self.make_move(col), bg='blue')
            button.grid(row=0, column=col, sticky="nsew")
            button.grid_propagate(False)
            self.buttons.append(button)

        self.game_board = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
        for row in range(ROWS):
            for col in range(COLUMNS):
                label = tk.Label(self.master, text='', width=4, height=2, relief="sunken", bg='blue')
                label.grid(row=row+1, column=col, sticky="nsew")
                label.grid_propagate(False)  
                self.game_board[row][col] = label

    #creates a label for the game status
    def create_labels(self):
        self.status_label = tk.Label(self.master, text="Player X Turn")
        self.status_label.grid(row=ROWS+1, columnspan=COLUMNS)

    #handles a user move when a button is clicked
    def make_move(self, col):
        for row in range(ROWS-1, -1, -1):
            if self.board[row][col] == EMPTY:
                self.board[row][col] = self.current_player
                self.update_board_space(row, col)
                if self.check_winner():
                    self.status_label.config(text=f"Player {self.current_player} wins!")
                    self.disable_buttons()
                elif self.is_board_full():
                    self.status_label.config(text="It's a tie!")
                    self.disable_buttons()
                else:
                    self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
                    if self.current_player == PLAYER_X:
                        self.status_label.config(text="Player X Turn")
                    else:
                        self.status_label.config(text="Player O Turn")
                        if self.ai_type == 'mcts':
                            self.make_computer_move()
                        else:
                            self.make_computer_move_astar()
                break

    #handles a computer move when it is the computer's turn MCST
    def make_computer_move(self):
        root_state = GameState(self.board, self.current_player)
        root_node = CMTS(root_state)
        for _ in range(SIMULATION_COUNT):
            node = root_node
            state = root_state.copy()
            while not node.is_fully_expanded() and not state.check_winner() and not state.is_board_full():
                if not node.is_fully_expanded():
                    child = node.expand()
                    if child:
                        node = child
                        state.make_move(random.choice(state.get_legal_moves()))
                    else:
                        break
            if not state.check_winner() and not state.is_board_full():
                moves = state.get_legal_moves()
                move = random.choice(moves)
                state.make_move(move)
                node = CMTS(state, parent=node)
                node.expand()
            while not state.check_winner() and not state.is_board_full():
                moves = state.get_legal_moves()
                move = random.choice(moves)
                state.make_move(move)
            
            result = 1 if state.check_winner() and state.current_player == PLAYER_O else 0
            node.backpropagate(result)

        best_child = root_node.select_child(exploration_factor=0)
        if best_child:
            self.board = best_child.state.board
            self.current_player = PLAYER_X if self.current_player == PLAYER_O else PLAYER_O
            self.update_board()

    #handles a computer move when it is the computer's turn A*
    def make_computer_move_astar(self):
        ai = AStar(self.board)
        col = ai.get_best_move(GameState(self.board, self.current_player))
        self.board[ROWS-1][col] = self.current_player
        self.update_board()

    #updates the game board by changing the background color of each button
    def update_board(self):
        for row in range(ROWS):
            for col in range(COLUMNS):
                if self.board[row][col] == PLAYER_X:
                    color = 'red'
                elif self.board[row][col] == PLAYER_O:
                    color = 'yellow'
                else:
                    color = 'blue'
                self.game_board[row][col].config(bg=color)

    #method updates a single button in the game board
    def update_board_space(self, row, col):
        if self.current_player == PLAYER_X:
            color = 'red'
        else:
            color = 'yellow'
        self.game_board[row][col].config(bg=color)

    #method checks if there is a winner
    def check_winner(self):
        # Horizontal 
        for row in self.board:
            for i in range(COLUMNS - 3):
                if all(piece == self.current_player for piece in row[i:i+4]):
                    return True

        # Vertical 
        for col in range(COLUMNS):
            for i in range(ROWS - 3):
                if all(self.board[row][col] == self.current_player for row in range(i, i+4)):
                    return True

        # Diagonal (left to right) 
        for row in range(ROWS - 3):
            for col in range(COLUMNS - 3):
                if all(self.board[row+i][col+i] == self.current_player for i in range(4)):
                    return True

        # Diagonal (right to left) 
        for row in range(ROWS - 3):
            for col in range(3, COLUMNS):
                if all(self.board[row+i][col-i] == self.current_player for i in range(4)):
                    return True

        return False

    #checks if the board is full
    def is_board_full(self):
        return all(piece != EMPTY for row in self.board for piece in row)

    #disables all the buttons
    def disable_buttons(self):
        for button in self.buttons:
            button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    ai_type = tk.StringVar(root)
    ai_type.set('mcts')
    tk.Radiobutton(root, text="MCTS", variable=ai_type, value='mcts').grid(row=ROWS+2, column=0, sticky="w")
    tk.Radiobutton(root, text="A*", variable=ai_type, value='astar').grid(row=ROWS+2, column=1, sticky="w")

    game = ConnectFourGUI(root, ai_type=ai_type.get())
    root.mainloop()

if __name__ == "__main__":
    main()
