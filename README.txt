Social Map

created in Python 3.10
using imported libraries: NumPy, TKinter, Pandas, Networkx, and matplotlib

Copyright (c) 2022, Will Neely

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Credit to Zach Carter for the idea and inspiration

===HELP===

==========
What It Is
==========

Social Map is an application designed for creating simple social network graphs. Originally conceived as a way of mapping influence via correspondance, it can be safely applied to any network with single-dimensional weighted relationships.

=============
How To Use It
=============

You will need a two-dimensional spreadsheet (in .xlsx file format) containing the names of your nodes and weight of influence as measured in integers. For example:

       Alice Bob   Carl  Donna
Alice  0     2     3     0
Bob    4     0     1     3
Carl   0     4     0     2
Donna  3     1     3     0

Make sure you save this spreadsheet to the same directory as the Social Map application file. When you launch the application, simply enter the name of your spreadsheet file into the "Source File" box and click "Create Network Graph" to see your graph.

From there you can manipulate your graph zoom, pan, and stretch, and save your graph to an image file.

**NOTE** Your .xlsx spreadsheet is the only component required to create your network graph. Every other parameter and piece of information will revert to default settings if left empty.

===============
Data Parameters
===============

-Graph Title-
(text)
The displayed title of your network graph. Optional, will not display if left blank.

-Source File-
(text)
The .xlsx spreadsheet from which you generate your graph. Please ensure that it is formatted correctly and contains no extraneous data, otherwise unpredictable results may occur. Required.

-Minimum Edge Threshold-
(integer from 1 to 1000)
The level at which your data is factored into the graph. Measurements below this threshold will not be displayed and will not affect the graph layout. Optional, will default to 1.

==================
Display Parameters
==================

-Node Display Size-
(integer from 1000 to 5000)
The size of your nodes. Optional, will default to 2000.

-Node Transparency-
(integer from 0 to 100)
The transparency of each node as measured in percents. Useful for better seeing the various connections of edge to node. Optional, will default to 40.

-Font Size-
(integer from 6 to 64)
The size of each node's text label. Optional, will default to 8.

-Edge Width Factor-
(decimal number from 1.1 to 4.0)
The logarithmic base for determining the display width of the edges, based on the measurement of each edge. The lower the number, the wider the edge grows as its measurement increases. Optional, will default to 2.1.

=================
Layout Parameters
=================

-Centrality Algorithm-
The formula used for determining which nodes will be explicitly positioned in the center of the graph:
   -Betweenness (default): Weights nodes based on the fraction of all-pairs shortest paths that pass through the node.
   -Load: Weights nodes based on the fraction of all shortest paths that pass through the node.
   -Eigenvector: Weights nodes based on the centrality of its neighboring nodes.
   -None: No nodes will be explicitly centered.

-Explicitly Positioned Central Nodes-
(integer from 0 to 4)
The maximum number of nodes positioned at the center of the graph based on the selected Centrality Algorithm. Setting this parameter to 0 OR selected an algorithm of None will result in no nodes being explicitly centered. Optional, will default to 0.

**NOTES**
   -Nodes greater than one Standard Deviation below the node with the highest centrality measure (according to the selected algorithm) will not be explicitly centered.
   -Only the Fruchterman-Reingold layout allows for explicit centering of multiple nodes; the other layouts will only center the single node with the highest centrality measure.

-Graph Layout-
The layout algorithm for the graph based on edge weights:
   -Kamada-Kawai: Positions nodes using the Kamada-Kawai path-length cost-function.
   -Fruchterman-Reingold: Positions nodes using the Fruchterman-Reingold force-directed algorithm.
   -Spectral: Position nodes using eigenvectors of graph Laplacian.
   -Spiral: Position nodes in an expanding spiral pattern.
	