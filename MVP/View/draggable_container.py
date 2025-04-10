# MVP/View/draggable_container.py
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItemGroup
from PyQt6.QtGui import QPen, QColor, QCursor
from PyQt6.QtCore import Qt

class DraggableContainer(QGraphicsRectItem):
    def __init__(self, track_height, max_pos: tuple[int, int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_height = track_height
        self.max_pos = max_pos
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.setZValue(1)
        self.notes_group = QGraphicsItemGroup(self)
        self.current_track = 0

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.snap_to_tracks()
        if self.x() < 0:
            self.setX(0)
        if self.y() < 0:
            self.setY(0)
        if self.y() > self.max_pos[1] - self.track_height:
            self.setY(self.max_pos[1] - self.track_height)
        if self.x() > self.max_pos[0] - self.boundingRect().width():
            self.setX(self.max_pos[0] - self.boundingRect().width())

    def snap_to_tracks(self):
        new_y = round(self.y() / self.track_height) * self.track_height
        self.setY(new_y)
        self.current_track = int(new_y / self.track_height)
        
    def mousePressEvent(self, event):
        print(f"Container clicked at track {self.current_track}")
        super().mousePressEvent(event)