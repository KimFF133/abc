import tkinter as tk
from tkinter import messagebox
import time

# ---------- 我们自己实现的随机数生成器（LCG）----------
class LCG:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time_ns() % (2**31 - 1))
        self.modulus = 2**31 - 1
        self.multiplier = 1103515245
        self.increment = 12345
        self.state = seed

    def next(self):
        self.state = (self.multiplier * self.state + self.increment) % self.modulus
        return self.state

    def randint(self, low, high):
        return low + self.next() % (high - low + 1)


# ---------- 游戏逻辑 ----------
class TreasureGame:
    def __init__(self, size=5, rng=None):
        self.size = size
        self.rng = rng if rng else LCG()
        self.reset()

    def reset(self):
        self.treasure_row = self.rng.randint(0, self.size-1)
        self.treasure_col = self.rng.randint(0, self.size-1)
        self.guesses = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.steps = 0
        self.game_over = False

    def manhattan_distance(self, row, col):
        return abs(row - self.treasure_row) + abs(col - self.treasure_col)

    def guess(self, row, col):
        if self.game_over:
            return False, -1, "游戏已结束，请重新开始"
        if self.guesses[row][col] is not None:
            return False, -1, "已经猜过这个格子了"
        self.steps += 1
        if row == self.treasure_row and col == self.treasure_col:
            self.guesses[row][col] = True
            self.game_over = True
            return True, 0, ""
        else:
            self.guesses[row][col] = False
            dist = self.manhattan_distance(row, col)
            return False, dist, ""

    def get_hint(self, dist):
        if dist == 0:
            return "🔥 烫到啦！就是这里！"
        elif dist == 1:
            return "🥵 非常热！就在隔壁"
        elif dist == 2:
            return "😅 有点热"
        elif dist == 3:
            return "😐 温温的"
        else:
            return "❄️ 很冷"


# ---------- 图形界面 ----------
class TreasureGUI:
    def __init__(self, master, size=5):
        self.master = master
        self.size = size
        self.master.title("寻宝游戏 - 使用自己的随机数")

        # 初始化游戏引擎
        seed = int(time.time_ns() % (2**31 - 1))
        rng = LCG(seed)
        self.game = TreasureGame(size, rng)

        # 存储按钮
        self.buttons = [[None for _ in range(size)] for _ in range(size)]

        # 主框架
        main_frame = tk.Frame(master)
        main_frame.pack(padx=10, pady=10)

        # 左侧网格
        grid_frame = tk.Frame(main_frame)
        grid_frame.pack(side=tk.LEFT, padx=10)

        for r in range(size):
            for c in range(size):
                btn = tk.Button(grid_frame, text="?", width=4, height=2,
                                font=("Arial", 16),
                                command=lambda row=r, col=c: self.on_click(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn

        # 右侧信息面板
        info_frame = tk.Frame(main_frame)
        info_frame.pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        # 步数
        self.steps_label = tk.Label(info_frame, text="步数: 0", font=("Arial", 12))
        self.steps_label.pack(pady=5)

        # 动态提示
        self.hint_label = tk.Label(info_frame, text="点击格子开始", font=("Arial", 12),
                                   wraplength=150, justify=tk.LEFT)
        self.hint_label.pack(pady=5)

        # 重新开始按钮
        self.reset_btn = tk.Button(info_frame, text="重新开始", command=self.reset_game,
                                   font=("Arial", 12), bg="lightgray")
        self.reset_btn.pack(pady=10)

        # ---------- 游戏规则区域（新增） ----------
        rule_text = """
游戏规则：
1. 宝藏随机藏在5×5格子中
2. 点击格子猜测宝藏位置
3. 右侧提示会告诉你“冷热”程度（曼哈顿距离）
4. 越近提示越热，直到找到💎
5. 每步计数，最后看谁步数少
6. 点击“重新开始”新的一局
        """
        rule_label = tk.Label(info_frame, text=rule_text, font=("Arial", 9),
                              justify=tk.LEFT, wraplength=160, bg="#f0f0f0",
                              relief=tk.GROOVE, padx=5, pady=5)
        rule_label.pack(pady=10, fill=tk.BOTH)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("游戏进行中...")
        status_bar = tk.Label(master, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_board(self):
        for r in range(self.size):
            for c in range(self.size):
                state = self.game.guesses[r][c]
                if state is True:
                    self.buttons[r][c].config(text="💎", state=tk.DISABLED, bg="gold")
                elif state is False:
                    self.buttons[r][c].config(text="❌", state=tk.DISABLED, bg="lightgray")
                else:
                    self.buttons[r][c].config(text="?", state=tk.NORMAL, bg="SystemButtonFace")

    def on_click(self, row, col):
        if self.game.game_over:
            self.status_var.set("游戏已结束，请按「重新开始」")
            return

        hit, dist, err = self.game.guess(row, col)
        if err:
            self.status_var.set(err)
            return

        self.update_board()
        self.steps_label.config(text=f"步数: {self.game.steps}")

        if hit:
            self.status_var.set(f"🎉 恭喜！用了 {self.game.steps} 步找到宝藏！")
            messagebox.showinfo("胜利", f"你用了 {self.game.steps} 步找到了宝藏！\n点击「重新开始」继续挑战。")
            for r in range(self.size):
                for c in range(self.size):
                    if self.game.guesses[r][c] is None:
                        self.buttons[r][c].config(state=tk.DISABLED)
        else:
            hint = self.game.get_hint(dist)
            self.hint_label.config(text=f"提示：{hint}\n距离: {dist}")
            self.status_var.set(f"猜测 ({row},{col}) 未中，{hint}")

    def reset_game(self):
        self.game.reset()
        self.update_board()
        self.steps_label.config(text="步数: 0")
        self.hint_label.config(text="新游戏！点击格子开始")
        self.status_var.set("游戏已重置，继续寻宝吧")
        for r in range(self.size):
            for c in range(self.size):
                self.buttons[r][c].config(state=tk.NORMAL)


# ---------- 运行 ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = TreasureGUI(root, size=5)
    root.mainloop()