import PySimpleGUI as sg
from scipy.interpolate import interp1d
from os_memory import *

'''processes_dict = {'p1': [("Code", 30, 40), ("Data", 0, 30), ("Stack", 100, 200)],
              'p2': [("Code", 70, 20), ("Data", 300, 50), ("Stack", 350, 100)]}'''


processes_dict = {}
processes_class = {}
keys = list(processes_dict.keys())
BAR_WIDTH = 150
BAR_SPACING = 110
EDGE_OFFSET = 3
GRAPH_SIZE = (400, 500)
DATA_SIZE = (400, 520)

sg.theme('Topanga')

Mem_size = 512

scale_slider_value = 0
offset_slider_value = 0

offsetSlider = [[sg.Slider(range=(0, 500), default_value=250, size=(25, 5), orientation="v",
                           enable_events=True, key="offset_slider",
                           disable_number_display=True, visible=False)]]

scaleSlider = [sg.Slider(range=(1, 10), default_value=1, size=(40, 5), pad=(20, 0), orientation="h",
                         enable_events=True, key="scale_slider", resolution=.1, disable_number_display=True,
                         visible=False)]

segmentsSlider = [[sg.Slider(range=(0, 10), default_value=0, size=(6, 5), pad=(0, 30), orientation="v",
                             enable_events=True, key="segments_slider",
                             disable_number_display=True, visible=False)]]

graph = sg.Graph(GRAPH_SIZE, (0, -20), DATA_SIZE, drag_submits=True, change_submits=True, key='graphmouse')
graph2 = sg.Graph((400, 180), (0, -20), (400, 180), visible=False, key='graph2')
layout_graph = [[sg.Text('Memory Visualization', pad=(131, 0), visible=False, key='memory_header')], [graph],
                [sg.Text('   scale:', key='zoom', visible=False)], scaleSlider]
