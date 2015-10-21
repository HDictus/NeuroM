#!/usr/bin/env python
# Copyright (c) 2015, Ecole Polytechnique Federale de Lausanne, Blue Brain Project
# All rights reserved.
#
# This file is part of NeuroM <https://github.com/BlueBrain/NeuroM>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#     3. Neither the name of the copyright holder nor the names of
#        its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''Moprhology Dendrogram Functions Example'''

from neurom.view import common
from neurom.analysis.morphmath import segment_length
from neurom.core.tree import isegment, val_iter
from matplotlib.collections import LineCollection
from numpy import sin, cos, pi


def get_transformed_position(segment, segments_dict, y_length):
    '''Calculate Dendrogram Line Position
    '''

    start, end = segment

    start_node_id = start.value[-2]

    end_node_id = end.value[-2]

    # The parent node is connected with the child
    # line type:
    # 0 straight segment
    # 1 upward segment
    # -1 downward segment
    (x0, y0), line_type = segments_dict[start_node_id]

    # increase horizontal dendrogram length by segment length
    x1 = x0 + segment_length(list(val_iter(segment)))

    # if the parent node is visited for the first time
    # the dendrogram segment is drawn from below. If it
    # is visited twice it is drawn from above
    y1 = y0 + y_length[start_node_id] * line_type

    # reduce the vertical y for subsequent children
    y_length[end_node_id] = y_length[start_node_id] * (1. - 0.5 * abs(line_type))

    # horizontal segment
    segments = [[(x0, y1), (x1, y1)]]

    # vertical segment
    if line_type != 0:
        segments.extend([[(x0, y0), (x0, y1)]])

    # If the segment has children, the first child will be drawn
    # from below. If no children the child will be a straight segment
    segments_dict[end_node_id] = [(x1, y1), 1 - len(end.children)]

    # the second branch will have diff direction
    segments_dict[start_node_id][1] += 2

    return segments


def dendro_transform(tree_object):
    '''Extract Dendrogram Lines and Diameters from tree structure
    '''
    root_id = tree_object.value[-2]

    y_length = {root_id: 1.}

    segments_dict = {tree_object.value[-2]: [(0., 0.), 0.]}

    positions = []
    diameters = []

    for seg in isegment(tree_object):

        tr_pos = get_transformed_position(seg, segments_dict, y_length)

        # mean segment diameter
        seg_diam = seg[0].value[3] + seg[1].value[3]

        positions.extend(tr_pos)

        diameters.extend([seg_diam] * (len(tr_pos) / 2))

    return positions, diameters


def affine2D_transfrom(pos, a, b, c, d):
    '''Affine 2D transformation for the positions of the line collection
    '''

    for i, elements in enumerate(pos):
        for j, _ in enumerate(elements):

            x = pos[i][j][0]
            y = pos[i][j][1]

            x_prime = a * x + b * y
            y_prime = c * x + d * y

            pos[i][j] = (x_prime, y_prime)


def dendrogram(tree_object, show_diameters=False, new_fig=True,
               subplot=False, rotation='right', **kwargs):
    '''Generates the deondrogram of the input neurite

    Arguments:

        tree_object : input tree object

    Options:

        show_diameters : bool for showing mean segment diameters

        subplot : Default is False, which returns a matplotlib figure object. If True,
        returns a matplotlib axis object, for use as a subplot.

        rotation : angle in degrees of rotation of the dendrogram.

    Returns:

        figure_output : list
            [fig|ax, figdata, figtext]
            The first item is either a figure object (if subplot is False) or an
            axis object. The second item is an object containing the data used to
            generate the figure. The final item is text used in report generation
            as a figure legend. This text needs to be manually entered in each
            figure file.
    '''
    # get line segment positions and respective diameters
    positions, linewidths = dendro_transform(tree_object)

    linewidths = linewidths / min(linewidths) if show_diameters else 1

    xlabel = 'Length (um)'
    ylabel = ''

    if rotation == 'left':

        angle = pi

    elif rotation == 'up':

        angle = pi / 2.

        xlabel, ylabel = ylabel, xlabel

    elif rotation == 'down':

        angle = - pi / 2.

        xlabel, ylabel = ylabel, xlabel

    else:

        angle = 0.

    affine2D_transfrom(positions, cos(angle), -sin(angle), sin(angle), cos(angle))

    collection = LineCollection(positions, color='k', linewidth=linewidths)

    fig, ax = common.get_figure(new_fig=new_fig, subplot=subplot)

    ax.add_collection(collection)

    ax.autoscale(enable=True, tight=None)

    kwargs['title'] = 'Morphology Dendrogram'

    kwargs['xlabel'] = xlabel

    kwargs['ylabel'] = ylabel

    return common.plot_style(fig=fig, ax=ax, **kwargs)