"""
gtp_connection.py
Module for playing games of Go using GoTextProtocol

Parts of this code were originally based on the gtp module
in the Deep-Go project by Isaac Henrion and Amos Storkey
at the University of Edinburgh.
"""
import traceback
from sys import stdin, stdout, stderr
from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    PASS,
    MAXSIZE,
    coord_to_point,
)
import numpy as np
import re

WIN = 4
BLOCK_WIN = 3
OPEN_FOUR = 2
BLOCK_OPEN_FOUR = 1
RANDOM = 0


class GtpConnection:
    def __init__(self, go_engine, board, debug_mode=False):
        """
        Manage a GTP connection for a Go-playing engine

        Parameters
        ----------
        go_engine:
            a program that can reply to a set of GTP commandsbelow
        board:
            Represents the current board state.
        """
        self._debug_mode = debug_mode
        self.go_engine = go_engine
        self.policy = "random"
        self.board = board
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "genmove": self.genmove_cmd,
            "policy": self.policy_cmd,
            "policy_moves": self.policy_moves_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "legal_moves": self.legal_moves_cmd,
            "gogui-rules_game_id": self.gogui_rules_game_id_cmd,
            "gogui-rules_board_size": self.gogui_rules_board_size_cmd,
            "gogui-rules_legal_moves": self.gogui_rules_legal_moves_cmd,
            "gogui-rules_side_to_move": self.gogui_rules_side_to_move_cmd,
            "gogui-rules_board": self.gogui_rules_board_cmd,
            "gogui-rules_final_result": self.gogui_rules_final_result_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd
        }

        # used for argument checking
        # values: (required number of arguments,
        #          error message on argnum failure)
        self.argmap = {
            "boardsize": (1, "Usage: boardsize INT"),
            "komi": (1, "Usage: komi FLOAT"),
            "known_command": (1, "Usage: known_command CMD_NAME"),
            "genmove": (1, "Usage: genmove {w,b}"),
            "play": (2, "Usage: play {b,w} MOVE"),
            "legal_moves": (1, "Usage: legal_moves {w,b}"),
        }

    def write(self, data):
        stdout.write(data)

    def flush(self):
        stdout.flush()

    def start_connection(self):
        """
        Start a GTP connection.
        This function continuously monitors standard input for commands.
        """
        line = stdin.readline()
        while line:
            self.get_cmd(line)
            line = stdin.readline()

    def get_cmd(self, command):
        """
        Parse command string and execute it
        """
        if len(command.strip(" \r\t")) == 0:
            return
        if command[0] == "#":
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]
        args = elements[1:]
        if self.has_arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".format(traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error("Unknown command")
            stdout.flush()

    def has_arg_error(self, cmd, argnum):
        """
        Verify the number of arguments of cmd.
        argnum is the number of parsed arguments
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg):
        """ Write msg to the debug stream """
        if self._debug_mode:
            stderr.write(msg)
            stderr.flush()

    def error(self, error_msg):
        """ Send error msg to stdout """
        stdout.write("? {}\n\n".format(error_msg))
        stdout.flush()

    def respond(self, response=""):
        """ Send response to stdout """
        stdout.write("= {}\n\n".format(response))
        stdout.flush()

    def reset(self, size):
        """
        Reset the board to empty board of given size
        """
        self.board.reset(size)

    def board2d(self):
        return str(GoBoardUtil.get_twoD_board(self.board))

    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond("2")

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the Go engine """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the  Go engine """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game with new boardsize args[0]
        """
        self.reset(int(args[0]))
        self.respond()

    def showboard_cmd(self, args):
        self.respond("\n" + self.board2d())

    def komi_cmd(self, args):
        """
        Set the engine's komi to args[0]
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if command args[0] is known to the GTP interface
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(" ".join(list(self.commands.keys())))

    def legal_moves_cmd(self, args):
        """
        List legal moves for color args[0] in {'b','w'}
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = " ".join(sorted(gtp_moves))
        self.respond(sorted_moves)

    def play_cmd(self, args):
        """
        play a move args[1] for given color args[0] in {'b','w'}
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            color = color_to_int(board_color)
            if args[1].lower() == "pass":
                self.board.play_move(PASS, color)
                self.board.current_player = GoBoardUtil.opponent(color)
                self.respond()
                return
            coord = move_to_coord(args[1], self.board.size)
            if coord:
                move = coord_to_point(coord[0], coord[1], self.board.size)
            else:
                self.respond("unknown: {}".format(args[1]))
                return
            if not self.board.play_move(move, color):
                self.respond("illegal move: \"{}\" occupied".format(args[1].lower()))
                return
            else:
                self.debug_msg(
                    "Move: {}\nBoard:\n{}\n".format(board_move, self.board2d())
                )
            self.respond()
        except Exception as e:
            self.respond("illegal move: {}".format(str(e).replace('\'','')))

    def genmove_cmd(self, args):
        """
        Generate a move for the color args[0] in {'b', 'w'}, for the game of gomoku.
        """
        result = self.board.detect_five_in_a_row()
        if result == GoBoardUtil.opponent(self.board.current_player):
            self.respond("resign")
            return
        if self.board.get_empty_points().size == 0:
            self.respond("pass")
            return
        board_color = args[0].lower()
        color = color_to_int(board_color)
        move = self.go_engine.get_move(self.board, color)
        move_coord = point_to_coord(move, self.board.size)
        move_as_string = format_point(move_coord)
        if self.board.is_legal(move, color):
            self.board.play_move(move, color)
            self.respond(move_as_string.lower())
        else:
            self.respond("Illegal move: {}".format(move_as_string))

    def policy_cmd(self, args):
        if args[0] != "random" and args[0] != "rule_based":
            self.respond("invalid policy! Please use valid policytype: random or rule_based")
        else:
            self.policy = args[0]
            self.respond("policy set to " + self.policy)

    def policy_moves_cmd(self, args):
        # checks for game over
        if self.board.detect_five_in_a_row() != EMPTY:
            self.respond("")
            return
        # set for Random as defualt
        move_type = "Random"
        move_list = self.board.get_empty_points()
        if move_list.size == 0:
            self.respond("")
            return
        # change moves to rule_based if policy type is rule_based 
        if self.policy == "rule_based":
            print("yes move based")
            move_type, move_list = self.rule_based_move(self.board,self.board.current_player)
        
        # sort the move list
        output = []
        for move in move_list:
            move_coord = point_to_coord(move, self.board.size)
            output.append(format_point(move_coord))
        output.sort()
        output_str = move_type
        for move_string in output:
            output_str += " " + move_string

        self.respond(output_str)
        return 
    def rule_based_move(self, board, color):
        """
        returns best move for color
        """
        #bestMove = None
        bestMoveType = RANDOM
        # print(board.get_empty_points())
        moves = []

        for move in board.get_empty_points():
            moveScore = self.check_move(board, color, move)
            print('move',move)
            print('moveScore', moveScore)
            if ((bestMoveType == WIN) and (moveScore == WIN)):
                    moves.append(move)
            elif ((bestMoveType != WIN) and (moveScore == WIN)):
                bestMoveType = WIN
                moves = []
                moves.append(move)
            elif ((bestMoveType == BLOCK_WIN) and (moveScore == BLOCK_WIN)):
                moves.append(move)
            elif ((bestMoveType!= WIN) and (bestMoveType != BLOCK_WIN) and (moveScore == BLOCK_WIN)):
                bestMoveType = BLOCK_WIN
                moves = []
                moves.append(move)
            elif((bestMoveType == OPEN_FOUR)  and  (moveScore == OPEN_FOUR)):
                moves.append(move)
            elif((bestMoveType!= WIN) and (bestMoveType != BLOCK_WIN) and (bestMoveType != OPEN_FOUR) and (moveScore == OPEN_FOUR)):
                bestMoveType = OPEN_FOUR
                moves = []
                moves.append(move)
            elif((bestMoveType == BLOCK_OPEN_FOUR)  and  (moveScore == BLOCK_OPEN_FOUR)):
                moves.append(move)
            elif((bestMoveType!= WIN) and (bestMoveType != BLOCK_WIN) and (bestMoveType != OPEN_FOUR) and (bestMoveType!= BLOCK_OPEN_FOUR) and (moveScore == BLOCK_OPEN_FOUR)):
                bestMoveType = BLOCK_OPEN_FOUR
                moves = []
                moves.append(move)
            elif (bestMoveType==RANDOM):
                moves.append(move)

        if (bestMoveType == WIN): 
            bestMoveType = 'Win'
        elif (bestMoveType == BLOCK_WIN):
            bestMoveType = 'Block win'
        elif (bestMoveType == BLOCK_OPEN_FOUR):
            bestMoveType = 'Block open four'
        elif (bestMoveType == OPEN_FOUR):
            bestMoveType = 'Open four'
        else:
            bestMoveType = 'Random'
        print('best move type', bestMoveType)
        print('moves', moves)

        return bestMoveType , moves  
    
    def check_move(self, board, color, move):
        """
        returns:
            4 if winning
            3 if block win
            2 if open four
            1 if block open four
            0 otherwise (random)
        """
        newpoint = board.unpadded_point(move)
        lines = board.boardLines[newpoint]
        maxScore = RANDOM
        for line in lines:
            counts = self.get_counts(board, line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            if myCount == 4:
                return WIN
            elif oppCount == 4:
                maxScore = max(BLOCK_WIN, maxScore)
            elif myCount == 3 and oppCount == 0:
                maxScore = max(OPEN_FOUR, maxScore)
            elif myCount == 0 and oppCount == 3:
                maxScore = max(BLOCK_OPEN_FOUR, maxScore)
            else:
                maxScore = max(RANDOM, maxScore)

        return maxScore

    @staticmethod
    def get_counts(board, five_line):
        b_count = 0
        w_count = 0
        e_count = 0

        for p in five_line:
            stone = board.board[p]
            if stone == BLACK:
                b_count += 1
            elif stone == WHITE:
                w_count += 1
            else:
                e_count += 1

        return b_count, w_count, e_count


    def rule_based(self, board, color):
        orignal_board = board.copy()
        moves = board.get_empty_points()

        win = []
        block_win = []
        open_four = []
        block_open_four = []

        found_win = False
        found_block_win = False
        found_open_four = False
        found_block_open_four = False

        for move in moves:
            opp_color = GoBoardUtil.opponent(color)
            test_board = board.copy()
            test_board.play_move(move, color)
            test_board2 = board.copy()
            test_board2.play_move(move, opp_color)

            # check for win
            check_win = test_board.detect_five_in_a_row()
            if check_win == BLACK or check_win == WHITE:
                win.append(move)
                found_win = True
        
            if not found_win:
                # check if move blocks a win
                check_win = test_board2.detect_five_in_a_row()
                if check_win == BLACK or check_win == WHITE:
                    block_win.append(move)
                    found_block_win = True

            if not found_win and not found_block_win:
                # check if move creates an open four
                found_open_four = True

            if not found_win and not found_block_win and not found_open_four:
                # check if move blocks an open four
                found_block_open_four = True

        if found_win:
            return "Win", win
        elif found_block_win:
            return "BlockWin", block_win
        elif found_open_four:
            return "OpenFour", open_four
        elif found_block_open_four:
            return "BlockOpenFour", block_open_four
        else:
            return "Random", moves








           
    def gogui_rules_game_id_cmd(self, args):
        self.respond("Gomoku")

    def gogui_rules_board_size_cmd(self, args):
        self.respond(str(self.board.size))

    def gogui_rules_legal_moves_cmd(self, args):
        if self.board.detect_five_in_a_row() != EMPTY:
            self.respond("")
            return
        empty = self.board.get_empty_points()
        output = []
        for move in empty:
            move_coord = point_to_coord(move, self.board.size)
            output.append(format_point(move_coord))
        output.sort()
        output_str = ""
        for i in output:
            output_str = output_str + i + " "
        self.respond(output_str.lower())
        return

    def gogui_rules_side_to_move_cmd(self, args):
        color = "black" if self.board.current_player == BLACK else "white"
        self.respond(color)

    def gogui_rules_board_cmd(self, args):
        size = self.board.size
        str = ''
        for row in range(size-1, -1, -1):
            start = self.board.row_start(row + 1)
            for i in range(size):
                #str += '.'
                point = self.board.board[start + i]
                if point == BLACK:
                    str += 'X'
                elif point == WHITE:
                    str += 'O'
                elif point == EMPTY:
                    str += '.'
                else:
                    assert False
            str += '\n'
        self.respond(str)

    def gogui_rules_final_result_cmd(self, args):
        if self.board.get_empty_points().size == 0:
            self.respond("draw")
            return
        result = self.board.detect_five_in_a_row()
        if result == BLACK:
            self.respond("black")
        elif result == WHITE:
            self.respond("white")
        else:
            self.respond("unknown")

    def gogui_analyze_cmd(self, args):
        self.respond("pstring/Legal Moves For ToPlay/gogui-rules_legal_moves\n"
                     "pstring/Side to Play/gogui-rules_side_to_move\n"
                     "pstring/Final Result/gogui-rules_final_result\n"
                     "pstring/Board Size/gogui-rules_board_size\n"
                     "pstring/Rules GameID/gogui-rules_game_id\n"
                     "pstring/Show Board/gogui-rules_board\n"
                     )

def point_to_coord(point, boardsize):
    """
    Transform point given as board array index
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)


def format_point(move):
    """
    Return move coordinates as a string such as 'A1', or 'PASS'.
    """
    assert MAXSIZE <= 25
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if move == PASS:
        return "PASS"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1] + str(row)


def move_to_coord(point_str, board_size):
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return PASS
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            raise ValueError
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            raise ValueError
    except (IndexError, ValueError):
        raise ValueError("invalid point: '{}'".format(s))
    if not (col <= board_size and row <= board_size):
        raise ValueError("\"{}\" wrong coordinate".format(s))
    return row, col


def color_to_int(c):
    """convert character to the appropriate integer code"""
    color_to_int = {"b": BLACK, "w": WHITE, "e": EMPTY, "BORDER": BORDER}

    try:
        return color_to_int[c]
    except:
        raise KeyError("\"{}\" wrong color".format(c))