layout_inputs = [
    [sg.Text('Enter memory size:', key='t1')],
    [sg.Input(justification='center', key='Mem_in')],
    [sg.Text('Hole\'s starting address:', key='t2'), sg.Input(justification='center', key='1', size=(10, 1)),
     sg.Text('Hole\'s size:', key='t3'), sg.Input(justification='center', key='2', size=(10, 1)),
     sg.Button('Add Hole', size=(10, 1), visible=True), sg.Button('Add Segment', size=(10, 1), visible=False)],
    [
        sg.Column([[graph2]]),
        sg.Column(segmentsSlider)
    ],
    [sg.Radio('Best fit', visible=False, key='best', default=True, group_id='algo'),
     sg.Radio('First fit', visible=False, key='first', group_id='algo'),
     sg.Radio('Worst fit', visible=False, key='worst', group_id='algo')],
    [sg.Button('Allocate', key='allocate', visible=False, size=(20, 1))],
    [sg.HorizontalSeparator(key='h', pad=(0, 15))],
    [sg.Text('Choose process to deallocate:', key='t4', visible=False)],
    [sg.Combo(values=keys, key='menu', visible=False, size=(40, 1), readonly=True)],
    [sg.Button('Deallocate', key='deallocate', visible=False, size=(20, 1), pad=(0, 10))],
    [sg.Button('Memory Defragmentation', key='fragmentation', visible=False, size=(20, 1))],
    [sg.Button('Next', size=(15, 1))]
]
holes = []
segments = []
layout = [
    [sg.Column(offsetSlider),
     sg.Column(layout_graph, key='graph'),
     sg.VSeparator(),
     sg.Column(layout_inputs, element_justification='center', key='mem_size_in')
     ]
]
process_index = 1
window = sg.Window('Window Title', layout)
inputs_taken = False
mouseX = 0
mouseY = 250
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Add Hole':
        try:
            hole_start = int(values['1'])
            hole_size = int(values['2'])
            if hole_start < 0 or hole_size <= 0:
                sg.popup_error('Hole\'s starting address and size must be greater than zero', title='Error')
            else:
                holes.append([hole_start, hole_size])

        except ValueError:
            sg.popup_error('Hole\'s starting address and size must be integer', title='Error')
        window['1'].update('')
        window['2'].update('')
        graph.erase()
        graph.draw_text(text="Hole\'s starting address", location=(150, 500), color='white', )
        graph.draw_text(text="Hole\'s size", location=(300, 500), color='white')
        for i in range(len(holes)):
            graph.draw_rectangle(top_left=(70, 480 - (i * 25)), bottom_right=(350, 460 - (i * 25)),
                                 fill_color='#284B5A')
            graph.draw_text(text='Hole ' + str(i + 1), location=(30, 470 - (i * 25)), color='#E7C855')
            graph.draw_text(text=holes[i][0], location=(150, 470 - (i * 25)), color='#E7C855', )
            graph.draw_text(text=holes[i][1], location=(300, 470 - (i * 25)), color='#E7C855')

    elif event == 'Add Segment':
        try:
            segment_name = values['1']
            segment_size = int(values['2'])
            if segment_size <= 0:
                sg.popup_error('Segment size must be greater than zero', title='Error')
            else:
                segments.append([segment_name, segment_size])

        except ValueError:
            sg.popup_error('Segment size must be integer', title='Error')
        window['1'].update('')
        window['2'].update('')
        graph2.erase()
        graph2.draw_text(text="Segment name", location=(135, 170), color='white')
        graph2.draw_text(text="Segment size", location=(285, 170), color='white')
        for i in range(len(segments)):
            graph2.draw_rectangle(top_left=(70, 155 - (i * 25)), bottom_right=(350, 135 - (i * 25)),
                                  fill_color='#284B5A')
            graph2.draw_text(text=segments[i][0], location=(135, 145 - (i * 25)), color='#E7C855')
            graph2.draw_text(text=segments[i][1], location=(285, 145 - (i * 25)), color='#E7C855')
        if len(segments) > 7:
            window['segments_slider'].update(visible=True, range=(0, (len(segments) - 7) * 25))

    elif event == 'segments_slider':
        graph2.erase()
        graph2.draw_text(text="Segment name", location=(135, 170 + values['segments_slider']), color='white', )
        graph2.draw_text(text="Segment size", location=(285, 170 + values['segments_slider']), color='white')
        for i in range(len(segments)):
            graph2.draw_rectangle(top_left=(70, 155 - (i * 25) + values['segments_slider']),
                                  bottom_right=(350, 135 - (i * 25) + values['segments_slider']),
                                  fill_color='#284B5A')
            graph2.draw_text(text=segments[i][0], location=(135, 145 - (i * 25) + values['segments_slider']),
                             color='#E7C855')
            graph2.draw_text(text=segments[i][1], location=(285, 145 - (i * 25) + values['segments_slider']),
                             color='#E7C855')

    elif event == 'Next':
        try:
            Mem_size = abs(int(values['Mem_in']))

        except ValueError:
            sg.popup('Invalid Memory size, size will be set to default (512).', title='Warning')
            Mem_size = 512
        processes_class = DynamicAllocator(Mem_size, holes)
        processes_dict = processes_class.initalize_memory()
        keys = list(processes_dict.keys())
        window['menu'].update(values=keys, size=(40, 1))
        inputs_taken = True
        window['Mem_in'].hide_row()
        window['Next'].hide_row()
        # window.extend_layout(window['mem_size_in'], new_layout(0))
        window['t1'].update('Process ' + str(process_index))
        window['t2'].update('Segment name:')
        window['t3'].update('Size:')
        window['Add Hole'].update(visible=False)
        window['Add Segment'].update(visible=True)
        window['allocate'].update(visible=True)
        window['deallocate'].update(visible=True)
        window['menu'].update(visible=True)
        window['t4'].update(visible=True)
        window['graph2'].update(visible=True)
        window['best'].update(visible=True)
        window['first'].update(visible=True)
        window['worst'].update(visible=True)
        window['scale_slider'].update(visible=True)
        window['zoom'].update(visible=True)
        window['memory_header'].update(visible=True)
        window['fragmentation'].update(visible=True)

    elif event == 'allocate':
        # segments array will be passed to a function to add it to dict.
        # Update values of menu.
        if len(segments) != 0:
            if values['best']:
                processes_dict, size_check = processes_class.best_fit(process_index, segments)
            elif values['first']:
                processes_dict, size_check = processes_class.first_fit(process_index, segments, 0)
            elif values['worst']:
                processes_dict, size_check = processes_class.worst_fit(process_index, segments)

            if size_check == 1:
                sg.popup('failed to allocate memory for Process ' + str(process_index), title='Warning')

            segments = []
            graph2.erase()
            process_index += 1
            keys = list(processes_dict.keys())
            window['t1'].update('Process ' + str(process_index))
            window['menu'].update(values=keys, size=(40, 1))
            window['segments_slider'].update(visible=False)

    elif event == 'fragmentation':
        processes_dict = processes_class.defragmentation()

    elif event == 'deallocate':
        process = values['menu']
        if process != '':
            _, processes_dict = processes_class.remove_process(process)
            keys = list(processes_dict.keys())
            window['menu'].update(values=keys, size=(40, 1))
        else:
            sg.popup('Please select a process to deallocate', title='Error')

    # mouse position
    elif event == 'graphmouse':
        temp1, temp2 = values['graphmouse']
        if 0 < temp2 < 500:
            if (mouseY - 40) < temp2 < (mouseY + 40):
                mouseX, mouseY = values['graphmouse']

    if inputs_taken:
        graph.erase()

        graph.draw_rectangle(top_left=(BAR_SPACING + EDGE_OFFSET,
                                       (GRAPH_SIZE[1] - values['offset_slider']) * values['scale_slider'] + values[
                                           'offset_slider']),
                             bottom_right=(BAR_SPACING + EDGE_OFFSET + BAR_WIDTH,
                                           (0 - values['offset_slider']) * values['scale_slider'] + values[
                                               'offset_slider']), fill_color='gray',
                             line_color='black', line_width=1)
        graph.draw_text(text=0, location=(
            BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH + 15),
            (GRAPH_SIZE[1] - values['offset_slider']) * values['scale_slider'] + values['offset_slider']),
                        color='white', )
        graph.draw_text(text=Mem_size, location=(
            BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH + 15),
            (GRAPH_SIZE[1] - values['offset_slider'] - (Mem_size * (GRAPH_SIZE[1] / Mem_size))) * values[
                'scale_slider'] + values['offset_slider']),
                        color='white')

        # middle digits
        x = (GRAPH_SIZE[1] - values['offset_slider']) * values['scale_slider'] + values['offset_slider']
        y = (0 - values['offset_slider']) * values['scale_slider'] + values['offset_slider']
        m = interp1d(
            [x, y],
            [0, Mem_size])

        graph.draw_text(text=round(float(m(mouseY))), location=(
            BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH + 60),
            mouseY),
                        color='white', )

        # show,hide and reset the offset slider
        if values['scale_slider'] == 1.0:
            window['offset_slider'].update(visible=False)
            window['offset_slider'].update(value=250)
        else:
            window['offset_slider'].update(visible=True)
        for key in processes_dict:
            for seg in processes_dict[key]:
                graph.draw_rectangle(
                    top_left=(BAR_SPACING + EDGE_OFFSET,
                              (GRAPH_SIZE[1] - (seg[1]) * (GRAPH_SIZE[1] / Mem_size) - values['offset_slider']) *
                              values['scale_slider']
                              + values['offset_slider']),
                    bottom_right=(BAR_SPACING + EDGE_OFFSET + BAR_WIDTH,
                                  (GRAPH_SIZE[1] - ((seg[1] + seg[2]) * (GRAPH_SIZE[1] / Mem_size)) - values[
                                      'offset_slider']) * values['scale_slider']
                                  + values['offset_slider']),
                    fill_color='#284B5A', line_color='black', line_width=1)
                graph.draw_text(text=key + ": " + seg[0], location=(BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH / 2),
                                                                    (GRAPH_SIZE[1] - (
                                                                            (seg[1] + seg[1] + seg[2]) / 2) * (
                                                                             GRAPH_SIZE[1] / Mem_size) - values[
                                                                         'offset_slider']) * (values['scale_slider'])
                                                                    + values['offset_slider']),
                                color='#E7C855')
                graph.draw_text(text=seg[1], location=(
                    BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH + 15),
                    (GRAPH_SIZE[1] - (seg[1]) * (GRAPH_SIZE[1] / Mem_size) - values['offset_slider']) * (
                        values['scale_slider'])
                    + values['offset_slider']),
                                color='white', )
                graph.draw_text(text=(seg[1] + seg[2]), location=(BAR_SPACING + EDGE_OFFSET + (BAR_WIDTH + 15),
                                                                  (GRAPH_SIZE[1] - ((seg[1] + seg[2]) * (
                                                                          GRAPH_SIZE[1] / Mem_size)) - values[
                                                                       'offset_slider']) * (values['scale_slider'])
                                                                  + values['offset_slider']),
                                color='white')
                # middle line
        graph.draw_rectangle(top_left=(85, mouseY), bottom_right=(290, mouseY), line_color='white')
window.close()
