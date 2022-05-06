from tkinter import *
from tk_html_widgets import *
import plotly.express as px

root = Tk()
root.geometry("700x500")



map = ""
with open("MapNoData.html", "r") as f:
    map = f.read()

print(map)
html_content = "tttttetest" + map

body = HTMLLabel(root, html = html_content)
body.place(x = 20, y = 20, width = 600, height = 600)

root.mainloop()

"""
fig = px.scatter_geo({}, 
                     scope='world',
                     title='Affichage des morts et des naissances')

fig.update_layout(autosize=False, width=1000, height=1000)
fig.update(layout_coloraxis_showscale=False)

fig.write_html("./MapNoData.html")
"""