# ui/custom_widgets.py
from PyQt6.QtWidgets import QTreeWidget, QAbstractItemView
from PyQt6.QtCore import Qt

class RobustTreeWidget(QTreeWidget):
    """高级交互拖拽架构树：实现纯物理层级变更，完美保留节点内部绑定的 UserRole 数据字典"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        if event.source() == self:
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        target_item = self.itemAt(event.position().toPoint())
        # 安全规约：如果拖拽提示线处于“文件”项的正上方，严禁放置（文件不能吞噬其他节点）
        if target_item and target_item.data(0, Qt.ItemDataRole.UserRole) == "file":
            if self.dropIndicatorPosition() == QAbstractItemView.DropIndicatorPosition.OnItem:
                event.ignore()
                return
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.source() != self:
            event.ignore()
            return

        dragged_item = self.currentItem()
        if not dragged_item:
            event.ignore()
            return

        target_item = self.itemAt(event.position().toPoint())
        indicator = self.dropIndicatorPosition()

        # 闭环保护：严禁将一个父文件夹拖入它自己的子孙目录中
        p = target_item
        while p:
            if p == dragged_item:
                event.ignore()
                return
            p = p.parent()

        # 切断旧有的层级脐带
        parent = dragged_item.parent()
        if parent:
            parent.removeChild(dragged_item)
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(dragged_item))

        # 根据拖动结束时的物理指示线，进行安全的内存位置重排
        if not target_item:
            self.addTopLevelItem(dragged_item)
        else:
            if indicator == QAbstractItemView.DropIndicatorPosition.OnItem:
                if target_item.data(0, Qt.ItemDataRole.UserRole) == "folder":
                    target_item.addChild(dragged_item)
                    self.expandItem(target_item)
                else:
                    t_parent = target_item.parent()
                    if t_parent:
                        t_parent.insertChild(t_parent.indexOfChild(target_item) + 1, dragged_item)
                    else:
                        self.insertTopLevelItem(self.indexOfTopLevelItem(target_item) + 1, dragged_item)
            elif indicator == QAbstractItemView.DropIndicatorPosition.AboveItem:
                t_parent = target_item.parent()
                if t_parent:
                    t_parent.insertChild(t_parent.indexOfChild(target_item), dragged_item)
                else:
                    self.insertTopLevelItem(self.indexOfTopLevelItem(target_item), dragged_item)
            elif indicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
                t_parent = target_item.parent()
                if t_parent:
                    t_parent.insertChild(t_parent.indexOfChild(target_item) + 1, dragged_item)
                else:
                    self.insertTopLevelItem(self.indexOfTopLevelItem(target_item) + 1, dragged_item)

        self.setCurrentItem(dragged_item)
        event.acceptProposedAction()
        # 拖拽重排后主动发射点击事件，让左侧属性面板感知并刷新同步
        self.itemClicked.emit(dragged_item, 0)