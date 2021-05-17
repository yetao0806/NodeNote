from PyQt5 import QtGui, QtCore, QtWidgets
from GraphicsView.scene import Scene
from Components import effect_water, attribute, port, pipe, effect_background, effect_cutline, container
from Model import constants, stylesheet

__all__ = ["View"]


class View(QtWidgets.QGraphicsView):
    def __init__(self, mainwindow, parent=None):
        super(View, self).__init__(parent)
        self.mainwindow = mainwindow
        # BASIC SETTINGS
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.root_scene = Scene(self.mainwindow.scene_list, self)
        self.setScene(self.root_scene)
        self.background_image =  self.root_scene.background_image
        self.cutline = self.root_scene.cutline

        # SCALE FUNCTION
        self.zoomInFactor = 1.25
        self.zoomOutFactor = 0.8
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # SCROLLBAR
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.horizontal_scrollbar = QtWidgets.QScrollBar()
        self.horizontal_scrollbar.setStyleSheet(stylesheet.STYLE_HSCROLLBAR)
        self.setHorizontalScrollBar(self.horizontal_scrollbar)
        self.vertical_scrollbar = QtWidgets.QScrollBar()
        self.vertical_scrollbar.setStyleSheet(stylesheet.STYLE_VSCROLLBAR)
        self.setVerticalScrollBar(self.vertical_scrollbar)

        # DRAW LINE
        self.drag_pipe = None
        self.item = None
        self.mode = constants.MODE_NOOP

        # STORE
        self.attribute_widgets = list()
        self.logic_widgets = list()
        self.pipes = list()
        self.containers = list()

        # Container
        self.container_widget = None

        # SUB SCENE
        self.root_scene_flag = QtWidgets.QTreeWidgetItem(self.mainwindow.scene_list,
                                                         ("Root Scene",))
        self.root_scene_flag.setData(0, QtCore.Qt.ToolTipRole, self.root_scene)
        self.current_scene = self.root_scene
        self.current_scene_flag = self.root_scene_flag

    def set_leftbtn_beauty(self, event):
        water_drop = effect_water.EffectWater()
        property_water_drop = QtWidgets.QGraphicsProxyWidget()
        property_water_drop.setWidget(water_drop)
        self.current_scene.addItem(property_water_drop)
        water_drop.move(self.mapToScene(event.pos()))
        water_drop.show()
        super(View, self).mousePressEvent(event)

    def change_svg_image(self):
        image_name, image_type = QtWidgets.QFileDialog.getOpenFileName(self, "select svg", "", "*.svg")
        if image_name != "":
            self.background_image.change_svg(image_name)

    def change_scale(self, event):
        if constants.DEBUG_VIEW_CHANGE_SCALE:
            print("View is zooming! Current zoom: ", self.zoom)
        if event.key() == QtCore.Qt.Key_Equal and event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom += self.zoomStep
            if self.zoom <= self.zoomRange[1]:
                self.scale(self.zoomInFactor, self.zoomInFactor)
            else:
                self.zoom = self.zoomRange[1]
        elif event.key() == QtCore.Qt.Key_Minus and event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom -= self.zoomStep
            if self.zoom >= self.zoomRange[0]:
                self.scale(self.zoomOutFactor, self.zoomOutFactor)
            else:
                self.zoom = self.zoomRange[0]

    def view_update_pipe_animation(self):
        if len(self.current_scene.selectedItems()) == 1:
            item = self.current_scene.selectedItems()[0]
            if isinstance(item, attribute.AttributeWidget) or isinstance(item, attribute.LogicWidget):
                if not item.attribute_animation:
                    item.start_pipe_animation()
                else:
                    item.end_pipe_animation()

    def delete_connections(self, item):
        if isinstance(item, attribute.AttributeWidget):
            for pipe_widget in item.true_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.true_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)  # todo debug: when
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
        elif isinstance(item, attribute.LogicWidget):
            for pipe_widget in item.input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)

    def delete_widgets(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for item in self.current_scene.selectedItems():
                if item in self.current_scene.selectedItems():
                    if isinstance(item, attribute.AttributeWidget):
                        self.delete_connections(item)
                        for next_widget in item.next_attribute:
                            next_widget.remove_last_attribute(item)
                        for next_widget in item.next_logic:
                            next_widget.remove_last_attribute(item)
                        for last_widget in item.last_attribute:
                            last_widget.remove_next_attribute(item)
                        for last_widget in item.last_logic:
                            last_widget.remove_next_attribute(item)
                        if item.parentItem():
                            parent_item = item.parentItem()
                            parent_item.delete_subwidget(item)
                            self.remove_attribute_widget(item)
                        else:
                            self.remove_attribute_widget(item)
                    elif isinstance(item, attribute.LogicWidget):
                        self.delete_connections(item)
                        for next_widget in item.next_attribute:
                            next_widget.remove_last_logic(item)
                        for next_widget in item.next_logic:
                            next_widget.remove_last_logic(item)
                        for last_widget in item.last_attribute:
                            last_widget.remove_next_logic(item)
                        for last_widget in item.last_logic:
                            last_widget.remove_next_logic(item)
                        self.remove_logic_widget(item)
                    elif isinstance(item, pipe.Pipe):
                        self.delete_pipe(item)
                    elif isinstance(item, container.Container):
                        self.current_scene.removeItem(item)
                        self.containers.remove(item)

    def delete_pipe(self, item):
        end_node = item.get_input_node()
        start_node = item.get_output_node()
        if isinstance(end_node, attribute.AttributeWidget):
            start_node.remove_next_attribute(end_node)
        else:
            start_node.remove_next_logic(end_node)
        if isinstance(start_node, attribute.AttributeWidget):
            end_node.remove_last_attribute(start_node)
        else:
            end_node.remove_last_logic(start_node)

        input_port = item.get_input_type_port()
        output_port = item.get_output_type_port()
        input_port.remove_pipes(item)
        output_port.remove_pipes(item)

        self.current_scene.removeItem(item)
        self.pipes.remove(item)

    def add_attribute_widget(self, event):
        basic_widget = attribute.AttributeWidget()
        self.current_scene.addItem(basic_widget)
        basic_widget.setPos(self.mapToScene(event.pos()))
        self.attribute_widgets.append(basic_widget)

    def add_truth_widget(self, event):
        basic_widget = attribute.LogicWidget()
        self.current_scene.addItem(basic_widget)
        basic_widget.setPos(self.mapToScene(event.pos()))
        self.logic_widgets.append(basic_widget)

    def add_drag_pipe(self, port_widget, pipe_widget):
        port_widget.add_pipes(pipe_widget)
        self.pipes.append(pipe_widget)
        self.current_scene.addItem(pipe_widget)

    def remove_attribute_widget(self, widget):
        self.current_scene.removeItem(widget)
        self.attribute_widgets.remove(widget)

    def remove_logic_widget(self, widget):
        self.current_scene.removeItem(widget)
        self.logic_widgets.remove(widget)

    def remove_drag_pipe(self, port_widget, pipe_widget):
        port_widget.remove_pipes(pipe_widget)
        self.pipes.remove(pipe_widget)
        self.current_scene.removeItem(pipe_widget)

    def drag_pipe_press(self, event):
        super(View, self).mouseDoubleClickEvent(event)
        if self.mode == constants.MODE_NOOP:
            self.item = self.itemAt(event.pos())
            if constants.DEBUG_DRAW_PIPE:
                print("mouse double pressed at", self.item)
            if isinstance(self.item, port.Port):
                if constants.DEBUG_DRAW_PIPE:
                    print("enter the drag mode and set input port: ", self.item)
                self.mode = constants.MODE_PIPE_DRAG
                self.drag_pipe = pipe.Pipe(start_port=self.item, end_port=None, node=self.item.parentItem())
                self.add_drag_pipe(self.item, self.drag_pipe)
                return
            if isinstance(self.item, pipe.Pipe):
                self.mode = constants.MODE_PIPE_DRAG
                if constants.DEBUG_DRAW_PIPE:
                    print("delete the output port and drag again")
                self.drag_pipe = self.item
                self.item.delete_input_type_port(self.mapToScene(event.pos()))
                return
        if self.mode == constants.MODE_PIPE_DRAG:
            self.mode = constants.MODE_NOOP
            item = self.itemAt(event.pos())
            if constants.DEBUG_DRAW_PIPE:
                print("end the drag mode and set output port or not: ", item)
            self.drag_pipe_release(item)

    def drag_pipe_release(self, item):
        if self.drag_pipe.get_output_type_port():
            self.item = self.drag_pipe.get_output_type_port()
        else:
            self.item = self.drag_pipe.get_input_type_port()
        if isinstance(item, port.Port):
            if item.port_type != self.item.port_type and not self.judge_same_pipe(item):

                self.drag_pipe.end_port = item
                item.add_pipes(self.drag_pipe)
                self.drag_pipe.update_position()

                if item.get_node() is self.drag_pipe.get_output_node():
                    output_node = item.get_node()
                    input_node = self.item.get_node()
                else:
                    output_node = self.item.get_node()
                    input_node = item.get_node()
                if isinstance(output_node, attribute.AttributeWidget) \
                        and isinstance(input_node, attribute.AttributeWidget):
                    output_node.add_next_attribute(input_node)
                    input_node.add_last_attribute(output_node)
                elif isinstance(output_node, attribute.AttributeWidget) \
                        and isinstance(input_node, attribute.LogicWidget):
                    output_node.add_next_logic(input_node)
                    input_node.add_last_attribute(output_node)
                elif isinstance(output_node, attribute.LogicWidget) \
                        and isinstance(input_node, attribute.AttributeWidget):
                    output_node.add_next_attribute(input_node)
                    input_node.add_last_logic(output_node)
                elif isinstance(output_node, attribute.LogicWidget) \
                        and isinstance(input_node, attribute.LogicWidget):
                    output_node.add_next_logic(input_node)
                    input_node.add_last_logic(output_node)

                if input_node.attribute_animation or output_node.attribute_animation:
                    input_node.start_pipe_animation()
                    output_node.start_pipe_animation()

            else:
                if constants.DEBUG_DRAW_PIPE:
                    print("delete drag pipe case 1")
                self.remove_drag_pipe(self.item, self.drag_pipe)
                self.item = None
        elif not isinstance(item, port.Port):
            if constants.DEBUG_DRAW_PIPE:
                print("delete drag pipe case 2 from port: ", self.item)
            self.remove_drag_pipe(self.item, self.drag_pipe)
            self.item = None

    def judge_same_pipe(self, item):
        for same_pipe in item.pipes:
            if same_pipe in self.item.pipes:
                return True
        return False

    def cut_interacting_edges(self):
        if constants.DEBUG_CUT_LINE:
            print("All pipes: ", self.pipes)
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]
            for pipe_widget in self.pipes:
                if pipe_widget.intersect_with(p1, p2):
                    if constants.DEBUG_CUT_LINE:
                        print("Delete pipe", pipe_widget)
                    self.delete_pipe(pipe_widget)

    def cutline_pressed(self):
        self.mode = constants.MODE_PIPE_CUT
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def cutline_released(self):
        self.cut_interacting_edges()
        self.cutline.line_points = list()
        self.cutline.update()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        self.mode = constants.MODE_NOOP

    def container_pressed(self, event):
        self.mode = constants.MODE_CONTAINER
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        self.container_widget = container.Container(self.mapToScene(event.pos()))
        self.current_scene.addItem(self.container_widget)
        self.containers.append(self.container_widget)

    def container_released(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        self.mode = constants.MODE_NOOP

    def new_sub_scene(self, attribute_widget):
        if not attribute_widget.sub_scene:
            sub_scene_flag = QtWidgets.QTreeWidgetItem(self.current_scene_flag,
                                                       (attribute_widget.attribute_widget.label_item.toPlainText(),))
            sub_scene = Scene(sub_scene_flag, self, attribute_widget)
            self.background_image = sub_scene.background_image
            self.cutline = sub_scene.cutline

            attribute_widget.set_sub_scene(sub_scene)

            sub_scene_flag.setData(0, QtCore.Qt.ToolTipRole, sub_scene)
        else:
            sub_scene = attribute_widget.sub_scene

        self.setScene(sub_scene)
        self.current_scene = sub_scene
        self.current_scene_flag = sub_scene.sub_scene_flag

    def change_current_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem):
        self.current_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
        self.current_scene_flag = sub_scene_item
        self.setScene(self.current_scene)
        self.background_image = self.current_scene.background_image
        self.cutline = self.current_scene.cutline

    def delete_sub_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem):
        parent_flag = sub_scene_item.parent()

        if parent_flag:
            # change current scene
            self.change_current_scene(parent_flag)
            # delete
            parent_flag.removeChild(sub_scene_item)
            sub_scene_item.data(0, QtCore.Qt.ToolTipRole).attribute_widget.sub_scene = None

    def mousePressEvent(self, event) -> None:
        try:
            self.itemAt(event.pos()).scenePos()  # debug for scale, i don't understand but it work
        except AttributeError:
            pass
        if constants.DEBUG_DRAW_PIPE:
            print("mouse press at", self.itemAt(event.pos()))
        if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.cutline_pressed()
            return
        if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.container_pressed(event)
            return
        if event.button() == QtCore.Qt.LeftButton:
            self.set_leftbtn_beauty(event)
        item = self.itemAt(event.pos())
        if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.AltModifier and \
                isinstance(item, attribute.AttributeWidget):
            self.new_sub_scene(item)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mode == constants.MODE_PIPE_CUT:
            self.cutline_released()
            return
        if self.mode == constants.MODE_CONTAINER:
            self.container_released()
            return
        super(View, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pipe_press(event)
        else:
            super(View, self).mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mode == constants.MODE_PIPE_DRAG:
            self.drag_pipe.update_position(self.mapToScene(event.pos()))
        elif self.mode == constants.MODE_PIPE_CUT:
            self.cutline.line_points.append(self.mapToScene(event.pos()))
            self.cutline.update()
        elif self.mode == constants.MODE_CONTAINER:
            self.container_widget.next_point = self.mapToScene(event.pos())
            self.container_widget.update()
        super(View, self).mouseMoveEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == QtCore.Qt.Key_0 and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.view_update_pipe_animation()
        if event.key() == QtCore.Qt.Key_Delete or \
                (event.key() == QtCore.Qt.Key_Delete and int(event.modifiers()) & QtCore.Qt.ControlModifier):
            self.delete_widgets(event)
        if (event.key() == QtCore.Qt.Key_Equal and event.modifiers() & QtCore.Qt.ControlModifier) or \
                (event.key() == QtCore.Qt.Key_Minus and event.modifiers() & QtCore.Qt.ControlModifier):
            self.change_scale(event)
        else:
            super(View, self).keyPressEvent(event)

    def contextMenuEvent(self, event) -> None:
        super(View, self).contextMenuEvent(event)
        if not event.isAccepted():
            context_menu = QtWidgets.QMenu(self)
            # context list
            create_attribute_widget = context_menu.addAction("Create Attribute Widget")
            create_attribute_widget.setIcon(QtGui.QIcon("Resources/ViewContextMenu/Attribute Widget.png"))
            create_truth_widget = context_menu.addAction("Create Truth Widget")
            create_truth_widget.setIcon((QtGui.QIcon("Resources/ViewContextMenu/Truth Widget.png")))
            change_background_image = context_menu.addAction("Change Background Image")
            change_background_image.setIcon(QtGui.QIcon("Resources/ViewContextMenu/Change Background Image.png"))

            action = context_menu.exec_(self.mapToGlobal(event.pos()))
            if action == create_attribute_widget:
                self.add_attribute_widget(event)
            elif action == create_truth_widget:
                self.add_truth_widget(event)
            elif action == change_background_image:
                self.change_svg_image()

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        self.background_image.setPos(self.mapToScene(0, 0).x(), self.mapToScene(0, 0).y())
        self.background_image.resize(self.size().width(), self.size().height())
