#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from typing import Literal, Optional

from Annotations2Sub.Color import Alpha, Color
from . import *


class Annotation(object):
    # 致谢 https://github.com/isaackd/annotationlib
    """Annotation 结构"""

    def __init__(self):
        self.id: str = ""
        # 这里仅列出需要的的 type 和 style
        self.type: Literal["text", "highlight", "branding"] = ""
        self.style: Literal[
            "popup",
            "title",
            "speech",
            "highlightText",
        ] = ""
        self.text: Optional[str] = ""
        self.timeStart: datetime.datetime = datetime.datetime()
        self.timeEnd: datetime.datetime = datetime.datetime()
        self.x: float = 0.0
        self.y: float = 0.0
        self.width: float = 0.0
        self.height: float = 0.0
        # sx, sy 是气泡锚点
        self.sx: float = 0.0
        self.sy: float = 0.0
        self.bgOpacity: Alpha = Alpha()
        self.bgColor: Color = Color()
        self.fgColor: Color = Color()
        self.textSize: float = 0.0
        # Sub 无法实现 action
        # self.actionType: Optional[str] = ''
        # self.actionUrl: Optional[str] = ''
        # self.actionUrlTarget: Optional[str] = ''
        # self.actionSeconds: float = 0.0
        # self.highlightId: Optional[str] = ''
