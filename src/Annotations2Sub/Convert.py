#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from datetime import datetime
from typing import List, Optional, cast
from xml.etree.ElementTree import Element

from Annotations2Sub.Annotation import Annotation
from Annotations2Sub.Color import Alpha, Color
from Annotations2Sub.Sub import Draw, Event, Point


def Parse(tree: Element) -> List[Annotation]:
    """XML 树转换为 Annotation 结构列表"""

    def ParseAnnotationAlpha(annotation_alpha_str: str) -> Alpha:
        """
        解析 Annotation 的透明度
        bgAlpha="0.600000023842" -> Alpha(alpha=102)
        """
        s0 = annotation_alpha_str
        if s0 == None:
            raise Exception("alpha is None")
        s1 = float(s0)
        s2 = 1 - s1
        s3 = s2 * 255
        s4 = int(s3)
        s5 = Alpha(alpha=s4)
        return s5

    def ParseAnnotationColor(annotation_color_str: str) -> Color:
        """
        bgColor="4210330" -> Color(red=154, green=62, blue=64)
        """
        s0 = annotation_color_str
        if s0 == None:
            raise Exception("color is None")
        s1 = int(s0)
        r = s1 & 255
        g = (s1 >> 8) & 255
        b = s1 >> 16
        s2 = Color(red=r, green=g, blue=b)
        return s2

    def White() -> Color:
        return Color(red=255, green=255, blue=255)

    def Black() -> Color:
        return Color(red=0, green=0, blue=0)

    def DefaultTransparency() -> Alpha:
        return Alpha(alpha=204)

    def MakeSureStr(s: Optional[str]) -> str:
        if isinstance(s, str):
            return str(s)
        raise TypeError

    def ParseAnnotation(each: Element) -> Optional[Annotation]:
        # 致谢: https://github.com/nirbheek/youtube-ass
        # 致谢: https://github.com/isaackd/annotationlib
        annotation = Annotation()

        annotation.id = MakeSureStr(each.get("id"))

        type = each.get("type")
        if type not in ("text", "highlight", "branding"):
            return None
        annotation.type = type  # type: ignore

        annotation.style = each.get("style")  # type: ignore

        text = each.find("TEXT")
        if text is not None:
            annotation.text = MakeSureStr(text.text)

        if len(each.find("segment").find("movingRegion")) == 0:  # type: ignore
            # 跳过没有内容的 Annotation
            return None

        Segment = each.find("segment").find("movingRegion").findall("rectRegion")  # type: ignore
        if len(Segment) == 0:
            Segment = (
                each.find("segment").find("movingRegion").findall("anchoredRegion")  # type: ignore
            )

        if len(Segment) == 0:
            if annotation.style != "highlightText":
                # 抄自 https://github.com/isaackd/annotationlib/blob/master/src/parser/index.js 第121行
                # "highlightText" 是一直显示在屏幕上的, 不应没有时间
                return None

        if len(Segment) != 0:
            t1 = MakeSureStr(Segment[0].get("t"))
            t2 = MakeSureStr(Segment[1].get("t"))
            Start = min(t1, t2)
            End = max(t1, t2)

        if "never" in (Start, End):
            # 跳过不显示的 Annotation
            return None

        try:
            annotation.timeStart = datetime.strptime(Start, "%H:%M:%S.%f")
            annotation.timeEnd = datetime.strptime(End, "%H:%M:%S.%f")
        except:
            annotation.timeStart = datetime.strptime(Start, "%M:%S.%f")
            annotation.timeEnd = datetime.strptime(End, "%M:%S.%f")

        annotation.x = float(MakeSureStr(Segment[0].get("x")))
        annotation.y = float(MakeSureStr(Segment[0].get("y")))

        def a(a) -> Optional[float]:
            if a is None:
                return None
            if isinstance(a, str):
                return float(a)
            raise TypeError

        annotation.width = a(Segment[0].get("w"))
        annotation.height = a(Segment[0].get("h"))
        annotation.sx = a(Segment[0].get("sx"))
        annotation.sy = a(Segment[0].get("sy"))

        Appearance = each.find("appearance")

        if Appearance != None:
            bgAlpha = MakeSureStr(Appearance.get("bgAlpha"))  # type: ignore
            bgColor = MakeSureStr(Appearance.get("bgColor"))  # type: ignore
            fgColor = MakeSureStr(Appearance.get("fgColor"))  # type: ignore
            textSize = MakeSureStr(Appearance.get("textSize"))  # type: ignore

        if bgAlpha != None:
            annotation.bgOpacity = ParseAnnotationAlpha(bgAlpha)
        else:
            annotation.bgOpacity = DefaultTransparency()

        if bgColor != None:
            annotation.bgColor = ParseAnnotationColor(bgColor)
        else:
            annotation.bgColor = White()

        if fgColor != None:
            annotation.fgColor = ParseAnnotationColor(fgColor)
        else:
            annotation.fgColor = Black()

        if textSize != None:
            annotation.textSize = float(textSize)
        else:
            annotation.textSize = 3.15

        return annotation

    annotations: List[Annotation] = []
    for each in tree.find("annotations").findall("annotation"):  # type: ignore
        annotation = ParseAnnotation(each)
        if annotation != None:
            annotations.append(annotation)  # type: ignore

    return annotations


def Convert(annotations: List[Annotation], libass: bool) -> List[Event]:
    """将 Annotation 列表转换为 Event 列表"""

    def MakeSureFloat(a: Optional[float]) -> float:
        if isinstance(a, float):
            return float(a)
        raise TypeError

    def ConvertAnnotation(each: Annotation) -> List[Event]:
        # 致谢: https://github.com/nirbheek/youtube-ass
        # 致谢: https://github.com/weizhenye/ASS/wiki/ASS-字幕格式规范
        events = []
        event = Event()

        event.Start = each.timeStart
        event.End = each.timeEnd
        event.Name = each.id

        text = each.text
        if text is None:
            text = ""
        text = text.replace("\n", r"\N")
        if libass:
            # 仅 libass 支持大括号转义
            text = text.replace(r"{", r"\{")
            text = text.replace(r"}", r"\}")
        event.Text = text

        if each.style == "popup":
            event.Name = event.Name + "_popup"
            # todo
            #
            events.append(event)

            event = copy.copy(event)
            width = MakeSureFloat(each.width)
            if libass:
                # 针对 libass 的 hack
                width = width * 1.776
            width = round(width, 3)

            d = Draw()
            d.Add(Point(0, 0, "m"))
            d.Add(Point(width, 0, "l"))
            d.Add(Point(width, each.height, "l"))
            d.Add(Point(0, each.height, "l"))
            d_str = d.Dump()
            box = r"{\p1}" + d_str + r"{\p0}"
            # todo
            #
            event.Text = box
            event.Name = event.Name + "_box"
            events.append(event)

        elif each.style == "title":
            pass
        elif each.style == "speech":
            pass
        elif each.style == "highlightText":
            pass

        return events

    events = []
    for each in annotations:
        events.extend(ConvertAnnotation(each))

    return events
