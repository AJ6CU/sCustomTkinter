left = sCTkScrollableFrame(root)
left.pack(side="left", fill="both", expand=True, padx=5, pady=5)
right = sCTkScrollableFrame(root)
right.pack(side="right", fill="both", expand=True, padx=5, pady=5)

for i in range(40):
    sCTkLabelSecondary(left, text=f"LEFT {i}").pack()
    sCTkLabelSecondary(right, text=f"RIGHT {i}").pack()

# Both start enabled. Confirm both scroll before the timer fires.
root.after(5000, lambda: left.disable_scroll())
root.mainloop()