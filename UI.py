'''
Created on May 21, 2020

@author: Gosha
'''

import clipboard

import Actions
from Graph import Graph
from Parser import parse
from TK_Turtle_Canvas import TurtleCanvas
from Tree import Tree
import Tree as TreeM
import tkinter as tk

LaTeXFile = "/Users/gosha/Google Drive/Programming/EclipseProjects/IMPP4/output.txt"
htmlFile = "/Users/gosha/Google Drive/Programming/EclipseProjects/IMPP4/output_equation.html"
htmlTemplateFile = "/Users/gosha/Google Drive/Programming/EclipseProjects/IMPP4/html_output_equation_template.html"

latexMode = "html"


class UI():

    def __init__(self):
        self.turtleCanvases = {}

        self.window = tk.Tk()
        self.window.title("MultiMath")

        self.mainFrame = tk.Frame(self.window)
        self.mainFrame.grid(row = 0, column = 0)
        for i in range(3):
            self.mainFrame.rowconfigure(i, weight = 1)
        for i in range(2):
            self.mainFrame.columnconfigure(i, weight = 1)

        notationOptions = ["Prefix", "Infix", "Postfix", "LaTeX", "HTML"]

        self.action = tk.StringVar(self.window)
        self.action.trace('w', self.changeAction)
        self.actionSelect = tk.OptionMenu(self.mainFrame, self.action, value = None)
        self.actionSelect.grid(row = 0, column = 0)

        self.actionSelect['menu'].delete(0, 'end')
        for category in Actions.categories:
            submenu = tk.Menu(self.mainFrame)

            for actionName in Actions.categories[category]:
                submenu.add_command(label = actionName, command = tk._setit(self.action, actionName))

            self.actionSelect['menu'].add_cascade(label = category, menu = submenu)

        self.notationVar = tk.StringVar(self.window)
        self.notationVar.trace('w', self.changeNotation)
        notationSelect = tk.OptionMenu(self.mainFrame, self.notationVar, *notationOptions)
        self.notationVar.set("Infix")
        notationSelect.grid(row = 0, column = 2)

        runButton = tk.Button(self.mainFrame, text = "Run", command = self.runCurrentAction)
        runButton.grid(row = 0, column = 1)

        copyOutputText = lambda: clipboard.copy(outputText["text"])

        self.outerOutputFrame = tk.Frame(self.mainFrame)

        outputCanvas = tk.Canvas(self.outerOutputFrame)
        outputScrollbar = tk.Scrollbar(self.outerOutputFrame, orient = tk.HORIZONTAL, command = outputCanvas.xview)
        outputScrollbar.pack(side = tk.BOTTOM)
        outputCanvas.pack()
        outputCanvas.config(xscrollcommand = outputScrollbar.set)

        outputFrame = tk.Frame(outputCanvas)
        outputFrame.grid(row = 0, column = 0, sticky = tk.EW)
        outputText = tk.Button(outputFrame, command = copyOutputText)
        outputText.grid(row = 0, column = 0, sticky = tk.EW)

        self.setOutputText = lambda text: outputText.config(text = text)

        outputText.bind(copyOutputText)

        self.action.set("Parse")

#       ══════════════════════════════════════════════════

        menubar = tk.Menu()

        NewMenu = tk.Menu()
        NewMenu.add_command(label = "New Turtle Canvas", command = self.newTurtleCanvas)
        NewMenu.add_command(label = "New Graph", command = self.newGraph)
        menubar.add_cascade(label = "New", menu = NewMenu)

        self.window.config(menu = menubar)

