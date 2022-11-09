import matplotlib
matplotlib.use("nbagg")
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import times
import visualizer

import matplotlib.pyplot as plt
import numpy as np
from os.path import exists




def interactive_plot(result, id_list, data_class):

    if exists('interactive_cache.png') == False:
        fig = plt.figure()
        plt.savefig('interactive_cache.png')
        plt.close(fig)

    result_stack = np.vstack(result)
    color_map_list = []
    window_indices_stack_list = []
    window_number_list = []
    for id in id_list:
        color_map_list.append(data_class[id].color_map)
        window_indices_stack_list.append(data_class[id].window_indices_stack)
        window_number_list.append(data_class[id].window_n)
    color_map_stack = np.hstack(color_map_list)
    window_indices_stack_stack = np.vstack(window_indices_stack_list)

    x = result_stack[:, 0]
    y = result_stack[:, 1]
    color_map = np.hstack(color_map_stack)

    norm = plt.Normalize(1, 4)
    cmap = plt.cm.RdYlGn

    fig, ax = plt.subplots(figsize=(10, 8))
    try:
        sc = plt.scatter(x, y, c=color_map, s=10, cmap=cmap, norm=norm)
    except:
        sc = plt.scatter(x, y, c='k', s=10, cmap=cmap, norm=norm)

    arr_img = plt.imread("interactive_cache.png", format='png')
    imagebox = OffsetImage(arr_img, zoom=0.5)
    imagebox.image.axes = ax

    ax.set_aspect(1.0)

    ab = AnnotationBbox(imagebox, xy=(0, 0),
                        xybox=(40, 40),
                        xycoords='data',
                        boxcoords="offset points",
                        pad=0.5,
                        arrowprops=dict(
                            arrowstyle="->", )
                        )

    # annot = ax.annotate("", xy=(0, 0), xytext=(-20, -20), textcoords="offset points",
    #                     bbox=dict(boxstyle="round", fc="w"),
    #                     arrowprops=dict(arrowstyle="->"))
    # annot.set_visible(False)

    ax.add_artist(ab)
    ab.set_visible(False)

    def update_annot(ind):

        pos = sc.get_offsets()[ind["ind"][0]]
        ab.xy = pos
        closest_ind = [ind["ind"][0]]
        patient_id, _ = visualizer.stack_patient_match(closest_ind, id_list, window_number_list)

        catalog_ind = times.find_closest_event_ind(window_indices_stack_stack[closest_ind, 0],
                                            data_class[patient_id].catalog['Event Start idx'])
        raw_data = data_class[patient_id].data[data_class[patient_id].catalog['Event Start idx'][catalog_ind]:
                                               data_class[patient_id].catalog['Event End idx'][catalog_ind]]
        df = data_class[patient_id].catalog.iloc[catalog_ind]
        visualizer.int_clips(raw_data, df, catalog_ind, window_indices_stack_stack[closest_ind, 0],
                             window_indices_stack_stack[closest_ind, 1])
        arr_img = plt.imread("interactive_cache.png", format='png')
        imagebox.set_data(arr_img)
        # annot.xy = pos

        # text = str(ind)
        # annot.set_text(text)
        # annot.get_bbox_patch().set_facecolor(cmap(norm(color_map[ind["ind"][0]])))
        # annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = ab.get_visible()
        if event.inaxes == ax:
            cont, ind = sc.contains(event)
            if cont:
                if event.button == 1:
                    update_annot(ind)
                    # annot.set_visible(True)
                    ab.set_visible(True)
                    fig.canvas.draw_idle()
                elif event.button == 3:
                    ab.set_visible(False)
                    fig.canvas.draw_idle()
            else:
                if vis:
                    ab.set_visible(False)
                    # annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_release_event", hover)

    plt.show()
