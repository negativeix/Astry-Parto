import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast


df = pd.read_csv("game_data.csv")
df['Accuracy'] = df['Player Hit'] / df['Total Bullets Fired']


if 'Power-ups Collected' in df.columns:
    df['Power-ups'] = df['Power-ups Collected'].apply(ast.literal_eval)


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
        try:
            power_lists = df['Power-ups'].dropna()
            total_counts = {'laser': 0, 'spread': 0, 'reverse': 0, 'shield': 0}
            for d in power_lists:
                for k, v in d.items():
                    total_counts[k] = total_counts.get(k, 0) + v

            num_rows = len(power_lists)
            avg_counts = {k: v / num_rows for k, v in total_counts.items()}

            colors = {
                'laser': 'red',
                'spread': 'green',
                'reverse': 'gray',
                'shield': 'skyblue'
            }
            ax.bar(avg_counts.keys(), avg_counts.values(), color=[colors[k] for k in avg_counts.keys()])
            ax.set_title("Average Power-ups Collected per Type")
            ax.set_ylabel("Average Collected")

        except Exception as e:
            ax.text(0.5, 0.5, f"Error reading power-ups:\n{e}", ha='center', va='center')

    canvas.draw()

def draw_stats(option):
    for i in stats_table.get_children():
        stats_table.delete(i)

    if option == "Accuracy":
        mean = df['Accuracy'].mean()
        std = df['Accuracy'].std()
        stats_table.insert('', 'end', values=("Mean", f"{mean:.3f}"))
        stats_table.insert('', 'end', values=("Standard Deviation", f"{std:.3f}"))

    elif option == "Time Played":
        mean = df['Time Played'].mean()
        stats_table.insert('', 'end', values=("Mean", f"{mean:.3f} sec"))

    elif option == "Bullets Fired":
        total = df['Total Bullets Fired'].sum()
        mean = df['Total Bullets Fired'].mean()
        stats_table.insert('', 'end', values=("Total", f"{total}"))
        stats_table.insert('', 'end', values=("Mean", f"{mean:.3f}"))

    elif option == "Obstacle Destroyed":
        total = df['Obstacles Destroyed'].sum()
        mean = df['Obstacles Destroyed'].mean()
        stats_table.insert('', 'end', values=("Total", f"{total}"))
        stats_table.insert('', 'end', values=("Mean", f"{mean:.3f}"))

    elif option == "Dash Usage":
        mean = df['Dash Usage'].mean()
        perc90 = np.percentile(df['Dash Usage'], 90)
        stats_table.insert('', 'end', values=("Mean", f"{mean:.3f}"))
        stats_table.insert('', 'end', values=("90th Percentile", f"{perc90:.3f}"))

root = tk.Tk()
root.title("Game Analytics Dashboard")

main_frame = ttk.Frame(root)
main_frame.pack(padx=10, pady=10)

left_frame = ttk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=10)

fig = plt.Figure(figsize=(6, 5), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=left_frame)
canvas.get_tk_widget().pack()

graph_options = ["Dash vs Time Played", "Bullet Fired vs Accuracy", "Power-up Frequency"]
var_graph = tk.StringVar()
var_graph.set(graph_options[0])

dropdown_graph = ttk.Combobox(left_frame, textvariable=var_graph, values=graph_options, state="readonly")
dropdown_graph.pack(pady=5)

graph_btn = ttk.Button(left_frame, text="Show Graph", command=lambda: draw_graph(var_graph.get()))
graph_btn.pack()

right_frame = ttk.Frame(main_frame)
right_frame.grid(row=0, column=1, padx=10)

stat_options = ["Accuracy", "Time Played", "Bullets Fired", "Obstacle Destroyed", "Dash Usage"]
var_stat = tk.StringVar()
var_stat.set(stat_options[0])

dropdown_stat = ttk.Combobox(right_frame, textvariable=var_stat, values=stat_options, state="readonly")
dropdown_stat.pack(pady=5)

stat_btn = ttk.Button(right_frame, text="Show Stats", command=lambda: draw_stats(var_stat.get()))
stat_btn.pack(pady=5)

stats_table = ttk.Treeview(right_frame, columns=("Metric", "Value"), show="headings", height=6)
stats_table.heading("Metric", text="Metric")
stats_table.heading("Value", text="Value")
stats_table.column("Metric", width=150, anchor="center")
stats_table.column("Value", width=120, anchor="center")
stats_table.pack(pady=5)

draw_graph(graph_options[0])
draw_stats(stat_options[0])

root.mainloop()