#       ══════════════════════════════════════════════════

        self.window.mainloop()

    def changeAction(self, *_):
        self.destroyAllArguments()
        requestedArguments = Actions.actions[self.action.get()].requestedArguments
        for requestedArgument in requestedArguments:
            Actions.arguments.append(UIArgument(requestedArgument, self))
        if(Actions.actions[self.action.get()].outputType == None):
            self.outerOutputFrame.grid_remove()
        else:
            self.outerOutputFrame.grid(row = 1 + len(Actions.arguments), column = 0, columnspan = 3, sticky = tk.EW)

    def runCurrentAction(self):
        actionFunc = Actions.actions[self.action.get()]
        actionFunc(self.setOutputText)

    def destroyAllArguments(self):
        for arg in Actions.arguments:
            arg.delete()
        Actions.arguments = []

    def changeNotation(self, *_):
        if(self.notationVar.get().lower() == "latex"):
            TreeM.notation = "latex"
            Actions.latexMode = "app"
        elif(self.notationVar.get().lower() == "html"):
            TreeM.notation = "latex"
            Actions.latexMode = "html"
        else:
            TreeM.notation = self.notationVar.get().lower()

    def newTurtleCanvas(self):
        TCid = max(list(self.turtleCanvases.keys()) + [-1]) + 1

        self.turtleCanvases[TCid] = TurtleCanvas(TCid)

    def newGraph(self):
        TCid = max(list(self.turtleCanvases.keys()) + [-1]) + 1

        self.turtleCanvases[TCid] = Graph(TCid)


class UIArgument():

    def __init__(self, args, UIObject):
        self.UIObject = UIObject

        if(len(args) == 2):
            self.text, self.argType = args
            self.default = None
        elif(len(args) == 3):
            self.text, self.argType, self.default = args

        row = len(Actions.arguments) + 1
        self.label = tk.Label(UIObject.mainFrame, text = self.text)
        self.label.grid(row = row, column = 0, sticky = tk.EW)

        self.interface = None

        self.get = lambda: self.argType(self.interface.get())

        if(self.argType == bool):
            self.var = tk.BooleanVar(UIObject.window)
            self.interface = tk.Checkbutton(UIObject.mainFrame, variable = self.var)
            self.get = lambda: self.var.get()
            if(self.default is True):
                self.interface.select()
            if(self.default is False):
                self.interface.deselect()
            self.interface.grid(row = row, column = 1)

        if(self.argType == str):
            self.interface = tk.Entry(UIObject.mainFrame)
            if(self.default != None):
                self.interface.insert(tk.END, self.default)
            self.interface.grid(row = row, column = 1)

        if(self.argType == Tree):
            self.interface = tk.Entry(UIObject.mainFrame)
            if(self.default != None):
                self.interface.insert(tk.END, self.default)
            self.interface.grid(row = row, column = 1)

            self.get = lambda: parse(self.interface.get())

        if(self.argType == float):

            def validate(value):
                if(value in ['', '-']):
                    return(True)

                try:
                    float(value)
                    return(True)
                except Exception:
                    return(False)

            reg = UIObject.window.register(validate)
            self.interface = tk.Entry(UIObject.mainFrame, validate = "key", validatecommand = (reg, '%P'))
            if(self.default != None):
                self.interface.insert(tk.END, str(self.default))
            self.interface.grid(row = row, column = 1)

        if(self.argType == int):

            def validate(value):
                if(value in ['', '-']):
                    return(True)

                try:
                    return(float(value) == int(value))
                except Exception:
                    return(False)

            reg = UIObject.window.register(validate)
            self.interface = tk.Entry(UIObject.mainFrame, validate = "key", validatecommand = (reg, '%P'))
            if(self.default != None):
                self.interface.insert(tk.END, str(self.default))
            self.interface.grid(row = row, column = 1)

        if(self.argType in (TurtleCanvas, Graph)):

            def validate(value):
                if(value in ['']):
                    return(True)

                try:
                    return(float(value) == int(value) and int(value) >= 0)
                except Exception:
                    return(False)

            reg = UIObject.window.register(validate)
            self.interface = tk.Entry(UIObject.mainFrame, validate = "key", validatecommand = (reg, '%P'))
            if(self.default != None):
                self.interface.insert(tk.END, str(self.default))
            self.interface.grid(row = row, column = 1)

            self.get = lambda: self.UIObject.turtleCanvases[int(self.interface.get())]

    def delete(self):
        self.label.destroy()
        self.interface.destroy()