#!/usr/bin/env python3

# SOCIAL MAP - A social networking data visualization

__author__      =   'Will Neely'
__copyright__   =   """Copyright 2022, Will Neely

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
__version__     =   '1.0'

from tkinter import *
from tkinter import ttk
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy
import math

class SocialMap:
    def __init__(self, defaults, **params):

        for p in params:
            setattr(self, p, params[p])

        for d in defaults:
            if not hasattr(self, d):
                setattr(self, d, defaults[d])

        try:
            letters = pd.read_excel(self.source_file + '.xlsx')
            letter_melt = letters.melt(id_vars=['Name'], var_name='Recipient', value_name='Letters')

            G = (nx.from_pandas_edgelist(letter_melt,
                                        source='Name',
                                        target='Recipient',
                                        edge_attr=['Letters'],
                                        create_using=nx.Graph()) if self.graph_directional == False else nx.from_pandas_edgelist(letter_melt,
                                        source='Name',
                                        target='Recipient',
                                        edge_attr=['Letters'],
                                        create_using=nx.DiGraph()))

            # dump empty values

            empty_edges = []

            for e in G.edges(data=True):
                if self.count_letters(e[2]['Letters']) < self.display_threshold:
                    empty_edges.append([e[0], e[1]])

            for e in empty_edges:
                G.remove_edge(e[0], e[1])

            #init graph params

            graph_params = {}
            if self.layout_select not in [nx.spiral_layout]:
                graph_params = graph_params | {'weight': 'Letters'}

            #find and set center nodes based on selected centrality

            if self.centrality_select:

                try:
                    center_dict = self.centrality_select(G)
                except:
                    center_dict = nx.betweenness_centrality(G)

                center_std = np.std(list(center_dict.values()))

                fixed_pos = {}

                if self.centrality_nodes > 0:
                    while len(fixed_pos) < self.centrality_nodes:
                        center = max(center_dict, key=center_dict.get)      
                        fixed_pos[center] = center_dict[center]
                        center_dict.pop(center)
                        if abs(fixed_pos[max(fixed_pos, key=fixed_pos.get)] - center_dict[max(center_dict, key=center_dict.get)]) > center_std:
                            break
                    
                    center = max(fixed_pos, key=fixed_pos.get)
                    highest_weight = fixed_pos[center]
                
                    angle = 0
                    for p in fixed_pos:
                        d = center_std + math.sqrt(highest_weight - fixed_pos[p]) / center_std 
                        fixed_pos[p] = ((math.cos(angle * 360 / len(fixed_pos) * math.pi / 180) * d), (math.sin(angle * 360 / len(fixed_pos) * math.pi / 180) * d))

                        angle += 1

                    fixed_nodes = fixed_pos.keys()

                # Select centrality layout vars

                if len(fixed_pos) > 0:
                    if self.layout_select in [nx.spiral_layout, nx.kamada_kawai_layout, nx.spectral_layout]:
                        graph_params = graph_params | {'center': fixed_pos[center]}
                    else:
                        graph_params = graph_params | {'pos': fixed_pos, 'fixed': fixed_nodes}

            #create pos from layout and centrality selections

            pos = self.layout_select(G, scale=self.graph_scale, dim=self.graph_dimensions, **graph_params)

            for e in G.edges(data=True):
                if self.count_letters(e[2]['Letters']) >= self.display_threshold:
                    width = max(1, int(math.log(self.count_letters(e[2]['Letters']), self.edge_weight_factor)))
                    nx.draw_networkx_edges(G, pos, edgelist=[e], width=width)

            self.node_transparency = (100 - self.node_transparency) / 100 

            nx.draw_networkx_nodes(G, pos, node_size=self.graph_node_size, node_color=self.graph_node_color, linewidths=self.graph_node_border, edgecolors='black', alpha=self.node_transparency)
            nx.draw_networkx_labels(G, pos, font_size=self.font_size)

            ax = plt.gca()
            ax.margins(0.20)
            plt.axis("off")
            plt.title(self.graph_title)
            plt.show()
        
        except:
            return

        # helper functions

    def count_letters(self, x):
        try:
            return int(x)
        except:
            return 0

class EntryParameter:
    def __init__(self, index, frame, var_name, label, minimum, maximum, float_allowed=False):
        self.root = frame
        self.minimum = minimum
        self.maximum = maximum
        self.float_allowed = float_allowed
        self.var_name = var_name
        self.value = { var_name: StringVar() }
        valid = self.root.register(self.validate)
        invalid = self.root.register(self.invalid)

        self.frame = ttk.Frame(frame, padding='1 1 1 1')
        self.frame.grid(columnspan=2, column=(index % 2) * 2, row=index // 2, sticky=(W, N))
        ttk.Label(self.frame, text=(f'{label} ({minimum} - {maximum})')).grid(columnspan=2, column=0, row=0)
       
        self.entry = ttk.Entry(self.frame, textvariable=self.value[var_name], width=20, validate='focus', invalidcommand=(invalid), validatecommand=(valid, '%P'))
        self.entry.grid(columnspan=2, column=0, row=1, sticky=(W, N))

    def validate(self, P):
        if self.float_allowed:
            try:
                info = float(P)
            except:
                return False 
        else:
            if not P.isnumeric():
                return False
            else:
                info = int(P)
        if info < self.minimum or info > self.maximum:
            return False
        return True

    def invalid(self):
        self.value[self.var_name].set('')

class MapCreator:
    def __init__(self, help_text='default_help', about_text='default'):

        self.root = Tk()
        self.root.title(f'Social Map v{__version__}')

        self.help_text = help_text
        self.about_text = about_text

        mainframe = ttk.Frame(self.root, padding='2 2 12 8', height=800, width=500)
        mainframe.grid(column=0, row=0, sticky=(N, E, S, W))
        self.graph_title = StringVar()
        self.source_file = StringVar()
        info_window = self.root.register(self.show_info)

        #sub-frames, assistance menus

        first_frame = ttk.Frame(mainframe, padding='4 4 4 4', height=200, width=300, relief='groove')
        first_frame.grid(columnspan=4, column=0, row=1, sticky=(W, N, E))
        second_frame = ttk.Frame(mainframe, padding='4 4 4 4', height=400, width=300, relief='groove')
        second_frame.grid(columnspan=4, column=0, row=2, sticky=(W, N, E))
        third_frame = ttk.Frame(mainframe, padding='4 4 4 4', height=300, width=300, relief='groove')
        third_frame.grid(columnspan=4, column=0, row=3, sticky=(W, N, E))

        self.helpframe = ttk.Frame(self.root, padding='12 2 2 8', height=800, width=300, relief='sunken')
        self.help = Text(self.helpframe, height=23, width=50, padx=4, wrap=WORD)
        self.help.grid(column=0, row=0, sticky=(W, N, E))
        self.help.insert('end', help_text)
        self.help.config(state=DISABLED)
        ttk.Button(self.helpframe, text='Close', command=self.hide_info).grid(column=0, row=1, sticky=(E, S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        program_title = ttk.Label(mainframe, text=f'Social Map v{__version__}')
        program_title.grid(column=0, columnspan=2, row=0, sticky=(W, N))

        help_button = ttk.Button(mainframe, text='Help', command=(info_window, self.help_text))
        help_button.grid(column=3, row=0, sticky=(N, E))

        about_button = ttk.Button(mainframe, text='About', command=(info_window, self.about_text))
        about_button.grid(column=2, row=0, sticky=(N, E))

        self.params_storage=[]

        # First frame - data params

        ttk.Label(first_frame, text='Graph Title').grid(columnspan=4, row=0, sticky=(W, N, E))
        self.graph_title_entry = ttk.Entry(first_frame, textvariable=self.graph_title, width=40)
        self.graph_title_entry.grid(columnspan=4, row=1, sticky=(W, N, E))

        ttk.Label(first_frame, text='Source File').grid(columnspan=4, row=2, sticky=(W, N, E))
        self.graph_title_entry = ttk.Entry(first_frame, textvariable=self.source_file, width=30)
        self.graph_title_entry.grid(columnspan=3, row=3, sticky=(W, N, E))
        ttk.Label(first_frame, text='.xlsx').grid(column=3, row=3, sticky=(W))

        self.params_storage.append(EntryParameter(8, first_frame, 'display_threshold', 'Minimum Edge Threshold', 1, 1000))

        # Second Frame - graphical params

        params_source = [
            ['graph_node_size', 'Node Display Size', 1000, 5000],
            ['node_transparency', 'Node Transparency', 0, 100],
            ['font_size', 'Font Size', 6, 64],
            ['edge_weight_factor', 'Edge Width Factor', 1.1, 4.0, True],
        ]

        for i in range(len(params_source)):
            self.params_storage.append(EntryParameter(i, second_frame, *params_source[i]))

        # Third frame - layout params

        ttk.Label(third_frame, text='Centrality Algorithm').grid(columnspan=2, row=0, column=0, sticky=(W, N))
        self.centrality_select = StringVar()
        self.centrality_options = {'Betweenness': nx.betweenness_centrality, 'Load': nx.load_centrality, 'Eigenvector': nx.eigenvector_centrality, 'None': None}
        self.centrality_keys = list(self.centrality_options.keys()) 
        self.centrality_menu = ttk.OptionMenu(third_frame, self.centrality_select, self.centrality_keys[0], *self.centrality_keys)
        self.centrality_menu.grid(columnspan=2, row=1, column=0, sticky=(W, N, E))

        self.params_storage.append(EntryParameter(4, third_frame, 'centrality_nodes', 'Explicitly Positioned Central Nodes', 0, 4))

        ttk.Label(third_frame, text='Graph Layout').grid(columnspan=2, row=3, column=0, sticky=(W, N))
        self.layout_select = StringVar()
        self.layout_options = {'Kamada-Kawai': nx.kamada_kawai_layout, 'Fruchterman-Reingold': nx.fruchterman_reingold_layout,
                                'Spectral': nx.spectral_layout, 'Spiral': nx.spiral_layout}
        self.layout_keys = list(self.layout_options.keys())     
        self.layout_menu = ttk.OptionMenu(third_frame, self.layout_select, self.layout_keys[0], *self.layout_keys)
        self.layout_menu.grid(columnspan=2, row=4, column=0, sticky=(W, N, E))

        # GO button

        create_button = ttk.Button(mainframe, text='Create Network Graph', command=self.create_social_map)
        create_button.grid(columnspan=4, column=0, row=4, sticky=(W, N, E, S))

        # Begin loop

        self.root.mainloop()
    
    def create_social_map(self):

        # Parameters

        defaults = {
            'graph_title': 'Social Map',
            'graph_scale': 100,
            'graph_dimensions': 2,
            'edge_weight_factor': 2.1,
            'graph_node_color': 'white',
            'graph_node_border': 1,
            'graph_node_size': 2000,
            'node_transparency': 40,
            'font_size': 8,
            'source_file': 'test-data',
            'display_threshold': 1,
            'graph_directional': False,
            'centrality_select': nx.betweenness_centrality,
            'layout_select': nx.spring_layout,
            'centrality_nodes': 0,
        }

        params = {}

        for p in self.params_storage:
            if p.value[p.var_name].get() != '':
                params[p.var_name] = int(p.value[p.var_name].get()) if not p.float_allowed else float(p.value[p.var_name].get())

        try:
            test_data = pd.read_excel(self.source_file.get() + '.xlsx')

            params['graph_title'] = self.graph_title.get()
            params['source_file'] = self.source_file.get()
            params['centrality_select'] = self.centrality_options[self.centrality_select.get()]
            params['layout_select'] = self.layout_options[self.layout_select.get()]

            SocialMap(defaults, **params)

        except:
            self.source_file.set('Please use a valid filename.')

    def show_info(self, info):
        self.helpframe.grid_remove()
        self.help.config(state=NORMAL)
        self.help.delete('1.0', 'end')
        self.help.insert('end', info)
        self.help.config(state=DISABLED)
        self.helpframe.grid(column=1, row=0, sticky=(N, E, S, W))

    def hide_info(self):
        self.helpframe.grid_remove()

# Main Program
try:
    info_file = open('README.txt', 'r')
    info_text = info_file.readlines()
    info_file.close()

    about_text = ''.join(info_text[:info_text.index('===HELP===\n')])
    help_text = ''.join(info_text[info_text.index('===HELP===\n') + 2:])

except:
   about_text = 'README.txt Not Found!'
   help_text =  'README.txt Not Found!'

MapCreator(help_text, about_text)