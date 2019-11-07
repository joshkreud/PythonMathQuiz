"""Generate random Math formula and ask user to solve it
"""
from enum import Enum
import random
import time
import csv
import os
import pathlib
from datetime import datetime
import ast, operator

binOps = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod
}

def arithmeticEval (s):
    node = ast.parse(s, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return binOps[type(node.op)](_eval(node.left), _eval(node.right))
        else:
            raise Exception('Unsupported type {}'.format(node))

    return _eval(node.body)


def input_int(message: str) -> int:
    """Asks user input, validates for int

    Arguments:
        message {str} -- What to ask

    Returns:
        int -- user answer
    """
    while True:
        try:
            user_input = int(input(message))
        except ValueError:
            print("Not an integer! Try again.")
            continue
        else:
            return user_input


class EnuOperand(Enum):
    """Standard Math operations
    """

    Plus = "+"
    Minus = "-"
    Divide = "/"
    Multiply = "*"


def generate_math(operand: EnuOperand, max_val: int) -> dict:
    """Generates random simple math equation

    Arguments:
        operand {EnuOperand} -- Which operand to use
        max_val {int} -- Max int for leftVal and RightVal

    Returns:
        dict -- MathEquation for Game Class
    """
    right = random.randint(1, max_val)
    if operand == operand.Divide:
        left = int(random.randint(1, max_val) * right)
    else:
        left = random.randint(1, max_val)
    equation = str(left) + operand.value + str(right)
    result = arithmeticEval(equation)
    return {
        "Op": operand.value,
        "Left": left,
        "Right": right,
        "Result": result,
    }


def user_eval_math(equation: dict, show_correct: bool) -> (bool, str, str):
    """Lets the user evaluate a equation

    Arguments:
        equation {dict} -- [Equation Dict from Game Class]
        show_correct {bool} -- [print correct result, if input was False]

    Returns:
        ({bool} -- [CalcResult],
        {str} --[which val was left out],
        {str} -- [user answer]
        )
    """
    leaveout, leaveout_val = random.choice(
        [
            (x, y)
            for x, y in equation.items()
            if x in ["Left", "Right", "Result"]
        ]
    )
    equation[leaveout] = "X"
    user_answer = input_int(
        f'Calculate "X": {equation["Left"]} {equation["Op"]} '
        f'{equation["Right"]} = {equation["Result"]}: '
    )
    if user_answer == leaveout_val:
        return True, leaveout, user_answer

    if show_correct:
        print(f"Correct answer was: {leaveout_val}")
    return False, leaveout, user_answer


class Game:
    """A Class, that generates a simple Math equation and asks
        the user to solve it. Records the time taken in CSV file
    """

    def __init__(self, name: str, _id: str):
        self.name = name
        self._id = _id
        self.result_path = (
            pathlib.Path.cwd()
            / "Results"
            / f'Results_{_id}_{time.strftime("%Y%m%d-%H%M%S")}.csv'
        )

    def log_answer(self, answer: dict):
        """Logs the useranswer into CSV File

        Arguments:
            answer {dict} -- Answer Dict with all the info to be logged
        """
        folder_path = self.result_path.parents[0]
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

        resultexist = os.path.exists(self.result_path)
        with open(self.result_path, "a", newline="") as file:
            dict_writer = csv.DictWriter(file, answer.keys(), -999)
            if not resultexist:
                dict_writer.writeheader()
            dict_writer.writerow(answer)

    def play(self, difficulty: int):
        """Plays a math game, logs the answer into CSV File afterwards

        Arguments:
            difficulty {int} -- Maximum integer for left and right notation
        """
        my_calc = generate_math(random.choice(list(EnuOperand)), difficulty)
        my_calc["TimeBegin"] = datetime.utcnow().isoformat()
        my_calc["EqResult"], my_calc["LeftOut"], my_calc[
            "UserAnswer"
        ] = user_eval_math(my_calc, True)
        my_calc["TimeEnd"] = datetime.utcnow().isoformat()
        my_calc["EqNumber"] = i
        my_calc["Name"] = self.name
        self.log_answer(my_calc)


if __name__ == "__main__":
    USER = input("Please enter your name: ")
    MYGAME = Game(USER, "Local")
    for i in range(1, 20):
        MYGAME.play(12)
