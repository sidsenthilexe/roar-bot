import matplotlib.pyplot as plt

class Plotter:

    def __init__(self, time_steps, targets, currents, name, target_label, current_label, fig_size, y_lim, limit):
        self.time_steps = time_steps
        self.targets = targets
        self.currents = currents
        self.y_lim = y_lim
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(fig_size[0], fig_size[1]))
        self.ax.set_ylim(y_lim[0], y_lim[1])
        self.step_counter = 0
        self.line_target, = self.ax.plot([], [], label=target_label, color="r", linestyle="--")
        self.line_current, = self.ax.plot([], [], label=current_label, color="b")
        self.ax.legend(loc="upper right")
        self.ax.grid(True)
        self.plots_out = 1
        self.limit = limit
        self.name = name

    def generate(self, target, current):
        #if (0 <= self.step_counter <= 500): print("Plotting " + self.name + " at step " + str(self.step_counter))
        self.step_counter += 1
        self.time_steps.append(self.step_counter)
        self.targets.append(target)
        self.currents.append(current)
        self.line_target.set_data(self.time_steps, self.targets)
        self.line_current.set_data(self.time_steps, self.currents)
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.set_ylim(top=self.y_lim[1], bottom=self.y_lim[0])
        if self.step_counter % self.limit == 0:
            name = "plot" + self.name + str(self.plots_out)
            self.fig.savefig(name, dpi=300, bbox_inches='tight')
            self.plots_out += 1
