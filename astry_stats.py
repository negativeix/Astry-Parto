import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast

# === โหลดข้อมูล CSV ===
df = pd.read_csv("game_data.csv")
df.rename(columns={"Power-ups Collected": "Power-ups"}, inplace=True)
df['Accuracy'] = df['Player Hit'] / df['Total Bullets Fired']

# === ฟังก์ชันวาดกราฟ ===
def draw_graph(option):
    fig.clear()
    ax = fig.add_subplot(111)

    if option == "Dash vs Time Played":
        ax.scatter(df['Time Played'], df['Dash Usage'], color='blue')
        ax.set_title("Dash Usage vs Time Played")
        ax.set_xlabel("Time Played (sec)")
        ax.set_ylabel("Dash Usage")

    elif option == "Bullet Fired vs Accuracy":
        ax.plot(df['Total Bullets Fired'], df['Accuracy'], marker='o', color='purple')
        ax.set_title("Bullet Fired vs Accuracy")
        ax.set_xlabel("Bullets Fired")
        ax.set_ylabel("Accuracy")

    elif option == "Power-up Frequency":
        if 'Power-ups' not in df.columns:
            ax.text(0.5, 0.5, "No 'Power-ups' column found", ha='center', va='center')
        else:
            try:
                power_lists = df['Power-ups'].dropna().apply(ast.literal_eval)
                total_counts = {}
                for d in power_lists:
                    for k, v in d.items():
                        total_counts[k] = total_counts.get(k, 0) + v
                num_rows = len(power_lists)
                avg_counts = {k: v / num_rows for k, v in total_counts.items()}

                color_map = {
                    'laser': 'red',
                    'spread': 'green',
                    'reverse': 'gray',
                    'shield': 'skyblue'
                }
                colors = [color_map.get(k, 'black') for k in avg_counts.keys()]

                ax.bar(avg_counts.keys(), avg_counts.values(), color=colors)
                ax.set_title("Average Power-ups Collected per Type")
                ax.set_ylabel("Average Collected")
            except Exception as e:
                ax.text(0.5, 0.5, f"Error reading power-ups:\n{e}", ha='center', va='center')

    canvas.draw()

# === ฟังก์ชันคำนวณค่าสถิติ ===
def draw_stats(option):
    output.delete(1.0, tk.END)  # ล้างข้อความเก่า

    if option == "Accuracy":
        mean = df['Accuracy'].mean()
        std = df['Accuracy'].std()
        output.insert(tk.END, f"Accuracy\nMean: {mean:.3f}\nStandard Deviation: {std:.3f}")

    elif option == "Time Played":
        mean = df['Time Played'].mean()
        output.insert(tk.END, f"Time Played\nMean: {mean:.3f} sec")

    elif option == "Bullets Fired":
        total = df['Total Bullets Fired'].sum()
        mean = df['Total Bullets Fired'].mean()
        output.insert(tk.END, f"Bullets Fired\nTotal: {total}\nMean: {mean:.3f}")

    elif option == "Obstacle Destroyed":
        total = df['Obstacles Destroyed'].sum()
        mean = df['Obstacles Destroyed'].mean()
        output.insert(tk.END, f"Obstacles Destroyed\nTotal: {total}\nMean: {mean:.3f}")

    elif option == "Dash Usage":
        mean = df['Dash Usage'].mean()
        perc90 = np.percentile(df['Dash Usage'], 90)
        output.insert(tk.END, f"Dash Usage\nMean: {mean:.3f}\n90th Percentile: {perc90:.3f}")

# === GUI Layout ===
root = tk.Tk()
root.title("Game Analytics Dashboard")

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# ซ้าย: กราฟ
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=10)

fig = plt.Figure(figsize=(7, 5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas.get_tk_widget().pack()

graph_options = ["Dash vs Time Played", "Bullet Fired vs Accuracy", "Power-up Frequency"]
graph_var = tk.StringVar()
graph_var.set(graph_options[0])

dropdown_graph = ttk.Combobox(left_frame, textvariable=graph_var, values=graph_options, state="readonly")
dropdown_graph.pack(pady=5)

btn_graph = ttk.Button(left_frame, text="Show Graph", command=lambda: draw_graph(graph_var.get()))
btn_graph.pack(pady=5)

# ขวา: สถิติ
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=10, sticky='n')

stat_options = ["Accuracy", "Time Played", "Bullets Fired", "Obstacle Destroyed", "Dash Usage"]
stat_var = tk.StringVar()
stat_var.set(stat_options[0])

dropdown_stat = ttk.Combobox(right_frame, textvariable=stat_var, values=stat_options, state="readonly")
dropdown_stat.pack(pady=5)

btn_stat = ttk.Button(right_frame, text="Show Stats", command=lambda: draw_stats(stat_var.get()))
btn_stat.pack(pady=5)

output = tk.Text(right_frame, height=10, width=35)
output.pack()

# เริ่มต้น
draw_graph(graph_options[0])
draw_stats(stat_options[0])

root.mainloop()
